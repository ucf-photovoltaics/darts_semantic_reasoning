"""
Created on June 3 2025 at 4:30 PM

Graph Databases operations module

Author: Lauren Mutugi

"""

import pandas as pd



class Neo4J_operations: #abstracts all graph database operations, specifically Neo4j operations
    def __init__(self, name, type, column):
        self.name = name
        self.type = type
        self.column = column
        
        
Neo4J_operations.close()
