import pandas as pd

# Load your module-metadata CSV file
df = pd.read_csv(df, sep='\t')
df = fm.get_files()[0]
# Define RDF prefixes
PREFIXES = """@prefix ex: <http://example.org/schema/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

# Function to generate RDF triples for each row
def row_to_rdf(row):
    rdf = f"ex:{row['module-id']} a ex:Module ;\n"
    for col, value in row.items():
        if pd.isna(value):  # Skip null values
            continue
        predicate = f"ex:{col.replace(' ', '-').lower()}"  # Convert column name to RDF predicate
        if isinstance(value, int):
            rdf += f"    {predicate} {value}^^xsd:integer ;\n"
        elif isinstance(value, float):
            rdf += f"    {predicate} {value}^^xsd:decimal ;\n"
        else:
            rdf += f"    {predicate} \"{value}\" ;\n"
    rdf = rdf.rstrip(" ;\n") + " .\n\n"
    return rdf

# Convert all rows
rdf_data = PREFIXES + "\n".join(df.apply(row_to_rdf, axis=1))

# Save to file
with open("module-metadata.ttl", "w") as f:
    f.write(rdf_data)

print("RDF data saved as module-metadata.ttl")


"""PREFIX ex: <http://example.org/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

ex:ModuleShape {
    ex:moduleID xsd:string ;
    ex:serialNumber xsd:string? ;
    ex:make xsd:string? ;
    ex:model xsd:string? ;
    ex:nameplatePmp xsd:decimal? ;
    ex:nameplateVmp xsd:decimal? ;
    ex:nameplateImp xsd:decimal? ;
    ex:nameplateVoc xsd:decimal? ;
    ex:nameplateIsc xsd:decimal? ;
    ex:temperatureCoefficientVoltage xsd:string? ;
    ex:temperatureCoefficientPower xsd:string? ;
    ex:temperatureCoefficientCurrent xsd:string? ;
    ex:modulePackaging xsd:string? ;
    ex:interconnectionScheme xsd:string? ;
    ex:numberParallelStrings xsd:string? ;
    ex:cellsPerString xsd:string? ;
    ex:moduleArc xsd:string? ;
    ex:connectorType xsd:string? ;
    ex:junctionBoxLocations xsd:string? ;
    ex:numberJunctionBox xsd:string? ;
    ex:numberBusbars xsd:string? ;
    ex:cellArea xsd:string? ;
    ex:moduleArea xsd:string? ;
    ex:cellTechnology xsd:string? ;
    ex:waferDopingPolarity xsd:string? ;
    ex:waferCrystallinity xsd:string? ;
    ex:encapsulant xsd:string? ;
    ex:backsheet xsd:string? ;
    ex:frameMaterial xsd:string? ;
    ex:x xsd:integer? ;
    ex:y xsd:integer? ;
}"""

@prefix ex: <http://example.org/schema/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:F2203-0003 a ex:Module ;
    ex:moduleID "F2203-0003" ;
    ex:make "HQST" ;
    ex:model "10D" ;
    ex:nameplatePmp 10.0^^xsd:decimal ;
    ex:nameplateVmp 17.5^^xsd:decimal ;
    ex:nameplateVoc 21.6^^xsd:decimal ;
    ex:connectorType "MC4" .
    
    PREFIX ex: <http://example.org/schema/>

SELECT ?moduleID ?make ?model
WHERE {
  ?module a ex:Module ;
          ex:moduleID ?moduleID ;
          ex:make ?make ;
          ex:model ?model .
}

PREFIX mds: <#>
PREFIX PMDCo: <#>
PREFIX pmd: <#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ex: <#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

start = @<ModuleShape>

<ModuleShape> {
  a [mds:ProdModule] ;
  mds:ProdModuleID xsd:string ;
  PMDCo:NodeSerialNumber xsd:string ;
  pmd:Manufacturer xsd:string ;
  dcterms:title xsd:string ;
  mds:PowerSTC xsd:decimal ; # Unit: QUDT:KiloW
  mds:VoltageOpenCircuit xsd:decimal ;
  mds:CurrentShortCircuit xsd:decimal ;
  ex:nameplateVmp xsd:decimal ;
  ex:nameplateImp xsd:decimal ;
  ex:temperatureCoefficientVoltage xsd:string ;
  ex:temperatureCoefficientPower xsd:string ;
  ex:temperatureCoefficientCurrent xsd:string ;
  ex:modulePackaging xsd:string ;
  ex:numberParallelStrings xsd:string ;
  ex:cellsPerString xsd:string ;
  pmd:component @<EncapsulantShape> ;
  pmd:component @<BacksheetShape> ;
  pmd:frameMaterial xsd:string ;
  mds:CellTechnologyType xsd:string ;
  ex:waferDopingPolarity xsd:string ;
  ex:waferCrystallinity xsd:string ;
  pmd:cellArea xsd:decimal ;
  pmd:moduleArea xsd:decimal ;
  ex:moduleArc xsd:string ;
  ex:connectorType xsd:string ;
  ex:junctionBoxLocations xsd:string ;
  ex:numberJunctionBox xsd:string ;
  ex:numberBusbars xsd:string
}

<EncapsulantShape> {
    a [mds:ProdEncapsulant] ;
    mds:EncapsulantMaterial xsd:string
}

<BacksheetShape> {
    a [mds:ProdBacksheet] ;
    mds:BacksheetMaterial xsd:string
}


@prefix ex: <http://example.org/schema/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

ex:ModuleShape
  a sh:NodeShape ;
  sh:targetClass ex:Module ;
  
  # PRIMARY KEY
  sh:property [
    sh:path ex:moduleID ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:unique true ;
    sh:name "module-id" ;
  ] ;

  # STRING fields (TEXT in SQL)
  sh:property [ sh:path ex:serialNumber ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "serial-number" ] ;
  sh:property [ sh:path ex:make ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "make" ] ;
  sh:property [ sh:path ex:model ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "model" ] ;
  sh:property [ sh:path ex:modulePackaging ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "module-packaging" ] ;
  sh:property [ sh:path ex:interconnectionScheme ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "interconnection-scheme" ] ;
  sh:property [ sh:path ex:connectorType ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "connector-type" ] ;
  sh:property [ sh:path ex:junctionBoxLocations ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "junction-box-locations" ] ;
  sh:property [ sh:path ex:cellTechnology ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "cell-technology" ] ;
  sh:property [ sh:path ex:waferDopingPolarity ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "wafer-doping-polarity" ] ;
  sh:property [ sh:path ex:waferCrystallinity ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "wafer-crystallinity" ] ;
  sh:property [ sh:path ex:encapsulant ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "encapsulant" ] ;
  sh:property [ sh:path ex:backsheet ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "backsheet" ] ;
  sh:property [ sh:path ex:frameMaterial ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "frame-material" ] ;
  sh:property [ sh:path ex:moduleArc ; sh:datatype xsd:string ; sh:minCount 0 ; sh:name "module-arc" ] ;

  # DECIMAL fields (REAL in SQL)
  sh:property [ sh:path ex:nameplatePmp ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "nameplate-pmp" ] ;
  sh:property [ sh:path ex:nameplateVmp ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "nameplate-vmp" ] ;
  sh:property [ sh:path ex:nameplateImp ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "nameplate-imp" ] ;
  sh:property [ sh:path ex:nameplateVoc ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "nameplate-voc" ] ;
  sh:property [ sh:path ex:nameplateIsc ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "nameplate-isc" ] ;
  sh:property [ sh:path ex:temperatureCoefficientVoltage ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "temperature-coefficient-voltage" ] ;
  sh:property [ sh:path ex:temperatureCoefficientPower ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "temperature-coefficient-power" ] ;
  sh:property [ sh:path ex:temperatureCoefficientCurrent ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "temperature-coefficient-current" ] ;
  sh:property [ sh:path ex:cellArea ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "cell-area" ] ;
  sh:property [ sh:path ex:moduleArea ; sh:datatype xsd:decimal ; sh:minCount 0 ; sh:name "module-area" ] ;

  # INTEGER fields
  sh:property [ sh:path ex:numberParallelStrings ; sh:datatype xsd:integer ; sh:minCount 0 ; sh:name "number-parallel-strings" ] ;
  sh:property [ sh:path ex:cellsPerString ; sh:datatype xsd:integer ; sh:minCount 0 ; sh:name "cells-per-string" ] ;
  sh:property [ sh:path ex:numberBusbars ; sh:datatype xsd:integer ; sh:minCount 0 ; sh:name "number-busbars" ] ;
  sh:property [ sh:path ex:numberJunctionBox ; sh:datatype xsd:integer ; sh:minCount 0 ; sh:name "number-junction-box" ] ;
  sh:property [ sh:path ex:x ; sh:datatype xsd:integer ; sh:minCount 0 ; sh:name "cells_x" ] ;
  sh:property [ sh:path ex:y ; sh:datatype xsd:integer ; sh:minCount 0 ; sh:name "cells_y" ] .
  
  
  
  
  
  
  
  
  
  
  
PREFIX mds: <https://cwrusdle.bitbucket.io/mds/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

<mds:PVModuleShape> {
  # Required properties
  mds:PhotovoltaicModuleID   xsd:string ;           # module-id
  mds:SerialNumber           xsd:string ;           # serial-number
  mds:Make                   xsd:string ;           # make
  mds:PhotovoltaicModel      xsd:string ;           # model
  mds:NameplatePmp           xsd:float ;            # nameplate-pmp
  mds:NameplateVmp           xsd:float ;            # nameplate-vmp
  mds:NameplateImp           xsd:float ;            # nameplate-imp
  mds:NameplateVoc           xsd:float ;            # nameplate-voc
  mds:NameplateIsc           xsd:float ;            # nameplate-isc

  mds:TemperatureCoefficientVoltage xsd:float ? ;   # temperature-coefficient-voltage
  mds:TemperatureCoefficientPower     xsd:float ? ;   # temperature-coefficient-power
  mds:TemperatureCoefficientCurrent   xsd:float ? ;   # temperature-coefficient-current
  mds:ModulePackaging                   xsd:string ? ;  # module-packaging
  mds:InterconnectionScheme             xsd:string ? ;  # interconnection-scheme
  mds:NumberParallelStrings             xsd:integer ? ; # number-parallel-strings
  mds:CellsPerString                    xsd:integer ? ; # cells-per-string
  mds:ModuleArc                         xsd:string ? ;  # module-arc
  mds:ConnectorType                     xsd:string ? ;  # connector-type
  mds:JunctionBoxLocations              xsd:string ? ;  # junction-box-locations
  mds:NumberJunctionBox                 xsd:integer ? ; # number-junction-box
  mds:NumberBusbars                     xsd:integer ? ; # number-busbars
  mds:CellArea                          xsd:float ? ;   # cell-area
  mds:ModuleArea                        xsd:float ? ;   # module-area
  mds:CellTechnology                    xsd:string ? ;  # cell-technology
  mds:WaferDopingPolarity               xsd:string ? ;  # wafer-doping-polarity
  mds:WaferCrystallinity                xsd:string ? ;  # wafer-crystallinity
  mds:Encapsulant                       xsd:string ? ;  # encapsulant
  mds:Backsheet                         xsd:string ? ;  # backsheet
  mds:FrameMaterial                     xsd:string ? ;  # frame-material
  mds:NumberCellsX                      xsd:int ? ;     # cells-x
  mds:NumberCellsY                      xsd:int ?       # cells-y
}



@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mds: <https://cwrusdle.bitbucket.io/mds/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

mds:PVModuleShape a sh:NodeShape ;
    sh:targetClass mds:PhotovoltaicModule ;

    # Required properties
    sh:property [
        sh:path mds:PhotovoltaicModuleID ;  # module-id
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:SerialNumber ;           # serial-number
        sh:datatype xsd:string ;
        sh:minCount 1 ; sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:Make ;                   # make
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:PhotovoltaicModel ;      # model
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NameplatePmp ;           # nameplate-pmp
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NameplateVmp ;           # nameplate-vmp
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NameplateImp ;           # nameplate-imp
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NameplateVoc ;           # nameplate-voc
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NameplateIsc ;           # nameplate-isc
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;

    # Optional properties
    sh:property [
        sh:path mds:TemperatureCoefficientVoltage ;  # temperature-coefficient-voltage
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:TemperatureCoefficientPower ;      # temperature-coefficient-power
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:TemperatureCoefficientCurrent ;    # temperature-coefficient-current
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:ModulePackaging ;                  # module-packaging
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:InterconnectionScheme ;            # interconnection-scheme
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NumberParallelStrings ;            # number-parallel-strings
        sh:datatype xsd:integer ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:CellsPerString ;                   # cells-per-string
        sh:datatype xsd:integer ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:ModuleArc ;                        # module-arc
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:ConnectorType ;                    # connector-type
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:JunctionBoxLocations ;             # junction-box-locations
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NumberJunctionBox ;                # number-junction-box
        sh:datatype xsd:integer ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:NumberBusbars ;                    # number-busbars
        sh:datatype xsd:integer ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:CellArea ;                         # cell-area
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:ModuleArea ;                       # module-area
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:CellTechnology ;                   # cell-technology
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:WaferDopingPolarity ;              # wafer-doping-polarity
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:WaferCrystallinity ;               # wafer-crystallinity
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:Encapsulant ;                      # encapsulant
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:Backsheet ;                        # backsheet
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:FrameMaterial ;                    # frame-material
        sh:datatype xsd:string ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    
    # Custom properties for coordinates (not defined in the TTL file)
    sh:property [
        sh:path mds:x ;
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path mds:y ;
        sh:datatype xsd:float ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
    ] .
