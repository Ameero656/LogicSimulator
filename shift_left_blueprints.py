from blueprint import Blueprint, register_blueprint, SinkPort, SourcePort


register_blueprint(Blueprint(
    _id='2BIT_SHIFT_LEFT',
    _node_list = [],
    num_inputs = 3,
    num_outputs = 3,
    input_labels=[],
    output_labels=[],
    _connections=
            {SinkPort(None, 0): SourcePort(None, 2),
                SinkPort(None, 1): SourcePort(None, 0),
                SinkPort(None, 2): SourcePort(None, 1),} 
))