from twisted.internet import reactor, protocol
import json
import socket

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5005

authorisedPlaces = {"1020390":{"name":"Hangout Club","max-size":8}} #Containts a list of games that can operated with kingdom net
activeLobbies = {"1020390":[]} #Game lobbies that have players in it
messageQueue = [] #Queue of messages to send
connectedUsers = {} #Dict containing an ip as a key and the place it is at

messageDictionary = {"method":1, "message": 2, "projectId": 3}

class MyServer(protocol.Protocol):
    def connectionMade(self):
        addr = self.transport.getPeer()
        userId = self.getUserId(addr)
        connectedUsers[userId] = None # Add the user as connected
        
    def dataReceived(self, data):
        data = data.decode()
        self.interpretData(data, self.transport.getPeer())

    def connectionLost(self, reason):
        addr = self.transport.getPeer()
        userId = self.getUserId(addr)
        if connectedUsers[userId] != None:
            projectId = connectedUsers.pop(userId) #remove user
            activeLobbies[projectId].remove(self) #Remove the client
            print("({}:{}) has disconnected from project ({})".format(addr.host, addr.port, projectId))

    def interpretData(self, data, addr):
        try:
            userId = self.getUserId(addr)
            instruction = json.loads(data)
            method = instruction[messageDictionary["method"]]
            if  method == "join":
                if connectedUsers[userId] == None:
                    projectId = str(instruction[messageDictionary["projectId"]])
                    activeLobbies[projectId].append(self) #Add the client
                    connectedUsers[userId] = projectId
                    print("({}:{}) has joined project ({})".format(addr.host, addr.port, projectId))
            if method == "send":
                message = instruction[messageDictionary["message"]].encode()
                projectId = connectedUsers[userId]
                addresses = activeLobbies[projectId]
                #Send message to each user
                for address in addresses:
                    if address.transport.getPeer() != addr:
                        address.transport.write(message)
        except Exception as error:
            print(error)
        
    def getUserId(self, addr):
        addr = addr.host+str(addr.port)
        return addr.replace(".", '')
    
class MyServerFactory(protocol.Factory):
    protocol = MyServer

factory = MyServerFactory()
reactor.listenTCP(SERVER_PORT, factory, interface=SERVER_IP)
print("Server started on {}:{}".format(SERVER_IP, SERVER_PORT))
reactor.run()


