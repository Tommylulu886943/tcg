import json
import logging
import glob
from collections import OrderedDict
from itertools import chain
from lib.general_tool import GeneralTool

class CaseRefactor:
    """A class that provides methods for updating query rules and dependent test cases."""

    @classmethod
    def update_query_rule_name(cls, issue: dict, new_doc: dict) -> None:
        """Updates the query rule for a given issue and new document.

        Args:
            issue (dict): The openapi doc issu that needs to be updated.
            new_doc (dict): The new openapi doc.
        """
        
        api_name = issue['affected_api_list'][0]
        op_id = GeneralTool.parse_api_name_to_op_id(api_name, new_doc)
        query_rule_path = f"./artifacts/QueryRule/{op_id}.json"
        try:
            with open(query_rule_path, 'r+') as f:
                query_rule = json.load(f)
                # * New rule is a OrderedDict to keep the order of the keys.
                new_rule = OrderedDict()
                for k, v in query_rule.items():
                    if k == issue['old_value']:
                        new_rule[issue['new_value']] = v
                    else:
                        new_rule[k] = v
                f.seek(0)
                json.dump(new_rule, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            logging.error(f"Cannot find '{query_rule_path}'. Please update it manually.")

        # * Update the dependent test cases.
        query_list = glob.glob(f"./artifacts/DependencyRule/*.json")
        for file in query_list:
            with open(file, 'r+') as f:
                d_query_rule = json.load(f)
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
                        d_query_rule['Teardown'][k]['query'] = new_query
                f.seek(0)
                json.dump(d_query_rule, f, indent=4)
                f.truncate()

    @classmethod
    def update_query_rule_enum_name(issue: dict, doc: dict):
        # Currently, Query does not render enums, so no implementation is needed.
        pass