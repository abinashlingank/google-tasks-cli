from colorama import Fore, Style, init
init(autoreset=True)

def fetch_task_lists(service):
    '''
    Fetches the user's task lists from the Google Tasks API.
    '''
    try:
        tasklists = service.tasklists().list().execute()
        # print(Fore.MAGENTA + "Fetched tasklists successfully.")
        return tasklists
    except Exception as e:
        print(Fore.RED + "❌ Error fetching tasklists: " + str(e))
        return None
    
def list_tasks_by_list_name(tasklist_name, service, show_completed=True):
    '''
    Lists tasks from a specific task list by name.
    '''
    try:
        tasklists = fetch_task_lists(service)
        if not tasklists:
            return []

        matched = next((l for l in tasklists.get('items', []) if l['title'].lower() == tasklist_name.lower()), None)
        if not matched:
            print(Fore.RED + f"❌ Task list '{tasklist_name}' not found.")
            return []

        tasks = service.tasks().list(
            tasklist=matched['id'],
            showCompleted=show_completed,
            showHidden=show_completed
        ).execute().get('items', [])
        
        # print(Fore.MAGENTA + f"Found {len(tasks)} tasks in '{tasklist_name}' list.")
        return tasks

    except Exception as e:
        print(Fore.RED + "❌ Error listing tasks: " + str(e))
        return None
    
def sort_tasks_by_status(tasks):
    '''
    Sorts tasks into completed and pending lists.
    '''
    completed_tasks = [task for task in tasks if task.get('status') == 'completed']
    pending_tasks = [task for task in tasks if task.get('status') != 'completed']
    
    return completed_tasks, pending_tasks
    
if __name__ == '__main__':
    from auth import login  
    service = login()
    
    if service:
        task_lists = fetch_task_lists(service)
        if task_lists:
            print(Fore.MAGENTA + "Task lists fetched successfully.")
            for idx, tasklist in enumerate(task_lists.get('items', [])):
                print(f"{Fore.CYAN}{idx + 1}. {tasklist.get('title', 'No Title')}")

        else:            
            print(Fore.YELLOW + "⚠️ No task lists found.")

        tasklist_idx = int(input(Fore.YELLOW + "Enter the task list number to view tasks: ")) - 1
        if 0 <= tasklist_idx < len(task_lists.get('items', [])):
            tasklist_name = task_lists.get('items', [])[tasklist_idx].get('title', 'No Title')
            tasks = list_tasks_by_list_name(tasklist_name, service)
            if tasks:
                completed_tasks, pending_tasks = sort_tasks_by_status(tasks)
                if pending_tasks:
                    print(Fore.YELLOW + f"Pending Tasks in '{tasklist_name}':")
                    for task in pending_tasks:
                        print(Fore.YELLOW + f"❗ {task.get('title', 'No Title')}")
                if completed_tasks:
                    print(Fore.GREEN + f"Completed Tasks in '{tasklist_name}':")
                    for task in completed_tasks:
                        print(Fore.GREEN + f"✅ {task.get('title', 'No Title')}")
            else:
                print(Fore.YELLOW + "⚠️ No tasks found in this list.")
        else:
            print(Fore.RED + "❌ Invalid task list number.")
    else:
        print(Fore.RED + "❌ Failed to authenticate with Google Tasks API.")