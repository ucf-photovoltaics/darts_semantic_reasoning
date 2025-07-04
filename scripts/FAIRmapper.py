# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 13:50:13 2025

@author: Brent Thompson, Lauren Mutugi
"""

import streamlit as st
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import SH, RDF, RDFS, XSD
from io import StringIO # To read uploaded file content
import os # used for connecting the ontology file to fairmapper

from rdfpandas.graph import to_dataframe

# Assuming postgres_operations.py is in the same directory and working correctly
from postgres_operations import PostgresDB

# --- Database Connection Initialization ---
# It's good practice to initialize this once, maybe outside functions that get re-run
# Consider adding configuration for host, user, password if not hardcoded in PostgresDB
DPV = PostgresDB('dpv', 'sun')

# --- Page Configuration ---
st.set_page_config(
    page_title="Interactive DataFrame Mapper",
    page_icon="🔗",
    layout="wide"
)

# --- Session State Initialization ---
if 'mappings' not in st.session_state:
    st.session_state.mappings = {}
if 'selected_term_1' not in st.session_state:
    st.session_state.selected_term_1 = None
if 'selected_db_table' not in st.session_state:
    st.session_state.selected_db_table = None
if 'all_db_tables_info' not in st.session_state:
    st.session_state.all_db_tables_info = None

# --- Helper Functions ---
def handle_df1_click(term):
    """Callback function to handle selection from the first dataframe."""
    st.session_state.selected_term_1 = term

def handle_df2_click(field):
    """Callback function to handle selection from the second dataframe and create a mapping."""
    if st.session_state.selected_term_1:
        st.session_state.mappings[st.session_state.selected_term_1] = field
        # Reset selection after mapping
        st.session_state.selected_term_1 = None

def reset_mappings():
    """Clears all existing mappings and selections."""
    st.session_state.mappings = {}
    st.session_state.selected_term_1 = None

@st.cache_data
def get_all_db_tables():
    """Fetches all table names and comments from the database."""
    try:
        return DPV.get_table_names_and_comments()
    except Exception as e:
        st.error(f"Error fetching database tables: {e}")
        return pd.DataFrame(columns=['table_name', 'table_comment']) # Return empty DataFrame on error

def load_db_columns(table_name):
    """Loads column names for a given database table."""
    if not table_name:
        return []
    try:
        # Limit 0 fetches only schema information, no actual rows
        query = f"SELECT * FROM instrument_data.{table_name} LIMIT 0"
        df_schema = DPV.read_records_from_postgres(query)
        return list(df_schema.columns)
    except Exception as e:
        st.error(f"Error loading columns for table '{table_name}': {e}")
        return []

def load_ontology_terms(filename="MDS-Onto-BuiltEnv-PV-Module-v0.3.0.0.ttl"):
    """Loads ontology terms from an uploaded RDF file."""

    try:
        # Get the absolute path to the ontology file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)


        g = Graph()
        g.parse(file_path, format='turtle')
        ontology_df = to_dataframe(g)
        all_terms = list(ontology_df.index)

        # Get namespaces from URIs
        namespaces = sorted(set(
            uri.rsplit("#", 1)[0] if "#" in uri else uri.rsplit("/", 1)[0]
            for uri in all_terms
        ))

        return all_terms, namespaces
    except Exception as e:
        st.error(f"Error loading ontology file '{file_path}': {e}")
        return [], []

def generate_shacl_file(mappings, db_table_name="DatabaseTable"):
    """
    Generates a SHACL Turtle file describing the mappings.
    This uses a custom predicate `ex:mapsTo` to link database columns
    (represented as sh:path) to ontology terms.
    """
    g = Graph()

    # Define namespaces
    EX = Namespace("http://example.com/shacl-mappings#")
    DBP = Namespace("http://example.com/database-properties#") # For database column properties
    g.bind("sh", SH)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("ex", EX)
    g.bind("dbp", DBP)
    # Note: We don't bind a specific ontology prefix here as ontology terms are full URIs

    # Define a NodeShape for the database table
    table_shape_uri = EX[f"{db_table_name}Shape"]
    g.add((table_shape_uri, RDF.type, SH.NodeShape))
    g.add((table_shape_uri, RDFS.label, Literal(f"SHACL Shape for {db_table_name}")))
    g.add((table_shape_uri, SH.targetClass, EX[db_table_name.replace('.', '_') + "Record"])) # A placeholder target class

    for db_column, ontology_term in mappings.items():
        # Create a blank node for the PropertyShape
        prop_shape = EX[f"{db_table_name.replace('.', '_')}_{db_column.replace('.', '_')}PropertyShape"]
        g.add((table_shape_uri, SH.property, prop_shape))
        g.add((prop_shape, RDF.type, SH.PropertyShape))

        # Define the path for the database column
        db_column_uri = DBP[db_column]
        g.add((prop_shape, SH.path, db_column_uri))

        # Add the custom mapping predicate
        g.add((prop_shape, EX.mapsTo, URIRef(ontology_term)))

        # Add a comment for clarity
        g.add((prop_shape, RDFS.comment, Literal(f"Maps database column '{db_column}' to ontology term '{ontology_term}'.")))

    return g.serialize(format='turtle')


# --- UI Rendering ---
st.title("🔗 Interactive DataFrame Mapper")
st.markdown("Click a term on the left, then a term on the right to create a one-to-one mapping.")

# --- Configuration Section ---
st.header("Configuration", divider='blue')

col_config_left, col_config_right = st.columns(2, gap="large")

with col_config_left:
    st.subheader("Database Tables Overview")
    # Fetch all table names once and cache them
    if st.session_state.all_db_tables_info is None:
        st.session_state.all_db_tables_info = get_all_db_tables()

    if not st.session_state.all_db_tables_info.empty:
        st.dataframe(st.session_state.all_db_tables_info, use_container_width=True, hide_index=True)
        table_names = st.session_state.all_db_tables_info['table_name'].tolist()
        selected_db_table = st.selectbox(
            "Select a Database Table for Mapping (Source Columns)",
            options=[''] + table_names, # Add an empty option
            index=0 if st.session_state.selected_db_table is None else (table_names.index(st.session_state.selected_db_table) + 1 if st.session_state.selected_db_table in table_names else 0),
            key="db_table_selector"
        )
        if selected_db_table and selected_db_table != st.session_state.selected_db_table:
            st.session_state.selected_db_table = selected_db_table
            # Reset mappings if table changes
            reset_mappings()
    else:
        st.warning("No database tables found or connection error. Check your `PostgresDB` setup.")

with col_config_right:
    st.subheader("Upload Ontology File")
    

# --- Data Loading ---
database_list = []
ontology_list = []

if st.session_state.selected_db_table:
    database_list = load_db_columns(st.session_state.selected_db_table)

ontology_list, available_namespaces = load_ontology_terms()


# Create DataFrames for display and interaction
df1 = pd.DataFrame({'term': database_list})
df2 = pd.DataFrame({'field': ontology_list})


# --- Status Bar ---
st.info(
    f"**Status:** " +
    (f"Selected from Database: **{st.session_state.selected_term_1}**. Now select a match from Ontology."
     if st.session_state.selected_term_1
     else "Select a term from Database to begin mapping.")
)

# --- Main Layout (Side-by-Side DataFrames for Mapping) ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.header(f"Columns from: {st.session_state.selected_db_table or 'No Table Selected'}")
    if not df1.empty:
        st.dataframe(df1, use_container_width=True, hide_index=True)
        st.markdown("---")
        for _, row in df1.iterrows():
            term = row['term']
            is_mapped = term in st.session_state.mappings
            btn_type = "primary" if st.session_state.selected_term_1 == term else "secondary"
            
            st.button(
                f"Map: **{term}**",
                key=f"df1_{term}",
                on_click=handle_df1_click,
                args=(term,),
                disabled=is_mapped,
                use_container_width=True,
                type=btn_type
            )
    else:
        st.info("Please select a database table above to load its columns for mapping.")

with col2:
    st.header("Ontology Terms")
    if not df2.empty:
        st.dataframe(df2, use_container_width=True, hide_index=True)
        st.markdown("---")
        # Only show dropdown if a database term is selected
        if st.session_state.selected_term_1:
            # Exclude ontology terms already mapped as destinations
            unmapped_ontology_terms = [field for field in df2['field'] if field not in st.session_state.mappings.values()]
            selected_ontology_term = st.selectbox(
                f"Map to: (Ontology term for '{st.session_state.selected_term_1}')",
                options=[''] + unmapped_ontology_terms,
                index=0,
                key=f"ontology_dropdown_{st.session_state.selected_term_1}"
            )
            if selected_ontology_term:
                handle_df2_click(selected_ontology_term)
        else:
            st.info("Select a database column on the left to map to an ontology term.")
    else:
        st.info("Please upload an ontology file above to load its terms.")

# --- Mappings Display and SHACL Export ---
st.header("Resulting Mappings", divider='rainbow')

if st.session_state.mappings:
    for source, destination in st.session_state.mappings.items():
        st.success(f"**{source}** `->` **{destination}**")

    st.subheader("SHACL Input (JSON representation of mappings):")
    st.json(st.session_state.mappings)
    
    shacl_content = generate_shacl_file(st.session_state.mappings, st.session_state.selected_db_table)
    st.subheader("Generated SHACL File Content (Turtle):")
    st.code(shacl_content, language='turtle')

    # Download button for SHACL file
    st.download_button(
        label="Download SHACL Mappings (.ttl)",
        data=shacl_content,
        file_name=f"shacl_mappings_{st.session_state.selected_db_table or 'default'}.ttl",
        mime="text/turtle",
        use_container_width=True,
        type="primary"
    )
    
    st.button("Reset Mappings", on_click=reset_mappings, use_container_width=True, type="secondary")

else:
    st.write("No mappings created yet.")