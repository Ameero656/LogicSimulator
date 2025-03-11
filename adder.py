from blueprint import Blueprint, register_blueprint, SinkPort, SourcePort


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
    input_labels=["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "Cin"],
    output_labels=["S1", "S2", "S3", "S4", "Cout"],

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