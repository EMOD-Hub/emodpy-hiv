# How to create migration files

You can create the JSON metadata and binary migration files needed by EMOD to run simulations
from either CSV or JSON data using Python scripts provided by IDM. You can assign the same
probability of migration to each individual in a node (vector or human), or you can assign different
migration rates based on age and/or gender (human only).

> **NOTE:**
> The **IdReference** must match the value in the demographics file. Each node can be connected a
> maximum of 100 destination nodes.
>
> For both scripts, use one of the following migration types:
>
> * LOCAL_MIGRATION
> * AIR_MIGRATION
> * REGIONAL_MIGRATION
> * SEA_MIGRATION

For regional migration, you may want to set up migration such that if a node is not part of the
network, the migration of individuals to and from that node considers the closest road hub city. You
can do this by constructing a Voronoi_ tiling based on road hubs, with each non-hub connected to
the hub of its tile.

## Create from CSV input

To use the same average migration rate for every individual in a node, create the migration files from a CSV input file. 

1.  Create a CSV file with the following three columns (do not include column headers):

    From_Node_ID
        The origin node, which must match a node ID in the demographics file. You do not need to have the same number of entries for each **From_Node_ID**. 
    To_Node_ID
        The destination node, which must match a node ID in the demographics file.
    Rate
        The average number of trips per day.

1.  Run the [convert_txt_to_bin.py][emod-convert-txt-to-bin] script using the command format below::

        python convert_txt_to_bin.py [input-migration-csv] [output-bin] [migration-type] [idreference]

This will create both the metadata and binary file needed by EMOD. 

## Create from JSON input

To vary the average migration rate based on age and/or gender, create the migration files from a JSON input file.

1.  Create a JSON file with the structure described in the sections below.

1.  Run the [convert_json_to_bin.py][emod-convert-json-to-bin] script using the command format below::

        python convert_json_to_bin.py [input-json] [output-bin] [migration-type]

This will create both the metadata and binary file needed by EMOD. 

### JSON parameters

The following parameters are used in the JSON file for migration file generation.  

### Example file

*See example: [migration-input-file.json](../json/migration-input-file.json)*
