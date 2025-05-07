# darts\_semantic\_reasoning

**Project Page:** [Cloud-Based Semantic Data Retrieval and Graph Database Ingestion](https://ucf-dpv.notion.site/Cloud-Based-Semantic-Data-Retrieval-and-Graph-Database-Ingestion-1c18d52e71518086831ad6723e3bcb62?pvs=4)

# Code Summary

## 1. SHACL Constraints & JSON-LD Data

### iv-shacl-shape.ttl:

* Defines validation rules for IV measurements using SHACL, ensuring data consistency (e.g., `mds:SampleCellArea` must be an `xsd:float`).
* Links properties to MDS ontology terms (e.g., `sh:path mds:SampleCellArea`), providing semantic context.

### IVT20241209-QCELLS...jsonld:

* Represents IV measurement data as JSON-LD, using MDS ontology terms (e.g., `mds:ShortCircuitCurrent`).
* **Strengths:** Validates against SHACL, uses standardized URIs, and embeds units (e.g., `"mds:ShortCircuitCurrent": 10.273036`).
* **Gap:** No explicit links to QUDT units (e.g., `qudt:MilliM` for cm²) in the JSON-LD context.

## 2. MDS Ontologies

**MDS-Onto-BuiltEnv-PV-Module.ttl**, **MDS-Onto-Charact-Elec-IV-v0.3.0.0.ttl**, etc.:

* Define PV module concepts (e.g., `mds:PhotovoltaicModule`, `mds:CellEfficiency`) with subclass hierarchies and semantic relationships.
* Integrate QUDT units (e.g., `QUDT:KiloW` for `mds:PowerSTC`) and align with PMDco (Process-Material-Data Core Ontology).
* **Strengths:** Rich semantic definitions, cross-ontology imports (QUDT, PMDco), and alignment with industry standards (OrangeButton Taxonomy).
* **Gap:** Some properties (e.g., `mds:value`) lack explicit unit annotations, limiting automated reasoning.

## 3. Python Script (`module_metadata_rdf_triples.py`)

* Maps SQL columns to RDF triples using MDS ontology terms (e.g., `"module-id"` → `MDS.PhotovoltaicModuleID`).
* Generates typed literals (e.g., `xsd:float` for `nameplate-pmp`) and validates data integrity (skips `"UNKNOWN"` values).
* **Strengths:** Translates relational data to RDF, enabling SPARQL querying.
* **Gaps:**

  * No R2RML mapping file (required for automated relational → RDF conversion).
  * Limited handling of complex relationships (e.g., `pmd:component` links between modules and junction boxes).

## R2RML Mapping File:

* The Python script performs a direct column→predicate mapping but does not generate R2RML.
* A tool like **RMLMapper** could automate this using the existing mappings.

## Postgres Table Comments:

* The MDS ontologies define units (e.g., `QUDT:KiloW`), but these are not yet propagated to Postgres column comments.
* A script could update comments using:

  ```sql
  COMMENT ON COLUMN ... IS 'mds:PowerSTC (unit: qudt:KiloW)';
  ```

## OnTop Virtual Graph:

* The generated RDF triples (e.g., `pv_modules.ttl`) can be loaded into a triplestore like GraphDB.
* OnTop requires **R2RML mappings** to virtualize the relational data as RDF.

## Recommendations

### Enhance Ontologies:

* Add explicit QUDT unit annotations (e.g., `pmd:unit qudt:Ohm` for `mds:SeriesResistance`).
* Define object properties for relationships (e.g., `mds:composedOf` links modules to cells).

### Generate R2RML:

* Convert the Python script’s mappings into R2RML syntax to enable scalable ETL.

### Update Postgres Metadata:

* Use the MDS and QUDT URIs in Postgres column comments to enrich schema documentation.

### Leverage SHACL for Validation:

* Integrate SHACL validation into the ETL pipeline to ensure data quality before RDF conversion.

## Conclusion

These files provide a strong foundation for semantic reasoning but require R2RML mappings and tighter integration with QUDT units to fully achieve sprint goals. By extending the ontologies, automating R2RML generation, and enriching Postgres metadata, we can unlock advanced querying and inference capabilities via OnTop.
