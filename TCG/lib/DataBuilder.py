import os
import sys
import re
import json
import random
import string
import exrex
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
            with open(f"./GenerationRule/{operation_id}.json", "r") as f:
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
            with open(f"./DependencyRule/{operation_id}.json", "r") as f:
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
        
        result = {}
        if generation_rules is None:
            return result
        for key in generation_rules:
            keys = key.split('.')
            info = generation_rules[key]
            rule = generation_rules[key]['rule']
            if 'ReadOnly' in info and info['ReadOnly'] == True:
                continue
            elif generation_rules[key]['Default'] != "":
                value = generation_rules[key]['Default']
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
            else:
                value = None
            cls._create_nested_dict(result, keys, value)
        return result
        
    @classmethod
    def _create_nested_dict(cls, data, keys, value):
        # * if keys is last element
        if len(keys) == 1:
            key = keys[0]
           # * if key is array element
            if key.endswith("[0]"):
                key = key.rstrip("[0]")
                if key not in data:
                    data[key] = [{}]
                data[key][0] = value
            else:
                data[key] = value
        else:
            key = keys.pop(0)
            # * if key is array element
            if key.endswith("[0]"):
                key = key.rstrip("[0]")
                if key not in data:
                    data[key] = [{}]
                next_data = data[key][0]
            else:
                if key not in data:
                    data[key] = {}
                next_data = data[key]
            cls._create_nested_dict(next_data, keys, value)
                    
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
        return exrex.getone(regex)
    
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
    def generate_random_string_from_openapi_pattern(cls, pattern):
        return exrex.getone(pattern)
    
    @classmethod
    def generate_random_int32(cls):
        return random.randint(-2147483648, 2147483647)
    
    @classmethod
    def generate_random_int64(cls):
        return random.randint(-9223372036854775808, 9223372036854775807)
    
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
    
class TestDataBuilder:
    # Tests that generate_random_string() returns a string of length 10 without special characters when called with default parameters.
    def test_generate_random_string_default(self):
        # Arrange
        expected_length = 10
        
        # Act
        result = DataBuilder.generate_random_string()
        
        # Assert
        assert len(result) <= expected_length
        assert set(result).issubset(set(string.ascii_letters + string.digits))

    # Tests that generate_random_integer() raises a ValueError when called with min_value > max_value.
    def test_generate_random_integer_min_value_greater_than_max_value(self):
        # Arrange
        min_value = 10
        max_value = 5
        
        # Act & Assert
        with pytest.raises(ValueError):
            DataBuilder.generate_random_integer(min_value=min_value, max_value=max_value)

    # Tests that generate_random_integer() returns an integer of length 1 when called with max_len=1.
    def test_generate_random_integer_max_len_1(self):
        # Arrange
        expected_length = 1
        length_range = "[1,1]"
        
        # Act
        result = DataBuilder.generate_random_integer(length_range)
        
        # Assert
        assert len(str(result)) == expected_length

    # Tests that generate_random_custom_value() returns an empty string when called with an empty allowed_values.
    def test_generate_random_custom_value_empty_allowed_values(self):
        # Arrange
        expected_result = ''
        
        # Act
        result = DataBuilder.generate_random_custom_value(allowed_values='')
        
        # Assert
        assert result == expected_result
        
    def test_generate_random_email(self):
        # Arrange
        expected_result = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        
        # Act
        result = DataBuilder.generate_random_email()
        
        # Assert
        assert expected_result.match(result)
        
    def test_generate_random_password(self):
        # Arrange
        expected_result = re.compile(r"[a-zA-Z0-9_.+-]+")
        
        # Act
        result = DataBuilder.generate_random_password()
        
        # Assert
        assert expected_result.match(result)
        
    # Tests generating a random datetime within the default range (1900 to current year).
    def test_generate_random_datetime_default_range(self):
        # Happy path test for generating a random datetime within the default range
        random_datetime = DataBuilder.generate_random_datetime()
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    # Tests generating a random datetime within a specified range.
    def test_generate_random_datetime_specified_range(self):
        # Happy path test for generating a random datetime within a specified range
        random_datetime = DataBuilder.generate_random_datetime(start_year=2000, end_year=2010)
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    # Tests generating a random datetime at the start and end of the specified range.
    def test_generate_random_datetime_start_end_range(self):
        # Edge case test for generating a random datetime at the start and end of the specified range
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 12, 31)
        start_datetime = datetime.combine(start_date, datetime.min.time()).isoformat()
        end_datetime = datetime.combine(end_date, datetime.max.time()).isoformat()

        random_start_datetime = DataBuilder.generate_random_datetime(start_year=2000, end_year=2001)
        assert isinstance(random_start_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_start_datetime)
        assert start_datetime <= random_start_datetime <= end_datetime

        random_end_datetime = DataBuilder.generate_random_datetime(start_year=2001, end_year=2002)
        assert isinstance(random_end_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_end_datetime)
        assert start_datetime <= random_end_datetime <= end_datetime

    # Tests generating a random datetime with start_year and end_year set to the same year.
    def test_generate_random_datetime_same_year(self):
        # Edge case test for generating a random datetime with start_year and end_year set to the same year
        random_datetime = DataBuilder.generate_random_datetime(start_year=2000, end_year=2000)
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    # Tests for invalid input values and types for start_year and end_year.
    def test_generate_random_datetime_invalid_input(self):
        # Edge case test for invalid input values and types for start_year and end_year
        with pytest.raises(TypeError):
            DataBuilder.generate_random_datetime(start_year='2000', end_year=2010)
        with pytest.raises(ValueError):
            DataBuilder.generate_random_datetime(start_year=2010, end_year=2000)

    # Tests for edge cases where start_year and end_year are very far apart.
    def test_generate_random_datetime_far_apart_years(self):
        # Edge case test for generating a random datetime with start_year and end_year very far apart
        random_datetime = DataBuilder.generate_random_datetime(start_year=1000, end_year=3000)
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    # Tests that the function generates a random float within the range specified by a valid length_range string.
    def test_generate_random_float_with_valid_length_range(self):
        result = DataBuilder.generate_random_float("[1,10]")
        assert isinstance(result, float)
        assert 1 <= result <= 10

    # Tests that the function returns an error message when length_range is an empty string.
    def test_generate_random_float_with_empty_length_range(self):
        with pytest.raises(ValueError):
            DataBuilder.generate_random_float("[]")

    # Tests that the function returns an error message when length_range has only one integer inside the brackets.
    def test_generate_random_float_with_one_integer_in_length_range(self):
        with pytest.raises(ValueError):
            DataBuilder.generate_random_float("[1]")

    # Tests that the function returns an error message when length_range has non-integer values inside the brackets.
    def test_generate_random_float_with_non_integer_values_in_length_range(self):
        with pytest.raises(ValueError):
            DataBuilder.generate_random_float("[1.5,2.5]")

    # Tests that the function returns a float when length_range has two integers inside the brackets.
    def test_generate_random_float_with_negative_integers_in_length_range(self):
        result = DataBuilder.generate_random_float("[-5, -1]")
        assert isinstance(result, float)
        assert -5 <= result <= -1

    # Tests that the function returns a float when length_range has two integers inside the brackets.
    def test_generate_random_float_with_first_integer_greater_than_second_integer(self):
        result = DataBuilder.generate_random_float("[10,1]")
        assert isinstance(result, float)
        assert 1 <= result <= 10