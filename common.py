from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, NamedTuple, Dict


# A node is a instance of a Blueprint
# In Connection, the first tuple is usually an output of a node, and the second tuple is usually an input 
# of another node
# A None NodeIndex means the input port of the blueprint itself for SourcePort, 
# and the output port of the blueprint itself for SinkPort
NodeIndex = int
SourcePort = NamedTuple('SourcePort', [('node', NodeIndex|None), ('port', int)])
#SourcePort = Tuple[NodeIndex|None, int]
SinkPort = NamedTuple('SinkPort', [('node', NodeIndex|None), ('port', int)])
#SinkPort = Tuple[NodeIndex|None, int]
Connection = Tuple[SourcePort, SinkPort]
BlueprintID = str


# a data class
@dataclass
class Blueprint:
    _node_list: List[BlueprintID]
    
    # We will a dictionary with the sink being the key and the source being the value.
    # This guarantees that there is only one source for each sink and allows for easy
    # and efficient lookup of the source given the sink.
    # We will also make the source be either a SourcePort or a constant (0 or 1) to
    # allow for constant inputs to some nodes and even to some of the blueprint's
    # outputs.
    _connections: Dict[SinkPort, Union[SourcePort, bool]]
    num_inputs: int
    num_outputs: int
    _id: BlueprintID = None

    # Validate in post init
    def __post_init__(self):
        self.validate()

    def validate(self):
        """
        Check if the blueprint is valid
        - Each output port of this blueprint is connected to something
        - No port is sink to multiple sources (this cannot happen given the current data structure)
        - No cycles
        """

        # First, check that each output port of the blueprint is connected to something
        blueprint_connected_output_ports = sorted([s.port for s in self._connections if s.node is None])
        if blueprint_connected_output_ports != list(range(self.num_outputs)):
            raise ValueError(f'Error in blueprint {self.id}: Invalid connections to blueprint outputs (expected these ports: {list(range(self.num_outputs))}, got {blueprint_connected_output_ports})')

        # For each internal node, check that all input ports are connected
        for node_index, node_id in enumerate(self._node_list):
            node_inputs = sorted([s.port for s in self._connections if s.node == node_index])
            expected_node_inputs = list(range(BlueprintRepository[node_id].num_inputs))
            if node_inputs != expected_node_inputs:
                raise ValueError(f'Error in blueprint {self.id}: Invalid connections to node {node_id}:\nNode index: {node_index}\nExpected inputs: {expected_node_inputs}\nConnection inputs: {node_inputs}')

        def sink_port_info(sink: SinkPort) -> str:
            if sink.node is None:
                return f'{self.id} blueprint output port {sink.port}'
            else:
                return f'{self._node_list[sink.node]} (node index {sink.node}), input port {sink.port}'

        def source_port_info(source: SourcePort) -> str:
            if source.node is None:
                return f'{self.id} blueprint input port {source.port}'
            else:
                return f'{self._node_list[source.node]} (node index {source.node}), output port {source.port}'

        # check that all the sources are valid
        for sink, source in self._connections.items():
            if isinstance(source, SourcePort):
                if source.node is None: # source is the blueprint input itself
                    if source.port >= self.num_inputs:
                        raise ValueError(f'Error in blueprint {self.id}: Invalid source port. Expected to be < {self.num_inputs}:\nSource Port:\n{source_port_info(source)}\nSink Port:\n{sink_port_info(sink)}')
                else: # source is an internal node
                    num_outputs = BlueprintRepository[self._node_list[source.node]].num_outputs
                    if source.port >= num_outputs:
                        raise ValueError(f'Error in blueprint {self.id}: Invalid source port. Expected to be < {num_outputs}:\nSource Port:\n{source_port_info(source)}\nSink Port:\n{sink_port_info(sink)}')
                
            elif not isinstance(source, bool):
                raise ValueError(f'Error in blueprint {self.id}: Invalid source type {source} for sink {sink}')

        # do a cycle check by evaluating the blueprint with a dummy input
        try:
            self.evaluate([False] * self.num_inputs)
        except ValueError as e:
            raise ValueError(f'Error in blueprint {self.id}: {e}')
        

    

    @classmethod
    def from_json(cls, json_file: str) -> Blueprint:
        """TODO: Implement this"""
        return cls(_node_list=[], _connections=[], num_inputs=0, num_outputs=0)

    @classmethod
    def next_id(cls) -> BlueprintID:
        try:
            cls._next_id += 1
        except AttributeError:
            cls._next_id = 0
        return cls._next_id

    @property
    def id(self) -> BlueprintID:
        if self._id is None: # we will allow custom ids to be set; if not, generate one
            self._id = f'{self.__class__.next_id():04d}'
        return self._id

    def evaluate(self, inputs: List[bool]) -> List[bool]:
        """Evaluate the blueprint ouputs given the inputs
        """

        if len(inputs) != self.num_inputs:
            raise ValueError(f'Incorrect number of inputs provided for evaluation of blueprint {self.id} (expected {self.num_inputs}, got {len(inputs)})')

        # cache the internal outputs as they get evaluated; also treat the
        # blueprint's input values as outputs of a None node
        internal_outputs: Dict[NodeIndex, List[bool]] = {None: inputs}

        # this is not necessary for calculating the result but allows us to detect
        # cycles in the blueprint
        visited_nodes = set()

        def evaluate_inputs(node: NodeIndex|None) -> List[bool]:
            """Evaluate the inputs of a node, including node None representing
            the outputs of the blueprint itself
            """
            inputs: List[bool] = []
            sinks = [sink for sink in self._connections if sink.node == node]
            
            for sink in sinks:
                source = self._connections[sink]
                if isinstance(source, bool):
                    inputs.append(source)
                else:
                    if source.node not in internal_outputs:
                        if source.node in visited_nodes:
                            raise ValueError(f'Cycle detected at node {source.node}')
                        visited_nodes.add(source.node)
                        # If we don't have the source node's output yet, evaluate it.
                        # First, evaluate the source node's inputs.
                        source_node_inputs = evaluate_inputs(source.node)
                        # Then evaluate the source node itself and cache the output.
                        internal_outputs[source.node] = BlueprintRepository[self._node_list[source.node]].evaluate(source_node_inputs)
                    inputs.append(internal_outputs[source.node][source.port])
            return inputs

        return evaluate_inputs(None)


