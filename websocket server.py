#Scratch websocket server

#Server imports
import asyncio
import random
import websockets

#Data imports
import json

#Gui imports
from PyQt5 import QtGui, QtCore

#Address of the other machine it is connected to
global pairMachine

async def client(websocket, path):
    print("Succesfully connected to scratch.")
    receivedMessages = ["bob head", "samoan"]
    while True:
        data = await websocket.recv()
        print("RECEIVED:", data)
        if data == "%_fetch":
            #If no messages
            if receivedMessages == []:
                await websocket.send("")
                
            else:
                await websocket.send(json.dumps(receivedMessages))
                receivedMessages = []
                
        elif data == "%_disconnect":
            await websocket.send("disconnected from ...")

start_server = websockets.serve(client, '127.0.0.1', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
