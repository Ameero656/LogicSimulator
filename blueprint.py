from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, NamedTuple, Dict, Union
from prettytable import PrettyTable
import itertools, json



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


def make_truth_table(blueprint_name: str):

    print(f'{blueprint_name} Truth Table:')
    
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


def json_export_blueprint(blueprint: Blueprint, file_name: str):
    """Export a blueprint to a json file
    """
    
    
    def source_port_to_json(source: SourcePort) -> Dict:
        if source is None:
            return None
        elif isinstance(source, int):
            return {'constant': source}
        else:
            return {'node': source.node, 'port': source.port}

    def sink_port_to_json(sink: SinkPort) -> Dict:
        if sink is None:
            return None
        elif isinstance(sink, int):
            return {'constant': sink}
        else:
            return {'node': sink.node, 'port': sink.port}
        
    def connection_to_json(connection: Connection) -> Dict:
        return
    
    def blueprint_to_json(blueprint: Blueprint) -> Dict:
        return {
            'node_list': blueprint._node_list,
            'connections': [ {'sink': sink_port_to_json(sink_port), 'source': source_port_to_json(source_port)} for sink_port, source_port in blueprint._connections.items()],
            'num_inputs': blueprint.num_inputs,
            'num_outputs': blueprint.num_outputs,
            'input_labels': blueprint.input_labels,
            'output_labels': blueprint.output_labels,
            'id': blueprint.id
        }

    with open(file_name, 'w') as f:

        json.dump(blueprint_to_json(blueprint), f, indent=4)


def json_import_blueprint(file_name: str) -> Blueprint:
    """Import a blueprint from a json file
    """

    def source_port_from_json(source: Dict) -> SourcePort:
        if source is None:
            return None
        elif 'constant' in source:
            return source['constant']
        else:
            return SourcePort(node=source['node'], port=source['port'])

    def sink_port_from_json(sink: Dict) -> SinkPort:
        if sink is None:
            return None
        elif 'constant' in sink:
            return sink['constant']
        else:
            return SinkPort(node=sink['node'], port=sink['port'])
        
    
    def blueprint_from_json(blueprint: Dict) -> Blueprint:
        print
   
        return Blueprint(
            _node_list=blueprint['node_list'],
            _connections={sink_port_from_json(blueprint["connections"][i]["sink"]): source_port_from_json(blueprint["connections"][i]["source"]) for i, _ in enumerate(blueprint['connections'])},
            num_inputs=blueprint['num_inputs'],
            num_outputs=blueprint['num_outputs'],
            input_labels=blueprint['input_labels'],
            output_labels=blueprint['output_labels'],
            _id=blueprint['id']
        )

    with open(file_name, 'r') as f:
        return blueprint_from_json(json.load(f))