BlueprintRepository: Dict[BlueprintID, Blueprint] = {}



# NAND Blueprint
@dataclass
class NAND_Blueprint(Blueprint):
    def __init__(self):
        # connections contains a dummy connection to pass the validation check
        super().__init__(_node_list=[], _connections={SinkPort(None, 0): True}, num_inputs=2, num_outputs=1)

    #override id
    @property
    def id(self) -> BlueprintID:
        return 'NAND'

    def evaluate(self, inputs: List[bool]) -> List[bool]:
        return [not (inputs[0] and inputs[1])]

BlueprintRepository['NAND'] = NAND_Blueprint()

def test_nand():
    assert BlueprintRepository['NAND'].evaluate([False, False]) == [True]
    assert BlueprintRepository['NAND'].evaluate([False, True]) == [True]
    assert BlueprintRepository['NAND'].evaluate([True, False]) == [True]
    assert BlueprintRepository['NAND'].evaluate([True, True]) == [False]

# NOT Blueprint (using NAND)
BlueprintRepository['NOT'] = Blueprint(
    _id='NOT',
    _node_list=['NAND'], 
    _connections=
            {SinkPort(None, 0): SourcePort(0, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(0, 1): True},
    num_inputs=1, 
    num_outputs=1)

def test_not():
    assert BlueprintRepository['NOT'].evaluate([False]) == [True]
    assert BlueprintRepository['NOT'].evaluate([True]) == [False]

# AND Blueprint (using NAND)
BlueprintRepository['AND'] = Blueprint(
    _id='AND',
    _node_list=['NAND', 'NAND'], 
    num_inputs=2, 
    num_outputs=1,
    _connections=
            {SinkPort(None, 0): SourcePort(1, 0),
                SinkPort(1, 0): SourcePort(0, 0),
                SinkPort(1, 1): SourcePort(0, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(0, 1): SourcePort(None, 1)}
    
    )

def test_and():
    assert BlueprintRepository['AND'].evaluate([False, False]) == [False]
    assert BlueprintRepository['AND'].evaluate([False, True]) == [False]
    assert BlueprintRepository['AND'].evaluate([True, False]) == [False]
    assert BlueprintRepository['AND'].evaluate([True, True]) == [True]
        



# OR Blueprint (using NAND and NOT)
# OR(a, b) = NAND(NOT(a), NOT(b))
BlueprintRepository['OR'] = Blueprint(
    _id='OR',
    _node_list=['NOT', 'NOT', 'NAND'], 
    num_inputs=2, 
    num_outputs=1,
    _connections=
            {SinkPort(None, 0): SourcePort(2, 0),
                SinkPort(2, 0): SourcePort(1, 0),
                SinkPort(2, 1): SourcePort(0, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(1, 0): SourcePort(None, 1)}
    )

def test_or():
    assert BlueprintRepository['OR'].evaluate([False, False]) == [False]
    assert BlueprintRepository['OR'].evaluate([False, True]) == [True]
    assert BlueprintRepository['OR'].evaluate([True, False]) == [True]
    assert BlueprintRepository['OR'].evaluate([True, True]) == [True]