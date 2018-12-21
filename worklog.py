from collections import OrderedDict
import datetime
import os
import sys

from peewee import *

db = SqliteDatabase('work_log.db')

DATE_FORMAT = "%d-%m-%Y"


class Entry(Model):
    task = CharField(max_length=255)
    date = DateTimeField()
    employee = CharField(max_length=255)
    duration = IntegerField()
    notes = CharField(max_length=255)

    class Meta:
        database = db


def clear():
    """Clear the screen in the command prompt."""
    os.system('cls' if os.name == 'nt' else 'clear')


def quit():
    """ Quit Program"""
    clear()
    input("Goodbye!")
    clear()
    sys.exit()


def initialize():
    """ Create database and table if they don't exist"""
    db.connect()
    db.create_tables([Entry], safe=True)


def menu_loop():
    """Show the menu"""
    clear()
    choice = None
    while choice != 'q':
        print("Enter 'q' to quit.")
        # Value is a function
        for key, value in menu.items():
            print("{}) {}".format(key, value.__doc__))
        choice = input("Action: ").lower().strip()

        if choice in menu:
            return menu[choice]()


def search_menu():
    """ Search menu """
    entries = fetch_tasks()
    clear()
    if len(entries) == 0:
        input("Sorry. No entries to search. Press any button to go back to "
              "the Main Menu and add some tasks.")
        clear()
        menu_loop()
    else:
        search_choice = None
        while search_choice != 'q':
            print("Enter 'q' to quit.")
            # Value is a function
            for key, value in search_menu.items():
                print("{}) {}".format(key, value.__doc__))
            search_choice = input("Action: ").lower().strip()

            if search_choice in search_menu:
                search_menu[search_choice]()


def add_entry():
    """ Add an entry """
    clear()
    print("Add an entry")
    # Retieve and validate task information
    task = input("Please enter the name of your task:  ")
    task = validate_task_name(task)
    clear()
    date = input("Please input a date of the task in DD-MM-YYYY format:  ")
    date = validate_task_date(date)
    clear()
    employee = input("Please enter the name of the employee who "
                     "carried out this task:  ")
    employee = validate_task_employee(employee)
    clear()
    duration = input("Please enter a duration of the task "
                     "in minutes:  ")
    duration = validate_task_duration(duration)
    clear()
    notes = input("Please enter your task notes (optional) - "
                  "otherwise press enter to save task:  ")
    notes = validate_task_notes(notes)
    # Add to database
    add_to_database(task, date, employee, duration, notes)


def add_to_database(task, date, employee, duration, notes):
    Entry.create(task=task, date=date, employee=employee,
                 duration=duration, notes=notes)
    clear()
    input("Entry Saved! Press any button to continue.")
    menu_loop()


def validate_task_name(task):
    """ Validate task name """
    while True:
        if len(task) == 0:
            print("Task name not valid. Must not be blank.")
            task = input("Please try again:  ")
            continue
        if len(task) > 255:
            print("Task Name too long.")
            task = input("Please try again:  ")
            continue
        else:
            return task


def validate_task_date(date):
    """ Validates the date """
    while True:
        try:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            print("Sorry, not a valid date.")
            date = input("Please try again. Enter a date "
                         "in DD-MM-YYYY format:  ")
            continue
        else:
            return date


def validate_task_employee(employee):
    """ Retrieve task employee """
    while True:
        if len(employee) == 0:
            print("Employee not valid. Must not be blank.")
            employee = input("Please try again:  ")
            continue
        if len(employee) > 255:
            print("Employee Name too long.")
            employee = input("Please try again:  ")
            continue
        else:
            return employee


def validate_task_duration(duration):
    """ Validate task duration """
    while True:
        try:
            duration = int(duration)
        except ValueError:
            print("Not a valid number of minutes.")
            duration = input("Please try again:  ")
            continue
        else:
            return duration


def validate_task_notes(notes):
    """ Validates task notes """
    while True:
        if len(notes) > 255:
            print("Task Notes too long.")
            notes = input("Please try again:  ")
            continue
        else:
            return notes


def fetch_tasks():
    """ Select all tasks from database """
    entries = Entry.select().order_by(Entry.date.desc())
    return entries


