function tasky() {
    local command="$1"
    shift

    local cli_path="$HOME/Main/tasks-cli/task-cli.py"
    local venv_path="$HOME/Main/tasks-cli/taskscli"

    # Activate virtual environment
    if [ -d "$venv_path" ]; then
        source "$venv_path/bin/activate"
    else
        echo "❌ Virtual environment not found at $venv_path. Please set it up first."
        return 1
    fi

    case "$command" in
        read|"")
            python3 "$cli_path"
            ;;
        create)
            if [ $# -ge 1 ]; then
                python3 "$cli_path" create "$@"
            else
                python3 "$cli_path" create
            fi
            ;;
        do)
            if [ $# -ge 1 ] && [[ "$1" =~ ^[0-9]+$ ]]; then
                python3 "$cli_path" do "$1"
            else
                python3 "$cli_path" do
            fi
            ;;
        undo)
            if [ $# -ge 1 ] && [[ "$1" =~ ^[0-9]+$ ]]; then
                python3 "$cli_path" undo "$1"
            else
                python3 "$cli_path" undo
            fi
            ;;
        delete)
            if [ $# -ge 1 ] && [[ "$1" =~ ^[0-9]+$ ]]; then
                python3 "$cli_path" delete "$1"
            else
                python3 "$cli_path" delete
            fi
            ;;
        clean)
            python3 "$cli_path" clean
            ;;
        logout)
            python3 "$cli_path" logout
            ;;
        help|--help|-h)
            echo "🧠 Usage: tasky {read|create|do|undo|delete|clean|logout}"
            echo "  read          - Show current tasks"
            echo "  create        - Create a task (interactive if no args)"
            echo "  do [index]    - Mark task done (interactive if no index)"
            echo "  undo [index]  - Undo completed task (interactive if no index)"
            echo "  delete [index]- Delete task (interactive if no index)"
            echo "  clean         - Clean completed tasks"
            echo "  logout        - Logout from your Google account"
            ;;
        *)
            echo "❓ Unknown command: $command"
            tasky help
            ;;
    esac

    deactivate
    return 0
}
