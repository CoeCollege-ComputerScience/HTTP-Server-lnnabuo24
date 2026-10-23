from netTools import *
import threading
from pathlib import Path


resourceDirectory = "public_resources/"

def doesResourceExist(resourceName):
    print("looking for " + resourceName)
    somePath = Path(resourceDirectory + resourceName)
    return somePath.is_file()
    #return True

def sendFileNotFound(s):
    response = "HTTP/1.0 404 Not Found\r\n"
    response += "\r\n"
    response += "you sent me a file type i can process but why did you ask me to look for something i dont have"
    s.send(response.encode("utf-8"))

def openResource(resource, openType):
    hello = open(resourceDirectory + resource, openType)
    return hello

def attemptImageSend(resource, mediaType, s):
    # i feel like i could do something with the extension here so i dont need to pass in the media type
    # maybe string split the resource name with "."
    # then grab whatever the last thing is (the file extension)
    # thing is i dont want to realize theres a weird media type that doesnt have the content type image/<file extension>
    #
    # nevermind, svg files have svg+xml
    # but i guess i could include an exception for those?
    if doesResourceExist(resource):
        inFile = open(resourceDirectory + resource, "rb")
        response = "HTTP/1.0 200 OK\r\n"
        response += "Content-Type: image/" + mediaType + "\r\n"
        response += "\r\n"
        s.send(response.encode("utf-8"))

        s.send(inFile.read())
        inFile.close()
        s.send(response.encode("utf-8"))
    else:
        sendFileNotFound(s)

def processRequest(s,addr):
    request = getMessage(s)
    print(request)

    if request[:3] == "GET":
        request = request[4:]
        spaceLoc = request.find(' ')
        resource = request[:spaceLoc]
        resource = resource.strip("/")

        if resource[-5:].lower() == ".html":
            if doesResourceExist(resource):
                print("yeah the html exists")
                inFile = open(resourceDirectory + resource, "r")
                response = "HTTP/1.0 200 OK\r\n"
                response += "Content-Type: text/html\r\n"
                response += "\r\n"
                response += inFile.read()
                inFile.close()
                s.send(response.encode("utf-8"))
            else:
                sendFileNotFound(s)

        elif resource[-4:].lower() == ".jpg":
            attemptImageSend(resource, "jpg", s)
        elif resource[-4:].lower() == ".bmp":
            attemptImageSend(resource, "bmp", s)
        elif resource[-4:].lower() == ".png":
            attemptImageSend(resource, "png", s)
        elif resource[-4:].lower() == ".gif":
            attemptImageSend(resource, "gif", s)
        elif resource[-4:].lower() == ".ico":
            if doesResourceExist(resource):
                #print("found the favicon")
                inFile = open(resourceDirectory + resource, "rb")
                response = "HTTP/1.0 200 OK\r\n"
                response += "Content-Type: image/vnd.microsoft.icon\r\n"
                response += "\r\n"
                s.send(response.encode("utf-8"))

                s.send(inFile.read())
                inFile.close()
                s.send(response.encode("utf-8"))
            else:
                sendFileNotFound(s)

        elif resource[-4:].lower() == ".pdf":
            if doesResourceExist(resource):
                inFile = open(resourceDirectory + resource, "rb")
                response = "HTTP/1.0 200 OK\r\n"
                response += "Content-Type: application/pdf\r\n"
                response += "\r\n"
                s.send(response.encode("utf-8"))

                s.send(inFile.read())
                inFile.close()
                s.send(response.encode("utf-8"))
            else:
                sendFileNotFound(s)

        else:
            # something that hasnt been implemented
            response = "HTTP/1.0 403 Forbidden\r\n"
            response += "\r\n"
            response += "i have no idea how to handle " + resource
            s.send(response.encode("utf-8"))
            # i spent a few minutes wondering why trying an actual browser would just send an empty string
            # it turns out its because i wasnt specifying any page or resource
            # so of course i got the 403 forbidden

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
    print("Listening on: ", host, ":8001")
    serversocket.bind((host, 8001))
    serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversocket.listen()

    while True:
        print("Waiting for connection....")
        clientsocket, addr = serversocket.accept()

        print("Connnection from", addr)
        threading.Thread(target=processRequest, args=(clientsocket,addr)).start()

    serversocket.close()


SimpleServer()
