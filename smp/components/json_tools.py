from langchain_google_genai import GoogleGenerativeAI
from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
from langchain_community.tools.json.tool import JsonSpec
import json

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

# # Example usage
# data = {'data': [{'user_name':'Shanthosh', 'shift_name':'Shift1', 'id': '1'}]}
# query = "what shift does Shanthosh work in"
# result = query_user_shift_info(query, data)
# print("Json agent returns:", result)