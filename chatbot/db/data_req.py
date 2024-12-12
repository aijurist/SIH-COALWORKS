import requests

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