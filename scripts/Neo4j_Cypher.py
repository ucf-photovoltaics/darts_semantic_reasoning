""""
Author: Jackson Windhorst
R2RML autogenerate file
References: Brent 
"""

# imports the postgresdb class that Brent made
from postgres_operations import PostgresDB 

# Defining column to predicate mapping for R2RML
# Use a simple dictionary
column_mapping = {
    "module_id": "mds:ProdModuleID",
    "serial_number": "co:NodeSerialNumber",
    "make": "co:Manufacturer",
    "model": "mds:ModuleModel",
    "nameplate_pmp": "mds:NameplateMaximumPower",
    "nameplate_vmp": "mds:NameplateVoltageAtMaximumPower",
    "nameplate_imp": "mds:NameplateCurrentAtMaximumPower",
    "nameplate_voc": "mds:NameplateOpenCircuitVoltage",
    "nameplate_isc": "mds:NameplateShortCircuitCurrent",
    "temperature_coefficient_voltage": "mds:VoltageTemperatureCoefficient",
    "temperature_coefficient_power": "mds:PowerTemperatureCoefficient",
    "temperature_coefficient_current": "mds:CurrentTemperatureCoefficient",
    "module_packaging": "mds:ModulePackaging",
    "interconnection_scheme": "mds:InterconnectionScheme",
    "number_parallel_strings": "mds:NumberOfParallelStrings",
    "cells_per_string": "mds:CellsPerString",
    "module_arc": "mds:ModuleARC",
    "connector_type": "mds:ConnectorType",
    "junction_box_locations": "mds:JunctionBoxLocation",
    "number_junction_box": "mds:NumberOfJunctionBoxes",
    "number_busbars": "mds:NumberOfBusbars",
    "cell_area": "mds:CellArea",
    "module_area": "mds:ModuleArea",
    "cell_technology": "mds:CellTechnology",
    "wafer_doping_polarity": "mds:WaferDopingPolarity",
    "wafer_crystallinity": "mds:WaferCrystallinity",
    "encapsulant": "mds:EncapsulantMaterial",
    "backsheet": "mds:BacksheetMaterial",
    "frame_material": "mds:FrameMaterial",
    "x": "geo:lat",
    "y": "geo:long"
}

# Output path and table for logical table mapping
output_path = "module_metadata.cypher"
table_name = "module_metadata"

# Helper function to escape safely and format values for Cypher
def escape_value(value):
    if isinstance(value, str):
        return f'"{value}"'
    elif value is None:
        return 'null'
    return str(value)


# Main function that generates Cypher CREATE statements
def generate_cypher(df):
    lines = []
    lines.append("// Cypher script for custom ontology import")
    lines.append(f"// Each row from `{table_name}` becomes a :PhotovoltaicModule node with MDS properties")

    for _, row in df.iterrows():
        props = []
        for col, val in row.items():
            predicate = column_mapping.get(col)
            if predicate:
                props.append(f"`{predicate}`: {escape_value(val)}") # uses ontology term as key
            else:
                props.append(f"`{col}`: {escape_value(val)}")  # fallback to original column name

        cypher = f"CREATE (:PhotovoltaicModule {{ {', '.join(props)} }});"
        lines.append(cypher)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Cypher mapping script written to: {output_path}")

# Main entry point of script
if __name__ == "__main__":
    username = "dpv"
    password = "sun"
    db = PostgresDB(username, password)
    df = db.read_records_from_postgres(f"SELECT * FROM instrument_data.{table_name}")

    # If data exists, generate Cypher script
    if df is not None and not df.empty:
        generate_cypher(df)
    else:
        print("No data found for table:", table_name)