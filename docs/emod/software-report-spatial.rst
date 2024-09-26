=============
SpatialReport
=============

The spatial output report breaks the :term:`channel` data down per node, rather than across the
entire simulation. It is a *set* of binary files, consisting of one file per channel. For each value
set in the **Spatial_Output_Channels** configuration parameter array, a binary file with the name
convention SpatialReport_<channel>.bin is generated. In addition, **Enable_Spatial_Output** must be
set to 1.


The binary format of the file consists of a stream of 4-byte integers followed by a stream of 4-byte
floating point values. The first value is a 4-byte integer representing the number of nodes in the
file and the second is a 4-byte integer that contains the number of time steps in the file.
Following these two values is a stream of 4-byte integers that contain the node ID values in the
order they will appear in the rest of the file. Following the node IDs is an array of 4-byte
floating point values that represent the output values at the first time step for each node. The
next array contains the values at the second time step, and so on.

The following diagram shows the format for data in the spatial output report file:

.. image:: ../images/file-structure/spatialOutputBFF.jpg


Configuration
=============


The following is an example of a spatial output channel configuration (config.json), and the
following table defines the spatial output channels you can add to this report.

.. literalinclude:: ../json/report-spatial.json
    :language: json

