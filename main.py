
from blueprint import BlueprintRepository, make_truth_table, json_export_blueprint, json_import_blueprint

import embedded_blueprints
import basic_blueprints
import adder_blueprints
import shift_left_blueprints
import shift_right_blueprints
import uncategorized_blueprints
import unit_tests



def list_loaded_blueprints():
    print('Loaded Blueprints:')
    for blueprint in BlueprintRepository:
        print(f'->{blueprint}')



def main():
    list_loaded_blueprints()
    
    unit_tests.run_all_tests()
    make_truth_table("AND")
    json_export_blueprint(BlueprintRepository["AND"], "AND.json")



if __name__ == '__main__':  
    main()