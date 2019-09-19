import sys

from twisted.internet import reactor, protocol, ssl
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

import txaio

import json, base64

linkConnection = ["tcp","ws"] # Set this to transport so that the scratchServer can send messages to it

messageDictionary = {"method":1, "message": 2, "projectId": 3}

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

def base64encode(message):
    message = base64.b64encode(str(message).encode("utf-8"))
    message = message.decode("utf-8")
    return message

class scratchServer(WebSocketServerProtocol):     
    def onOpen(self):
        print("WebSocket connection open.")
        self.tcpConnection = central_factory.protocol
        linkConnection[1] = self # Allow the tcpsocket to message the server

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))
        
    def onMessage(self, payload, isBinary):
        response = self.handle_request(payload)
        self.sendMessage(response.encode(), isBinary)
            
    def send(data):
        payload = json.dumps({
                "jsonrpc": "2.0",
                "method":"didReceiveMessage",
                "params":{
                    "message": base64encode(data),
                    "encoding": "base64",
                    "channel": 1,
                }
                })
        linkConnection[1].sendMessage(payload.encode(), False)

    def handle_request(self, request):
        response = json.loads(request)
        request = json.loads(request)
        method = request["method"]
        if method == "discover":
            response = {
                "jsonrpc": request["jsonrpc"],
                "method": "didDiscoverPeripheral",
                "params": {
                    "peripheralId": "0x0000",
                    "name": "Kingdom Net",
                    "rssi": -1
                    }
                }
        elif method == "connect":
            response = {
                "jsonrpc": request["jsonrpc"],
                "id": request["id"],
                "result": "null"
                }
            self.connected = True
        elif method == "getVersion":
            response = {
                "jsonrpc": request["jsonrpc"],
                "id": request["id"],
                "result":{
                    "protocol": "1.2"
                    }
                }
        elif method == "send" or method == "write":
            #message = request["params"]["message"].encode()
            #decoded = base64.decodebytes(message)
            #response = {
                #"jsonrpc": request["jsonrpc"],
                #"id": request["id"],
                #"result":len(decoded)
                #}
            #if request["params"]["channel"] == "Channel 1":
                #self.tcpConnection.send(json.dumps({"method":"send","message":decoded.decode()}).encode())

            message = request["params"]["message"].encode()
            decoded = base64.decodebytes(message)
            response = {
                "jsonrpc": request["jsonrpc"],
                "id": request["id"],
                "result":len(decoded)
                }
            if request["params"]["channel"] == "Channel 1":
                if decoded.decode() == "join":
                    self.tcpConnection.send(json.dumps({commandDictionary["method"]:"join",commandDictionary["projectId"]:1020390}).encode())
                else:
                    self.tcpConnection.send(json.dumps({commandDictionary["method"]:"send",commandDictionary["message"]:decoded.decode()}).encode())
                
        return json.dumps(response)

# Central server tcp connection
class MyClient(protocol.Protocol):
    def connectionMade(self):
        #self.transport.write(json.dumps({"method":"join","projectId":1020390}).encode())
        self.websocketConnection = factory.protocol
        linkConnection[0] = self.transport # Allow the websocket to message the server

    def send(data):
        linkConnection[0].write(data)
    
    def dataReceived(self, data):
        self.websocketConnection.send(data.decode())


class MyClientFactory(protocol.ClientFactory):
    protocol = MyClient
    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)

if __name__ == '__main__':

    # TCP connection to the central server
    central_factory = MyClientFactory()

    log.startLogging(sys.stdout)

    # SSL server context: load server key and certificate
    # We use this for both WS and Web!
    contextFactory = ssl.DefaultOpenSSLContextFactory('scratch-multiplayer.pem',
                                                      'scratch-multiplayer.pem')

    factory = WebSocketServerFactory(u"wss://device-manager.scratch.mit.edu:20110")
    # by default, allowedOrigins is "*" and will work fine out of the
    # box, but we can do better and be more-explicit about what we
    # allow. We are serving the Web content on 8080, but our WebSocket
    # listener is on 9000 so the Origin sent by the browser will be
    # from port 8080...
    factory.setProtocolOptions(
        allowedOrigins=[
            "https://kingdompy.github.io:*",
        ]
    )

    factory.protocol = scratchServer
    listenWS(factory, contextFactory)

    webdir = File(".")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)
    reactor.listenSSL(8080, web, contextFactory)

    # TCP connection to the central server
    reactor.connectTCP("192.168.0.47", 5005, central_factory)
    
    reactor.run()
