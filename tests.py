import unittest
import datetime
import unittest.mock as mock
from worklog import Entry

from peewee import *

import worklog

test_entry = {
    "task": "Beau test",
    "date": datetime.datetime.strptime("24-08-1992", worklog.DATE_FORMAT),
    "employee": "Ben Employee test",
    "duration": 20,
    "notes": "Some test notes",
}

test_entry_2 = {
    "task": "Task two",
    "date": datetime.datetime.strptime("23-06-2001", worklog.DATE_FORMAT),
    "employee": "Second employee",
    "duration": 110,
    "notes": "Notes test",
}

test_entries = [test_entry, test_entry_2]

# string with zero chars for testing
zero_string = ""

# A string over 255 chars for testing errors
bad_string = """Lorem ipsum dolor sit amet, consectetur adipiscing
 elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
 Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi 
 ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
 in voluptate velit esse cillum dolore eu fugiat nulla pariatur."""


class WorkLogTests(unittest.TestCase):
    @staticmethod
    def create_entries():
        worklog.Entry.create(
            task=test_entry["task"],
            date=test_entry["date"],
            emplyoee=test_entry["employee"],
            duration=test_entry["duration"],
            notes=test_entry["notes"]
        )

        worklog.Entry.create(
            task=test_entry_2["task"],
            date=test_entry_2["date"],
            emplyoee=test_entry_2["employee"],
            duration=test_entry_2["duration"],
            notes=test_entry_2["notes"]
        )

    # test validation of task info

    def test_validate_task_name(self):
        with unittest.mock.patch('builtins.input', side_effect=["Beau test"],
                                 return_value=test_entry["task"]):
            assert worklog.validate_task_name(bad_string) == test_entry["task"]

    def test_validate_task_name_zero(self):
        with unittest.mock.patch('builtins.input', side_effect=["Beau test"],
                                 return_value=test_entry["task"]):
            assert worklog.validate_task_name(zero_string) == test_entry["task"]

    def test_validate_date(self):
        with unittest.mock.patch('builtins.input', side_effect=["24-08-1992"],
                                 return_value=test_entry["date"]):
            assert worklog.validate_task_date("string") == test_entry["date"]

    def test_validate_task_employee(self):
        with unittest.mock.patch('builtins.input', side_effect=["Ben Employee test"],
                                 return_value=test_entry["employee"]):
            assert worklog.validate_task_employee(bad_string) == test_entry["employee"]

    def test_validate_task_employee_zero(self):
        with unittest.mock.patch('builtins.input', side_effect=["Ben Employee test"],
                                 return_value=test_entry["employee"]):
            assert worklog.validate_task_employee(zero_string) == test_entry["employee"]

    def test_validate_task_duration(self):
        with unittest.mock.patch('builtins.input', side_effect=[20],
                                 return_value=test_entry["duration"]):
            assert worklog.validate_task_duration("non convertible string") == test_entry["duration"]

    def test_validate_task_notes(self):
        with unittest.mock.patch('builtins.input', side_effect=["Some test notes"],
                                 return_value=test_entry["notes"]):
            assert worklog.validate_task_notes(bad_string) == test_entry["notes"]


if __name__ == '__main__':
    unittest.main()
