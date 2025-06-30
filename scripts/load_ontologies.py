import pandas as pd
from rdflib import Graph
from rdfpandas.graph import to_dataframe
# 1. Create an RDF graph
g = Graph()
# 2. Parse the TTL file into the graph
# Replace 'mdsonto.ttl' with the actual path to your file
try:
    g.parse('\darts_semantic_reasoning\ontology\MDS-Onto-BuiltEnv.txt', format='turtle')
    print(f"Successfully parsed the TTL file with {len(g)} triples.")
    # 3. Convert the graph to a Pandas DataFrame
    df = to_dataframe(g)
    # 4. Display the DataFrame
    print("\nDataFrame representation of the TTL file:")
    print(df.head())
except FileNotFoundError:
    print("Error: The file 'mdsonto.ttl' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")







