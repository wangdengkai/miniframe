import socket
import multiprocessing
import re
import sys

class WebServer(object):
    def __init__(self,port=7890,app=None,static_path=None):
        #创建套接字,生成服务器
        self.tcp_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #设置地址复用
        self.tcp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        #绑定地址
        self.tcp_socket.bind(("127.0.0.1",port))
        #变为监听模式
        self.tcp_socket.listen(3)
        self.header=[("server","mini_web v8.8")]
        self.app=app
        self.static=static_path

    def handle_connect(self,new_client):
        #接受浏览器发来的消息
        browse_msg=new_client.recv(1024)
        # print(browse_msg)
        #将二进制转化为字符串
        browse_msg_str=browse_msg.decode("utf-8")
        browse_msg_list=browse_msg_str.splitlines()
        if not len(browse_msg_list):
            return 
        #从字符串中匹配出路径
        request_url=re.match("[^/]*(/[^ ]*)",browse_msg_list[0])
        if request_url:
            #匹配到东西
            file_name=request_url.group(1)
            if file_name=="/":
                file_name='/index.html'
        else:
            file_name="/index.html"
        if not file_name.endswith(".html"):
            try:
                if file_name == "/index.html":
                    f=open("./templates/index.html",'rb')
                else:
                    # print(self.static%s"%file_name)
                    f=open(self.static+file_name,'rb')
            except Exception:
                response="HTTP/1.1 404 not found \r\n"
                response+="\r\n"
                response+="--------file not found------"
                new_client.send(response.encode("utf-8"))
            else:
                html_content=f.read()
                f.close()
                response="HTTP/1.1 200 Ok\r\n"
                response+="\r\n"
                new_client.send(response.encode("utf-8"))
                new_client.send(html_content)
        else:
            #如果是用.py结尾的那么就认为是动态请求
            # response="HTTP/1.1 200 OK\r\n\r\n"
            # response_body="hahaha"
            # new_client.send(response.encode("utf-8"))
            # new_client.send(response_body.encode("utf-8"))
            #调用框架
            env={
                "file_path":file_name
            }
            response_body=self.app(env,self.set_header)
            header="HTTP/1.1 %s\r\n"%self.status
            for temp in self.header:
                header+="%s:%s\r\n"%(temp[0],temp[1])
            header+="\r\n"
            new_client.send(header.encode("utf-8"))
            new_client.send(response_body.encode("utf-8"))
        new_client.close()

    def set_header(self,status,response_header):
        self.status=status
        self.header+=response_header
    def run_forever(self):
        #开启无限循环,接受服务器的连接
        print("服务器运行啦")
        while True:
            #接受连接,生成新的对象和地址
            new_client,new_addr=self.tcp_socket.accept()
            #创建一个进程处理新的连接
            p_client=multiprocessing.Process(target=self.handle_connect,args=(new_client,))
            p_client.start()
            print("有一个新的连接")
            new_client.close()

    def __del__(self):
        #关闭服务器套接字
        self.tcp_socket.close()


def main():

    if len(sys.argv)==3:
        port=sys.argv[1]
        package_name=sys.argv[2]
        try:
            port = int(port)
        except Exception:
            print("请输入正确的端口号")
            print("运行格式为:python web_server.py 7890")
            return

    else:
        print("请输入正确的命令方式")
        print("运行格式为:python web_server.py 7890 miniframe:application")
        return
    with open("./web_server.conf") as f:
        content=eval(f.read())
    sys.path.append(content["frame_path"])
    package_name_list=package_name.split(":")
    # sys.path.append("./frame")
    print(package_name_list)
    app_name=package_name_list[1]
    frame_name=package_name_list[0]
    #导入模块,获得运行方法
    frame=__import__(frame_name)
    app=getattr(frame,app_name)
    print(content["static_path"])
    # 创建服务器对象,运行服务器
    web_ser=WebServer(port,app,content["static_path"])


    web_ser.run_forever()

if __name__ == '__main__':
    main()