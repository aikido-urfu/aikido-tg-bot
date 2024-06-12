import asyncio
import logging
import os
import shutil
import subprocess
import signal
import pickle
from datetime import datetime
from pathlib import Path
import settings as st


# signal.signal(signal.SIGTERM, handler)
def save_notif_settings():
    with open(Path('.', 'storage', 'notif_settings.pkl'), 'wb') as f:
        pickle.dump(st.notif_settings, f)


def load_notif_settings():
    path = Path('.', 'storage', 'notif_settings.pkl')
    if path.exists():
        with open(path, 'rb') as f:
            st.notif_settings = pickle.load(f)


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


def restart_task(task_name: str):
    logging.info(f'restarting {task_name}')
    res = subprocess.run(f'schtasks /End /TN {task_name} & schtasks /Run /TN {task_name}',
                         capture_output=True, shell=True)
    logging.info(f'restart_code: {str(res.returncode)}')


def kill_task(task_name: str):
    logging.info(f'killing {task_name}')
    res = subprocess.run(f'schtasks /End /TN {task_name}', capture_output=True, shell=True)
    logging.info(f'kill_code: {str(res.returncode)}')


async def repeat(interval, func, *args, **kwargs):
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.

    *args and **kwargs are passed as the arguments to func.
    """
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval),
        )


def copy_and_replace(source_path, destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copy2(source_path, destination_path)


# Converts ISO date string to datetime
def parse_date(date: str) -> datetime:
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
