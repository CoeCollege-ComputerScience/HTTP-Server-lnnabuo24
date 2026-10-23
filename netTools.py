from socket import *

def getIPAddress():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getMessage(sock):
    data = sock.recv(1024)
    return data.decode('utf-8')

def getLongMessage(sock):
    '''
    Use to get an arbitrary sized message
    requires the sender to close connection, otherwise it will keep waiting
    '''
    data = sock.recv(1024)
    response = data
    while data:
        data = sock.recv(1024)  # null when server closes socket
        response += data
    return response.decode("utf-8")

def sendMessage(sock, msg):
    sock.send(msg.encode('utf-8'))