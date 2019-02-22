# scratch_websockets
Extension to allow the scratch player to communicate without cloud data

Extension connects to 127.0.0.1:8765

Goal:
scratch(1) <--> machine(1) <--> machine(2) <--> scratch(2)

### Current blocks: 
open socket | command - start websocket connection
close socket | command - end websocket connection
active | boolean reporter - return true/false if websocket is connected
send [data] | command - send data to the server
send command >commands< | command - preset commands to interact with the server
socket data | reporter - holds a record of the most recently fetched data from the server
