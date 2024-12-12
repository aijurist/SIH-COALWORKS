from chatbot.db.data_req import data_requester
from chatbot.db.endpoints import endpoints
from chatbot.agent.json_agent.agent import query_json


host_ip = 'http://192.168.110.11:3000'

for key, value in endpoints.items():
    endpoint_url = host_ip + value
    res = data_requester(endpoint_url)
    
    
    
    