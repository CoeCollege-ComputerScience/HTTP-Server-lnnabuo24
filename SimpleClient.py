from netTools import *


def SimpleBrowser(ip, resource):
    s = socket()
    s.connect((ip, 8000))
    msg = "GET "+ resource + " HTTP/1.0\r\n"
    msg += "\r\n"
    msg = msg.encode("utf-8")

    s.send(msg)
    response = s.recv(1024)
    data = ""
    while response:
        data += response.decode("utf-8")
        response = s.recv(1024)

    #data = data.decode("utf-8")
    s.close()
    print(data)

#SimpleBrowser("httpbin.org","/#/Anything")
SimpleBrowser("192.168.0.225", "/kitten.html")

