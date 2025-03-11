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
    input_labels: List[str]
    output_labels: List[str]
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
            sinks = [sink for sink in self._connections if sink.node == node]
            inputs: List[bool] = [None] * len(sinks)
            
            for sink in sinks:
                source = self._connections[sink]
                if isinstance(source, bool):
                    inputs[sink.port] = source
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
                    inputs[sink.port] = internal_outputs[source.node][source.port]
            return inputs

        return evaluate_inputs(None)


BlueprintRepository: Dict[BlueprintID, Blueprint] = {}
def register_blueprint(blueprint: Blueprint):
    BlueprintRepository[blueprint.id] = blueprint


# NAND Blueprint
@dataclass
class NAND_Blueprint(Blueprint):
    def __init__(self):
        # connections contains a dummy connection to pass the validation check
        super().__init__(_node_list=[], _connections={SinkPort(None, 0): True}, num_inputs=2, num_outputs=1, input_labels=["A", "B", "C"], output_labels=["X", "Y", "Z"])

    #override id
    @property
    def id(self) -> BlueprintID:
        return 'NAND'

    def evaluate(self, inputs: List[bool]) -> List[bool]:
        return [not (inputs[0] and inputs[1])]

register_blueprint(NAND_Blueprint())

# NOT Blueprint (using NAND)
register_blueprint(Blueprint(
    _id='NOT',
    _node_list=['NAND'], 
    _connections=
            {SinkPort(None, 0): SourcePort(0, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(0, 1): True},
    num_inputs=1, 
    num_outputs=1,
    input_labels=[],
    output_labels=[],))

# AND Blueprint (using NAND)
register_blueprint(Blueprint(
    _id='AND',
    _node_list=['NAND', 'NAND'], 
    num_inputs=2, 
    num_outputs=1,
    input_labels=[],
    output_labels=[],
    _connections=
            {SinkPort(None, 0): SourcePort(1, 0),
                SinkPort(1, 0): SourcePort(0, 0),
                SinkPort(1, 1): SourcePort(0, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(0, 1): SourcePort(None, 1)}
    )
)
 
# OR Blueprint (using NAND and NOT)
# OR(a, b) = NAND(NOT(a), NOT(b))
register_blueprint(Blueprint(
    _id='OR',
    _node_list=['NOT', 'NOT', 'NAND'], 
    num_inputs=2, 
    num_outputs=1,
    input_labels=[],
    output_labels=[],
    _connections=
            {SinkPort(None, 0): SourcePort(2, 0),
                SinkPort(2, 0): SourcePort(1, 0),
                SinkPort(2, 1): SourcePort(0, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(1, 0): SourcePort(None, 1)}
    )
)

# XOR Blueprint (using NAND, NOT, AND, OR)
# XOR(a, b) = OR(AND(a, NOT(b)), AND(NOT(a), b))
register_blueprint(Blueprint(
    _id='XOR',
    _node_list=['NOT', 'AND', 'NOT', 'AND', 'OR'], 
    num_inputs=2, 
    num_outputs=1,
    input_labels=["I1", "I2"],
    output_labels=["O1"],
    _connections=
            {SinkPort(None, 0): SourcePort(4, 0),
                SinkPort(4, 0): SourcePort(3, 0),
                SinkPort(4, 1): SourcePort(1, 0),
                SinkPort(3, 0): SourcePort(None, 0),
                SinkPort(3, 1): SourcePort(2, 0),
                SinkPort(1, 0): SourcePort(0, 0),
                SinkPort(1, 1): SourcePort(None, 1),
                SinkPort(2, 0): SourcePort(None, 1),
                SinkPort(0, 0): SourcePort(None, 0)}
    )
)

# an half adder that takes two 1-bit inputs and produces a 2-bit output (sum and carry)
# The sum is XOR(a, b) and the carry is AND(a, b)
register_blueprint(Blueprint(
    _id='HALF_ADDER',
    _node_list=['XOR', 'AND'], 
    num_inputs=2, 
    num_outputs=2,
    input_labels=[],
    output_labels=[],
    _connections=
            {SinkPort(None, 0): SourcePort(0, 0),
                SinkPort(None, 1): SourcePort(1, 0),
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(0, 1): SourcePort(None, 1),
                SinkPort(1, 0): SourcePort(None, 0),
                SinkPort(1, 1): SourcePort(None, 1)}
    )
)

# a full adder that takes two 1-bit inputs and a carry input and produces a 2-bit output (sum and carry)
# Input is a, b, carry
# Output is sum, carry
# Using the half adder and OR, we can calculate the sum and carry
# S1,C1 = HALF_ADDER(a, b)
# S2,C2 = HALF_ADDER(S1, carry)
# SUM = S2
# CARRY = OR(C1, C2)
register_blueprint(Blueprint(
    _id='FULL_ADDER',
    _node_list=['HALF_ADDER', 'HALF_ADDER', 'OR'],
    num_inputs=3,
    num_outputs=2,
    input_labels=[],
    output_labels=[],
    _connections=
            {SinkPort(None, 0): SourcePort(1, 0),
             SinkPort(None, 1): SourcePort(2, 0),
                SinkPort(2, 0): SourcePort(0, 1),
                SinkPort(2, 1): SourcePort(1, 1),
                SinkPort(1, 0): SourcePort(0, 0),
                
                SinkPort(0, 0): SourcePort(None, 0),
                SinkPort(0, 1): SourcePort(None, 1),
                SinkPort(1, 1): SourcePort(None, 2),
                
                }
    )
)

#2-bit Full Adder
# an 2-bit adder that takes two 2-bit inputs and produces a 3-bit output (2b sum and 1b carry)
# Input is a0, a1, b0, b1, carry

register_blueprint(Blueprint(
    _id='2BIT_FULL_ADDER',
    _node_list=['FULL_ADDER', 'FULL_ADDER'],
    num_inputs=5,
    num_outputs=3,
    input_labels=[],
    output_labels=[],

    _connections= {
            #outputs
            SinkPort(None, 0): SourcePort(0, 0),
            SinkPort(None, 1): SourcePort(1, 0),

            #carry in/out
            SinkPort(0, 2): SourcePort(None, 4),
            SinkPort(1, 2): SourcePort(0, 1),
            SinkPort(None, 2): SourcePort(1, 1), #carry out

            #input a
            SinkPort(0, 0): SourcePort(None, 0),
            SinkPort(1, 0): SourcePort(None, 1),

            #input b
            SinkPort(0, 1): SourcePort(None, 2),
            SinkPort(1, 1): SourcePort(None, 3)
        }
))

#4-bit Full Adder
# an 4-bit adder that takes two 4-bit inputs and produces a 5-bit output (4b sum and 1b carry)
# Input is a0, a1, a2, a3, b0, b1, b2, b3, carry

register_blueprint(Blueprint(
    _id='4BIT_FULL_ADDER',
    _node_list=['2BIT_FULL_ADDER', '2BIT_FULL_ADDER'],
    num_inputs=9,
    num_outputs=5,
    input_labels=[],
    output_labels=[],

    _connections= {
        SinkPort(None, 0): SourcePort(0, 0),
        SinkPort(None, 1): SourcePort(0, 1),
        SinkPort(None, 2): SourcePort(1, 0),
        SinkPort(None, 3): SourcePort(1, 1),

        #carry in/out
        SinkPort(0, 4): SourcePort(None, 8),
        SinkPort(1, 4): SourcePort(0, 2),

        SinkPort(None, 4): SourcePort(1, 2), #carry out

        #input a
        SinkPort(0, 0): SourcePort(None, 0),
        SinkPort(0, 1): SourcePort(None, 1),
        SinkPort(1, 0): SourcePort(None, 2),
        SinkPort(1, 1): SourcePort(None, 3),

        #input b
        SinkPort(0, 2): SourcePort(None, 4),
        SinkPort(0, 3): SourcePort(None, 5),
        SinkPort(1, 2): SourcePort(None, 6),
        SinkPort(1, 3): SourcePort(None, 7)

    }
))

# an 8-bit adder that takes two 8-bit inputs and produces a 9-bit output (8b sum and 1b carry)
# Input is a0, a1...a7, b0, b1...b7, carry
# Output is sum0, sum1...sum7, carry_out
# S0,C1 = FULL_ADDER(a0, b0, carry)
# S1,C2 = FULL_ADDER(a1, b1, C1)
#...
# S7,C8 = FULL_ADDER(a7, b7, C7)
# SUM = S0, S1...S7
# CARRY_OUT = C8
register_blueprint(Blueprint(
    _id='8BIT_FULL_ADDER',
    _node_list=['4BIT_FULL_ADDER', '4BIT_FULL_ADDER'],
    num_inputs=17,
    num_outputs=9,
    input_labels=[],
    output_labels=[],
    _connections= {
        SinkPort(None, 0): SourcePort(0, 0),
        SinkPort(None, 1): SourcePort(0, 1),
        SinkPort(None, 2): SourcePort(0, 2),
        SinkPort(None, 3): SourcePort(0, 3),
        SinkPort(None, 4): SourcePort(1, 0),
        SinkPort(None, 5): SourcePort(1, 1),
        SinkPort(None, 6): SourcePort(1, 2),
        SinkPort(None, 7): SourcePort(1, 3),

        #carry in/out
        SinkPort(0, 8): SourcePort(None, 16),
        SinkPort(1, 8): SourcePort(0, 4),

        SinkPort(None, 8): SourcePort(1, 4), #carry out

        #input a
        SinkPort(0, 0): SourcePort(None, 0),
        SinkPort(0, 1): SourcePort(None, 1),
        SinkPort(0, 2): SourcePort(None, 2),
        SinkPort(0, 3): SourcePort(None, 3),
        SinkPort(1, 0): SourcePort(None, 4),
        SinkPort(1, 1): SourcePort(None, 5),
        SinkPort(1, 2): SourcePort(None, 6),
        SinkPort(1, 3): SourcePort(None, 7),

        #input b
        SinkPort(0, 4): SourcePort(None, 8),
        SinkPort(0, 5): SourcePort(None, 9),
        SinkPort(0, 6): SourcePort(None, 10),
        SinkPort(0, 7): SourcePort(None, 11),
        SinkPort(1, 4): SourcePort(None, 12),
        SinkPort(1, 5): SourcePort(None, 13),
        SinkPort(1, 6): SourcePort(None, 14),
        SinkPort(1, 7): SourcePort(None, 15)
    }
    )
)

# #8-bit Adder-Subtractor 
# #Converts carry in to subtractor mode using 2's complement (XORing B inputs)
register_blueprint(Blueprint(
    _id='8BIT_FULL_ADDER-SUBTRACTOR',
    _node_list=['8BIT_FULL_ADDER', 'XOR', 'XOR', 'XOR', 'XOR', 'XOR', 'XOR', 'XOR', 'XOR'],
    num_inputs=17,
    num_outputs=9,
    input_labels=[],
    output_labels=[],
    _connections= {
            # a inputs
            SinkPort(0, 0): SourcePort(None, 0),
            SinkPort(0, 1): SourcePort(None, 1),
            SinkPort(0, 2): SourcePort(None, 2),
            SinkPort(0, 3): SourcePort(None, 3),
            SinkPort(0, 4): SourcePort(None, 4),
            SinkPort(0, 5): SourcePort(None, 5),
            SinkPort(0, 6): SourcePort(None, 6),
            SinkPort(0, 7): SourcePort(None, 7),

            # b inputs

            SinkPort(0, 8): SourcePort(1, 0),
            SinkPort(0, 9): SourcePort(2, 0),
            SinkPort(0, 10): SourcePort(3, 0),
            SinkPort(0, 11): SourcePort(4, 0),
            SinkPort(0, 12): SourcePort(5, 0),
            SinkPort(0, 13): SourcePort(6, 0),
            SinkPort(0, 14): SourcePort(7, 0),
            SinkPort(0, 15): SourcePort(8, 0),

            #carry

            SinkPort(0, 16): SourcePort(None, 16),

            #xoring B
            SinkPort(1, 0): SourcePort(None, 8),
            SinkPort(1, 1): SourcePort(None, 16),

            SinkPort(2, 0): SourcePort(None, 9),
            SinkPort(2, 1): SourcePort(None, 16),

            SinkPort(3, 0): SourcePort(None, 10),
            SinkPort(3, 1): SourcePort(None, 16),

            SinkPort(4, 0): SourcePort(None, 11),
            SinkPort(4, 1): SourcePort(None, 16),

            SinkPort(5, 0): SourcePort(None, 12),
            SinkPort(5, 1): SourcePort(None, 16),

            SinkPort(6, 0): SourcePort(None, 13),
            SinkPort(6, 1): SourcePort(None, 16),

            SinkPort(7, 0): SourcePort(None, 14),
            SinkPort(7, 1): SourcePort(None, 16),

            SinkPort(8, 0): SourcePort(None, 15),
            SinkPort(8, 1): SourcePort(None, 16),


            #outputs

            SinkPort(None, 0): SourcePort(0, 0),
            SinkPort(None, 1): SourcePort(0, 1),
            SinkPort(None, 2): SourcePort(0, 2),
            SinkPort(None, 3): SourcePort(0, 3),
            SinkPort(None, 4): SourcePort(0, 4),
            SinkPort(None, 5): SourcePort(0, 5),
            SinkPort(None, 6): SourcePort(0, 6),
            SinkPort(None, 7): SourcePort(0, 7),
            SinkPort(None, 8): SourcePort(0, 8)
            
        }
    )
)

# 8-bit ANDer 
#takes two 8-bit inputs and produces an 8-bit output
register_blueprint(Blueprint(
    _id='8BIT_AND',
    _node_list=['AND', 'AND', 'AND', 'AND', 'AND', 'AND', 'AND', 'AND'],
    num_inputs=16,
    num_outputs=8,
    input_labels=[],
    output_labels=[],
    _connections= {
            #outputs
            SinkPort(None, 0): SourcePort(0, 0),
            SinkPort(None, 1): SourcePort(1, 0),
            SinkPort(None, 2): SourcePort(2, 0),
            SinkPort(None, 3): SourcePort(3, 0),
            SinkPort(None, 4): SourcePort(4, 0),
            SinkPort(None, 5): SourcePort(5, 0),
            SinkPort(None, 6): SourcePort(6, 0),
            SinkPort(None, 7): SourcePort(7, 0),

            #input a
            SinkPort(0, 0): SourcePort(None, 0),
            SinkPort(1, 0): SourcePort(None, 1),
            SinkPort(2, 0): SourcePort(None, 2),
            SinkPort(3, 0): SourcePort(None, 3),
            SinkPort(4, 0): SourcePort(None, 4),
            SinkPort(5, 0): SourcePort(None, 5),
            SinkPort(6, 0): SourcePort(None, 6),
            SinkPort(7, 0): SourcePort(None, 7),

            #input b
            SinkPort(0, 1): SourcePort(None, 8),
            SinkPort(1, 1): SourcePort(None, 9),
            SinkPort(2, 1): SourcePort(None, 10),
            SinkPort(3, 1): SourcePort(None, 11),
            SinkPort(4, 1): SourcePort(None, 12),
            SinkPort(5, 1): SourcePort(None, 13),
            SinkPort(6, 1): SourcePort(None, 14),
            SinkPort(7, 1): SourcePort(None, 15)

        }
    )
)

#8-bit ORer
#takes two 8-bit inputs and produces an 8-bit output
register_blueprint(Blueprint(
    _id='8BIT_OR',
    _node_list=['OR', 'OR', 'OR', 'OR', 'OR', 'OR', 'OR', 'OR'],
    num_inputs=16,
    num_outputs=8,
    input_labels=[],
    output_labels=[],
    _connections= {
            #outputs
            SinkPort(None, 0): SourcePort(0, 0),
            SinkPort(None, 1): SourcePort(1, 0),
            SinkPort(None, 2): SourcePort(2, 0),
            SinkPort(None, 3): SourcePort(3, 0),
            SinkPort(None, 4): SourcePort(4, 0),
            SinkPort(None, 5): SourcePort(5, 0),
            SinkPort(None, 6): SourcePort(6, 0),
            SinkPort(None, 7): SourcePort(7, 0),

            #input a
            SinkPort(0, 0): SourcePort(None, 0),
            SinkPort(1, 0): SourcePort(None, 1),
            SinkPort(2, 0): SourcePort(None, 2),
            SinkPort(3, 0): SourcePort(None, 3),
            SinkPort(4, 0): SourcePort(None, 4),
            SinkPort(5, 0): SourcePort(None, 5),
            SinkPort(6, 0): SourcePort(None, 6),
            SinkPort(7, 0): SourcePort(None, 7),

            #input b
            SinkPort(0, 1): SourcePort(None, 8),
            SinkPort(1, 1): SourcePort(None, 9),
            SinkPort(2, 1): SourcePort(None, 10),
            SinkPort(3, 1): SourcePort(None, 11),
            SinkPort(4, 1): SourcePort(None, 12),
            SinkPort(5, 1): SourcePort(None, 13),
            SinkPort(6, 1): SourcePort(None, 14),
            SinkPort(7, 1): SourcePort(None, 15)

        }
    )
)

#8-bit NOTer
#takes an 8-bit input and produces an 8-bit output
register_blueprint(Blueprint(
    _id='8BIT_NOT',
    _node_list=['NOT', 'NOT', 'NOT', 'NOT', 'NOT', 'NOT', 'NOT', 'NOT'],
    num_inputs=8,
    num_outputs=8,
    input_labels=[],
    output_labels=[],
    _connections= {
            #outputs
            SinkPort(None, 0): SourcePort(0, 0),
            SinkPort(None, 1): SourcePort(1, 0),
            SinkPort(None, 2): SourcePort(2, 0),
            SinkPort(None, 3): SourcePort(3, 0),
            SinkPort(None, 4): SourcePort(4, 0),
            SinkPort(None, 5): SourcePort(5, 0),
            SinkPort(None, 6): SourcePort(6, 0),
            SinkPort(None, 7): SourcePort(7, 0),

            #input a
            SinkPort(0, 0): SourcePort(None, 0),
            SinkPort(1, 0): SourcePort(None, 1),
            SinkPort(2, 0): SourcePort(None, 2),
            SinkPort(3, 0): SourcePort(None, 3),
            SinkPort(4, 0): SourcePort(None, 4),
            SinkPort(5, 0): SourcePort(None, 5),
            SinkPort(6, 0): SourcePort(None, 6),
            SinkPort(7, 0): SourcePort(None, 7)

        }
    )
)

#8-bit shift right
#takes an 9-bit input (8-bit + carry bit) and produces an 8-bit output
register_blueprint(Blueprint(
    _id='8BIT_SHIFT_RIGHT',
    _node_list = [],
    num_inputs = 9,
    num_outputs = 9,
    input_labels=[],
    output_labels=[],

    _connections = {
        #outputs
        SinkPort(None, 0): SourcePort(None, 1),
        SinkPort(None, 1): SourcePort(None, 2),
        SinkPort(None, 2): SourcePort(None, 3),
        SinkPort(None, 3): SourcePort(None, 4),
        SinkPort(None, 4): SourcePort(None, 5),
        SinkPort(None, 5): SourcePort(None, 6),
        SinkPort(None, 6): SourcePort(None, 7),
        SinkPort(None, 7): SourcePort(None, 8), #assign the final bit to the carry in

        SinkPort(None, 8): SourcePort(None, 0), # assign carry out to the first bit
        

    }
    )
)

#8-bit shift left
#takes an 8-bit input and produces an 9-bit output (8-bit + carry bit)
register_blueprint(Blueprint(
    _id='8BIT_SHIFT_LEFT',
    _node_list = [],
    num_inputs = 9,
    num_outputs = 9,
    input_labels=[],
    output_labels=[],

    _connections = {
        #outputs
        SinkPort(None, 0): SourcePort(None, 8), #assign the first bit to the carry in
        SinkPort(None, 1): SourcePort(None, 0),
        SinkPort(None, 2): SourcePort(None, 1),
        SinkPort(None, 3): SourcePort(None, 2),
        SinkPort(None, 4): SourcePort(None, 3),
        SinkPort(None, 5): SourcePort(None, 4),
        SinkPort(None, 6): SourcePort(None, 5),
        SinkPort(None, 7): SourcePort(None, 6), 

        SinkPort(None, 8): SourcePort(None, 7), # assign carry out to the final bit
        

    }
    )
)

#2x4-bit decoder
#takes a 2-bit input and produces an 4-bit output
register_blueprint(Blueprint(
    _id='2X4BIT_DECODER',
    _node_list = ['NOT', 'NOT', 'AND', 'AND', 'AND', 'AND', 'AND', 'AND', 'AND', 'AND'], #NOT A, NOT B, AND(A, B), AND(A, NOT B), AND(NOT A, B), AND(NOT A, NOT B)
    num_inputs = 3,
    num_outputs = 4,
    input_labels=[],
    output_labels=[],

    _connections = {
        #outputs
        SinkPort(None, 0): SourcePort(6, 0),
        SinkPort(None, 1): SourcePort(7, 0),
        SinkPort(None, 2): SourcePort(8, 0),
        SinkPort(None, 3): SourcePort(9, 0),

        #NOT(a)
        SinkPort(0, 0): SourcePort(None, 0),

        #NOT(b)
        SinkPort(1, 0): SourcePort(None, 1),

        #AND(a, b)
        SinkPort(2, 0): SourcePort(None, 0),
        SinkPort(2, 1): SourcePort(None, 1),

        #AND(a, NOT(b))
        SinkPort(3, 0): SourcePort(None, 0),
        SinkPort(3, 1): SourcePort(1, 0),

        #AND(NOT(a), b)
        SinkPort(4, 0): SourcePort(0, 0),
        SinkPort(4, 1): SourcePort(None, 1),

        #AND(NOT(a), NOT(b))
        SinkPort(5, 0): SourcePort(0, 0),
        SinkPort(5, 1): SourcePort(1, 0),

        #Enableing
        SinkPort(6, 0): SourcePort(2, 0),
        SinkPort(6, 1): SourcePort(None, 2),

        SinkPort(7, 0): SourcePort(3, 0),
        SinkPort(7, 1): SourcePort(None, 2),
        
        SinkPort(8, 0): SourcePort(4, 0),
        SinkPort(8, 1): SourcePort(None, 2),
        
        SinkPort(9, 0): SourcePort(5, 0),
        SinkPort(9, 1): SourcePort(None, 2)

        
    }
    )
)

#3x8-bit decoder
# #takes a 3-bit input and produces an 8-bit output
# register_blueprint(Blueprint(
#     _id='3X8BIT_DECODER',
#     _node_list = ['2X4BIT_DECODER', '2X4BIT_DECODER'],
#     num_inputs = 3,
#     num_outputs = 8,

#     _connections = {
#         #outputs
#         SinkPort(None, 0): SourcePort(0, 0),
#         SinkPort(None, 1): SourcePort(0, 1),
#         SinkPort(None, 2): SourcePort(0, 2),
#         SinkPort(None, 3): SourcePort(0, 3),
#         SinkPort(None, 4): SourcePort(1, 0),
#         SinkPort(None, 5): SourcePort(1, 1),
#         SinkPort(None, 6): SourcePort(1, 2),
#         SinkPort(None, 7): SourcePort(1, 3),


#         #2X4BIT_DECODER(a, b)
#         SinkPort(0, 0): SourcePort(None, 0),
#         SinkPort(0, 1): SourcePort(None, 1),

#         #2X4BIT_DECODER(c, d)
#         SinkPort(1, 0): SourcePort(None, 2),
#         SinkPort(1, 1): SourcePort(None, 3),
#     }
#     )
# )

# #4x16-bit decoder
# #takes a 4-bit input and produces an 16-bit output
# register_blueprint(Blueprint(
#     _id='4X16BIT_DECODER',
#     _node_list = ['3X8BIT_DECODER', '3X8BIT_DECODER'],
#     num_inputs = 4,
#     num_outputs = 16,

#     _connections = {
#         #outputs
#         SinkPort(None, 0): SourcePort(0, 0),
#         SinkPort(None, 1): SourcePort(0, 1),
#         SinkPort(None, 2): SourcePort(0, 2),
#         SinkPort(None, 3): SourcePort(0, 3),
#         SinkPort(None, 4): SourcePort(0, 4),
#         SinkPort(None, 5): SourcePort(0, 5),
#         SinkPort(None, 6): SourcePort(0, 6),
#         SinkPort(None, 7): SourcePort(0, 7),
#         SinkPort(None, 8): SourcePort(1, 0),
#         SinkPort(None, 9): SourcePort(1, 1),
#         SinkPort(None, 10): SourcePort(1, 2),
#         SinkPort(None, 11): SourcePort(1, 3),
#         SinkPort(None, 12): SourcePort(1, 4),
#         SinkPort(None, 13): SourcePort(1, 5),
#         SinkPort(None, 14): SourcePort(1, 6),
#         SinkPort(None, 15): SourcePort(1, 7),

#         #3X8BIT_DECODER(a, b, c)
#         SinkPort(0, 0): SourcePort(None, 0),
#         SinkPort(0, 1): SourcePort(None, 1),
#         SinkPort(0, 2): SourcePort(None, 2),

#         #3X8BIT_DECODER(d, e, f)
#         SinkPort(1, 0): SourcePort(None, 3),
#         SinkPort(1, 1): SourcePort(None, 4),
#         SinkPort(1, 2): SourcePort(None, 5),
#     }
#     )
# )

# 8-bit Comparator
# takes two 8-bit inputs and produces a 3-bit output (A<B, A=B, A>B)


def make_truth_table(blueprint_name: str):
    from prettytable import PrettyTable
    import itertools

    input_chars = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    output_chars = input_chars[::-1]

    blueprint = BlueprintRepository.get(blueprint_name)

    if blueprint is None:
        print(f"Error: Blueprint '{blueprint_name}' not found.")
        return

    num_inputs = blueprint.num_inputs
    num_outputs = blueprint.num_outputs

    table = PrettyTable()

    if num_inputs == len(blueprint.input_labels):
        input_vars = blueprint.input_labels
    else:
        input_vars = input_chars[:num_inputs]
    
    if num_outputs == len(blueprint.output_labels):
        output_vars = blueprint.output_labels
    else:
        output_vars = output_chars[:num_outputs] 


    table.field_names = input_vars + output_vars

    
    combinations = list(itertools.product([False, True], repeat=num_inputs))

    for combination in combinations:
        row = [int(value) for value in combination]  
        outputs = blueprint.evaluate(combination)
        row.extend(int(output) for output in outputs) 
        table.add_row(row)

    print(table)







def test_nand():
    assert BlueprintRepository['NAND'].evaluate([False, False]) == [True]
    assert BlueprintRepository['NAND'].evaluate([False, True]) == [True]
    assert BlueprintRepository['NAND'].evaluate([True, False]) == [True]
    assert BlueprintRepository['NAND'].evaluate([True, True]) == [False]

def test_not():
    assert BlueprintRepository['NOT'].evaluate([False]) == [True]
    assert BlueprintRepository['NOT'].evaluate([True]) == [False]

def test_and():
    assert BlueprintRepository['AND'].evaluate([False, False]) == [False]
    assert BlueprintRepository['AND'].evaluate([False, True]) == [False]
    assert BlueprintRepository['AND'].evaluate([True, False]) == [False]
    assert BlueprintRepository['AND'].evaluate([True, True]) == [True]

def test_or():
    assert BlueprintRepository['OR'].evaluate([False, False]) == [False]
    assert BlueprintRepository['OR'].evaluate([False, True]) == [True]
    assert BlueprintRepository['OR'].evaluate([True, False]) == [True]
    assert BlueprintRepository['OR'].evaluate([True, True]) == [True]

def test_xor():
    assert BlueprintRepository['XOR'].evaluate([False, False]) == [False]
    assert BlueprintRepository['XOR'].evaluate([False, True]) == [True]
    assert BlueprintRepository['XOR'].evaluate([True, False]) == [True]
    assert BlueprintRepository['XOR'].evaluate([True, True]) == [False]

def test_half_adder():
    assert BlueprintRepository['HALF_ADDER'].evaluate([False, False]) == [False, False]
    assert BlueprintRepository['HALF_ADDER'].evaluate([False, True]) == [True, False]
    assert BlueprintRepository['HALF_ADDER'].evaluate([True, False]) == [True, False]
    assert BlueprintRepository['HALF_ADDER'].evaluate([True, True]) == [False, True]

def test_full_adder():
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, False, False]) == [False, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, False, True]) == [True, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, True, False]) == [True, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, True, True]) == [False, True]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, False, False]) == [True, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, False, True]) == [False, True]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, True, False]) == [False, True]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, True, True]) == [True, True]
    # equivalently:
    for a in [0,1]:
        for b in [0,1]:
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['FULL_ADDER'].evaluate([a, b, c]) == [sum % 2, sum >= 2]

