"""
Created on June 3 2025 at 4:30 PM
Updated on June 10 2025

Neo4j operations module

Author: Lauren Mutugi

"""

from neo4j import GraphDatabase
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

class Neo4j_operations: 
    """
   Class that abstracts all Neo4J Aura database operations. 
   Also provides methods for common database operations and query execution
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j connection.
        
        Parameter explanations:
            uri: str - Neo4j Aura connection URI
            username: str -  username for database
            password: str - password for database
        """
        self._uri = uri
        self._username = username
        self._password = password
        self._driver = None
        self.logger = logging.getLogger(__name__)
        
       "Initialize connection"
        self._connect()
    
    def _connect(self) -> None:
        "Connect to the Neo4j database"
        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password)
            )
            # Verify connection
            self._driver.verify_connectivity()
            self.logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self) -> None:
        "Close the database connection"
        if self._driver:
            self._driver.close()
            self.logger.info("Neo4j connection closed")
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Run a Cypher query and return results.
        
        Parameter explation:
            query:str - Cypher query to run
            parameters (dict, optional) - Query parameters
            database (str, optional) - Choose which database to query
            
        What is Returned:
            List[Dict]: List of results from query
        """
        try:
            with self._driver.session(database=database) as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def create_node(self, label: str, properties: Dict[str, Any], database: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new node in database.
        
        Parameters:
            label (str) - Node label
            properties (dict) - Node properties
            database (str, optional) - Specific database to use
            
        What is returned:
            dict: Created node properties
        """
        query = (
            f"CREATE (n:{label} $properties) "
            "RETURN n"
        )
        result = self.execute_query(query, {"properties": properties}, database)
        return result[0] if result else None
    
    def create_relationship(self, start_node_label: str, start_node_property: Dict[str, Any], end_node_label: str, end_node_property: Dict[str, Any], relationship_type: str,
        relationship_properties: Optional[Dict[str, Any]] = None, database: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a connection between two nodes.
        
        Parameters:
            start_node_label (str)- Starting node label
            start_node_property (dict) - Property to identify start node
            end_node_label (str) - Ending node label
            end_node_property (dict) - Property to identify end node
            relationship_type (str) - Type of relationship
            relationship_properties (dict, optional) - Relationship properties
            database (str, optional) - Specific database to use
            
        What is returned:
            dict: Created relationship properties
        """
        query = (
            f"MATCH (a:{start_node_label}), (b:{end_node_label}) "
            f"WHERE a = $start_props AND b = $end_props "
            f"CREATE (a)-[r:{relationship_type} $rel_props]->(b) "
            "RETURN r"
        )
        params = {
            "start_props": start_node_property,
            "end_props": end_node_property,
            "rel_props": relationship_properties or {}
        }
        result = self.execute_query(query, params, database)
        return result[0] if result else None
    
    def get_node(self, label: str, properties: Dict[str, Any], database: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a node based on properties and label.
        
        Parameters:
            label (str) - Node label
            properties (dict) - Node properties to match
            database (str, optional) - Specific database to use
            
        What is returned:
            Optional[dict] - if found, there is a node. Otherwise, there is None
        """
        query = (
            f"MATCH (n:{label}) "
            "WHERE n = $properties "
            "RETURN n"
        )
        result = self.execute_query(query, {"properties": properties}, database)
        return result[0] if result else None
    
    def update_node(self, label: str, match_properties: Dict[str, Any], new_properties: Dict[str, Any], database: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update the node properties.
        
        Parameters:
            label (str) - Node label
            match_properties (dict) - Properties to identify the node
            new_properties (dict) - New properties to set
            database (str, optional) - Specific database to use
            
        What is Returned:
            Optional[dict] - Updated node if found, None otherwise
        """
        query = (
            f"MATCH (n:{label}) "
            "WHERE n = $match_props "
            "SET n += $new_props "
            "RETURN n"
        )
        params = {
            "match_props": match_properties,
            "new_props": new_properties
        }
        result = self.execute_query(query, params, database)
        return result[0] if result else None
    
    def delete_node(self, label: str, properties: Dict[str, Any], database: Optional[str] = None) -> bool:
        """
        Delete a node and its connections.
        
        Parameters:
            label (str) - Node label
            properties (dict) - Properties to identify the node
            database (str, optional) - Specific database to use
            
        What is returned:
            boolean - If node was deleted, return True, False otherwise
        """
        query = (
            f"MATCH (n:{label}) "
            "WHERE n = $properties "
            "DETACH DELETE n"
        )
        try:
            self.execute_query(query, {"properties": properties}, database)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete node: {str(e)}")
            return False
    
    def get_all_nodes(self, label: Optional[str] = None, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all nodes with optional label filter.
        
        Parameters:
            label (str, optional) -  Node label to filter by
            database (str, optional) - Specific database to use
            
        What is returned:
            List[dict] - List of nodes
        """
        query = "MATCH (n{}) RETURN n".format(f":{label}" if label else "")
        return self.execute_query(query, database=database)
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()

