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
output_path = "module_metadata_r2rml.ttl"
table_name = "module_metadata"

# This function generates a turtle file from a dataframe
def generate_r2rml(df):
    columns = df.columns.tolist()

    # Begins the r2rml turtle content with prefixes and logical table
    lines = []
    lines.append(f"""@prefix rr: <http://www.w3.org/ns/r2rml#> .
@prefix mds: <https://cwrusdle.bitbucket.io/mds#> .
@prefix co: <https://w3id.org/pmd/co#> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix ex: <http://example.org/> .

<#ModuleMetadataTriplesMap>
  a rr:TriplesMap ;
  rr:logicalTable [ rr:tableName "{table_name}" ] ;

  rr:subjectMap [
    rr:template "http://example.org/module/{{module_id}}" ;
    rr:class mds:PhotovoltaicModule ;
  ] ;
""")
    # Add predicate-object maps for each matching column
    predicates_added = 0
    for col in columns:
        predicate = column_mapping.get(col)
        if not predicate:
            continue
        suffix = " ;"
        lines.append(f"""  rr:predicateObjectMap [
    rr:predicate {predicate} ;
    rr:objectMap [ rr:column "{col}" ]
  ]{suffix}""")
        predicates_added += 1
    # Replace final semicolon with a period to properly end a turtle syntax(very important)
    if predicates_added > 0:
        lines[-1] = lines[-1][:-2] + " ."

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"R2RML mapping written to: {output_path}")


# Main exe
if __name__ == "__main__":
    username = "dpv"
    password = "sun"
    db = PostgresDB(username, password)
    df = db.read_records_from_postgres("SELECT * FROM instrument_data.module_metadata")

    # Just to check if data is generated
    if df is not None and not df.empty:
        generate_r2rml(df)
    else:
        print("No data available to generate R2RML.")