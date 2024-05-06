import os
import shutil
from datetime import datetime


def rus_month(input_string):
    months_translation = {
        "January": "Января",
        "February": "Февраля",
        "March": "Марта",
        "April": "Апреля",
        "May": "Мая",
        "June": "Июня",
        "July": "Июля",
        "August": "Августа",
        "September": "Сентября",
        "October": "Октября",
        "November": "Ноября",
        "December": "Декабря"
    }
    for english_month, russian_translation in months_translation.items():
        if english_month in input_string:
            input_string = input_string.replace(english_month, russian_translation)
            break
    return input_string


def copy_and_replace(source_path, destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copy2(source_path, destination_path)


# Converts ISO date string to datetime
def parse_date(date: str) -> datetime:
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")


