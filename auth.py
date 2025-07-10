import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from colorama import Fore, Style, init
init(autoreset=True)

SCOPES = ['https://www.googleapis.com/auth/tasks']
TOKEN_FILE = '/home/abinashlingank/Main/tasks-cli/token.json'
CREDENTIALS_FILE = '/home/abinashlingank/Main/tasks-cli/credentials.json'

def login():
    '''
    Authenticates the user and returns a Google Tasks API service object.
    If the user has already authenticated, it uses the existing token.
    If not, it prompts the user to log in and saves the token for future use.
    '''
    creds = None
    # Load token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        # print(Fore.YELLOW + "Using existing credentials.")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print(Fore.GREEN + Style.BRIGHT + "Welcome to Tasks CLI!")
            print(Fore.YELLOW + "No valid credentials found. Please log in.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('tasks', 'v1', credentials=creds)
    return service

def logout():
    '''
    Logs out the user by deleting the token file.
    '''
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print(Fore.GREEN + "✅ Logged out successfully.")
    else:
        print(Fore.YELLOW + "⚠️ No active login found to log out.")

if __name__ == '__main__':
    service = login()
    print(Fore.GREEN + "✅ Logged in successfully.")
    tasklists = service.tasklists().list().execute()
    print(Fore.GREEN + "✅ Fetched tasklists successfully.")
    # logout()