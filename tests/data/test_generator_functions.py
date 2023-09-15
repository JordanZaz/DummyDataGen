import pytest
from unittest.mock import patch
from data.generator_functions import *


# generate_incremental_field
def test_generate_incremental_field():
    assert generate_incremental_field(0, {}, "int") == "1"
    assert generate_incremental_field(
        0, {"start": 10, "step": 2}, "int") == "10"
    assert generate_incremental_field(
        1, {"start": 10, "step": 2}, "int") == "12"
    assert generate_incremental_field(
        2, {"start": 10, "step": 2}, "int") == "14"


# generate_random_value
def test_generate_random_value():
    with patch(
        "data.generator_functions.generate_random_number_from_range"
    ) as mock_generate_random_number_from_range:
        mock_generate_random_number_from_range.return_value = "42"
        assert isinstance(generate_random_value(0, {}, "string"), str)
        mock_generate_random_number_from_range.assert_not_called()

        assert isinstance(generate_random_value(0, {}, "int"), str)
        mock_generate_random_number_from_range.assert_called_with({}, "int")

        assert isinstance(generate_random_value(0, {}, "float"), str)
        mock_generate_random_number_from_range.assert_called_with({}, "float")


# generate_random_email
def test_generate_random_email():
    email = generate_random_email(0, {}, "string")
    assert isinstance(email, str)
    assert "@" in email
    assert "." in email


# generate_random_date
def test_generate_random_date():
    date = generate_random_date(0, {}, "string")
    assert isinstance(date, str)
    assert len(date) == 10
    assert date.count("-") == 2


# generate_iso8601_date
def test_generate_iso8601_date():
    iso_date = generate_iso8601_date(0, {}, "string")
    assert isinstance(iso_date, str)
    assert len(iso_date) == 19
    assert iso_date.count("-") == 2
    assert iso_date.count("T") == 1
    assert iso_date.count(":") == 2


# return_default_value
def test_return_default_value():
    assert return_default_value(0, {"value": "default"}, "string") == "default"
    assert return_default_value(0, {}, "string") == ""


# generate_random_number_from_range
def test_generate_random_number_from_range():
    number = generate_random_number_from_range(
        0, {"min": 1, "max": 100}, "int")
    assert isinstance(number, str)
    assert number.isdigit()

    float_number = generate_random_number_from_range(
        0, {"min": 1, "max": 100}, "float")
    assert isinstance(float_number, str)
    assert "." in float_number


# generate_random_dictionary_value
def generate_random_dictionary_value(counter, params, data_type):
    dictionary_type = params.get("dictionary_type")
    if dictionary_type == "countries":
        return random.choice(countries)["country"]
    elif dictionary_type == "countries_abbreviation":
        return random.choice(countries)["abbreviation"]
    elif dictionary_type == "customers":
        customer_name = random.choice(customers)
        return f"{customer_name['name']['first']} {customer_name['name']['last']}"
    elif dictionary_type == "companies":
        return random.choice(companies)["name"]
    else:
        return ""
