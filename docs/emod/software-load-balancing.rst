====================
Load-balancing files
====================

If you are running a large simulation with multiple nodes, you may want to use a load balancing file
to distribute the computing load among multiple cores. This can be especially helpful if the nodes
vary considerably in size and, therefore, processing time. If no load balancing file is submitted,
the |exe_s| allocates simulation nodes to cores according to a checkerboard pattern.

For each simulation, the load balancing file contains information about the relative level of
processing time required for each geographical :term:`node`. The |exe_s| can then allocate nodes to
processors in such a way that the total processing required is evenly distributed across all
processors.

To use a load balancing file, you must set the configuration parameter **Load_Balance_Filename** to
the path to the load balancing file, relative to the input file directory. Load-balancing files can
be :term:`JSON (JavaScript Object Notation)` files, which are preferred, or binary files.

JSON file
=========

A JSON load-balancing file contains the **Load_Balance_Scheme_Nodes_On_Core_Matrix** parameter,
assigned an array of arrays, each of which represents a core and lists the **NodeID** of each node
to be processed on that core. If any node contained in the demographics file is not listed in the
load-balancing file, it will be processed on the first core.

For example, the load-balancing file shown below distributes the processing for 100 nodes across
4 cores, assigning more nodes to particular cores when those nodes require less processing time.

.. literalinclude:: ../json/load-balancing.json
   :language: json


Binary file
===========

A binary load-balancing file starts with an initial unsigned 4-byte integer that indicates the
number of nodes. Following that value is a series of 4-byte unsigned integers representing the
**NodeID** values. The number of values will be equal to the previously read number of nodes.
Following that, another series of 4-byte floating point values, with each value representing the
relative processing time required for each geographic node. Again, the number of values will be
equal to the previously read number of nodes. The series of values are set up such that the
:math:`i^{th}` entry in the series is equal to the cumulative proportion of the processing load for
all the previous nodes 0 through :math:`i`.

The cumulative nature of each node's value does not mean each node is assigned that amount for its
processing load. Rather, it is a way to make the internal calculations more efficient. For example,
if you had ten nodes and each node was assigned 10% of the load, the values assigned from node0 to
node9 would be the following: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 and 1.0.

The following diagram shows the format for the binary load-balancing file data:

.. image:: ../images/file-structure/loadbalancingBFF.jpg
