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
        obj_name , action_name = GeneralTool._retrieve_obj_and_action(method + " " + uri)
        basic_test_plan = {
            'test_info': {
                'summary': method + ' ' + uri,
                'method': method,
                'uri': uri,
                'object': obj_name,
                'action': action_name,
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
    def functional_test(
        cls,
        test_type,
        operation_id,
        uri,
        method,
        operation,
        test_plan_path,
        serial_number,
        baseline_data,
        dependency_testdata
    ):
        try:
            with open(f"./GenerationRule/{operation_id}.json", 'r') as f:
                generation_rules = json.load(f)
                is_exist_g_rule = True
        except FileNotFoundError:
            logging.info(f"This api does not have a generation rule: {operation_id}")
            is_exist_g_rule = False
        
        # * Load assertion rule
        with open(f"./AssertionRule/{operation_id}.json", 'r') as f:
            assertion_rule = json.load(f)
            if test_type == 'positive_test':
                assertion_rule = assertion_rule["positive"]
        
        # * Load Path rule
        if os.path.exists(f"./PathRule/{operation_id}.json"):
            with open(f"./PathRule/{operation_id}.json", 'r') as f:
                path_rule = json.load(f)
        
        # * Load Query Rule
        if os.path.exists(f"./QueryRule/{operation_id}.json"):
            with open(f"./QueryRule/{operation_id}.json", 'r') as f:
                query_rule = json.load(f)
                
        # * Load Additional Action
        if os.path.exists(f"./AdditionalAction/{operation_id}.json"):
            with open(f"./AdditionalAction/{operation_id}.json", 'r') as f:
                additional_action = json.load(f)
        
        test_point_number = 1
        if test_type == 'positive_test':
            testdata = copy.deepcopy(baseline_data)
            test_point_list = {}
            if is_exist_g_rule:
                testdata_file = f'{operation_id}_{serial_number}_{test_point_number}'
                testdata_path = f'./TestData/{testdata_file}.json'
                with open(testdata_path, 'w') as f:
                    json.dump(testdata, f, indent=4) 
                test_point_list[str(test_point_number)] = {'config_name': testdata_file}
            else:
                test_point_list[str(test_point_number)] = {'config_name': None}    
                
            with open(f"./Template/TestStrategy/positive_functional_test.j2", 'r') as f:
                test_temp = f.read()
            test_temp = Template(test_temp)
            rendered_template = test_temp.render(tp=test_point_list[str(test_point_number)])
              
            parsed_json = json.loads(rendered_template)
            for i in range(1, len(parsed_json['test_point']) + 1):
                i = str(i)
                
                # * Add dependency rule to test plan.
                d_rule = GeneralTool.generate_dependency_test_data_file(copy.deepcopy(dependency_testdata), operation_id, serial_number, i)   
                parsed_json['test_point'][i]['dependency'] = d_rule
                
                # * Add path rule value to test plan.
                if os.path.exists(f"./PathRule/{operation_id}.json"):
                    for key, path_item in path_rule.items():
                        parsed_json['test_point'][i]['path'][key] = path_item['Value']
                
                # * Add query rule value to test plan.
                if os.path.exists(f"./QueryRule/{operation_id}.json"):
                    for key, query_item in query_rule.items():
                        parsed_json['test_point'][i]['query'][key] = query_item['Value']       
                
                # * Add Assertion rule value to test plan.
                parsed_json['test_point'][i]['assertion'] = assertion_rule
                
                # * Add additional action to test plan.
                parsed_json['test_point'][i]['additional_action'] = additional_action
                                    
                if DEBUG:
                    logging.debug(f'parsed_json: {parsed_json}')
                        
                with open(test_plan_path, 'r', encoding='utf-8') as f:
                    existing_test_plan = json.load(f)
                existing_test_plan['test_cases'][serial_number] = parsed_json
                
                with open(test_plan_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_test_plan, f, ensure_ascii=False, sort_keys=False, indent=4)
                    
                test_point_number += 1
            serial_number += 1
        return serial_number
        
    @classmethod
    def null_value_test(
        cls,
        test_type,
        operation_id,
        uri,
        method,
        operation,
        test_plan_path,
        serial_number,
        baseline_data,
        dependency_testdata
    ):
        try:
            with open(f"./GenerationRule/{operation_id}.json", 'r') as f:
                generation_rules = json.load(f)
        except FileNotFoundError:
            logging.warning(f'This API does not have a generation rule: {operation_id}, so the nullable_value_test case cannot be generated.')
            return serial_number
        
        # * Load assertion rule
        with open(f"./AssertionRule/{operation_id}.json", 'r') as f:
            assertion_rule = json.load(f)
            if test_type == 'negative_test':
                assertion_rule = assertion_rule["negative"]
            elif test_type == 'positive_test':
                assertion_rule = assertion_rule["positive"]
        
        # * Load Path rule
        if os.path.exists(f"./PathRule/{operation_id}.json"):
            with open(f"./PathRule/{operation_id}.json", 'r') as f:
                path_rule = json.load(f)

        # * Load Query Rule
        if os.path.exists(f"./QueryRule/{operation_id}.json"):
            with open(f"./QueryRule/{operation_id}.json", 'r') as f:
                query_rule = json.load(f)
                
        # * Load Additional Action
        if os.path.exists(f"./AdditionalAction/{operation_id}.json"):
            with open(f"./AdditionalAction/{operation_id}.json", 'r') as f:
                additional_action = json.load(f)
                
        for key in generation_rules:
            test_point_number = 1
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']
            nullable = rule['Nullable']
            
            if nullable == False:
                continue
            else:
                if test_type == "positive_test":
                    testdata = copy.deepcopy(baseline_data)
                    replace_key = keys.copy()
                    DataBuilder._create_nested_dict(testdata, replace_key, None)
                    testdata_file = f'{operation_id}_{serial_number}_{test_point_number}'
                    testdata_path = f'./TestData/{testdata_file}.json'
                    with open(testdata_path, 'w') as f:
                        json.dump(testdata, f, indent=4)
                        
                    test_point_list = {}
                    test_point_list[str(test_point_number)] = {
                        'key': key,
                        'null_value': None,
                        'config_name': testdata_file,
                        'prop_type': generation_rules[key]['Type'],
                    }
                    
                    with open(f"./Template/TestStrategy/positive_parameter_nullable_test.j2", 'r') as f:
                        test_temp = f.read()
                    test_temp = Template(test_temp)
                    rendered_template = test_temp.render(test_point_list=test_point_list)
                    
                    parsed_json = json.loads(rendered_template)
                    for i in range(1, len(parsed_json['test_point']) + 1):
                        i = str(i)
                        # * Add dependency rule to test plan.
                        d_rule = GeneralTool.generate_dependency_test_data_file(copy.deepcopy(dependency_testdata), operation_id, serial_number, i)   
                        parsed_json['test_point'][i]['dependency'] = d_rule
                        
                        # * Add path rule value to test plan.
                        if os.path.exists(f"./PathRule/{operation_id}.json"):
                            for key, path_item in path_rule.items():
                                parsed_json['test_point'][i]['path'][key] = path_item['Value']
                                
                        # * Add query rule value to test plan.
                        if os.path.exists(f"./QueryRule/{operation_id}.json"):
                            for key, query_item in query_rule.items():
                                parsed_json['test_point'][i]['query'][key] = query_item['Value']
                                
                        # * Add assertion rule value to test plan.
                        parsed_json['test_point'][i]['assertion'] = assertion_rule
                        
                        # * Add additional action to test plan.
                        parsed_json['test_point'][i]['additional_action'] = additional_action                        
                                    
                    if DEBUG:
                        logging.debug(f'parsed_json: {parsed_json}')
                        
                    with open(test_plan_path, 'r', encoding='utf-8') as f:
                        existing_test_plan = json.load(f)
                    existing_test_plan['test_cases'][serial_number] = parsed_json
                    
                    with open(test_plan_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_test_plan, f, ensure_ascii=False, sort_keys=False, indent=4)
                        
                    test_point_number += 1
                serial_number += 1
        return serial_number
    
    @classmethod
    def enum_value_test(
        cls,
        test_type,
        operation_id,
        uri,
        method,
        operation,
        test_plan_path,
        serial_number,
        baseline_data,
        dependency_testdata
    ):
        
        try:
            with open(f"./GenerationRule/{operation_id}.json", 'r') as f:
                generation_rules = json.load(f)
        except FileNotFoundError:
            logging.warning(f'This API does not have a generation rule: {operation_id}, so the enum_parameter_test case cannot be generated.')
            return serial_number
        
        # * Load assertion rule
        with open(f"./AssertionRule/{operation_id}.json", 'r') as f:
            assertion_rule = json.load(f)
            if test_type == 'negative_test':
                assertion_rule = assertion_rule["negative"]
            elif test_type == 'positive_test':
                assertion_rule = assertion_rule["positive"]
        
        # * Load Path rule
        if os.path.exists(f"./PathRule/{operation_id}.json"):
            with open(f"./PathRule/{operation_id}.json", 'r') as f:
                path_rule = json.load(f)

        # * Load Query Rule
        if os.path.exists(f"./QueryRule/{operation_id}.json"):
            with open(f"./QueryRule/{operation_id}.json", 'r') as f:
                query_rule = json.load(f) 
                               
        # * Load Additional Action
        if os.path.exists(f"./AdditionalAction/{operation_id}.json"):
            with open(f"./AdditionalAction/{operation_id}.json", 'r') as f:
                additional_action = json.load(f)
                
        for key in generation_rules:
            test_point_number = 1
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']
            enum = rule['Enum']
            
            if enum == []:
                continue
            else:
                if test_type == 'positive_test':
                    test_point_list = {}
                    for enum_value in enum:       
                        testdata = copy.deepcopy(baseline_data)
                        replace_key = keys.copy()
                        DataBuilder._create_nested_dict(testdata, replace_key, enum_value)
                        testdata_file = f'{operation_id}_{serial_number}_{test_point_number}'
                        testdata_path = f'./TestData/{testdata_file}.json'    
                        with open(testdata_path, 'w') as f:
                            json.dump(testdata, f, indent=4)        
                                            
                        test_point_list[str(test_point_number)] = {
                            'testdata': testdata,
                            'replace_key': replace_key,
                            'key': key,
                            'config_name': testdata_file,
                            'enum_value': enum_value,
                            'prop_type': generation_rules[key]['Type'],
                        }
                        test_point_number += 1
                        
                    with open(f"./Template/TestStrategy/positive_parameter_enum_test.j2", 'r') as f:
                        test_temp = f.read()
                    test_temp = Template(test_temp)
                    rendered_template = test_temp.render(test_point_list=test_point_list)

                elif test_type == 'negative_test':
                    test_point_list = {}
                    testdata = copy.deepcopy(baseline_data)
                    replace_key = keys.copy()
                    enum_value = DataBuilder.generate_random_string()
                    DataBuilder._create_nested_dict(testdata, replace_key, enum_value)
                    testdata_file = f'{operation_id}_{serial_number}_{test_point_number}'
                    testdata_path = f'./TestData/{testdata_file}.json'
                    
                    with open(testdata_path, 'w') as f:
                        json.dump(testdata, f, indent=4)
                        
                    test_point_list[str(test_point_number)] = {
                        'testdata': testdata,
                        'replace_key': replace_key,
                        'key': key,
                        'config_name': testdata_file,
                        'enum_value': enum_value,
                        'prop_type': generation_rules[key]['Type'],
                    }
                    test_point_number += 1
                    
                    with open(f"./Template/TestStrategy/negative_parameter_enum_test.j2", 'r') as f:
                        test_temp = f.read()
                    test_temp = Template(test_temp)
                    rendered_template = test_temp.render(test_point_list=test_point_list)
                
                parsed_json = json.loads(rendered_template)
                for i in range(1, len(parsed_json['test_point']) + 1):
                    i = str(i)
                    # * Add dependency rule to test plan.
                    d_rule = GeneralTool.generate_dependency_test_data_file(copy.deepcopy(dependency_testdata), operation_id, serial_number, i)   
                    parsed_json['test_point'][i]['dependency'] = d_rule
                    
                    # * Add path rule value to test plan.
                    if os.path.exists(f"./PathRule/{operation_id}.json"):
                        for key, path_item in path_rule.items():
                            parsed_json['test_point'][i]['path'][key] = path_item['Value']
                            
                    # * Add query rule value to test plan.
                    if os.path.exists(f"./QueryRule/{operation_id}.json"):
                        for key, query_item in query_rule.items():
                            parsed_json['test_point'][i]['query'][key] = query_item['Value']

                    # * Add assertion rule value to test plan.                         
                    parsed_json['test_point'][i]['assertion'] = assertion_rule
                    
                    # * Add additional action to test plan.
                    parsed_json['test_point'][i]['additional_action'] = additional_action
                                    
                with open(test_plan_path, 'r', encoding='utf-8') as f:
                    existing_test_plan = json.load(f)
                existing_test_plan['test_cases'][serial_number] = parsed_json
                
                with open(test_plan_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_test_plan, f, ensure_ascii=False, sort_keys=False, indent=4)
                
                test_point_number += 1
            serial_number += 1
        return serial_number
    
    @classmethod
    def required_parameter_test(
        cls,
        test_type,
        operation_id,
        uri, 
        method, 
        operation, 
        test_plan_path, 
        serial_number, 
        baseline_data, 
        dependency_testdata
    ):
        
        try:
            with open(f"./GenerationRule/{operation_id}.json", 'r') as f:
                generation_rules = json.load(f)
        except FileNotFoundError:
            logging.warning(f'This API does not have a generation rule: {operation_id}, so the required_parameter_test case cannot be generated.')
            return serial_number
        
        # * Load assertion rule
        with open(f"./AssertionRule/{operation_id}.json", 'r') as f:
            assertion_rule = json.load(f)
            if test_type == 'negative_test':
                assertion_rule = assertion_rule["negative"]
            elif test_type == 'positive_test':
                assertion_rule = assertion_rule["positive"]
        
        # * Load Path rule
        if os.path.exists(f"./PathRule/{operation_id}.json"):
            with open(f"./PathRule/{operation_id}.json", 'r') as f:
                path_rule = json.load(f)
                
        # * Load Query Rule
        if os.path.exists(f"./QueryRule/{operation_id}.json"):
            with open(f"./QueryRule/{operation_id}.json", 'r') as f:
                query_rule = json.load(f)
                
        # * Load Additional Action
        if os.path.exists(f"./AdditionalAction/{operation_id}.json"):
            with open(f"./AdditionalAction/{operation_id}.json", 'r') as f:
                additional_action = json.load(f)
                   
        test_point_number = 1
        for key in generation_rules:
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']
            
            required = rule['Required']
            if required == False:
                continue
            else:
                if test_type == 'negative_test':
                    testdata = copy.deepcopy(baseline_data)
                    replace_key = keys.copy()
                    GeneralTool.remove_key_in_json(testdata, replace_key)
                    testdata_file = f'{operation_id}_{serial_number}_{test_point_number}.json'
                    testdata_path = f'./TestData/{testdata_file}'
                    with open(testdata_path, 'w') as f:
                        json.dump(testdata, f, indent=4)
                    
                    with open(f"./Template/TestStrategy/negative_parameter_required_test.j2", 'r') as f:
                        test_temp = f.read()
                    test_temp = Template(test_temp)
                    rendered_template = test_temp.render(
                        key=key,
                        prop_type=generation_rules[key]['Type'],
                        config_name=testdata_file
                    )
                    
                    parsed_json = json.loads(rendered_template)
                    for i in range(1, len(parsed_json['test_point']) + 1):
                        i = str(i)
                        # * Add dependency rule to test plan.
                        d_rule = GeneralTool.generate_dependency_test_data_file(copy.deepcopy(dependency_testdata), operation_id, serial_number, i)   
                        parsed_json['test_point'][i]['dependency'] = d_rule
                        
                        # * Add path rule value to test plan.
                        if os.path.exists(f"./PathRule/{operation_id}.json"):
                            for key, path_item in path_rule.items():
                                parsed_json['test_point'][i]['path'][key] = path_item['Value']
                                    
                        # * Add query rule value to test plan.
                        if os.path.exists(f"./QueryRule/{operation_id}.json"):
                            for key, query_item in query_rule.items():
                                parsed_json['test_point'][i]['query'][key] = query_item['Value']                                
                                    
                        # * Add assertion rule value to test plan.
                        parsed_json['test_point'][i]['assertion'] = assertion_rule
                        
                        # * Add additional action to test plan.
                        parsed_json['test_point'][i]['additional_action'] = additional_action                        
                        
                    with open(test_plan_path, 'r', encoding='utf-8') as f:
                        existing_test_plan = json.load(f)
                    existing_test_plan['test_cases'][serial_number] = parsed_json
                    
                    with open(test_plan_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_test_plan, f, ensure_ascii=False, sort_keys=False, indent=4)
                    
                    test_point_number += 1
            serial_number += 1          
        return serial_number
    
    @classmethod
    def parameter_min_max_test(
        cls, 
        test_type, 
        operation_id, 
        uri, 
        method, 
        operation, 
        test_plan_path, 
        serial_number, 
        baseline_data, 
        dependency_testdata
    ):
 
        try:
            with open(f"./GenerationRule/{operation_id}.json", 'r') as f:
                generation_rules = json.load(f)
        except FileNotFoundError:
            logging.warning(f'This API does not have a generation rule: {operation_id}, so the parameter_min_max_test case cannot be generated.')
            return serial_number
        
        for key in generation_rules:
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']
            if rule['Data Length'] == "":
                logging.warning(f'{operation_id} field {key} does not have a Data Length rule, so the parameter_min_max_test case cannot be generated.')
                continue
            elif rule['Data Generator'] == "":
                logging.warning(f'{operation_id} field {key} does not have a Data Generator rule, so the parameter_min_max_test case cannot be generated.')
                continue
            elif info['Type'] not in ['string', 'integer', 'number', 'float']:
                logging.warning(f'{operation_id} field {key} has an invalid Type rule, so the parameter_min_max_test case cannot be generated.')
                continue
            elif info['Default'] != "":
                logging.warning(f'{operation_id} field {key} has a Default value, so the parameter_min_max_test case cannot be generated.')
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
            
            # * Load assertion rule
            with open(f"./AssertionRule/{operation_id}.json", 'r') as f:
                assertion_rule = json.load(f)
                if test_type == 'negative_test':
                    assertion_rule = assertion_rule["negative"]
                elif test_type == 'positive_test':
                    assertion_rule = assertion_rule["positive"]
            
            # * Load Path rule
            if os.path.exists(f"./PathRule/{operation_id}.json"):
                with open(f"./PathRule/{operation_id}.json", 'r') as f:
                    path_rule = json.load(f)

            # * Load Query Rule
            if os.path.exists(f"./QueryRule/{operation_id}.json"):
                with open(f"./QueryRule/{operation_id}.json", 'r') as f:
                    query_rule = json.load(f)
                                    
            # * Load Additional Action
            if os.path.exists(f"./AdditionalAction/{operation_id}.json"):
                with open(f"./AdditionalAction/{operation_id}.json", 'r') as f:
                    additional_action = json.load(f)
            
            if test_type == 'positive_test':
                min_testdata = copy.deepcopy(baseline_data)
                replace_key = keys.copy()
                DataBuilder._create_nested_dict(min_testdata, replace_key, min_value)
                min_testdata_path = f"./TestData/{operation_id}_{serial_number}_1.json"
                with open(min_testdata_path, 'w') as f:
                    json.dump(min_testdata, f, indent=4)
                    
                max_testdata = copy.deepcopy(baseline_data)
                replace_key = keys.copy()
                DataBuilder._create_nested_dict(max_testdata, replace_key, max_value)
                max_testdata_path = f"./TestData/{operation_id}_{serial_number}_2.json"
                with open(max_testdata_path, 'w') as f:
                    json.dump(max_testdata, f, indent=4)
                    
                median_testdata = copy.deepcopy(baseline_data)
                replace_key = keys.copy()
                DataBuilder._create_nested_dict(median_testdata, replace_key, mid_value)
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
                replace_key = keys.copy()
                DataBuilder._create_nested_dict(under_min_value_testdata, replace_key, under_min_value)
                under_min_value_testdata_path = f"./TestData/{operation_id}_{serial_number}_1.json"
                with open(under_min_value_testdata_path, 'w') as f:
                    json.dump(under_min_value_testdata, f, indent=4)
                    
                over_max_value_testdata = copy.deepcopy(baseline_data)
                replace_key = keys.copy()
                DataBuilder._create_nested_dict(over_max_value_testdata, replace_key, over_max_value)
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
                i = str(i)
                # * Add dependency rule to test plan.
                d_rule = GeneralTool.generate_dependency_test_data_file(copy.deepcopy(dependency_testdata), operation_id, serial_number, i)   
                parsed_json['test_point'][i]['dependency'] = d_rule
                
                # * Add path rule value to test plan.
                if os.path.exists(f"./PathRule/{operation_id}.json"):
                    for key, path_item in path_rule.items():
                        parsed_json['test_point'][i]['path'][key] = path_item['Value']
                    
                # * Add query rule value to test plan.
                if os.path.exists(f"./QueryRule/{operation_id}.json"):
                    for key, query_item in query_rule.items():
                        parsed_json['test_point'][i]['query'][key] = query_item['Value']   
                                      
                # * Add asssertion rule value to test plan.
                parsed_json['test_point'][i]['assertion'] = assertion_rule

                # * Add additional action to test plan.
                parsed_json['test_point'][i]['additional_action'] = additional_action
                               
            if DEBUG:
                logging.debug(f'parsed_json: {parsed_json}')
                
            with open(test_plan_path, 'r', encoding='utf-8') as f:
                existing_test_plan = json.load(f)
            existing_test_plan['test_cases'][serial_number] = parsed_json
            
            with open(test_plan_path, 'w', encoding='utf-8') as f:
                json.dump(existing_test_plan, f, ensure_ascii=False, sort_keys=False, indent=4)

            serial_number += 1  
        return serial_number
