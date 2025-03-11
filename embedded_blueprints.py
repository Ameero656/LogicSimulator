from dataclasses import dataclass
from typing import List, Tuple, NamedTuple, Dict, Union
from blueprint import Blueprint, BlueprintID, NodeIndex, SourcePort, SinkPort, Connection, register_blueprint


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