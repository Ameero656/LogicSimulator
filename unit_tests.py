from blueprint import BlueprintRepository
import embedded_blueprints
import basic_blueprints
import adder

def test_nand():
    print("Running NAND unit test...", end="")
    assert BlueprintRepository['NAND'].evaluate([False, False]) == [True]
    assert BlueprintRepository['NAND'].evaluate([False, True]) == [True]
    assert BlueprintRepository['NAND'].evaluate([True, False]) == [True]
    assert BlueprintRepository['NAND'].evaluate([True, True]) == [False]
    print("Passed")

def test_not():
    print("Running NOT unit test...", end="")
    assert BlueprintRepository['NOT'].evaluate([False]) == [True]
    assert BlueprintRepository['NOT'].evaluate([True]) == [False]
    print("Passed")

def test_and():
    print("Running AND unit test...", end="")
    assert BlueprintRepository['AND'].evaluate([False, False]) == [False]
    assert BlueprintRepository['AND'].evaluate([False, True]) == [False]
    assert BlueprintRepository['AND'].evaluate([True, False]) == [False]
    assert BlueprintRepository['AND'].evaluate([True, True]) == [True]
    print("Passed")

def test_or():
    print("Running OR unit test...", end="")
    assert BlueprintRepository['OR'].evaluate([False, False]) == [False]
    assert BlueprintRepository['OR'].evaluate([False, True]) == [True]
    assert BlueprintRepository['OR'].evaluate([True, False]) == [True]
    assert BlueprintRepository['OR'].evaluate([True, True]) == [True]
    print("Passed")

def test_xor():
    print("Running XOR unit test...", end="")
    assert BlueprintRepository['XOR'].evaluate([False, False]) == [False]
    assert BlueprintRepository['XOR'].evaluate([False, True]) == [True]
    assert BlueprintRepository['XOR'].evaluate([True, False]) == [True]
    assert BlueprintRepository['XOR'].evaluate([True, True]) == [False]
    print("Passed")

def test_half_adder():
    print("Running HALF_ADDER unit test...", end="")
    assert BlueprintRepository['HALF_ADDER'].evaluate([False, False]) == [False, False]
    assert BlueprintRepository['HALF_ADDER'].evaluate([False, True]) == [True, False]
    assert BlueprintRepository['HALF_ADDER'].evaluate([True, False]) == [True, False]
    assert BlueprintRepository['HALF_ADDER'].evaluate([True, True]) == [False, True]
    print("Passed")

def test_full_adder():
    print("Running FULL_ADDER unit test...", end="")
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, False, False]) == [False, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, False, True]) == [True, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, True, False]) == [True, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([False, True, True]) == [False, True]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, False, False]) == [True, False]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, False, True]) == [False, True]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, True, False]) == [False, True]
    assert BlueprintRepository['FULL_ADDER'].evaluate([True, True, True]) == [True, True]
    for a in [0,1]:
        for b in [0,1]:
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['FULL_ADDER'].evaluate([a, b, c]) == [sum % 2, sum >= 2]
    print("Passed")

def test_2bit_full_adder():
    print("Running 2BIT_FULL_ADDER unit test...", end="")
    for a in [0,1,2,3]:
        for b in [0,1,2,3]:
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['2BIT_FULL_ADDER'].evaluate([ a&1, (a>>1)&1, b&1, (b>>1)&1, c]) == [ sum&1, (sum>>1)&1, sum >= 4]
    print("Passed")

def test_4bit_full_adder():
    print("Running 4BIT_FULL_ADDER unit test...", end="")
    for a in [0,1,2,3,4,5,6,7]:
        for b in [0,1,2,3,4,5,6,7]:
            for c in [0,1]:
                sum = a + b + c
                assert BlueprintRepository['4BIT_FULL_ADDER'].evaluate([ a&1, (a>>1)&1, (a>>2)&1, (a>>3)&1, b&1, (b>>1)&1, (b>>2)&1, (b>>3)&1, c]) == [ sum&1, (sum>>1)&1, (sum>>2)&1, (sum>>3)&1, sum >= 16]
    print("Passed")

def test_8bit_full_adder():
    print("Running 8BIT_FULL_ADDER unit test...", end="")
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
    print("Passed")

def test_8bit_full_adder_subtractor():
    print("Running 8BIT_FULL_ADDER-SUBTRACTOR unit test...", end="")
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
    print("Passed")

def run_all_tests():
    print('Running unit tests...')
    tests = [test_nand(), test_not(), test_and(), test_or(), test_xor(), test_half_adder(), test_full_adder(), test_2bit_full_adder(), test_4bit_full_adder(), test_8bit_full_adder()]
    for test in tests:
        test
    print('All tests passed')