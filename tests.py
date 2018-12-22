import unittest
from worklog import Entry
import unittest.mock as mock
from peewee import *
import worklog
import datetime

MODELS = [Entry]

test_entry = {
    "task": "Beau test",
    "date": datetime.datetime.strptime("24-08-1992", worklog.DATE_FORMAT),
    "employee": "Ben Employee test",
    "duration": 20,
    "notes": "Some test notes",
}

test_entry_date = {
    "task": "Beau test",
    "date": "24-08-1992",
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

zero_string = ""

# A string over 255 chars for testing errors
bad_string = """Lorem ipsum dolor sit amet, consectetur adipiscing
 elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
 Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
 ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit
 in voluptate velit esse cillum dolore eu fugiat nulla pariatur."""


# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)

        Entry.create(task=test_entry['task'],
                     date=test_entry['date'],
                     employee=test_entry['employee'],
                     duration=test_entry['duration'],
                     notes=test_entry['notes'])

        Entry.create(task=test_entry_2['task'],
                     date=test_entry_2['date'],
                     employee=test_entry_2['employee'],
                     duration=test_entry_2['duration'],
                     notes=test_entry_2['notes'])

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    # Test validate info

    def test_validate_task_name(self):
        with unittest.mock.patch('builtins.input', side_effect=["Beau test"],
                                 return_value=test_entry["task"]):
            assert worklog.validate_task_name(bad_string) == test_entry["task"]

    def test_validate_task_name_zero(self):
        with unittest.mock.patch('builtins.input', side_effect=["Beau test"],
                                 return_value=test_entry["task"]):
            assert worklog.validate_task_name(zero_string) == \
                   test_entry["task"]

    def test_validate_date(self):
        with unittest.mock.patch('builtins.input', side_effect=["24-08-1992"],
                                 return_value=test_entry["date"]):
            assert worklog.validate_task_date("string") == test_entry["date"]

    def test_validate_task_employee(self):
        with unittest.mock.patch('builtins.input',
                                 side_effect=["Ben Employee test"],
                                 return_value=test_entry["employee"]):
            assert worklog.validate_task_employee(bad_string) == \
                   test_entry["employee"]

    def test_validate_task_employee_zero(self):
        with unittest.mock.patch('builtins.input',
                                 side_effect=["Ben Employee test"],
                                 return_value=test_entry["employee"]):
            assert worklog.validate_task_employee(zero_string) == \
                   test_entry["employee"]

    def test_validate_task_duration(self):
        with unittest.mock.patch('builtins.input', side_effect=[20],
                                 return_value=test_entry["duration"]):
            assert worklog.validate_task_duration("non convertible string") \
                   == test_entry["duration"]

    # Test initialize

    def test_initialize(self):
        expected = True
        actual = worklog.initialize()
        self.assertEqual(actual, expected)

    def test_clear(self):
        """testing clear function calls os.system"""
        with unittest.mock.patch('worklog.os') as Mocked_os:
            worklog.clear()
            Mocked_os.system.assert_called_once()

    # Add to log

    def test_get_unique_employees(self):
        expected = ['Terry', 'Chris', 'Ben']
        entries = [Entry(employee='Terry'),
                   Entry(employee='Chris'),
                   Entry(employee='Ben')]
        actual = worklog.get_unique_employees(entries)
        self.assertEqual(actual, expected)

    def test_get_unique_dates(self):
        expected = ['24-08-1992', '24-09-1996', '01-01-2001']
        entries = [Entry(date=datetime.datetime.strptime("24-08-1992",
                                                         worklog.DATE_FORMAT)),
                   Entry(date=datetime.datetime.strptime("24-09-1996",
                                                         worklog.DATE_FORMAT)),
                   Entry(date=datetime.datetime.strptime("01-01-2001",
                                                         worklog.DATE_FORMAT))]
        actual = worklog.get_unique_dates(entries)
        self.assertEqual(actual, expected)

    def test_fetch_tasks(self):
        expected = 2
        actual = worklog.fetch_tasks()
        self.assertEqual(len(actual), expected)

    def test_search_by_term(self):
        expected = 1
        entries = Entry.select()
        with unittest.mock.patch('builtins.input',
                                 side_effect=["Beau test"]):
            actual = worklog.search_by_term(entries)
            self.assertEqual(actual.select().count(), expected)

    def test_search_by_employee(self):
        expected = 1
        entries = Entry.select()
        with unittest.mock.patch('builtins.input',
                                 side_effect=["Ben Employee test"]):
            actual = worklog.search_by_employee(entries)
            self.assertEqual(actual.select().count(), expected)

    def test_search_by_date(self):
        expected = 1
        entries = Entry.select()
        with unittest.mock.patch('builtins.input',
                                 ide_effect=["24-08-1992"]):
            actual = worklog.search_by_date(entries)
            self.assertEqual(len(actual), expected)

    def test_search_by_date_range(self):
        expected = 1
        entries = Entry.select()
        with unittest.mock.patch('builtins.input',
                                 side_effect=["24-08-1991", "24-08-1997"]):
            actual = worklog.search_by_date_range(entries)
            self.assertEqual(len(actual), expected)

    def test_search_by_duration(self):
        expected = 1
        entries = Entry.select()
        with unittest.mock.patch('builtins.input', side_effect=["20"]):
            actual = worklog.search_by_time_spent(entries)
            self.assertEqual(len(actual), expected)

    def test_view_all_tasks(self):
        expected = 2
        entries = Entry.select()
        with unittest.mock.patch('builtins.input', side_effect=[""]):
            actual = worklog.view_all_tasks(entries)
            self.assertEqual(len(actual), expected)

    def test_delete_entry(self):
        entries = Entry.select()
        index = 0

        with mock.patch('builtins.input', side_effect=["y", ""]):
            worklog.delete_task(index, entries)
            self.assertEqual(Entry.select().count(), 1)


if __name__ == '__main__':
    unittest.main()
