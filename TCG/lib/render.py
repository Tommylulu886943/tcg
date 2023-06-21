import sys
import os
import json
import yaml
import glob
import logging

from jinja2 import Environment, Template
from lib.general_tool import GeneralTool
class Render:
    
    @classmethod
    def generate_robot_test_case(cls) -> None:
        """ Generate robot test case from all test plan files."""
        
        for test_plan_file in glob.glob('./test_plan/*.json'):
            with open(test_plan_file, 'r') as f:
                test_plan = json.load(f)
            
            # * If the test plan is not included any test case, skip it.
            if len(test_plan['test_cases']) == 0:
                continue
            
            robot_file = test_plan['test_info']['operationId'] + ".robot"
            robot_path = os.path.join('TestCases', 'RESTful_API', robot_file)
            os.makedirs(os.path.dirname(robot_path), exist_ok=True)
            
            with open('./Template/base.j2', 'r') as f:
                base_template = Template(f.read())
                rendered_base = base_template.render(test_plan)

            with open('./Template/testcase.j2', 'r') as f:
                template = Template(f.read())
                rendered_script = template.render(test_plan)
                
            with open(robot_path, "w", encoding="utf-8") as r:
                r.write(rendered_base)
                
            with open(robot_path, "a", encoding="utf-8") as r:
                r.write(rendered_script)
