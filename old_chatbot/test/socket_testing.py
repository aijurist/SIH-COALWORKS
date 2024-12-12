import asyncio
import websockets
import json
from chatbot.agent.socket.socket import WebSocketServer

async def send_page_number():
    uri = "ws://192.168.1.8:6789"
    async with websockets.connect(uri) as websocket:
        page_number = input("Enter Page Number: ")
        message = json.dumps({"pageNumber": page_number})
        await websocket.send(message)
        print(f"Sent: {message}")
        
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(send_page_number())
