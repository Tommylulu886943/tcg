import sys
import os
import json
import yaml
import glob
import logging

from jinja2 import Environment, Template

DEBUG = False
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.DEBUG)

class Render:
    
    @classmethod
    def _retrieve_obj_and_action(cls, test_plan: dict) -> str:
        
        with open('./config/obj_mapping.json', 'r') as f:
            obj_mapping = json.load(f)

        for obj_name, action_set in obj_mapping.items():
            for action, uri in action_set.items():
                method = action.split(' ')[0].lower()
                if test_plan['test_info']['uri'] == uri and method == test_plan['test_info']['method']:
                    return obj_name, action
    
    @classmethod
    def generate_robot_test_case(cls, test_plan):

        for test_plan_file in glob.glob('./test_plan/*.json'):

            with open(test_plan_file, 'r') as f:
                test_plan = json.load(f)
            robot_file = test_plan['test_info']['operationId'] + ".robot"
            robot_path = os.path.join('TestCases/RESTful_API/' + robot_file)
            os.makedirs(os.path.dirname(robot_path), exist_ok=True)

            obj_name, action = cls._retrieve_obj_and_action(test_plan)
            
            data = {
                'obj_name': obj_name,
                'action': action,
                'basic_selection': True,
            }
            
            for test_case in test_plan['test_cases']:
                with open('./Template/testcase.j2', 'r') as f:
                    template = f.read()
                template = Template(template)
                data.update({
                    'testcase_id': test_case,
                    'test_info': test_plan['test_info'],
                    'testcase': test_plan['test_cases'][test_case],
                })
                # * Add default configuration for POST and PUT requests
                if test_plan['test_info']['method'] in ["post", "put"]:
                    data.update({'config': 'config_name=Default'})
                # TODO - Add ${ID} template
                
                rendered_script = template.render(data)
                if data['basic_selection']:
                    data['basic_selection'] = False
                    
                with open(robot_path, "a", encoding="utf-8") as r:
                    r.write(rendered_script)


