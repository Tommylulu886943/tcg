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
    def update_query_rule_enum_name(cls, issue: dict, doc: dict):
        """
        Updates the query rule enum name for a given issue and document (not implemented).

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            doc (dict): The openapi doc.
        """
        # Currently, Query does not render enums, so no implementation is needed.
        pass
    
    def add_assertion_rule(self, issue: dict, doc: dict) -> None:
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
            
    def remove_assertion_rule(self, issue: dict, doc: dict) -> None:
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
            
    def update_schema_rule(self, issue: dict, doc: dict) -> None:
        """
        Updates the schema rule for a given issue and document.

        Args:
            issue (dict): The openapi doc issue that needs to be updated.
            doc (dict): The openapi doc.
        """
    
        # 做法：先找到issue所在的api，然后找到对应的response，然后找到对应的schema，然后找到对应的field，然后更新。
        # 先按照影響的 API 來找 request 再找 response 再找 schema 再找 field 再更新
        # 1. 找到影響的 API
        for api in issue['affected_api_list']:
            op_id = GeneralTool.parse_api_name_to_op_id(api_name, doc)
            # 2. 找到 request (有可能沒有 request，所以要先判斷有沒有 request)
            try:
                with open(f"../artifacts/GenerationRule/{op_id}.json", 'r+') as f:
                    rule = json.loads(f.read())
                    for k, v in rule.items():
                        if k == issue['field']:
                            rule[k] = issue['new_value']
                    f.seek(0)
                    f.write(json.dumps(rule, indent=4))
                    f.truncate()
            except FileNotFoundError:
                logging.error(f"This API '{api}' does not have request.")
            # 3. 找到 response
            #TODO: 目前沒有支持測試 response 的測試策略，所以先不處理 response 的情況。
            # 4. 找到 schema
            schema = GeneralTool.find_schema(response)
            # 5. 找到 field
            field = GeneralTool.find_field(schema, issue['field'])
            # 6. 更新 field
            field['name'] = issue['new_value']

        
        


