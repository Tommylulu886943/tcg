import os
import sys
import logging
import json
import copy

from jinja2 import Environment, Template

from lib.general_tool import GeneralTool
from lib.DataBuilder import DataBuilder

DEBUG = True

class TestStrategy:
    
    @classmethod
    def init_test_plan(cls, uri: str, method: str, operationId: str) -> str:
        """Write basic test plan information to test plan .json file.

        Args:
            uri: The uri of the test case.
            method: The method of the test case.
            operationId: The operationId of the test case.

        Returns:
            The path of the test plan .json file.
        """        
        basic_test_plan = {
            'test_info': {
                'summary': method + ' ' + uri,
                'method': method,
                'uri': uri,
                'operationId': operationId,

            },
            'test_cases': {}
        }
        
        if not os.path.exists('test_plan'):
            os.makedirs('test_plan')
        test_plan_path = f'test_plan/{operationId}.json'
        with open(test_plan_path, 'w', encoding='utf-8') as f:
            json.dump(basic_test_plan, f, ensure_ascii=False, sort_keys=False)
 
        return test_plan_path
    
    @classmethod
    def parameter_min_max_test(cls, test_type, operation_id, uri, method, operation, test_plan_path, serial_number, baseline_data):
 
        try:
            with open(f"./GenerationRule/{operation_id}.json", 'r') as f:
                generation_rules = json.load(f)
        except FileNotFoundError:
            logging.warning(f'This API does not have a generation rule: {operation_id}, so the parameter_min_max_test case cannot be generated.')
            return
        
        for key in generation_rules:
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']

            if 'readOnly' in rule and rule['readOnly'] == True:
                continue
            elif rule['Data Length'] == "":
                logging.warning(f'{operation_id} field {key} does not have a Data Length rule, so the parameter_min_max_test case cannot be generated.')
                continue
            elif rule['Data Generator'] == "":
                logging.warning(f'{operation_id} field {key} does not have a Data Generator rule, so the parameter_min_max_test case cannot be generated.')
                continue
            elif info['Type'] not in ['string', 'integer', 'number', 'float']:
                logging.warning(f'{operation_id} field {key} has an invalid Type rule, so the parameter_min_max_test case cannot be generated.')
                continue
            else:
                genType = rule['Data Generator']
                min_len, max_len = map(int, rule['Data Length'].strip('[]').split(','))
            
            # * Generate test data according to the generation rule of the field
            if genType == 'Random String (Without Special Characters)':
                if test_type == 'positive_test':
                    min_value = DataBuilder.generate_random_string([min_len, min_len])
                    max_value = DataBuilder.generate_random_string([max_len, max_len])
                    mid_value = DataBuilder.generate_random_string([int((min_len + max_len) / 2), int((min_len + max_len) / 2)])
                elif test_type == 'negative_test':
                    over_max_value = DataBuilder.generate_random_string([max_len + 1, max_len + 1])
                    under_min_value = DataBuilder.generate_random_string([min_len - 1, min_len - 1])
            elif genType == rule['Data Generator'] == 'Random String':
                if test_type == 'positive_test':
                    min_value = DataBuilder.generate_random_string([min_len, min_len], specical_char=True)
                    max_value = DataBuilder.generate_random_string([max_len, max_len], specical_char=True)
                    mid_value = DataBuilder.generate_random_string([int((min_len + max_len) / 2), int((min_len + max_len) / 2)], specical_char=True)
                elif test_type == 'negative_test':
                    over_max_value = DataBuilder.generate_random_string([max_len + 1, max_len + 1], specical_char=True)
                    under_min_value = DataBuilder.generate_random_string([min_len - 1, min_len - 1], specical_char=True)
            elif genType == rule['Data Generator'] == 'Random Integer':
                if test_type == 'positive_test':
                    min_value = DataBuilder.generate_random_integer([min_len, min_len])
                    max_value = DataBuilder.generate_random_integer([max_len, max_len])
                    mid_value = DataBuilder.generate_random_integer([int((min_len + max_len) / 2), int((min_len + max_len) / 2)])
                elif test_type == 'negative_test':
                    over_max_value = DataBuilder.generate_random_integer([max_len + 1, max_len + 1])
                    under_min_value = DataBuilder.generate_random_integer([min_len - 1, min_len - 1])
            else:
                logging.warning(f'Field {key} has an invalid Data Generator rule, so the parameter_min_max_test case cannot be generated.')
                continue
            
            if DEBUG:
                if test_type == 'positive_test':
                    logging.debug(f'key: {key}, min_value: {min_value}, max_value: {max_value}, mid_value: {mid_value}')
                else:
                    logging.debug(f'key: {key}, under_min_value: {under_min_value}, over_max_value: {over_max_value}')
                
            # TODO : 上面的template 需要重新整理
            # TODO : 上方的數據生成器需要重新整理，需要考慮一下能否復用或簡化
            
            # * Load assertion rule
            with open(f"./AssertionRule/{operation_id}.json", 'r') as f:
                assertion_rule = json.load(f)
                if test_type == 'negative_test':
                    assertion_rule = assertion_rule["negative"]
                elif test_type == 'positive_test':
                    assertion_rule = assertion_rule["positive"]
            
            # *　Load Dependency rule
            with open(f"./DependencyRule/{operation_id}.json", 'r') as f:
                dependency_rule = json.load(f)
                
            # * Load Path rule
            if os.path.exists(f"./PathRule/{operation_id}.json"):
                with open(f"./PathRule/{operation_id}.json", 'r') as f:
                    path_rule = json.load(f)
            
            if test_type == 'positive_test':
                min_testdata = copy.deepcopy(baseline_data)
                DataBuilder._create_nested_dict(min_testdata, keys, min_value)
                min_testdata_path = f"./TestData/{operation_id}_{serial_number}_1.json"
                with open(min_testdata_path, 'w') as f:
                    json.dump(min_testdata, f, indent=4)
                    
                max_testdata = copy.deepcopy(baseline_data)
                DataBuilder._create_nested_dict(max_testdata, keys, max_value)
                max_testdata_path = f"./TestData/{operation_id}_{serial_number}_2.json"
                with open(max_testdata_path, 'w') as f:
                    json.dump(max_testdata, f, indent=4)
                    
                median_testdata = copy.deepcopy(baseline_data)
                DataBuilder._create_nested_dict(median_testdata, keys, mid_value)
                median_testdata_path = f"./TestData/{operation_id}_{serial_number}_3.json"
                with open(median_testdata_path, 'w') as f:
                    json.dump(median_testdata, f, indent=4)
                    
                with open(f"./Template/TestStrategy/positive_parameter_min_max_test.j2", 'r') as f:
                    test_temp = f.read()
                test_temp = Template(test_temp)
                rendered_template = test_temp.render(
                    serial_number=serial_number,
                    key=key,
                    prop_type=generation_rules[key]['Type'],
                    min_value=min_value,
                    min_value_info=min_len,
                    min_testdata=f"{operation_id}_{serial_number}_1",
                    max_value=max_value,
                    max_value_info=max_len,
                    max_testdata=f"{operation_id}_{serial_number}_2",
                    median_value=mid_value,
                    median_value_info=int((min_len + max_len) / 2),
                    median_testdata=f"{operation_id}_{serial_number}_3",
                )
                    
            elif test_type == 'negative_test':
                
                under_min_value_testdata = copy.deepcopy(baseline_data)
                DataBuilder._create_nested_dict(under_min_value_testdata, keys, under_min_value)
                under_min_value_testdata_path = f"./TestData/{operation_id}_{serial_number}_1.json"
                with open(under_min_value_testdata_path, 'w') as f:
                    json.dump(under_min_value_testdata, f, indent=4)
                    
                over_max_value_testdata = copy.deepcopy(baseline_data)
                DataBuilder._create_nested_dict(over_max_value_testdata, keys, over_max_value)
                over_max_value_testdata_path = f"./TestData/{operation_id}_{serial_number}_2.json"
                with open(over_max_value_testdata_path, 'w') as f:
                    json.dump(over_max_value_testdata, f, indent=4)
                    
                with open(f"./Template/TestStrategy/negative_parameter_min_max_test.j2", 'r') as f:
                    test_temp = f.read()
                test_temp = Template(test_temp)
                rendered_template = test_temp.render(
                    serial_number=serial_number,
                    key=key,
                    prop_type=generation_rules[key]['Type'],
                    negative_min_value=under_min_value,
                    min_value_info=int(min_len - 1),
                    min_testdata=f"{operation_id}_{serial_number}_1",
                    negative_max_value=over_max_value,
                    max_value_info=int(max_len + 1),
                    max_testdata=f"{operation_id}_{serial_number}_2",
                )

            parsed_json = json.loads(rendered_template)
            for i in range(1, len(parsed_json['test_point']) + 1):
                parsed_json['test_point'][str(i)]['dependency'] = dependency_rule
                # * Add path rule value to test plan.
                if os.path.exists(f"./PathRule/{operation_id}.json"):
                    for key, path_item in path_rule.items():
                        parsed_json['test_point'][str(i)]['path'][key] = path_item['Value']
                parsed_json['test_point'][str(i)]['assertion'] = assertion_rule
                               
            if DEBUG:
                logging.debug(f'parsed_json: {parsed_json}')
                
            with open(test_plan_path, 'r', encoding='utf-8') as f:
                existing_test_plan = json.load(f)
            existing_test_plan['test_cases'][serial_number] = parsed_json
            
            with open(test_plan_path, 'w', encoding='utf-8') as f:
                json.dump(existing_test_plan, f, ensure_ascii=False, sort_keys=False, indent=4)

            serial_number += 1
            
        return serial_number
