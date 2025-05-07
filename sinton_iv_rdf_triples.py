# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 17:33:29 2025

@author: Doing
"""

"""
Created on Wed Feb 26 14:42:30 2025

@author: Brent Thompson
"""
import pandas as pd
from sqlite_operations import SQLiteDB
import os
import json

# Connect to SQL database
db = SQLiteDB("C:/Users/Doing/University of Central Florida/UCF_Photovoltaics_GRP - module_databases/Complete_Dataset.db")

rows = db.read_records('"sinton-metadata-results-joined"')

# JSON-LD context and predicate mappings
jsonld_context = {
    "mds": "https://cwrusdle.bitbucket.io/mds/"
}

field_mapping = {
    "serial_number": {"prop": "mds:SerialNumber", "datatype": "string"},
    "Sample_ID": {"prop": "mds:CurrentVoltageSample", "datatype": "string"},
    "Measurement_Date-Time": {"prop": "mds:CurrentVoltageResultsTimestamp", "datatype": "string"},
    "Isc_(A)": {"prop": "mds:ShortCircuitCurrent", "datatype": "float"},
    "Voc_(V)": {"prop": "mds:OpenCircuitVoltage", "datatype": "float"},
    "Imp_(A)": {"prop": "mds:CurrentAtMaxPower", "datatype": "float"},
    "Vmp_(V)": {"prop": "mds:VoltageAtMaxPower", "datatype": "float"},
    "Pmp_(W)": {"prop": "mds:MaximumPowerPoint", "datatype": "float"},
    "FF_(percent)": {"prop": "mds:FillFactor", "datatype": "float"},
    "Efficiency_(percent)": {"prop": "mds:CellEfficiency", "datatype": "float"},
    "Rsh_(ohm)": {"prop": "mds:ShuntResistance", "datatype": "float"},
    "Rs_(ohm)": {"prop": "mds:SeriesResistance", "datatype": "float"},
    "Intensity_(suns)": {"prop": "mds:SunIntensity", "datatype": "float"},
    "Cell_Area_(cm2)": {"prop": "mds:SampleCellArea", "datatype": "float"},
    "Total_Area_(cm2)": {"prop": "mds:SampleTotalArea", "datatype": "float"},
    "Sample_Type": {"prop": "mds:CurrentVoltageSample", "datatype": "string"},
    "Number_of_Cells_per_String": {"prop": "mds:NumberOfCellsPerString", "datatype": "int"},
    "Number_of_Strings": {"prop": "mds:NumberStrings", "datatype": "int"},
    "Resistivity_(ohm-cm)": {"prop": "mds:SampleResistivity", "datatype": "float"},
    "Reference_Constant_(V/sun)": {"prop": "mds:CellReferenceConstant", "datatype": "float"},
    "Voltage_Temperature_Coefficient_(mV/C)": {"prop": "mds:VoltageTemperatureCoefficient", "datatype": "float"}
}

# Create output directory
output_dir = "C:/Data/jsonld_output"
os.makedirs(output_dir, exist_ok=True)

# Iterate over each row in the DataFrame to create JSON-LD files
for _, row in rows.iterrows():
    mfr_filename = str(row["mfr_filename"]).strip()
    if mfr_filename.lower() == "nan" or mfr_filename == "":
        continue

    module_data = {
        "@context": jsonld_context,
        "@id": f"mds:{row['sinton_iv_id']}",
        "@type": "mds:CurrentVoltageResults"
    }

    for col, info in field_mapping.items():
        if col not in row:
            continue
        value = row[col]
        if pd.isna(value):
            continue
        if isinstance(value, str) and (value.strip() == "" or value.strip().upper() == "UNKNOWN"):
            continue

        dtype = info["datatype"]
        try:
            if dtype == "string":
                converted_value = str(value).strip()
            elif dtype == "float":
                converted_value = float(value)
            elif dtype == "int":
                converted_value = int(float(value))
            else:
                converted_value = value
            module_data[info["prop"]] = converted_value
        except:
            continue

    # Write JSON-LD
    safe_name = mfr_filename.replace("/", "_").replace("\\", "_").strip('.mfr')
    output_file = os.path.join(output_dir, f"{safe_name}.jsonld")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(module_data, f, indent=2)
    print(f"Saved JSON-LD for {row['sinton_iv_id']} to {output_file}")