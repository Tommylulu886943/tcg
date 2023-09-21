import json
import logging
import glob
from collections import OrderedDict
from itertools import chain
from lib.general_tool import GeneralTool

class CaseRefactor:
    """
    A class that provides methods for updating query rules and dependent test cases.

    Methods:
        update_query_rule_name(issue: dict, new_doc: dict) -> None:
            Updates the query rule for a given issue and new document.

        update_query_rule_enum_name(issue: dict, doc: dict) -> None:
            Updates the query rule enum name for a given issue and document (not implemented).
    """
    
    @classmethod
    def update_test_cases(cls, issue_list: list, new_doc: dict) -> None:
        """
        Update the existing test cases according to the issue list's trigger action.
        """
        for issue in issue_list:
            if issue['trigger_action'] == None:
                print(issue['trigger_action'])
                print(f"No trigger action for this '{issue['severity']}' issue '{issue['field']}'. Please update it manually.")
            elif issue['trigger_action'] == 'Update Schema':
                print("Run Update Schema Process...")
                cls.update_schema_rule(issue, new_doc)
            elif issue['trigger_action'] == 'Update Query Parameter Name':
                cls.update_query_rule_name(issue, new_doc)
            elif issue['trigger_action'] == 'Update Query Parameter Enum Name':
                cls.update_query_rule_enum_name(issue, new_doc)

    @classmethod
    def update_query_rule_name(cls, issue: dict, new_doc: dict) -> None:
        """
        Updates the query rule for a given issue and new document.

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            new_doc (dict): The new openapi doc.
        """
        
        api_name = issue['affected_api_list'][0]
        op_id = GeneralTool.parse_api_name_to_op_id(api_name, new_doc)
        query_rule_path = f"../artifacts/QueryRule/{op_id}.json"
        try:
            with open(query_rule_path, 'r+') as f:
                query_rule = json.loads(f.read())
                # * New rule is a OrderedDict to keep the order of the keys.
                new_rule = OrderedDict()
                for k, v in query_rule.items():
                    if k == issue['old_value']:
                        new_rule[issue['new_value']] = v
                    else:
                        new_rule[k] = v
                f.seek(0)
                f.write(json.dumps(new_rule, indent=4))
                f.truncate()
        except FileNotFoundError:
            logging.error(f"Cannot find '{query_rule_path}'. Please update it manually.")

        # * Update the dependent test cases.
        query_list = glob.glob(f"../artifacts/DependencyRule/*.json")
        for file in query_list:
            with open(file, 'r+') as f:
                d_query_rule = json.loads(f.read())
                new_query = OrderedDict()
                for k, v in chain(d_query_rule['Setup'].items(), d_query_rule['Teardown'].items()):
                    if v['api'] == api_name and v['query'] != {}:
                        for key, value in v['query'].items():
                            if key == issue['old_value']:
                                new_query[issue['new_value']] = value
                            else:
                                new_query[key] = value
                    if d_query_rule['Setup'][k]['api'] == api_name and issue['old_value'] in d_query_rule['Setup'][k]['query']:
                        d_query_rule['Setup'][k]['query'] = new_query
                    else:
                        if d_query_rule['Teardown'] != {}:
                            d_query_rule['Teardown'][k]['query'] = new_query
                f.seek(0)
                f.write(json.dumps(d_query_rule, indent=4))
                f.truncate()

    @classmethod
    def add_assertion_rule(cls, issue: dict, doc: dict) -> None:
        """
        Adds a new assertion rule for a given issue and document.

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            doc (dict): The openapi doc.
            
        # TODO : Need to test this method.
        """
        api_name = issue['affected_api_list'][0]
        op_id = GeneralTool.parse_api_name_to_op_id(api_name, doc)
        assertion_path = f"../artifacts/AssertionRule/{op_id}.json"
        try:
            with open(assertion_path, 'r+') as f:
                rule = json.loads(f.read())
                assertion_type = GeneralTool.obtain_assertion_type(issue['field'])
                seq_num = GeneralTool.calculate_dict_key_index(rule[assertion_type])
                rule[assertion_type][seq_num] = {
                    "source": "Status Code",
                    "field_expression": "",
                    "filter_expression": "",
                    "assertion_method": "Should Be Equal",
                    "expected_value": issue['field'],
                }
                f.seek(0)
                f.write(json.dumps(rule, indent=4))
                f.truncate()
        except FileNotFoundError:
            logging.error(f"Cannot find '{assertion_path}'. Please update it manually.")
    
    @classmethod
    def remove_assertion_rule(cls, issue: dict, doc: dict) -> None:
        """
        Removes an assertion rule for a given issue and document.

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            doc (dict): The openapi doc.
            
        #TODO: Need unit test for this method.
        """
        api_name = issue['affected_api_list'][0]
        op_id = GeneralTool.parse_api_name_to_op_id(api_name, doc)
        assertion_path = f"../artifacts/AssertionRule/{op_id}.json"
        try:
            with open(assertion_path, 'r+') as f:
                rule = json.loads(f.read())
                assertion_type = GeneralTool.obtain_assertion_type(issue['field'])
                for k, v in rule[assertion_type].items():
                    if v['expected_value'] == issue['field']:
                        del rule[assertion_type][k]
                f.seek(0)
                f.write(json.dumps(rule, indent=4))
                f.truncate()
        except FileNotFoundError:
            logging.error(f"Cannot find '{assertion_path}'. Please update it manually.")
    
    @classmethod        
    def update_schema_rule(cls, issue: dict, doc: dict) -> None:
        """
        Updates the schema rule for a given issue and document.

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            doc (dict): The openapi doc.
        """
        from lib.diff import DiffFinder
        for api in issue['affected_api_list']:
            # * Find the schema name.
            path = DiffFinder.parse_key_path(issue['path'])
            # * Determine the reference API and reference type. request, response, or parameter (in path or query)
            action_list = DiffFinder.found_reference_api_and_ref_type(path[2], doc)
            op_id = GeneralTool.parse_api_name_to_op_id(api, doc)
            
            for action in action_list:
                action_type = action.split(' ')[-1]
                if action_type == 'Request':
                    logging.debug("Run Update Schema Request Process...")
                    cls._update_request_body_with_new_schema(op_id, issue, path)
                elif action_type == 'Response':
                    logging.debug("For now, we do not support updating response field. Please update it manually.")
                    pass
                elif action_type == 'Path':
                    pass
                elif action_type == 'Query':
                    pass
                elif action_type == 'Header':
                    logging.info(f"For now, we do not support updating header field. Please update it manually.")
                    pass
                elif action_type == 'Cookie':
                    logging.info(f"For now, we do not support updating cookie field. Please update it manually.")
                    pass

    @classmethod
    def _update_request_body_with_new_schema(cls, op_id: str ,issue: dict, path: list) -> None:
        """
        Updates the request body with new schema for a given issue and document.

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            doc (dict): The openapi doc.
        """       
        key, field = GeneralTool.parse_field_path_to_key(path)
        try:
            with open(f"../artifacts/GenerationRule/{op_id}.json", 'r+') as f:
                rule = json.loads(f.read())
                logging.debug(f"rule: {rule[key]}")
                
                # f.seek(0)
                # f.write(json.dumps(rule, indent=4))
                # f.truncate()
        except FileNotFoundError:
            pass
            logging.error(f"This API '{op_id}' does not have request.")


