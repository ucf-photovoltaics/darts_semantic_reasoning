"""
Created on June 3 2025 at 4:30 PM

Graph Databases operations module

Author: Lauren Mutugi

"""

import pandas as pd
import requests


class graph_database:
    def __init__(self, base_url, repository = "darts_semantic_reasoning"):
        self.base_url = base_url
        self.repository = repository
        self.session = requests.Session()

    def query(self, query):
        url = f"{self.base_url}/repositories/{self.repository}/statements"
        response = self.session.post(url, json={"query": query})
        response.raise_for_status() #throws an exception if there is an HTTP error
        return response.json()

    def close(self):
        self.session.close()
