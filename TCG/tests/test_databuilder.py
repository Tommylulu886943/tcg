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

sys.path.append('C:\\pyqt6\\TCG')

from lib.databuilder import DataBuilder

class TestDataBuilder:

    def test_generate_random_string_default(self):
        """
        Test method to verify the behavior of the `generate_random_string` function when generating a random string with default parameters.
        """
        expected_length = 10
        result = DataBuilder.generate_random_string()
        assert len(result) <= expected_length
        assert set(result).issubset(set(string.ascii_letters + string.digits))

    def test_generate_random_integer_min_value_greater_than_max_value(self):
        """
        Test method to verify the behavior of the `generate_random_integer` function when generating a random integer with min_value > max_value.
        """
        min_value = 10
        max_value = 5
        result = DataBuilder.generate_random_integer(number_range=f"[{min_value}, {max_value}]")
        assert isinstance(result, int)
        assert result >= 5 and result <= 10

    def test_generate_random_integer_max_len_1(self):
        """
        Test method to verify the behavior of the `generate_random_integer` function when generating a random integer with max_len=1.
        """
        expected_length = 1
        min_value = 1
        max_value = 1
        result = DataBuilder.generate_random_integer(number_range=f"[{min_value}, {max_value}]")
        assert len(str(result)) == expected_length

    def test_generate_random_custom_value_empty_allowed_values(self):
        """
        Test method to verify the behavior of the `generate_random_custom_value` function when generating a random custom value with empty allowed_values.
        """
        expected_result = ''
        result = DataBuilder.generate_random_custom_value(allowed_values='')
        assert result == expected_result
        
    def test_generate_random_email(self):
        """
        Test method to verify the behavior of the `generate_random_email` function when generating a random email.
        """
        expected_result = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        result = DataBuilder.generate_random_email()
        assert expected_result.match(result)
        
    def test_generate_random_password(self):
        """
        Test method to verify the behavior of the `generate_random_password` function when generating a random password.
        """
        expected_result = re.compile(r"[a-zA-Z0-9_.+-]+")
        result = DataBuilder.generate_random_password()
        assert expected_result.match(result)
        
    def test_generate_random_datetime_default_range(self):
        """
        Test method to verify the behavior of the `generate_random_datetime` function when generating a random datetime within the default range.
        Happy path test for generating a random datetime within the default range
        """
        random_datetime = DataBuilder.generate_random_datetime()
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    def test_generate_random_datetime_specified_range(self):
        """
        Test method to verify the behavior of the `generate_random_datetime` function when generating a random datetime within a specified range.
        Happy path test for generating a random datetime within a specified range
        """
        random_datetime = DataBuilder.generate_random_datetime(start_year=2000, end_year=2010)
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)
        
    def test_generate_random_datetime_start_end_range(self):
        """
        Test method to verify the behavior of the `generate_random_datetime` function when generating a random datetime at the start and end of the specified range.
        Edge case test for generating a random datetime at the start and end of the specified range
        """
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2002, 12, 31)
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

    def test_generate_random_datetime_same_year(self):
        """
        Test method to verify the behavior of the `generate_random_datetime` function when generating a random datetime with start_year and end_year set to the same year.
        Edge case test for generating a random datetime with start_year and end_year set to the same year
        """
        start_year = 2000
        end_year = 2000
        random_datetime = DataBuilder.generate_random_datetime(start_year=start_year, end_year=end_year)
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    def test_generate_random_datetime_invalid_input(self):
        """
        Test method to verify the behavior of the `generate_random_datetime` function when generating a random datetime with invalid input values and types for start_year and end_year.
        Edge case test for invalid input values and types for start_year and end_year
        """
        with pytest.raises(TypeError):
            DataBuilder.generate_random_datetime(start_year='2000', end_year=2010)
            
        with pytest.raises(ValueError):
            DataBuilder.generate_random_datetime(start_year=2010, end_year=2000)

    def test_generate_random_datetime_far_apart_years(self):
        """
        Test method to verify the behavior of the `generate_random_datetime` function when generating a random datetime with start_year and end_year very far apart.
        Edge case test for generating a random datetime with start_year and end_year very far apart
        """
        start_year = 1000
        end_year = 3000
        random_datetime = DataBuilder.generate_random_datetime(start_year=start_year, end_year=end_year)
        assert isinstance(random_datetime, str)
        assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', random_datetime)

    def test_generate_random_float_with_valid_length_range(self):
        """
        Test method to verify the behavior of the `generate_random_float` function when generating a random float with a valid length_range.
        """
        min_value = 1
        max_value = 10
        result = DataBuilder.generate_random_float(f"[{min_value}, {max_value}]")
        assert isinstance(result, float)
        assert 1 <= result <= 10

    def test_generate_random_float_with_empty_length_range(self):
        """
        Test method to verify the behavior of the `generate_random_float` function when generating a random float with an empty length_range.
        """
        with pytest.raises(ValueError):
            DataBuilder.generate_random_float("[]")

    def test_generate_random_float_with_one_integer_in_length_range(self):
        """
        Test method to verify the behavior of the `generate_random_float` function when generating a random float with one integer in the length_range.
        """
        with pytest.raises(ValueError):
            min_value = 1
            DataBuilder.generate_random_float(f"[{min_value}]")

    def test_generate_random_float_with_non_integer_values_in_length_range(self):
        """
        Test method to verify the behavior of the `generate_random_float` function when generating a random float with non-integer values in the length_range.
        """
        with pytest.raises(ValueError):
            min_value = 1.5
            max_value = 2.5
            DataBuilder.generate_random_float(f"[{min_value}, {max_value}]")
            
    def test_generate_random_float_with_negative_integers_in_length_range(self):
        """
        Test method to verify the behavior of the `generate_random_float` function when generating a random float with negative integers in the length_range.
        """
        min_value = -5
        max_value = -1
        result = DataBuilder.generate_random_float(f"[{min_value}, {max_value}]")
        assert isinstance(result, float)
        assert -5 <= result <= -1

    def test_generate_random_float_with_first_integer_greater_than_second_integer(self):
        """
        Test method to verify the behavior of the `generate_random_float` function when generating a random float with the first integer greater than the second integer in the length_range.
        """
        min_value = 10
        max_value = 1
        result = DataBuilder.generate_random_float(f"[{min_value}, {max_value}]")
        assert isinstance(result, float)
        assert 1 <= result <= 10
        
    def test_create_nested_dict_single_key(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with a single key and value.
        """
        data = {}
        keys = ["key"]
        value = "value"
        expected_output = {"key": "value"}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output

    def test_create_nested_dict_single_key_array(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with a single key and an array value.
        """
        data = {}
        keys = ["key[0]"]
        value = "value1"
        expected_output = {"key": ["value1"]}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output

    def test_create_nested_dict_single_key_array_multiple_values(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with a single key and an array value containing multiple values.
        """
        data = {}
        keys = ["key[0]"]
        value = "value1, value2, value3"
        expected_output = {"key": ["value1", "value2", "value3"]}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output

    def test_create_nested_dict_single_key_array_multiple_values_numeric(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with a single key and an array value containing multiple numeric values with whitespace.
        """
        data = {}
        keys = ["key[0]"]
        value = "1, 2, 3"  # With whitespace
        expected_output = {"key": [1, 2, 3]}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output
    
    def test_create_nested_dict_single_key_array_multiple_values_numeric_without_whitespace(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with a single key and an array value containing multiple numeric values without whitespace.
        """
        data = {}
        keys = ["key[0]"]
        value = "1,2,3"  # No whitespace
        expected_output = {"key": [1, 2, 3]}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output

    def test_create_nested_dict_multiple_keys(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with multiple keys.
        """
        data = {}
        keys = ["key1", "key2"]
        value = "value"
        expected_output = {"key1": {"key2": "value"}}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output

    def test_create_nested_dict_multiple_keys_array(self):
        """
        Test method to verify the behavior of the `_create_nested_dict` function when creating a nested dictionary with multiple keys and an array value.
        """
        data = {}
        keys = ["key1[0]", "key2"]
        value = "value"
        expected_output = {"key1": [{"key2": "value"}]}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output
        
    def test_create_nested_dict_list(self):
        # BUG
        data = {}
        keys = ["key1[0]"]
        value = ["value1", "value2"]
        expected_output = {"key1": ["value1", "value2"]}
        DataBuilder._create_nested_dict(data, keys, value)
        assert data == expected_output