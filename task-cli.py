from auth import login, logout
from create import create_task
from read import fetch_task_lists, list_tasks_by_list_name, sort_tasks_by_status
from update import update_task_status
from delete import delete_task, clean_up_completed_tasks
from colorama import Fore, Style, init
import sys
from os import system

init(autoreset=True)


def display_task_lists(tasks):
    completed_tasks, pending_tasks = sort_tasks_by_status(tasks)
    task_list_idx = 0

    print(Fore.MAGENTA + Style.DIM + "------------------------------------------------")
    print(Fore.CYAN + Style.BRIGHT + "      Tasky – Type it. Track it. Tackle it.")
    print(Fore.MAGENTA + Style.DIM + "------------------------------------------------")

    if pending_tasks:
        print(Fore.RED + Style.BRIGHT + "Pending Tasks")
        print(Fore.MAGENTA + Style.DIM + "------------------------------------------------")
        for task in pending_tasks:
            print(Fore.YELLOW + f"❗ |{task_list_idx + 1:2}| {task.get('title', 'No Title')}")
            task_list_idx += 1

    if completed_tasks:
        print(Fore.MAGENTA + Style.DIM + "------------------------------------------------")
        print(Fore.GREEN + Style.BRIGHT + "Completed Tasks")
        print(Fore.MAGENTA + Style.DIM + "------------------------------------------------")
        for task in completed_tasks:
            print(Fore.GREEN + Style.DIM + f"✅ |{task_list_idx + 1:2}| {task.get('title', 'No Title')}")
            task_list_idx += 1

    print(Fore.MAGENTA + Style.DIM + "------------------------------------------------")


def clear():
    # system("clear")
    pass


def usage():
    print(Fore.YELLOW + "Usage:")
    print("  tasky.py create             Create a new task")
    print("  tasky.py do [index]         Mark a task as done")
    print("  tasky.py undo [index]       Mark a completed task as pending")
    print("  tasky.py delete [index]     Delete a task (only pending)")
    print("  tasky.py clean              Clean all completed tasks")
    print("  tasky.py logout             Logout from Google account")
    print("  tasky.py                    Show current tasks")


def main():
    service = login()
    task_list = "ToDo"

    if len(sys.argv) == 1:
        clear()
        tasks = list_tasks_by_list_name(task_list, service)
        if tasks:
            display_task_lists(tasks)
        else:
            print(Fore.GREEN + "✅ No tasks left. All done!")
        return

    command = sys.argv[1].lower()
    index = int(sys.argv[2]) - 1 if len(sys.argv) > 2 and sys.argv[2].isdigit() else None

    if command == "logout":
        logout()
        print(Fore.YELLOW + "Logged out successfully.")
        return

    if command == "create":
        title = input(Fore.YELLOW + "Enter task title: " + Fore.RESET)
        due = input(Fore.YELLOW + "Due date (YYYY-MM-DD)? [optional]: " + Fore.RESET) or None
        notes = input(Fore.YELLOW + "Notes? [optional]: " + Fore.RESET) or None
        task = create_task(task_list, title, service, due=due, notes=notes)
        if task:
            print(Fore.GREEN + f"✅ Task '{task.get('title', 'No Title')}' created!")
            tasks = list_tasks_by_list_name(task_list, service)
            display_task_lists(tasks)
        else:
            print(Fore.RED + "❌ Failed to create task.")
        return

    if command in ["do", "undo", "delete"]:
        tasks = list_tasks_by_list_name(task_list, service)
        if not tasks:
            print(Fore.GREEN + "✅ No tasks to show.")
            return

        completed_tasks, pending_tasks = sort_tasks_by_status(tasks)
        # display_task_lists(tasks)

        if index is None:
            try:
                index = int(input(Fore.YELLOW + f"Enter task number to {command}: ")) - 1
            except ValueError:
                print(Fore.RED + "❌ Invalid task number.")
                return

        total_tasks = pending_tasks + completed_tasks

        if not (0 <= index < len(total_tasks)):
            print(Fore.RED + "❌ Task number out of range.")
            return

        task = total_tasks[index]

        if command == "do":
            if task in completed_tasks:
                print(Fore.YELLOW + "⚠️ Task already completed.")
            else:
                if update_task_status(task_list, task['title'], service):
                    print(Fore.GREEN + f"✅ Task '{task['title']}' marked as completed.")
                    tasks = list_tasks_by_list_name(task_list, service)
                    display_task_lists(tasks)

        elif command == "undo":
            if task in pending_tasks:
                print(Fore.YELLOW + "⚠️ Task already pending.")
            else:
                if update_task_status(task_list, task['title'], service):
                    print(Fore.YELLOW + f"❗ Task '{task['title']}' marked as pending.")
                    tasks = list_tasks_by_list_name(task_list, service)
                    display_task_lists(tasks)

        elif command == "delete":
            if task in completed_tasks:
                print(Fore.YELLOW + "⚠️ Cannot delete completed task directly. Use 'clean' instead.")
            else:
                confirm = input(Fore.YELLOW + f"Are you sure to delete '{task['title']}'? (y/N): ").lower()
                if confirm == "y":
                    delete_task(task_list, task['title'], service)
                    print(Fore.GREEN + f"🗑️ Task '{task['title']}' deleted.")
                    tasks = list_tasks_by_list_name(task_list, service)
                    display_task_lists(tasks)
        return

    if command == "clean":
        count = clean_up_completed_tasks(task_list, service)
        print(Fore.GREEN + f"🧹 Cleaned {count} completed tasks.")
        return

    usage()


if __name__ == "__main__":
    main()
