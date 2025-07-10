from colorama import Fore, Style, init
init(autoreset=True)
import os

def delete_task(tasklist_name, task_title, service):
    """
    Deletes a task from the specified task list by its title.

    Args:
        tasklist_name (str): The name of the task list
        task_title (str): The title of the task to delete
        service: Authenticated Google Tasks API service

    Returns:
        bool: True if the task was deleted successfully, False otherwise
    """
    try:
        all_lists = service.tasklists().list(maxResults=100).execute().get('items', [])
        matched_list = next((l for l in all_lists if l['title'].lower() == tasklist_name.lower()), None)

        if not matched_list:
            print(f"❌ Task list '{tasklist_name}' not found.")
            return False

        tasklist_id = matched_list['id']

        tasks = service.tasks().list(
            tasklist=tasklist_id,
            showCompleted=True,
            showHidden=True
        ).execute().get('items', [])

        task = next((t for t in tasks if t.get('title', '').lower() == task_title.lower()), None)

        if not task:
            print(f"❌ Task '{task_title}' not found in '{tasklist_name}'.")
            return False

        service.tasks().delete(tasklist=tasklist_id, task=task['id']).execute()
        # print(f"✅ Task '{task_title}' deleted successfully from '{tasklist_name}'.")
        return True

    except Exception as e:
        print("❌ Error deleting task:", e)
        return False
    
def clean_up_completed_tasks(tasklist_name, service):
    """
    Deletes all completed tasks from the specified task list.

    Args:
        tasklist_name (str): The name of the task list
        service: Authenticated Google Tasks API service

    Returns:
        int: Number of completed tasks deleted
    """
    try:
        all_lists = service.tasklists().list(maxResults=100).execute().get('items', [])
        matched_list = next((l for l in all_lists if l['title'].lower() == tasklist_name.lower()), None)

        if not matched_list:
            print(f"❌ Task list '{tasklist_name}' not found.")
            return 0

        tasklist_id = matched_list['id']
        # tasks = service.tasks().list(tasklist=tasklist_id, showCompleted=True).execute().get('items', [])
        tasks = service.tasks().list(
            tasklist=tasklist_id,
            showCompleted=True,
            showHidden=True
        ).execute().get('items', [])

        completed_tasks = [t for t in tasks if t.get('status') == 'completed']
        # writing the completed tasks to a file for future reference
        if os.path.exists('completed_tasks.txt'):
            with open('completed_tasks.txt', 'a') as f:
                for task in completed_tasks:
                    f.write(f"{task.get('title', 'No Title')} (ID: {task['id']})\n")
        else:
            with open('completed_tasks.txt', 'w') as f:
                f.write(f"Completed tasks from '{tasklist_name}':\n")
                f.write("------------------------------------------------\n")
                f.write("Task Title (ID)\n")
                for task in completed_tasks:
                    f.write(f"{task.get('title', 'No Title')} (ID: {task['id']})\n")
        
        for task in completed_tasks:
            service.tasks().delete(tasklist=tasklist_id, task=task['id']).execute()
        
        print(f"✅ Deleted {len(completed_tasks)} completed tasks from '{tasklist_name}'.")
        return len(completed_tasks)

    except Exception as e:
        print("❌ Error cleaning up completed tasks:", e)
        return 0
    
if __name__ == '__main__':
    from auth import login
    from read import fetch_task_lists
    from read import list_tasks_by_list_name
    from read import sort_tasks_by_status
    service = login()
    if service:
        task_lists = fetch_task_lists(service)
        if task_lists:
            print(Fore.MAGENTA + "Task lists fetched successfully.")
            for idx, tasklist in enumerate(task_lists.get('items', [])):
                print(f"{Fore.CYAN}{idx + 1}. {tasklist.get('title', 'No Title')}")

            tasklist_idx = int(input(Fore.YELLOW + "Select task list by number: ")) - 1
            if 0 <= tasklist_idx < len(task_lists.get('items', [])):
                tasklist_name = task_lists.get('items', [])[tasklist_idx].get('title', 'No Title')
                tasks = list_tasks_by_list_name(tasklist_name, service)
            if tasks:
                completed_tasks, pending_tasks = sort_tasks_by_status(tasks)
                task_list_idx = 0
                if pending_tasks:
                    print(Fore.YELLOW + f"Pending Tasks in '{tasklist_name}':")
                    for task in pending_tasks:
                        print(Fore.YELLOW + f"❗| {task_list_idx + 1}| {task.get('title', 'No Title')}")
                        task_list_idx += 1
                if completed_tasks:
                    print(Fore.GREEN + f"Completed Tasks in '{tasklist_name}':")
                    for task in completed_tasks:
                        print(Fore.GREEN + f"✅ | {task_list_idx + 1}| {task.get('title', 'No Title')}")
                        task_list_idx += 1
                task_idx = int(input(Fore.YELLOW + "Enter the task number to delete: ")) - 1
                if 0 <= task_idx < len(pending_tasks):
                    task_title = pending_tasks[task_idx].get('title', 'No Title')
                    print(Fore.YELLOW + f"Are you sure you want to delete the task '{task_title}'? (Y/[N]): ", end="")
                    confirm = input().strip().lower() or None
                    if confirm == 'y' or confirm == 'yes':
                        delete_task(tasklist_name, task_title, service)
                elif completed_tasks:
                    print(Fore.YELLOW + "You can only delete pending tasks.")
                    clean_up = input(Fore.YELLOW + "Do you want to clean up completed tasks? (Y/[N]): ").strip().lower() or None
                    if clean_up == 'y' or clean_up == 'yes':
                        clean_up_completed_tasks(tasklist_name, service)