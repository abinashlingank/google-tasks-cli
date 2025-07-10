from colorama import Fore, Style, init
init(autoreset=True)

def create_task(tasklist_name, title, service, due=None, notes=None):
    """
    Creates a new task in the specified task list.

    Args:
        tasklist_name (str): The name of the task list
        title (str): The title of the task
        service: Authenticated Google Tasks API service
        due (str): Due date in YYYY-MM-DD format [optional]
        notes (str): Additional notes for the task [optional]

    Returns:
        dict: The created task object
    """
    try:
        all_lists = service.tasklists().list(maxResults=100).execute().get('items', [])
        matched_list = next((l for l in all_lists if l['title'].lower() == tasklist_name.lower()), None)

        if not matched_list:
            print(f"❌ Task list '{tasklist_name}' not found.")
            return None

        tasklist_id = matched_list['id']

        task = {
            'title': title,
            'notes': notes,
            'due': due,
            'status': 'needsAction'
        }

        created_task = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
        # print(f"✅ Task '{title}' created successfully in '{tasklist_name}'.")
        return created_task

    except Exception as e:
        print("❌ Error creating task:", e)
        return None
    
if __name__ == '__main__':
    from auth import login 
    from read import fetch_task_lists
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
                title = input(Fore.YELLOW + "Enter task title: ")
                due = input(Fore.YELLOW + "Enter due date (YYYY-MM-DD) [optional]: ") or None
                notes = input(Fore.YELLOW + "Enter notes [optional]: ") or None

                create_task(tasklist_name, title, service, due=due, notes=notes)
        else:
            print(Fore.YELLOW + "⚠️ No task lists found.")
    else:
        print(Fore.RED + "❌ Failed to authenticate with Google Tasks API.")
