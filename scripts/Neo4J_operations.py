"""
Created on June 3 2025 at 4:30 PM

Graph Databases operations module

Author: Lauren Mutugi

"""

import pandas as pd



class Neo4J_operations: #abstracts all graph database operations, specifically Neo4j operations
    def __init__(self, read_data,stores_data, import_data):
        self.read_data = read_data
        self.stores_data = stores_data
        self.import_data = import_data
        
        #need a few more defs to do the abstraction stuff
        
        
Neo4J_operations.close()
