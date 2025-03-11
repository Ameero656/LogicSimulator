
from blueprint import BlueprintRepository, make_truth_table

import embedded_blueprints, basic_blueprints, adder, shift_left, shift_right, uncategorized_blueprints, unit_tests



def list_loaded_blueprints():
    print('Loaded Blueprints:')
    for blueprint in BlueprintRepository:
        print(f'->{blueprint}')



def main():
    list_loaded_blueprints()
    
    unit_tests.run_all_tests()
    make_truth_table("AND")



if __name__ == '__main__':  
    main()