def display_entries(entries):
    """ Displays the results """
    clear()
    index = 0
    while True:
        pagination = ['[E]dit entry', '[D]elete entry', '[N]ext',
                      '[P]revious', '[B]ack to main menu.']
        entry = entries[index]
        print("Task Name: {}\nDate: {} \nEmployee: "
              "{}\nDuration: {} minutes\n"
              "Notes: {}\n".format(entry.task,
                                   entry.date.strftime(DATE_FORMAT),
                                   entry.employee,
                                   entry.duration,
                                   entry.notes))
        if index == 0:
            pagination.remove("[P]revious")
        if index == len(entries) - 1:
            pagination.remove("[N]ext")

        options = ', '.join(pagination)
        print("Entry {} of {}.".format(index + 1, len(entries)))
        print(options)
        navigation = input(">")

        # Controls index count and continues in loop
        if navigation.lower() in "npbed" and navigation.upper() in \
                options:
            if navigation.lower() == "n":
                clear()
                index += 1
                continue
            elif navigation.lower() == "p":
                clear()
                index -= 1
                continue
            elif navigation.lower() == "b":
                menu_loop()
                break
            elif navigation.lower() == "e":
                edit_task(index, entries)
                break
            elif navigation.lower() == "d":
                delete_task(index, entries)
                break
        else:
            clear()
            print("Sorry, input not recognised. Please try again.\n")
            continue


def view_all_tasks():
    """ View all tasks """
    entries = fetch_tasks()
    display_entries(entries)


def get_unique_dates(entries):
    """ Find unique dates to display """
    unique_dates = []
    for entry in entries:
        date = entry.date.strftime(DATE_FORMAT)
        if date not in unique_dates:
            unique_dates.append(date)
    return unique_dates


def get_unique_employees(entries):
    """ Find all the unique employees to display """
    unique_employees = []
    for entry in entries:
        employee = entry.employee
        if employee not in unique_employees:
            unique_employees.append(employee)
    return unique_employees


def search_by_employee():
    """ Search by employee name"""
    entries = fetch_tasks()
    unique_employees = get_unique_employees(entries)
    employee_matches = []
    clear()
    while True:
        print("EMPLOYEES")
        for employee in unique_employees:
            print(employee)
        employee_search = input("\nPlease enter a name of an "
                                "employee to search by:  ")
        employee_search = validate_task_employee(employee_search)
        entries = entries.where(Entry.employee.contains(employee_search))
        if len(entries) == 0:
            clear()
            print("Sorry. None found. Please try again")
            continue
        else:
            for entry in entries:
                employee_match = entry.employee.strip()
                if employee_match not in employee_matches:
                    employee_matches.append(employee_match)
            if len(employee_matches) > 1:
                clear()
                while True:
                    print("EMPLOYEES THAY MATCH YOUR SEARCH:")
                    for employee_match in employee_matches:
                        print(employee_match)
                    employee_input = input("\nPlease choose an "
                                           "employee:  ").strip()
                    if employee_input in employee_matches:
                        entries = \
                            Entry.select().order_by(Entry.date.desc())\
                            .where(Entry.employee == employee_input)
                        display_entries(entries)
                    else:
                        clear()
                        print("Employee not found in list. Please try again.")
                        continue
            else:
                entries = Entry.select().order_by(Entry.date.desc()).where(
                    Entry.employee == employee_match)
                display_entries(entries)


def search_by_date():
    """ Search by a date """
    clear()
    results = []
    while True:
        entries = fetch_tasks()
        unique_dates = get_unique_dates(entries)
        print("Dates with tasks.")
        for date in unique_dates:
            print(date)
        search_date = input("Please enter a date in DD-MM-YYYY format:  ")
        try:
            datetime.datetime.strptime(search_date, DATE_FORMAT)
        except ValueError:
            print("Sorry, {} is not a valid date.".format(search_date))
            continue
        else:
            for entry in entries:
                if entry.date.strftime(DATE_FORMAT) == search_date:
                    results.append(entry)

            if len(results) == 0:
                clear()
                print("{} not found. "
                      "Please try again.".format(search_date))
                continue
            else:
                clear()
                display_entries(results)


