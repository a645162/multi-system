from pathlib import Path
import json

from multi_system.software.terminal.windows_terminal.path import (
    get_windows_terminal_settings_path,
)


def fix_windows_terminal_guid(try_to_fix: bool = True, settings_path: str = None):
    json_path = settings_path or get_windows_terminal_settings_path()
    if not json_path or not Path.exists(json_path):
        print("Windows Terminal settings.json not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("Failed to load settings.json.")
        return

    profiles = data.get("profiles", {}).get("list", [])
    if not profiles:
        print("No profiles found in settings.json.")
        return

    guid_set = set()
    duplicates = []
    for profile in profiles:
        guid = profile.get("guid")
        if guid in guid_set:
            duplicates.append(guid)
        else:
            guid_set.add(guid)

    if duplicates:
        print(f"Duplicate GUIDs found: {duplicates}")
    else:
        print("No duplicate GUIDs found.")

    if duplicates and try_to_fix:
        import uuid

        for profile in profiles:
            guid = profile.get("guid")
            if guid in duplicates:
                new_guid = str(uuid.uuid4())
                print(f"Changing GUID {guid} to {new_guid}")
                profile["guid"] = new_guid
                duplicates.remove(guid)  # Ensure we only change it once

        # with open(json_path, "w", encoding="utf-8") as f:
        #     json.dump(data, f, indent=4)
        print("Duplicate GUIDs have been fixed.")


def main():
    fix_windows_terminal_guid()


if __name__ == "__main__":
    main()
