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
        number_range = "[10,5]"
        
        # Act
        result = DataBuilder.generate_random_integer(number_range=number_range)
        
        # Assert
        assert isinstance(result, int)
        assert result >= 5 and result <= 10

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