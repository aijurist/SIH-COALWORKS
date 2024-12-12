import requests
from smp.data.endpoints import endpoints, mapping
from smp.components.json_tools import query_json

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
        response = requests.get(endpoint_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Failed to retrieve data. Status Code: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {"error": f"An exception occurred: {str(e)}"}
    
def rtd_analyser(query):
        combined_data = {}
        host_url = "http://192.168.137.53:3000"
        for key, value in mapping.items():
            endpoint_url = endpoints[key]
            query = queries[value] + f'. Do not use markdown language or style the text. The user has asked for activity/queried: {query}. Extract only relevant information'
            print(f"endpoint_url: {host_url + endpoint_url}, query: {query}")
            
            data = data_requester(endpoint_url=endpoint_url)
            res = query_json(query=query, data=data)
            
            print(res)
            combined_data[value] = res
        
        return combined_data
    
queries = {
    'shift': 'Provide a detailed breakdown of works in the current shift, categorized as: Completed works, Half Completed, Unfinished works',
    'user': 'For the current user and current shift, generate a comprehensive report of completed tasks',
    'smp': 'Provide a textual report for the current Safety Management Plan (SMP), identifying each activity/hazard and it\'s Consequences, Probability, Exposure.',
    'iot': 'Conduct a thorough anomaly detection analysis on the current IoT sensor data: 1) Identify any data points that deviate significantly from the established baseline or normal operating range. 2) Create a comprehensive report of: a) Unusual spikes in measurements, b) Values exceeding predefined thresholds, c) Unexpected patterns or correlations in sensor readings.'
}