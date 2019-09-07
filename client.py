import asyncio
import pathlib
import ssl
import websockets, socket
import json
import base64
import math

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5005
BUFFER_SIZE = 128

class psuedo_player:
    def __init__ (self):
        self.position = 0
        self.x,self.y = 0,0
        self.scratchX,self.scratchY = 0,0

    def respond(self, message):
        self.scratchX,self.scratchY = int(message[:3]),int(message[3:])

    def update(self):
        if self.x < self.scratchX:
            if (self.scratchX - self.x) >= 5:
                self.x +=5
            else:
                self.x +=self.scratchX - self.x
                
        elif self.x > self.scratchX:
            if (self.x - self.scratchX) >= 5:
                self.x -=5
            else:
                self.x -= self.x - self.scratchX
                
        if self.y < self.scratchY:
            if (self.scratchY - self.y) >= 5:
                self.y +=5
            else:
                self.y +=self.scratchY - self.y
                
        elif self.y > self.scratchY:
            if (self.y - self.scratchY) >= 5:
                self.y -=5
            else:
                self.y -=self.y - self.scratchY
            
        x,y = str(self.x), str(self.y)
        while len(x)< 3:
            x = "0"+x   
        while len(y) < 3:
            y = "0"+y
        return x+y
         
         
class server:

    def __init__(self, ip ,port):   
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        localhost_pem = pathlib.Path(__file__).with_name("scratch-multiplayer.pem")
        ssl_context.load_cert_chain(localhost_pem)

        start_clientServer = websockets.serve(
            self.run_client, ip, port, ssl=ssl_context
        )

        self.serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #main server connection
        self.serverConnection.connect((SERVER_IP, SERVER_PORT))
        self.serverConnection.send(json.dumps({"method":"join","projectId":1020390}).encode())

        asyncio.get_event_loop().run_until_complete(start_clientServer)
        asyncio.get_event_loop().run_until_complete(self.main_server_thread())
        asyncio.get_event_loop().run_forever()

    async def run_client(self, websocket, path):
        self.connected = False
        self.computer = psuedo_player()
        client = websocket
        while True:
            message = await websocket.recv()
            response = self.handle_request(message)
            #print(f"< {message}")
            
            await websocket.send(response)
            #print(f"> {response}")

            await client.send(json.dumps({
                "jsonrpc": "2.0",
                "method":"didReceiveMessage",
                "params":{
                    "message": self.encode(self.computer.update()),
                    "encoding": "base64",
                    "channel": 1,
                }
                }))

    async def main_server_thread(self):
        message = self.serverConnection.recv(BUFFER_SIZE)
        print(message)

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
            message = request["params"]["message"].encode()
            decoded = base64.decodebytes(message)
            response = {
                "jsonrpc": request["jsonrpc"],
                "id": request["id"],
                "result":len(decoded)
                }
            if request["params"]["channel"] == "Channel 1":
                self.serverConnection.send(json.dumps({"method":"send","message":decoded.decode()}).encode())
                self.computer.respond(decoded.decode())
        return json.dumps(response)

    def encode(self, message):
        message = base64.b64encode(str(message).encode("utf-8"))
        message = message.decode("utf-8")
        return message

startserver = server("device-manager.scratch.mit.edu", 20110)

