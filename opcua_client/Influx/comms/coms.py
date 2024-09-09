import requests

class RestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None, headers=None):
        """Send a GET request to the API."""
        url = self.base_url + endpoint
        print(url)
        response = requests.get(url, params=params, headers=headers, verify=False)
        return response

    def post(self, endpoint, data=None, headers=None):
        """Send a POST request to the API."""
        url = self.base_url + endpoint
        response = requests.post(url, json=data, headers=headers)
        return response

    def put(self, endpoint, data=None, headers=None):
        """Send a PUT request to the API."""
        url = self.base_url + endpoint
        response = requests.put(url, json=data, headers=headers)
        return response

    def delete(self, endpoint, headers=None):
        """Send a DELETE request to the API."""
        url = self.base_url + endpoint
        response = requests.delete(url, headers=headers)
        return response