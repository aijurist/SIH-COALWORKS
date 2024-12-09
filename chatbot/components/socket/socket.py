import asyncio
import websockets
import json
import aiohttp
import socket
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from chatbot.components.general_chatbot.knowledgebase import KnowledgeBase

class WebSocketServer:
    """
    A WebSocket server that handles incoming WebSocket connections, fetches resources 
    based on page number requests, and sends the response back to the client.

    Args:
        host (str, optional): The host to bind the server. Defaults to "localhost".
        port (int, optional): The port to bind the server. Defaults to 6789.
        page_resource_map (dict, optional): A dictionary mapping page numbers to resource endpoints.  Defaults to None
    """  
    def __init__(self, host="localhost", port=6789, page_resource_map=None, google_api_key=os.getenv("GOOGLE_API_KEY")):
        self.host = host
        self.port = port
        self.page_resource_map = page_resource_map or {}
        self.knowledge_base = KnowledgeBase(
            google_api_key=google_api_key, 
            vector_db_path='chatbot/database/faiss_index'
        )

    async def fetch_resource(self, endpoint):
        """
        Fetches resource from the given endpoint.

        Args:
            endpoint (str): The URL of the resource to fetch.

        Returns:
            dict: A dictionary containing either the fetched data or an error message.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint) as res:
                    if res.status == 200:
                        data = await res.json() 
                        return {"data": data}
                    else:
                        return {"error": f"Failed to fetch resource. Status code: {res.status}"}
            except Exception as e:
                return {"error": f"An error occurred: {str(e)}"}

    async def handle_connection(self, websocket):
        """
        Handles an incoming WebSocket connection, processes requests, 
        fetches the required resource, and sends the response to the client.

        Args:
            websocket (websockets.WebSocketServerProtocol): The WebSocket connection object.
        """
        print("Client connected!")
        try:
            async for i in websocket:
                data = json.loads(i)
                page_number = data.get("pageNumber")

                if page_number and page_number in self.page_resource_map:
                    endpoint = self.page_resource_map[page_number]
                    data = await self.fetch_resource(endpoint)
                    # Send the resource back to the client
                    # response = {"status": "Chatbot loaded with required resource"}
                    response = await self.listener(page_number, data, 200)
                    await websocket.send(json.dumps(response))
                    
                    # adding data to the knowledge base - cannot add via listener for some reason, need to fix it later
                    try:
                        self.knowledge_base.add_websocket_data(response)
                        print(f"Added page {page_number} data to knowledge base at {response['timestamp']}")
                    except Exception as e:
                        print(f"Knowledge base storage error: {e}")
                        
                    return response
                else:
                    error = {"error": "Invalid page number or no resource mapped."}
                    await websocket.send(json.dumps(error))
                    return "Data Not Loaded"
        except websockets.ConnectionClosed:
            print("Client disconnected.")
    
    async def listener(self, page_number, resource_data, response_status):
        """
        Listener function that processes and returns the data being retrieved and sent.

        Args:
            page_number (str): The requested page number.
            resource_data (dict): The fetched data or error.
            response_status (str): Status message to be sent to the client.

        Returns:
            dict: Combined response to be used by the application.
        """
        # returns structured response to be used by the application
        return {"page": page_number, "status": response_status, "data": resource_data, "timestamp": datetime.now().isoformat()}

    async def run(self):
        """
        Starts the WebSocket server and keeps it running indefinitely.

        This method binds the server to the provided host and port and waits for connections.
        """
        print(f"WebSocket server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_connection, self.host, self.port):
            await asyncio.Future()  # Run forever


def get_ip():
    """
    Get the local IP address of the machine.
    If the machine is not connected to any network, it will fallback to localhost.
    """
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip if local_ip != "127.0.0.1" else "localhost"
    except socket.gaierror:
        return "localhost" 


def start_server(host="localhost", port=6789, page_resource_map=None):
    """
    Function to start the WebSocket server with custom configurations.

    Args:
        host (str): The hostname to bind the server (default: "localhost").
        port (int): The port to bind the server (default: 6789).
        page_resource_map (dict): A dictionary mapping page numbers to resource endpoints.
    """
    page_resource_map = page_resource_map or {
        "1": "https://httpbin.org/ip",
        "2": "https://httpbin.org/uuid",
        "3": "https://httpbin.org/bytes/10",
    }

    # Calling get_ip function
    host = get_ip()

    # Initialize the WebSocket
    server = WebSocketServer(host=host, port=port, page_resource_map=page_resource_map)

    # Run Server with asyncio
    asyncio.run(server.run())
