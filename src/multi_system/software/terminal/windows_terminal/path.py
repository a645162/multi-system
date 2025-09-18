import os


def get_windows_terminal_data_path():
    # C:\Users\konghaomin\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe
    local_app_data = os.path.expanduser("~\\AppData\\Local")
    path = os.path.join(local_app_data, "Packages")
    # List all directories in path
    dirs = os.listdir(path)
    for dir in dirs:
        if dir.startswith("Microsoft.WindowsTerminal_"):
            return os.path.join(path, dir)


def get_windows_terminal_settings_path():
    data_path = get_windows_terminal_data_path()
    return os.path.join(data_path, "LocalState", "settings.json")


def _main():
    path = get_windows_terminal_settings_path()
    print(path)


if __name__ == "__main__":
    _main()