def test_2bit_full_adder():
    for a in [0,1,2,3]:
        for b in [0,1,2,3]:
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['2BIT_FULL_ADDER'].evaluate([ a&1, (a>>1)&1, b&1, (b>>1)&1, c]) == [ sum&1, (sum>>1)&1, sum >= 4]

def test_4bit_full_adder():
    for a in [0,1,2,3,4,5,6,7]:
        for b in [0,1,2,3,4,5,6,7]:
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['4BIT_FULL_ADDER'].evaluate([ a&1, (a>>1)&1, (a>>2)&1, (a>>3)&1, b&1, (b>>1)&1, (b>>2)&1, (b>>3)&1, c]) == [ sum&1, (sum>>1)&1, (sum>>2)&1, (sum>>3)&1, sum >= 16]

def test_8bit_full_adder():
    for a in range(16):
        for b in range(16):
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['8BIT_FULL_ADDER'].evaluate(
                    [ a&1, (a>>1)&1, (a>>2)&1, (a>>3)&1, 
                    (a>>4)&1, (a>>5)&1, (a>>6)&1, (a>>7)&1,

                    b&1, (b>>1)&1, (b>>2)&1, (b>>3)&1, 
                    (b>>4)&1, (b>>5)&1, (b>>6)&1, (b>>7)&1,
                    c]) \
                    ==  \
                    [ sum&1, (sum>>1)&1, (sum>>2)&1, (sum>>3)&1, 
                    (sum>>4)&1, (sum>>5)&1, (sum>>6)&1, (sum>>7)&1, 
                    sum >= 256]

