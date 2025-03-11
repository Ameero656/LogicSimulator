from blueprint import Blueprint, register_blueprint, SinkPort, SourcePort

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
    input_labels=["A", "B"],
    output_labels=["R"],
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