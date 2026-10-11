This is just a hobby project nothing much to see here

## The plan:

Each neuron object is comprised of a soma with an index of x_0, and is modelled as a spherical neuron. From the soma extend an arbitary number of "chains" with increasing indeces, such as x_1. Each chain is composed of individual comparments/nodes, which are sufficiently small as to be electrically uniform within. 

Each node is a cylinder, has a list of channels and its internal electrical state, and nodes are connected to each other at their ends through a simulated axial resistance. Nodes have indeces matching their chain, ie x_1-1, x_1-2. 

Chains can then be connected to each other, so that their the proximal chain's distal end connects to the next chain's proximal end. Thus the distal chains would have indeces of x_1_1, and x_1_2. Optimally each chain is a computationally separate unit which can be calculated in parallel until they merge into the parent chain. 

Eventually axons would also be modelled, however right now they're not in immediate consideration.


## Node architecture

Gate:
    Stores activation states
    Updates each timestep

Channel:
    Stores gates
    Computes current through itself each timestep

Node:
    Stores channels
    Stores electrical state and dimensions
    Computes axial currents to neighbours
    Updates each timestep

(Neuron:
    Stores nodes
    Keeps node indeces
    Updates propagate with timestep, neuron exists in "continuous time"
)