def test_8bit_full_adder_subtractor():
    bits = 8
    overflow = (1<<bits)    
    for a in range(-128, 128):
        for b in range(-128, 128):
            for c in [0,1]:

                ap, bp = overflow + a if a < 0 else a, overflow + b if b < 0 else b
                
                if c == 0:
                    sum = a + b
                    carry_out = ap + bp >=overflow
                    
                else:
                    sum = a - b
                    carry_out = ap-bp>=0               

                assert BlueprintRepository['8BIT_FULL_ADDER-SUBTRACTOR'].evaluate(
                    [ a&1, (a>>1)&1, (a>>2)&1, (a>>3)&1, 
                    (a>>4)&1, (a>>5)&1, (a>>6)&1, (a>>7)&1,

                    b&1, (b>>1)&1, (b>>2)&1, (b>>3)&1, 
                    (b>>4)&1, (b>>5)&1, (b>>6)&1, (b>>7)&1,
                    c]) \
                    ==  \
                    [ sum&1, (sum>>1)&1, (sum>>2)&1, (sum>>3)&1, 
                    (sum>>4)&1, (sum>>5)&1, (sum>>6)&1, (sum>>7)&1, 
                    carry_out]




                

# def test_2x4decoder():
#     for a in range(4):
#         for e in [0,1]:
#             if e == 0:
#                 out = 0
#             else:
#                 out = 1<<a

#             print(f'{a=}, {e=}, {out=}')

#             assert BlueprintRepository['2X4BIT_DECODER'].evaluate([a&1, (a>>1)&1, e]) == [out&1, (out>>1)&1, (out>>2)&1, (out>>3)&1]


make_truth_table("4BIT_FULL_ADDER")