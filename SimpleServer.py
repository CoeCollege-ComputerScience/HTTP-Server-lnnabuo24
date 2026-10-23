from netTools import *
import threading

def processRequest(s,addr):
    request = getMessage(s)
    print(request)

    if request[:3] == "GET":
        request = request[4:]
        spaceLoc = request.find(' ')
        resource = request[:spaceLoc]
        resource = resource.strip("/")

        if resource[-5:].lower() == ".html":
            inFile = open(resource, "r")
            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += inFile.read()
            inFile.close()
            s.send(response.encode("utf-8"))

        elif resource[-4:].lower() == ".jpg":
            inFile = open(resource, "rb")
            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: image/jpeg\r\n"
            response += "\r\n"
            s.send(response.encode("utf-8"))

            s.send(inFile.read())
            inFile.close()
            s.send(response.encode("utf-8"))

    else:
        response = "HTTP/1.0 501 Not Implemented\r\n"
        response += "\r\n"
        response += "I'm sorry Dave, I can't do that."
        s.send(response.encode("utf-8"))

    #response = "Gotcha"
    #s.send(response.encode("utf-8"))
    s.close()


def SimpleServer():
    serversocket = socket()
    host = getIPAddress()
    print("Listening on: ", host, ":8000")
    serversocket.bind((host, 8002))
    serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversocket.listen()

    while True:
        print("Waiting for connection....")
        clientsocket, addr = serversocket.accept()

        print("Connnection from", addr)
        threading.Thread(target=processRequest, args=(clientsocket,addr)).start()

    serversocket.close()


SimpleServer()
