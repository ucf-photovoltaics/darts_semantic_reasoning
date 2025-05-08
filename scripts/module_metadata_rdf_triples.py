# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:42:30 2025

@author: Brent Thompson
"""
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD, URIRef
from sqlite_operations import SQLiteDB
import file_management as fm


# Connect to SQL database
db = SQLiteDB()
rows = db.read_records('"module-metadata"') 

# Define namespaces
MDS = Namespace("https://cwrusdle.bitbucket.io/mds/")
EX = Namespace("http://example.org/module/")
graph = Graph()
graph.bind("mds", MDS)
graph.bind("ex", EX)


# Mapping between SQL column names and RDF predicates (from ShEx schema)
mapping = {
    "module-id": MDS.PhotovoltaicModuleID,           # module-id
    "serial-number": MDS.SerialNumber,               # serial-number
    "make": MDS.Make,                                # make
    "model": MDS.PhotovoltaicModel,                   # model
    "nameplate-pmp": MDS.NameplatePmp,                # nameplate-pmp
    "nameplate-vmp": MDS.NameplateVmp,                # nameplate-vmp
    "nameplate-imp": MDS.NameplateImp,                # nameplate-imp
    "nameplate-voc": MDS.NameplateVoc,                # nameplate-voc
    "nameplate-isc": MDS.NameplateIsc,                # nameplate-isc
    "temperature-coefficient-voltage": MDS.TemperatureCoefficientVoltage,  # temperature-coefficient-voltage
    "temperature-coefficient-power": MDS.TemperatureCoefficientPower,      # temperature-coefficient-power
    "temperature-coefficient-current": MDS.TemperatureCoefficientCurrent,  # temperature-coefficient-current
    "module-packaging": MDS.ModulePackaging,         # module-packaging
    "interconnection-scheme": MDS.InterconnectionScheme,  # interconnection-scheme
    "number-parallel-strings": MDS.NumberParallelStrings, # number-parallel-strings
    "cells-per-string": MDS.CellsPerString,          # cells-per-string
    "module-arc": MDS.ModuleArc,                     # module-arc
    "connector-type": MDS.ConnectorType,             # connector-type
    "junction-box-locations": MDS.JunctionBoxLocations, # junction-box-locations
    "number-junction-box": MDS.NumberJunctionBox,    # number-junction-box
    "number-busbars": MDS.NumberBusbars,             # number-busbars
    "cell-area": MDS.CellArea,                       # cell-area
    "module-area": MDS.ModuleArea,                   # module-area
    "cell-technology": MDS.CellTechnology,           # cell-technology
    "wafer-doping-polarity": MDS.WaferDopingPolarity,  # wafer-doping-polarity
    "wafer-crystallinity": MDS.WaferCrystallinity,    # wafer-crystallinity
    "encapsulant": MDS.Encapsulant,                  # encapsulant
    "backsheet": MDS.Backsheet,                      # backsheet
    "frame-material": MDS.FrameMaterial,             # frame-material
    "x": MDS.NumberCellsX,                           # cells-x (using 'x' column)
    "y": MDS.NumberCellsY                            # cells-y (using 'y' column)
}

# Build a comma-separated, quoted column list from the mapping keys
columns = list(mapping.keys())

# Iterate over each row in the result
for row in rows:
    # Use module-id (first column) to form a unique subject URI
    module_id = row[0]
    subject = URIRef(EX + str(module_id))
    
    # Optionally add an RDF type for the module
    graph.add((subject, RDF.type, MDS.PhotovoltaicModule))
    
    # For each column, add a triple if a valid value exists (skip None, empty, or "UNKNOWN")
    for col, value in zip(columns, row):
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
            if value == "" or value.upper() == "UNKNOWN":
                continue
        predicate = mapping[col]
        # Determine the datatype based on the ShEx schema (here using XSD.string, XSD.float, or XSD.int)
        # For simplicity, the script uses the following heuristic:
        if col in ["nameplate-pmp", "nameplate-vmp", "nameplate-imp", "nameplate-voc", "nameplate-isc",
                   "temperature-coefficient-voltage", "temperature-coefficient-power", "temperature-coefficient-current",
                   "cell-area", "module-area"]:
            dt = XSD.float
        elif col in ["number-parallel-strings", "cells-per-string", "number-junction-box"]:
            dt = XSD.integer
        elif col in ["x", "y"]:
            dt = XSD.int
        else:
            dt = XSD.string
        
        graph.add((subject, predicate, Literal(value, datatype=dt)))

# Serialize the RDF graph to Turtle format
    turtle_output = graph.serialize(format="turtle")
    graph.serialize(destination="pv_modules.ttl", format="turtle")

    print(turtle_output.decode("utf-8") if isinstance(turtle_output, bytes) else turtle_output)
