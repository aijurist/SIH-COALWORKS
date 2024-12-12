import requests
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
from langchain_community.tools.json.tool import JsonSpec
import json

def data_requester(endpoint_url, headers=None):
    """
    Fetches data from a GET endpoint.
    
    Args:
        endpoint_url (str): The URL of the GET endpoint.
        headers (dict, optional): Headers to include in the request (e.g., for authentication).
        
    Returns:
        dict: The data retrieved from the endpoint, or an error message.
    """
    try:
        res = requests.get(endpoint_url, headers=headers)

        if res.status_code == 200:
            return res.json()
        else:
            return {
                "error": f"Failed to retrieve data. Status Code: {res.status_code}",
                "details": res.text
            }
    except Exception as e:
        return {"error": f"An exception occurred: {str(e)}"}
    

def query_json(query, data):
    """
    Query user shift information using a JSON agent.
    
    Args:
        query (str): The query about user shift information
        data (dict): Dictionary containing user and shift information
    
    Returns:
        str: The agent's response to the query
    """
    json_spec = JsonSpec(dict_=data, max_value_length=40000)
    json_toolkit = JsonToolkit(spec=json_spec)
    
    llm = GoogleGenerativeAI(model='gemini-1.5-pro', temperature=0.2)
    json_agent = create_json_agent(llm=llm, toolkit=json_toolkit, verbose=True)
    res = json_agent.invoke({"input": query})
    
    return res["output"]
