import datetime

from netTools import *
import threading
from pathlib import Path

import datetime


resourceDirectory = "public_resources/"
portNum = 8001

textPlaceholder = "[MAIN_TEXT]"

kittens = 0
puppies = 0


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

def processVote(s, data):

    global kittens
    global puppies

    # lop off vote.ss this time
    file = open(resourceDirectory + "template.html", "r")
    whatToSend = file.read()
    file.close()

    whatToSend = whatToSend.replace("<TITLE_TEXT>", "Vote")

    properlyVoted = False
    votedFor = ""

    # wait a second
    # i feel like i should be locking here
    print("you should probably lock here (changing server data and all that)")
    if "chosenOne" in data:
        votedFor = data["chosenOne"]
        if data["chosenOne"] == "kittens":
            kittens += 1
            properlyVoted = True
        elif data["chosenOne"] == "puppies":
            puppies += 1
            properlyVoted = True

    voteString = "kittens: " + str(kittens) + "\n puppies: " + str(puppies)
    whichVoteTitle = ""
    if votedFor == "puppies":
        whichVoteTitle = "puppies (the incorrect option)"
    elif votedFor == "kittens":
        whichVoteTitle = "fluffy kittens"

    if properlyVoted:
        whatToSend = whatToSend.replace(textPlaceholder, "thank you for voting " + whichVoteTitle + ", " + voteString)
    else:
        whatToSend = whatToSend.replace(textPlaceholder, "thank you for...not voting? on either? " + voteString)

    response = "HTTP/1.0 200 OK\r\n"
    response += "Content-Type: text/html\r\n"
    response += "\r\n"
    response += whatToSend
    s.send(response.encode("utf-8"))




