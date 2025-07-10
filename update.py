from colorama import Fore, Style, init
init(autoreset=True)

def update_task_status(tasklist_name, task_title, service):
    """
    Updates the status of a task in the given task list by its title.

    Args:
        tasklist_name (str): The name of the task list
        task_title (str): The title of the task to update
        service: Authenticated Google Tasks API service

    Returns:
        True if marked as completed, False otherwise
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

        if task['status'] == 'completed':
            task['status'] = 'needsAction'
            # print(f"❗ Task '{task_title}' marked as pending in '{tasklist_name}'.")
        else:
            task['status'] = 'completed'
            # print(f"✅ Task '{task_title}' marked as completed in '{tasklist_name}'.")
        service.tasks().update(tasklist=tasklist_id, task=task['id'], body=task).execute()
        # print(f"✅ Task '{task_title}' marked as completed in '{tasklist_name}'.")
        return True

    except Exception as e:
        print("❌ Error marking task as completed:", e)
        return False

if __name__ == '__main__':
    from auth import login  
    from read import list_tasks_by_list_name  
    from read import fetch_task_lists  
    from read import sort_tasks_by_status  
    service = login()
    
    if service:
        task_lists = fetch_task_lists(service)
        if task_lists:
            print(Fore.MAGENTA + "Task lists fetched successfully.")
            for idx, tasklist in enumerate(task_lists.get('items', [])):
                print(f"{Fore.CYAN}{idx + 1}. {tasklist.get('title', 'No Title')}")

        else:
            print(Fore.YELLOW + "⚠️ No task lists found.")

        print(Style.BRIGHT + Fore.YELLOW + "Please select a task list to update tasks:")
        tasklist_idx = int(input(Fore.YELLOW + "Enter the task list number to view tasks: ")) - 1
        if 0 <= tasklist_idx < len(task_lists.get('items', [])):
            tasklist_name = task_lists.get('items', [])[tasklist_idx].get('title', 'No Title')
            tasks = list_tasks_by_list_name(tasklist_name, service)
            if tasks:
                completed_tasks, pending_tasks = sort_tasks_by_status(tasks)
                task_idx = 0
                if pending_tasks:
                    print(Fore.YELLOW + f"Pending Tasks in '{tasklist_name}':")
                    for task in pending_tasks:
                        print(Fore.YELLOW + f"❗| {task_idx}| {task.get('title', 'No Title')}")
                        task_idx += 1
                if completed_tasks:
                    print(Fore.GREEN + f"Completed Tasks in '{tasklist_name}':")
                    for task in completed_tasks:
                        # print(Fore.GREEN + f"✅| {task_idx}| {task.get('title', 'No Title')}")
                        task_idx += 1
                task_to_be_updated = int(input(Fore.YELLOW + "Enter the task number to update status: "))
                if 0 <= task_to_be_updated < task_idx:
                    if task_to_be_updated < len(pending_tasks):
                        task_title = pending_tasks[task_to_be_updated].get('title', 'No Title')
                    else:
                        task_to_be_updated -= len(pending_tasks)
                        task_title = completed_tasks[task_to_be_updated].get('title', 'No Title')
                    print(Fore.YELLOW + f"Updating status for task: {task_title} in list '{tasklist_name}'")
                    if update_task_status(tasklist_name, task_title, service):
                        print(Fore.GREEN + f"✅ Task '{task_title}' status updated successfully.")
                    else:
                        print(Fore.RED + "❌ Failed to update task status.")
                    
            else:
                print(Fore.YELLOW + "⚠️ No tasks found in this list.")
        else:
            print(Fore.RED + "❌ Invalid task list number.")
    else:
        print(Fore.RED + "❌ Failed to authenticate with Google Tasks API.")
    