def search_by_date_range():
    """ Search by a range of two dates """
    clear()
    results = []
    while True:
        entries = fetch_tasks()
        start_date = input("Search between two dates.\n"
                           "Enter the start date to begin in "
                           "DD-MM-YYYY format:   ")
        try:
            start_date = \
                datetime.datetime.strptime(start_date, DATE_FORMAT)
        except ValueError:
            print("Sorry, {} is not a valid date.".format(start_date))
            continue
        else:
            end_date = input("Enter the end date in "
                             "DD-MM-YYYY format:   ")
            try:
                end_date = \
                    datetime.datetime.strptime(end_date, DATE_FORMAT)
            except ValueError:
                print("Sorry, {} is not a valid date.".format(end_date))
                continue
            if start_date > end_date:
                clear()
                print("Sorry. the start date cannot be after the end "
                      "date. Please try again.")
                continue
            else:
                for entry in entries:
                    if entry.date.timestamp() >= start_date.timestamp() and\
                            entry.date.timestamp() <= end_date.timestamp():
                        results.append(entry)
                if len(results) == 0:
                    print("Sorry. No matches. Please try again.")
                    continue
                else:
                    clear()
                    display_entries(results)
                    break


def search_by_term():
    """ Search by any term """
    clear()
    while True:
        entries = fetch_tasks()
        print("Search by Keyword\n")
        search_term = input("Enter a search term: ")
        entries = entries.where(
            Entry.task.contains(search_term) or
            Entry.notes.contains(search_term)
        )
        if len(entries) == 0:
            clear()
            print("Sorry. No matches. Please try again.")
            continue
        else:
            display_entries(entries)


def search_by_time_spent():
    """ Search by time spent on task """
    clear()
    while True:
        entries = fetch_tasks()
        print("Search by Time Spent\n")
        time_search = input("Enter a duration to search (minutes):  ")
        time_search = validate_task_duration(time_search)
        entries = entries.where(
           Entry.duration == int(time_search)
        )
        if len(entries) == 0:
            clear()
            print("Sorry. No matches. Please try again.")
            continue
        else:
            display_entries(entries)


def edit_task(index, entries):
    """ Edit a task """
    entry = entries[index]
    clear()
    while True:
        print("a) Task name: {}\n"
              "b) Date: {}\n"
              "c) Employee: {}\n"
              "d) Duration: {} minutes\n"
              "e) Notes: {}\n"
              "\n\nm) Back to menu\n"
              .format(entry.task, entry.date, entry.employee,
                      entry.duration, entry.notes))
        edit_choice = input("Please select which part of the task to edit:  ")

        if edit_choice.lower() == 'a':
            task = input("Please enter a new task name:  ")
            task = validate_task_name(task)
            entry.task = task
            entry.save()
        elif edit_choice.lower() == 'b':
            date = input("Please enter a new date in the DD-MM-YYYY format:  ")
            date = validate_task_date(date)
            entry.date = date
            entry.save()
        elif edit_choice.lower() == 'c':
            employee = input("Please enter a new employee:  ")
            employee = validate_task_employee(employee)
            entry.employee = employee
            entry.save()
        elif edit_choice.lower() == 'd':
            duration = input("Please enter a new duration (minutes):  ")
            duration = validate_task_duration(duration)
            entry.duration = duration
            entry.save()
        elif edit_choice.lower() == 'e':
            notes = input("Please enter new notes (optional):  ")
            notes = validate_task_notes(notes)
            entry.notes = notes
            entry.save()
        elif edit_choice.lower() == 'm':
            menu_loop()
        else:
            clear()
            print("Choice not recognised. Please try again.")
            continue

        clear()
        input("Entry updated! Press any button to continue.")
        clear()
        continue


def delete_task(index, entries):
    """ Delete a task """
    entry = entries[index]

    clear()
    confirm_delete = input("Are you sure you want to delete this "
                           "entry? [Y/N]  ")

    if confirm_delete.lower() == 'y':
        clear()
        entry.delete_instance()
        input("Entry deleted. Press any button to return.")
    else:
        clear()
        input("Entry not deleted. Press any button to return to "
              "the main menu.")
        menu_loop()


menu = OrderedDict([
    ('a', add_entry),
    ('b', search_menu),
    ('c', quit)

])

search_menu = OrderedDict([
    ('a', view_all_tasks),
    ('b', search_by_employee),
    ('c', search_by_date),
    ('d', search_by_date_range),
    ('e', search_by_time_spent),
    ('f', search_by_term)

])

if __name__ == '__main__':
    initialize()
    menu_loop()
