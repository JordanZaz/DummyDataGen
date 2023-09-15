import random
import string
from datetime import datetime, timedelta
from .json.jsonfiles import *
from typing import Dict, Any


def generate_incremental_field(
    counter: int, params: Dict[str, Any], data_type: str
) -> str:
    start = params.get("start", 1)
    step = params.get("step", 1)
    return str(start + counter * step)


def generate_random_value(counter: int, params: Dict[str, Any], data_type: str) -> str:
    data_type_clear = data_type.lower().strip()
    if data_type_clear == "string":
        length = params.get("length", 10)
        allowed_chars = string.ascii_letters + string.digits
        return "".join(random.choice(allowed_chars) for _ in range(length))
    elif data_type_clear == "int":
        return generate_random_number_from_range(params, data_type_clear)
    elif data_type_clear == "float":
        return generate_random_number_from_range(params, data_type_clear)
    else:
        return ""


def generate_random_email(counter: int, params: Dict[str, Any], data_type: str) -> str:
    allowed_chars = string.digits + string.ascii_lowercase
    user_name_length = random.randint(6, 10)
    domain_length = random.randint(5, 8)
    user_name = "".join(random.choice(allowed_chars)
                        for _ in range(user_name_length))
    domain = "".join(random.choice(allowed_chars)
                     for _ in range(domain_length))
    return f"{user_name}@{domain}.com"


def generate_random_date(counter: int, params: Dict[str, Any], data_type: str) -> str:
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2 * 365)
    days = (end_date - start_date).days
    random_days = random.randint(0, days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def generate_iso8601_date(counter: int, params: Dict[str, Any], data_type: str) -> str:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2 * 365)

    # Create random date
    days = (end_date - start_date).days
    random_days = random.randint(0, days)
    random_date = start_date + timedelta(days=random_days)

    # Create random time
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    # Combine date and time
    random_date = random_date.replace(
        hour=random_hour, minute=random_minute, second=random_second
    )
    return random_date.strftime("%Y-%m-%dT%H:%M:%S")


def return_default_value(counter: int, params: Dict[str, Any], data_type: str) -> Any:
    return params.get("value", "")


def generate_random_number_from_range(
    counter: int, params: Dict[str, Any], data_type: str
) -> str:
    min_value = params.get("min", 1)
    max_value = params.get("max", 100)
    if data_type == "int":
        return str(random.randint(min_value, max_value))
    elif data_type == "float":
        return str(random.uniform(min_value, max_value))
    else:
        return ""


def generate_random_dictionary_value(
    counter: int, params: Dict[str, Any], data_type: str
) -> str:
    dictionary_type = params.get("dictionary_type")
    if dictionary_type == "countries":
        return random.choice(countries)["country"]
    elif dictionary_type == "countries_abbreviation":
        return random.choice(countries)["abbreviation"]
    elif dictionary_type == "customers":
        customer_name = random.choice(customers)["name"]
        full_name = (
            f"{customer_name['title']} {customer_name['first']} {customer_name['last']}"
        )
        return full_name
    elif dictionary_type == "companies":
        return random.choice(companies)["name"]
    else:
        return ""
