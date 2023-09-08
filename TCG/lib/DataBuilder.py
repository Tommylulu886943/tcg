import os
import sys
import re
import json
import random
import string
import genrex
import uuid
import pytest
import logging
from datetime import datetime, timedelta

DEBUG = False

class DataBuilder:
    
    @classmethod
    def init_test_data(cls, operation_id):
        # * Load generation rule from json file.
        try:
            with open(f"./artifacts/GenerationRule/{operation_id}.json", "r") as f:
                generation_rules = json.load(f)
        except FileNotFoundError:
            # * if generation rule not found, because this operation no request body, ex: GET, DELETE.
            logging.warning(f"Generation rule for {operation_id} not found. This operation no request body, so no test data is generated.")
            return None
        result = cls.data_builder(generation_rules)
        return result
    
    @classmethod
    def init_dependency_test_data(cls, operation_id):
        try:
            with open(f"./artifacts/DependencyRule/{operation_id}.json", "r") as f:
                dependency_data = json.load(f)
        except FileNotFoundError:
            logging.warning(f"Dependency data for {operation_id} not found. This operation no request body, so no dependency data is generated.")
            return None
        
        result = {"Setup": {}, "Teardown": {}}
        for action_type in ['Setup', 'Teardown']:
            for index, action in dependency_data[action_type].items():
                if 'data_generation_rules' in action and action['data_generation_rules'] != {}:
                    result[action_type][index] = cls.data_builder(action['data_generation_rules'])
                else:
                    logging.info(f"Data Generation Rules not found in {action_type} action {index}.")
        return result
                
    @classmethod
    def data_builder(cls, generation_rules):
        """
        Generates test data based on a set of generation rules.
        
        Args:
            generation_rules: a dictionary of generation rules
        
        Returns:
            A dictionary of test data generated from the given generation rules.
        """        
        result = {}
        if generation_rules is None:
            return result
        for key in generation_rules:
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']
            enum = rule['Enum']
            
            if generation_rules[key]['Default'] != "":
                value = generation_rules[key]['Default']
            elif rule['Regex Pattern'] != "":
                value = cls.generate_data_from_regex(rule['Regex Pattern'])
            elif rule['Data Generator'] == 'Random Enumeration Value':
                value = random.choice(enum)
                if generation_rules[key]['Type'] == 'string':
                    value = str(value)
                elif generation_rules[key]['Type'] == 'integer':
                    value = int(value)
            elif rule['Data Generator'] == 'Random String (Without Special Characters)':
                value = cls.generate_random_string(rule['Data Length'])
            elif rule['Data Generator'] == 'Random String':
                value = cls.generate_random_string(rule['Data Length'], specical_char=True)
            elif rule['Data Generator'] == 'Random Integer':
                value = cls.generate_random_integer(rule['Data Length'])
            elif rule['Data Generator'] == 'Random Boolean':
                value = cls.generate_random_boolean()
            elif rule['Data Generator'] == 'Random DATE-TIME':
                value = cls.generate_random_datetime()
            elif rule['Data Generator'] == 'Random EMAIL':
                value = cls.generate_random_email()
            elif rule['Data Generator'] == 'Random IPV4':
                value = cls.generate_random_ip()
            elif rule['Data Generator'] == 'Random IPV6':
                value = cls.generate_random_ipv6()
            elif rule['Data Generator'] == 'Random HOSTNAME':
                value = cls.generate_random_domain_name()
            elif rule['Data Generator'] == 'Random UUID':
                value = cls.generate_random_uuid()
            elif rule['Data Generator'] == 'Random Number (Float)':
                value = cls.generate_random_float(rule['Data Length'])
            elif rule['Data Generator'] == 'Random INT64':
                value = cls.generate_random_int64()
            elif rule['Data Generator'] == 'Random INT32':
                value = cls.generate_random_int32()
            elif rule['Data Generator'] == 'Random BINARY':
                value = cls.generate_random_binary()
            else:
                value = None
            cls._create_nested_dict(result, keys, value)
        return result
    
    @classmethod
    def _handle_list(cls, data: dict, key: list, value: str, overwrite: bool = False) -> list:
        """
        Handles the logic for adding a value to a list in the `data` dictionary.

        Args:
            data (dict): The dictionary to which the value will be added.
            key (str): The key in the `data` dictionary where the value will be added.
            value (any): The value to be added to the list.
            overwrite (bool): Indicates whether to overwrite the existing list or append to it.

        Returns:
            list: The updated list in the `data` dictionary.
        """
        value = eval(value)
        if overwrite:
            data[key] = [value]
        else:
            if isinstance(value, list):
                data[key].append(value)
            elif isinstance(value, tuple):
                data[key].extend(value)
        return data[key]

    @classmethod
    def _handle_dict(cls, data: dict, key: list, value: str, overwrite: bool = False) -> dict:
        """
        Handle the logic of adding a value to a dictionary in the `data` dictionary.

        Args:
            data (dict): The dictionary to which the value will be added.
            key (str): The key in the `data` dictionary where the value will be added.
            value (any): The value to be added to the dictionary.
            overwrite (bool): Indicates whether to overwrite the existing value or append to it.

        Returns:
            dict: The updated dictionary with the value added.
        """
        value = eval(value)
        if overwrite:
            if isinstance(data[key], dict):
                data[key] = value
            elif isinstance(data[key], list):
                data[key] = [value]
        else:
            if isinstance(data[key], dict):
                data[key].update(value)
            elif isinstance(data[key], list):
                data[key].append(value)
        return data[key]

    @classmethod
    def _handle_comma_separated(cls, data: dict, key: list, value: str, overwrite: bool = False) -> dict:
        """
        Handles the logic for adding values to a dictionary in the `data` dictionary when the value is a comma-separated string.
    
        Args:
            data (dict): The dictionary to which the values will be added.
            key (str): The key in the `data` dictionary where the values will be added.
            value (str): The comma-separated string of values to be added to the dictionary.
            overwrite (bool): Indicates whether to overwrite the existing values or append to them.
    
        Returns:
            dict: The updated dictionary with the values added.
        """
        if value.startswith('[') and value.endswith(']'):
            value = value.strip('[]')
            data[key].append([x.strip() for x in value.split('],')])
        else:
            for el in value.split(','):
                el = el.strip()
                logging.debug(el)
                if el.startswith('{') and el.endswith('}'):
                    el = el.strip('{}')
                    data[key].append(json.loads(el))
                elif el.startswith('[') and el.endswith(']'):
                    el = el.strip('[]')
                    data[key] = [x.strip() for x in el.split(',')]
                elif el.startswith('"') and el.endswith('"'):
                    el = el.strip('"')
                    data[key].append(el)
                elif el.isdigit():
                    if overwrite:
                        data[key] = [int(x.strip()) for x in value.split(',')]
                    else:
                        data[key].append(int(el))
                elif el.replace('.', '', 1).isdigit():
                    if overwrite:
                        data[key] = [float(x.strip()) for x in value.split(',')]
                    else:
                        data[key].append(float(el))
                else:
                    if overwrite:
                        data[key] = [x.strip() for x in value.split(',')]
                    else:
                        data[key].append(el)
        return data[key]

    @classmethod
    def _handle_digit(cls, data: dict, key: list, value: str, overwrite: bool = False) -> list:
        """
        Handle the logic of adding a value to a dictionary in the `data` dictionary when the value is a digit.

        Args:
            data (dict): The dictionary to which the value will be added.
            key (str): The key in the `data` dictionary where the value will be added.
            value (str): The value to be added to the dictionary.
            overwrite (bool): Indicates whether to overwrite the existing value or append to it.

        Returns:
            list: The updated list in the `data` dictionary.
        """
        if overwrite:
            return [int(value)]
        else:
            data[key].append(int(value))
            return data[key]
        
    @classmethod
    def _handle_float(cls, data: dict, key: list, value: str, overwrite: bool = False) -> list:
        """
        Handle the logic of adding a value to a dictionary in the `data` dictionary when the value is a float.

        Args:
            data (dict): The dictionary to which the value will be added.
            key (str): The key in the `data` dictionary where the value will be added.
            value (str): The value to be added to the dictionary.
            overwrite (bool): Indicates whether to overwrite the existing value or append to it.

        Returns:
            list: The updated list in the `data` dictionary.
        """
        if value.startswith('"') and value.endswith('"'):
            value = value.strip('"')
        if overwrite:
            return [float(value)]
        else:
            data[key].append(float(value))
            return data[key]

    @classmethod
    def _handle_default(cls, data: dict, key: list, value: str, overwrite: bool = False) -> list:
        """
        Add a value to the data dictionary at the specified key if the value is not a list, dictionary, or comma-separated string.

        Args:
            data (dict): The dictionary to which the value will be added.
            key (str): The key in the data dictionary where the value will be added.
            value (any): The value to be added to the dictionary.
            overwrite (bool): Indicates whether to overwrite the existing value or append to it.

        Returns:
            list: The updated list in the data dictionary.
        """
        if type(value) != dict and type(value) != list:
            if value.startswith('"') and value.endswith('"'):
                value = value.strip('"')
        if overwrite:
            return [value]
        else:
            data[key].append(value)
            logging.debug(data)
            return data[key]

    @classmethod
    def _create_nested_dict(cls, data: dict, keys: list, value: str, overwrite: bool = False) -> None:
        """
        Create a nested dictionary based on a list of keys and a corresponding value.

        Args:
            cls: The class object.
            data: The dictionary to which the nested dictionary will be added.
            keys: A list of keys representing the nested structure of the dictionary.
            value: The value to be added to the innermost key of the nested dictionary.
            overwrite: Indicates whether to overwrite existing values or append to them. Defaults to False.

        Returns:
            None

        Example:
            data = {}
            keys = ['key1', 'key2', 'key3']
            value = 'example value'
            DataBuilder._create_nested_dict(data, keys, value)
            print(data)
            # Output: {'key1': {'key2': {'key3': 'example value'}}}
        """
        
        type_mapping = {
            'list': cls._handle_list,
            'dict': cls._handle_dict,
            'comma_separated': cls._handle_comma_separated,
            'digit': cls._handle_digit,
            'float': cls._handle_float,
            'default': cls._handle_default,
        }
        if len(keys) == 1:
            key = keys[0]
            if key.endswith("[0]"):
                key = key.rstrip("[0]")
                data.setdefault(key, [])
                handler = None
                try:
                    if isinstance(eval(value), list | tuple):
                        handler = type_mapping['list']
                    elif isinstance(eval(value), dict):
                        handler = type_mapping['dict']
                    elif value.isdigit():
                        handler = type_mapping['digit']
                    elif isinstance(eval(value), float):
                        handler = type_mapping['float']
                    else:
                        handler = type_mapping['default']
                except (NameError, SyntaxError, TypeError):
                    # * If value just a string, not a list, dict the eval function will raise NameError, so we need to handle it defaultly.
                    if ',' in value:
                        handler = type_mapping['comma_separated']
                    else:
                        handler = type_mapping['default']

                if handler:
                    data[key] = handler(data, key, value, overwrite)
            else:
                try:
                    logging.debug(value)
                    data[key] = eval(value)
                except (NameError, SyntaxError, TypeError):
                    data[key] = value
        else:
            key = keys.pop(0)
            if key.endswith("[0]"):
                key = key.rstrip("[0]")
                if key not in data:
                    data[key] = [{}]
                next_data = data[key][0]
            else:
                if key not in data:
                    data[key] = {}
                next_data = data[key]
            cls._create_nested_dict(next_data, keys, value, overwrite)
                    
    @classmethod
    def generate_random_float(cls, length_range="[1,10]"):
        if isinstance(length_range, str):
            min_len, max_len = map(int, length_range.strip('[]').split(','))
        elif isinstance(length_range, list):
            min_len, max_len = length_range
            
        if min_len > max_len:
            # * Switch min_len and max_len
            min_len, max_len = max_len, min_len
            
        return random.uniform(min_len, max_len)
    
    @classmethod
    def generate_random_string(cls, length_range="[1,10]", specical_char=False, blacklist=None, whitelist=None):
        if isinstance(length_range, str):
            min_len, max_len = map(int, length_range.strip('[]').split(','))
        elif isinstance(length_range, list):
            min_len, max_len = length_range

        if min_len > max_len:
            # * Switch min_len and max_len
            min_len, max_len = max_len, min_len
        
        if not specical_char:
            alphabet = string.ascii_letters + string.digits
        else:
            alphabet = string.ascii_letters + string.digits + string.punctuation

        if blacklist is not None:
            for char in blacklist:
                alphabet = alphabet.replace(char, '')

        if whitelist is not None:
            for char in whitelist:
                alphabet += char

        length = random.randint(min_len, max_len)
        if length == 0:
            return ""
        else:
            s = ''.join(random.choices(alphabet, k=length))
            return s
        
    @classmethod
    def generate_random_integer(cls, number_range="[1,10]", blacklist=None):
        if isinstance(number_range, str):
            min_value, max_value = map(int, number_range.strip('[]').split(','))
        elif isinstance(number_range, list):
            min_value, max_value = number_range
            
        if min_value > max_value:
            # * Switch min_value and max_value
            min_value, max_value = max_value, min_value

        if blacklist:
            seq = [i for i in range(min_value, max_value+1) if i not in blacklist]
        else:
            seq = range(min_value, max_value+1)

        if not seq:
            raise ValueError("No valid numbers to generate from.")

        random_number = random.choice(seq)

        return random_number
    
    @classmethod
    def generate_random_integer_by_length(cls, length="[1,10]", min_value=0, max_value=9, blacklist=None):
        if isinstance(length, str):
            min_len, max_len = map(int, length.strip('[]').split(','))
        elif isinstance(length, list):
            min_len, max_len = length
        
        if min_len > max_len:
            # * Switch min_len and max_len
            min_len, max_len = max_len, min_len
        
        if blacklist:
            seq = [i for i in range(min_value, max_value+1) if i not in blacklist]
        else:
            seq = range(min_value, max_value+1)

        if not seq:
            raise ValueError("No valid numbers to generate from.")

        length = random.randint(min_len, max_len)
        if length == 0:
            return ""
        else:
            random_number_str = ''.join(str(random.choice(seq)) for _ in range(length))
            return int(random_number_str)
        
    @classmethod
    def generate_random_boolean(cls):
        return random.choice([True, False])
    
    @classmethod
    def generate_random_custom_value(cls, min_len=1, max_len=10, allowed_values=''):
        r = ''
        
        if allowed_values == '':
            return r
        length = random.randint(min_len, max_len)
        for i in range(length):
            r += str(random.choice(allowed_values))
        return r
    
    @classmethod
    def generate_data_from_regex(cls, regex):
        value = genrex.parse(regex)
        return value.random()
    
    @classmethod
    def generate_random_ip(cls):
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))
    
    @classmethod
    def generate_random_ipv6(cls):
        return ':'.join('{:x}'.format(random.randint(0, 2**16-1)) for _ in range(8))
    
    @classmethod
    def generate_random_domain_name(cls):
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 10))) + '.' + random.choice(['com', 'net', 'org', 'vn', 'edu'])
    
    @classmethod
    def generate_random_mac(cls):
        return ':'.join('{:x}'.format(random.randint(0, 255)) for _ in range(6))
    
    @classmethod
    def generate_random_email(cls):
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'mail.com']
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 10))) + '@' + random.choice(domains)
    
    @classmethod
    def generate_random_uuid(cls):
        return str(uuid.uuid4())
    
    @classmethod
    def generate_random_password(cls):
        return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(random.randint(8, 16)))
    
    @classmethod
    def generate_random_int32(cls):
        return random.randint(-2147483648, 2147483647)
    
    @classmethod
    def generate_random_int64(cls):
        return random.randint(-9223372036854775808, 9223372036854775807)
    
    @classmethod
    def generate_random_binary(cls):
        return ''.join(random.choice(['0', '1']) for _ in range(random.randint(8, 16)))
    
    @classmethod
    def generate_random_datetime(cls, start_year=1900, end_year=datetime.now().year):
        # * Random datetime between `start_year` and `end_year`
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)

        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)

        # * Random time between `start_time` and `end_time`
        random_time = datetime.strptime('{}:{}:{}'.format(random.randint(0, 23),
                                                        random.randint(0, 59),
                                                        random.randint(0, 59)), '%H:%M:%S').time()

        # * Concatenate random date and random time
        random_datetime = datetime.combine(random_date, random_time)

        # * Return RFC3339 datetime format
        return random_datetime.isoformat()
