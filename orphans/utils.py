# utils.py
from datetime import datetime


def get_school_year_choices():
    current_year = datetime.now().year
    return [(f"{year}-{year+1}", f"{year}-{year+1}") for year in range(current_year-1, current_year+1)]


def get_school_years(back=5, forward=5):
    current_year = datetime.datetime.now().year
    start_year = current_year - back
    end_year = current_year + forward
    school_years = [f"{year}-{year+1}" for year in range(start_year, end_year)]
    return school_years
