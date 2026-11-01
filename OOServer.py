import socket

from netTools import *
import threading
import time
import random

html = """<!DOCTYPE html>
<html>
    <head>
        <title>Simple Server</title>
    </head>
    <body>
        **Content**
    </body>
</html>
"""


class Server:
    #addr = "0.0.0.0"

    def __init__(self):
        self.host = getIPAddress()
        self.port = 8080
        self.coolCommands = {}
        #self.secretVisits = 0


    def run(self):
        serversocket = socket()
        serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print("listening on ", self.host, ":", self.port)
        serversocket.bind((self.host, self.port))
        serversocket.listen()

        while True:
            print("waiting for connection")
            clientsocket, addr = serversocket.accept()
            print("connection from", addr)
            threading.Thread(target=self.processRequest, args=(clientsocket,)).start()

        serversocket.close()

    def processRequest(self, cl):
        request = getMessage(cl)

        resource = request.split(" ")[1]
        print(resource)
        if request[:3] == "GET":
            print("GET " + resource)
            data = ""
            hasData = False

            if resource.find("?") != -1:
                # contains a question mark
                # split it (into resource + query)
                splitUp = resource.split("?")
                resource = splitUp[0]
                data = splitUp[1]
                hasData = True
                print("data:", data)
                print("resource:", resource)

            if resource == "/":
                homePage = html.replace("**Content**", "<h1> Simple Server </h1>")
                self.respondHTML(homePage, cl)

            #elif resource[-4:].lower() == "html":
            elif resource.lower().endswith("html"):
            # i think this accomplishes the same thing? just preference?
                try:
                    #with open(resource, "r") as inFile:
                    # vvv (borrowing the pages that already exist)
                    with open("public_resources/" + resource, "r") as inFile:
                        response = inFile.read()
                    self.respondHTML(response, cl)
                except FileNotFoundError:
                    self.respondNotFound(cl)

            #elif resource[-3:].lower() == "png":
            elif resource.lower().endswith("png"):
                self.respondImg(resource, cl)

            elif resource in self.coolCommands:
                try:
                    self.coolCommands[resource](cl, data)
                    """
                    if hasData:
                        self.coolCommands[resource](cl, data)
                    else:
                        self.coolCommands[resource](cl)
                    """
                except KeyError:
                    self.respondNotFound(cl)
                """
                # commented out
                # for now
                # maybe
                except TypeError:
                    # i really dont know if i need to be handling errors like this
                    # do i need to handle incorrect input? (if no data is sent too)
                    # i dont think we talked about it much in class so
                    print("uh oh someone didnt provide the proper input")
                    print("sent data:", data)
                    header = "HTTP/1.0 400 Bad Request\r\n\r\n"
                    body = homePage = html.replace("**Content**", "<h1> bad request (missing data or sent unneeded data most likely, probably) </h1>")
                    sendMessage(cl, header)
                    sendMessage(cl, body)

                    cl.close()
                """

        elif request.startswith("POST"):

            print("POST, initial:", request)

            # like before
            # turn the request into something that can be worked with a little easier
            request = request[5:] # lop off the POST
            spaceLoc = request.find(' ') # find the first space
            resource = request[:spaceLoc] # lop off the space as well
            #resource = resource.strip("/") # strip off the /
            # ^^^ nevermind (had to keep the / so the resource would be recognized as an endpoint)

            #print("altered:", resource)

            # split the request into the header(?) and query/data string
            splitUp = request.split("\r\n\r\n")
            data = splitUp[1] # yoink
            print("(POST) data:", data)
            print("(POST) resource:", resource)

            # my hands are clean
            # the greeting is an endpoint/decorator
            if resource in self.coolCommands:
                try:
                    self.coolCommands[resource](cl, data)
                except KeyError:
                    self.respondNotFound(cl)
            else:
                self.respondNotFound(cl)



    def respondHTML(self, body, cl):
        header = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
        sendMessage(cl, header)
        sendMessage(cl, body)
        cl.close()

    def respondImg(self, resource, cl):
        header = "HTTP/1.0 200 OK\r\n"
        header += "Content-type: image/png\r\n"
        header += "\r\n"
        try:
            #resource = "Image" + resource
            resource = "public_resources/" + resource
            print("Resource: \n", resource)
            infile = open(resource, "rb")
            data = infile.read()
            infile.close()
            sendMessage(cl, header)
            cl.send(data)
            cl.close()
            print("Sent")

        except FileNotFoundError:
            print("bosh", resource)
            self.respondHTML(resource, cl)


    def respondNotFound(self, cl):
        header = "HTTP/1.0 404 Not Found\r\n\r\n"
        body = homePage = html.replace("**Content**", "<h1> NOT FOUND </h1>")
        sendMessage(cl, header)
        sendMessage(cl, body)

        cl.close()
        print("Not Found")

    def newCommand(self, key):
        def wrapper(f):
            print("new command at key", key)
            self.coolCommands[key] = f
            return f
        return wrapper

