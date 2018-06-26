import re
import time
import pymysql
import urllib.parse

URL_FUNC_DICT=dict()

def route(url):
    def set_func(func):
        URL_FUNC_DICT[url] = func
        def wrapper(*args,**kwargs):
            return func(*args,**kwargs)
        return wrapper
    return set_func

def con_db(my_sql,*args):

    print("这是数据库")
    conn=pymysql.connect(host="localhost",port=3306,user="root",
                       password="mysql",database="stock_db",
                       charset="utf8")
    cur=conn.cursor()
    print("连接陈宫")
 
    cur.execute(my_sql,args)
    result=cur.fetchall()
 

    
    print(result)
    conn.commit()
    cur.close()
    conn.close()
    return result


@route(r"/index\.html")
def index(ret):
    print("---------")
    with open("./templates/index.html",encoding="utf-8") as f:
        content=f.read()
    sql="select * from info;"
    templat='''
        <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemIdVaule="%s">
            
        </td>
        </tr>
        '''
    html=""
    print("调用连接")
    templat_tuple=con_db(sql)
    for item in templat_tuple:
        print(item)
        turn_string=templat%(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[1])
        html+=turn_string
    content=re.sub(r"\{%content%\}",html,content)
    return content
@route(r"/center\.html")
def center(ret):
    with open("./templates/center.html",encoding="utf-8") as f:
        content=f.read()
    template_string="""
        <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>      
        <td>
            <a type="button" class="btn btn-default btn-xs"
            href="/update/%s.html"><span>修改</span></a>        
        </td>
        <td>
            <input type="button" value="删除" id="toDel"
            name="toDel" systemIdVaule="%s">
        </td>
        </tr>
            
    """

    sql="""
        select i.code,i.short,i.chg,i.turnover,i.price,i.highs,
        f.note_info from info as i inner join focus as f 
        on f.info_id = i.id;
    """
    html=""
    template_tuple=con_db(sql)
    for item in template_tuple:
        html+=template_string%(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[0],item[0])
    content=re.sub(r"\{%content%\}",html,content)
    return content
@route(r"/add/(\d+)\.html")
def add_focus(ret):
    #获取匹配的的股票编码
    stock_code=ret.group(1)
    search_sql="select id from info where code = %s;"
    result_info=con_db(search_sql,stock_code)
    # print("--------")
    # print(result_info)
    if not result_info:
        return "大哥,手下留情,创业公司."
    #检测是否是含有该股票编码
    
    # print("------------")
    # #检测该股票编码是否已经添加
    # print(result_info[0][0])
    search_sql="select id from focus where info_id=%s"
    result_focus=con_db(search_sql,int(result_info[0][0]))
    # print("=============")
    # print(result_focus)
    #将该股票添加进去
    
    insert_sql="insert into focus(info_id) values(%s)"
    result_insert=con_db(insert_sql,int(result_info[0][0]))
    # print("++++++++++++")
    # print(result_insert)

    return "add ok %s"%stock_code
@route(r"/del/(\d+)\.html")
def del_focus(ret):
    stock_code=ret.group(1)
    # return "stock_code%s"%stock_code
    #判断是否已经关注了这个code
    print("开始执行sql语句")
    sql="""
       select f.id from focus as f where f.info_id=(select id from info  where info.code = %s);
    """

    result_judge=con_db(sql,stock_code)
    print(result_judge)
    if  not result_judge:
        return "请先关注再取消"
    #删除已经关注了的这个code
    del_sql="""
            delete from focus where focus.id = %s;
        """
    con_db(del_sql,int(result_judge[0][0]))
    return "delete ok %s" %result_judge[0][0]
@route(r"/update/(\d+).html")
def update_info(ret):
    stock_code=ret.group(1)
    print("调用打开文件")
    with open ("./templates/update.html","r",encoding="utf-8") as f:
        print("文件错误")
        content = f.read()

    content=re.sub(r"\{%code%\}",stock_code,content)
    get_sql="select f.note_info from focus as f where f.info_id=(select id from info  where info.code = %s);"
    infomation=con_db(get_sql,stock_code)
    content=re.sub(r"\{%note_info%\}",infomation[0][0],content)

    return content
@route(r"/update/(\d+)/(.*?).html")
def modify_note(ret):
    stock_code=ret.group(1)
    stock_note=ret.group(2)
    stock_note=urllib.parse.unquote(stock_note)
    update_sql="select id from info where code =%s;"
    result_id=con_db(update_sql,stock_code)
    up_sql="update focus set note_info =%s where info_id=%s;"
    con_db(up_sql,stock_note,result_id[0][0])
    # update_sql="""
    #     update focus as f set f.note_info = %s where f.info_id= (select
    #     i.id from info as i where code = %s ;)
    # """
    # con_db(update_sql,stock_note,stock_code)
    return "--ok"

def application(env,start_response):

    start_response("200 OK",[("Content-type","text/html;charset=utf-8")])
    url_path=env["file_path"]
    try:
        for url,func in URL_FUNC_DICT.items():
            print(url)
            print(url_path)
            ret = re.match(url,url_path)
            print(ret)
            if ret:
                print("开始调用函数了")
                return func(ret)
        else:
            return "请求的url(%s)没有对应的函数......" % file_name
    except Exception:
        return "出现错误"