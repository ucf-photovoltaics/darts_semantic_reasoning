# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 17:41:16 2025

PostgreSQL operations module.

Author: Brent
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class PostgresDB:
    def __init__(self, username, password, host="34.73.180.136", port=5432, database="fsecdatabase"):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/{database}")

    def handle_error(self, error, context):
        print(f"Error in {context}: {str(error)}")  # Replace with logger if needed

    def create_postgres_records_from_dataframe(self, table_name, dataframe, if_exists='replace'):
        try:
            dataframe.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
        except SQLAlchemyError as e:
            self.handle_error(e, "inserting dataframe records")

    def read_records_from_postgres(self, query, params=None):
        try:
            return pd.read_sql(query, self.engine, params=params)
        except SQLAlchemyError as e:
            self.handle_error(e, "fetching data with SQLAlchemy")
            return None

    def fetch_data_by_date(self, table_name, start_date, end_date):
        query = f"""
        SELECT * FROM {table_name} 
        WHERE date BETWEEN %s AND %s;
        """
        return self.read_records_from_postgres(query, (start_date, end_date))

    def get_table_names_and_comments(self):
        query = """
        SELECT c.relname AS table_name, obj_description(c.oid) AS table_comment
        FROM pg_class c
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r' AND n.nspname NOT IN ('pg_catalog', 'information_schema');
        """
        return self.read_records_from_postgres(query)

    def get_table_schema(self, table_name):
        query = """
        SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s;
        """
        return self.read_records_from_postgres(query, (table_name,))

    def get_el_pairs(self, module_id):
        try:
            # Step 1: Get Isc
            isc_query = "SELECT \"nameplate_isc\" FROM instrument_data.module_metadata WHERE \"module_id\" = %s"
            isc_df = self.read_records_from_postgres(isc_query, (module_id,))
            if isc_df is None or isc_df.empty:
                raise ValueError(f"No Isc found for module {module_id}")
            isc_value = float(isc_df.iloc[0]["nameplate_isc"])
    
            # Step 2: Get EL measurements
            el_query = """
            SELECT "ID", "module-id", "date", "time", "current"  FROM instrument_data.el_metadata
            WHERE "module-id" = %s
            """
            el_df = self.read_records_from_postgres(el_query, (module_id,))
            if el_df is None or el_df.empty:
                return {"message": f"No EL measurements found for module {module_id}"}
    
            # Preprocess
            el_df["current"] = el_df["current"].astype(float)
            el_df["date"] = pd.to_datetime(el_df["date"]).dt.date
            el_df = el_df.sort_values(by=["date", "time"])  # Enforce sequential ordering

            # Step 3: Identify pairs for each date
            tolerance = 0.05 * isc_value
            pairs_by_date = {}
    
            grouped = el_df.groupby("date")
            for date, group in grouped:
                near_isc = group[group["current"].between(isc_value - tolerance, isc_value + tolerance)]
                near_01isc = group[group["current"].between(0.1 * isc_value - tolerance, 0.1 * isc_value + tolerance)]
    
                if not near_isc.empty and not near_01isc.empty:
                    # Use first match from each category to form a pair
                    pairs_by_date[str(date)] = {
                        "tenth_isc": near_01isc.iloc[0].to_dict(),
                        "one_isc": near_isc.iloc[0].to_dict()
                    }
    
            return pairs_by_date if pairs_by_date else {"message": "No matching EL pairs found."}

        except Exception as e:
            self.handle_error(e, "get_el_pairs")
            return {"error": str(e)}


# Example usage:
db = PostgresDB(username="dpv", password="sun")
#db.create_postgres_records_from_dataframe("table_name", dataframe)
 