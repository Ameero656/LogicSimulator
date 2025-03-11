from blueprint import Blueprint, BlueprintRepository, SinkPort, SourcePort, register_blueprint

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