def processRequest(s,addr):

    global kittens
    global puppies

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


        # i was handling greeting.ss the wrong way before
        #elif resource[:11] == "Greeting.ss":
        elif resource.startswith("Greeting.ss"):
            # follow the greeting stuff
            print("wahoo")
            print("sent:" + resource)

            # lop off greeting.ss (it served its purpose)
            resource = resource.removeprefix("Greeting.ss")
            # this should leave us with just the data


            # should i write code to make sure the name exists in the url?
            # that feels kinda important to check
            #print("remember to make sure data[\"name\"] exists here")

            file = open(resourceDirectory + "template.html", "r")
            whatToSend = file.read()
            file.close()

            # replace the placeholder string (strings now, actually) with the sent resource name
            whatToSend = whatToSend.replace("<TITLE_TEXT>", "Greeting")

            wasPlaceholderReplaced = False

            if resource.startswith("?"):
                # theres more data (good)
                resource = resource.removeprefix("?")
                # separate the data
                splitResource = resource.split(",")
                data = {}
                for line in splitResource:
                    # lines are in key/value pairs separated by =
                    splitLine = line.split("=")

                    # then make sure that they actually sent in data
                    # (im pretty sure an empty string gets included as a line if there was nothing sent)
                    if len(splitLine) > 1:
                        data[splitLine[0]] = splitLine[1]

                if "name" in data:
                    # make sure the key "name" exists
                    whatToSend = whatToSend.replace(textPlaceholder, "do you like fluffy kittens too, " + data["name"] + "?")
                    wasPlaceholderReplaced = True

            if not wasPlaceholderReplaced:
                # i couldve checked for [MAIN_TEXT]
                # but i also dont want someone getting really funny and saying their name is [MAIN_TEXT]
                # "consider using an extreme adjective for funny" pycharm says
                whatToSend = whatToSend.replace("<p> " + textPlaceholder + " </p>", "")

            # hm
            # do i add a send html function instead of copying and pasting this
            # probably yeah
            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += whatToSend
            s.send(response.encode("utf-8"))

        elif resource.startswith("Time.ss"):
            file = open(resourceDirectory + "template.html", "r")
            whatToSend = file.read()
            file.close()

            currentTime = datetime.datetime.now().time()
            whatToSend = whatToSend.replace(textPlaceholder, "the cat-shaped clock on my wall says that the time is " + str(currentTime))
            whatToSend = whatToSend.replace("<TITLE_TEXT>", "Time")

            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += whatToSend
            s.send(response.encode("utf-8"))

        elif resource.startswith("Vote.ss"):
            # lop off vote.ss this time
            resource = resource.removeprefix("Vote.ss")
            file = open(resourceDirectory + "template.html", "r")
            whatToSend = file.read()
            file.close()

            whatToSend = whatToSend.replace("<TITLE_TEXT>", "Vote")

            properlyVoted = False
            votedFor = ""
            #data = {}

            print("res:", resource)
            if resource.startswith("?"):
                # theres more data (good)
                # remove the ?
                resource = resource.removeprefix("?")
                # separate the data
                splitResource = resource.split(",")
                data = {}
                for line in splitResource:
                    # lines are in key/value pairs separated by =
                    splitLine = line.split("=")

                    # then make sure that they actually sent in data
                    # (im pretty sure an empty string gets included as a line if there was nothing sent)
                    if len(splitLine) > 1:
                        data[splitLine[0]] = splitLine[1]
                # wait a second
                # i feel like i should be locking here
                print("you should probably lock here (changing server data and all that)")
                print(data)
                if "chosenOne" in data:
                    print("okay, they voted")
                    votedFor = data["chosenOne"]
                    if data["chosenOne"] == "kittens":
                        kittens += 1
                        properlyVoted = True
                    elif data["chosenOne"] == "puppies":
                        puppies += 1
                        properlyVoted = True

            voteString = "kittens: " + str(kittens) + "\n puppies: " + str(puppies)

            if properlyVoted:
                whatToSend = whatToSend.replace(textPlaceholder, "thank you for voting " + votedFor + ", " + voteString)
            else:
                whatToSend = whatToSend.replace(textPlaceholder, "thank you for...not voting? " + voteString)

            # hm
            # do i add a send html function instead of copying and pasting this
            # probably yeah
            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += whatToSend
            s.send(response.encode("utf-8"))


        elif resource[-3:].lower() == ".ss":
            # now the .ss files

            resource = resource[:-3] # grab the name without the .ss at the end
            print(resource)

            # make sure its one of the resources that this server handles
            if resource == "Time" or resource == "Greeting" or resource == "Vote":
                # grab the template file and read it
                file = open(resourceDirectory + "template.html", "r")
                whatToSend = file.read()
                file.close()

                # replace the placeholder string with the sent resource name
                whatToSend = whatToSend.replace("<TITLE_TEXT>", resource)

                # hm
                # do i add a send html function instead of copying and pasting this
                # probably yeah
                response = "HTTP/1.0 200 OK\r\n"
                response += "Content-Type: text/html\r\n"
                response += "\r\n"
                response += whatToSend
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

    elif request[:4] == "POST":

        # convert the request into something a little easier to use
        request = request[5:]
        spaceLoc = request.find(' ')
        resource = request[:spaceLoc]
        resource = resource.strip("/")
        #print("are we posting now")
        #print(resource)

        if resource.startswith("Greeting.ss"):
            # the one thing this is listening for
            #print("yep, were posting")

            # read the file
            file = open(resourceDirectory + "template.html", "r")
            whatToSend = file.read()
            file.close()
            whatToSend = whatToSend.replace("<TITLE_TEXT>", "Greeting")

            # grab the data were looking for in the request
            splitUp = request.split("\r\n\r\n")
            #print("split: ")
            #print(splitUp)
            splitUp = splitUp[1]
            #print(splitUp)
            splitUp = splitUp.split(",")
            data = {}
            for line in splitUp:
                splitLine = line.split("=")
                data[splitLine[0]] = splitLine[1]

            if "name" in data:
                # make sure the key "name" exists
                # (again)
                whatToSend = whatToSend.replace(textPlaceholder, "do you like fluffy kittens too, " + data["name"] + "?")
            else:
                whatToSend = whatToSend.replace(textPlaceholder, "i should be sending you a bad request for this shouldnt i because i dont see a single name here")

            # you know
            # a function to handle greeting.ss might be useful
            # just takes in the sent data and sends a response

            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += whatToSend
            s.send(response.encode("utf-8"))

        elif resource.startswith("Vote.ss"):
            # read the file
            file = open(resourceDirectory + "template.html", "r")
            whatToSend = file.read()
            file.close()
            whatToSend = whatToSend.replace("<TITLE_TEXT>", "Greeting")

            # grab the data were looking for in the request
            splitUp = request.split("\r\n\r\n")
            # print("split: ")
            # print(splitUp)
            splitUp = splitUp[1]
            # print(splitUp)
            splitUp = splitUp.split(",")
            data = {}
            for line in splitUp:
                splitLine = line.split("=")
                data[splitLine[0]] = splitLine[1]

            processVote(s, data)

        else:
            # not greeting.ss
            # (bad!)
            response = "HTTP/1.0 400 Bad Request\r\n"
            response += "\r\n"
            response += "sorry i only handle one kind of post request (and you didnt send it)"
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
    print("Listening on: ", host, ":", portNum)
    serversocket.bind((host, portNum))
    serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversocket.listen()

    while True:
        print("Waiting for connection....")
        clientsocket, addr = serversocket.accept()

        print("Connnection from", addr)
        threading.Thread(target=processRequest, args=(clientsocket,addr)).start()

    serversocket.close()


SimpleServer()
