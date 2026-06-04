#!/usr/bin/env python3
"""macOS AppleScript and automation helpers.

Provides AppleScript execution and automation utilities.
"""

import subprocess
import os
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

if __name__ != "__main__":
    pass


@dataclass
class AutomationResult:
    """Result from an automation operation."""
    success: bool
    output: str
    error: Optional[str] = None


class AutomationError(Exception):
    """Exception raised for automation operations."""
    pass


def run_applescript(script: str) -> AutomationResult:
    """
    Run an AppleScript script.

    Args:
        script: AppleScript code to execute

    Returns:
        AutomationResult with output
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=60,
        )

        success = result.returncode == 0

        return AutomationResult(
            success=success,
            output=result.stdout.strip(),
            error=result.stderr.strip() if result.stderr else None,
        )

    except subprocess.TimeoutExpired:
        return AutomationResult(
            success=False,
            output='',
            error='Script execution timed out',
        )
    except Exception as e:
        return AutomationResult(
            success=False,
            output='',
            error=str(e),
        )


def run_multiline_applescript(script: str) -> AutomationResult:
    """
    Run a multi-line AppleScript script.

    Args:
        script: Multi-line AppleScript code

    Returns:
        AutomationResult with output
    """
    try:
        result = subprocess.run(
            ['osascript', '-'],
            input=script,
            capture_output=True,
            text=True,
            timeout=120,
        )

        success = result.returncode == 0

        return AutomationResult(
            success=success,
            output=result.stdout.strip(),
            error=result.stderr.strip() if result.stderr else None,
        )

    except subprocess.TimeoutExpired as e:
        return AutomationResult(
            success=False,
            output='',
            error='Script execution timed out',
        )
    except Exception as e:
        return AutomationResult(
            success=False,
            output='',
            error=str(e),
        )


def tell_app(app_name: str, command: str) -> AutomationResult:
    """Send a command to an application."""
    """
    Send a command to an application.

    Args:
        app_name: Name of the application
        command: AppleScript command

    Returns:
        AutomationResult with output
    """
    script = f'tell application "{app_name}"\n{command}\nend tell'
    return run_applescript(script)


def get_clipboard() -> AutomationResult:
    """
    Get the current clipboard contents.

    Returns:
        AutomationResult with clipboard text
    """
    return run_applescript('the clipboard')


def set_clipboard(text: str) -> AutomationResult:
    """
    Set the clipboard contents.

    Args:
        text: Text to put on clipboard

    Returns:
        AutomationResult
    """
    # Escape quotes in text
    escaped = text.replace('"', '\\"').replace('\n', '\\n')
    script = f'set the clipboard to "{escaped}"'
    return run_applescript(script)


def press_key(key: str, modifiers: Optional[List[str]] = None) -> AutomationResult:
    """
    Simulate a key press.

    Args:
        key: Key to press (e.g., 'v', 'return', 'escape')
        modifiers: Modifier keys (e.g., 'command', 'shift', 'option')

    Returns:
        AutomationResult
    """
    mod_str = ' '.join(modifiers) if modifiers else ''
    script = f'tell application "System Events" to key code {key} \
              using {mod_str}'
    return run_applescript(script)


def type_text(text: str) -> AutomationResult:
    """
    Type text using the keyboard.

    Args:
        text: Text to type

    Returns:
        AutomationResult
    """
    # Escape special characters
    escaped = text.replace('"', '\\"').replace('\\', '\\\\')
    script = f'tell application "System Events" to keystroke "{escaped}"'
    return run_applescript(script)


def click_menu(app_name: str, menu_path: List[str]) -> AutomationResult:
    """
    Click a menu item.

    Args:
        app_name: Application name
        menu_path: Path to menu item (e.g., ['File', 'Save'])

    Returns:
        AutomationResult
    """
    menu_items = ', '.join(f'"{item}"' for item in menu_path)
    script = f'tell application "{app_name}" to activate\n\
              tell application "System Events" to click menu item \
              {menu_items} of menu 1 of menu bar item 1 of \
              process "{app_name}"'
    return run_applescript(script)


def get_front_app() -> str:
    """
    Get the name of the frontmost application.

    Returns:
        Application name
    """
    result = run_applescript('name of application (path to frontmost \
                             application as text)')
    return result.output if result.success else ''


def open_app(app_name: str) -> AutomationResult:
    """
    Open an application.

    Args:
        app_name: Application name or path

    Returns:
        AutomationResult
    """
    return tell_app('Finder', f'open application "{app_name}"')


def quit_app(app_name: str) -> AutomationResult:
    """
    Quit an application.

    Args:
        app_name: Application name

    Returns:
        AutomationResult
    """
    return tell_app(app_name, 'quit')


def force_quit_app(app_name: str) -> AutomationResult:
    """
    Force quit an application.

    Args:
        app_name: Application name

    Returns:
        AutomationResult
    """
    script = f'tell application "System Events" to tell process \
              "{app_name}" to quit'
    return run_applescript(script)


def get_processes() -> List[Dict[str, str]]:
    """
    Get list of running processes.

    Returns:
        List of process information dictionaries
    """
    script = '''
    set processList to {}
    tell application "System Events"
        set processList to name of every process
    end tell
    return processList as text
    '''

    result = run_applescript(script)

    if result.success:
        processes = []
        for name in result.output.split(', '):
            if name:
                processes.append({'name': name.strip()})
        return processes

    return []


def show_notification(
    title: str,
    message: str,
    subtitle: Optional[str] = None,
    sound: Optional[str] = None,
) -> AutomationResult:
    """
    Show a notification.

    Args:
        title: Notification title
        message: Notification message
        subtitle: Optional subtitle
        sound: Optional sound name

    Returns:
        AutomationResult
    """
    script = f'display notification "{message}"'

    if subtitle:
        script += f' with title "{title}" subtitle "{subtitle}"'
    else:
        script += f' with title "{title}"'

    if sound:
        script += f' sound name "{sound}"'

    return run_applescript(script)


def display_dialog(
    message: str,
    title: Optional[str] = None,
    buttons: Optional[List[str]] = None,
    default_button: Optional[str] = None,
    with_icon: Optional[str] = None,
) -> AutomationResult:
    """
    Display a dialog.

    Args:
        message: Dialog message
        title: Dialog title
        buttons: List of buttons
        default_button: Default button text
        with_icon: Icon type ('stop', 'note', 'caution')

    Returns:
        AutomationResult with button clicked
    """
    script = f'display dialog "{message}"'

    if title:
        script += f' with title "{title}"'

    if buttons:
        script += f' buttons {buttons}'

    if default_button:
        script += f' default button "{default_button}"'

    if with_icon:
        script += f' with icon {with_icon}'

    return run_applescript(script)


def display_alert(
    message: str,
    title: Optional[str] = None,
    alert_style: str = 'informational',
    buttons: Optional[List[str]] = None,
) -> AutomationResult:
    """
    Display an alert.

    Args:
        message: Alert message
        title: Alert title
        alert_style: 'informational', 'warning', or 'critical'
        buttons: List of buttons

    Returns:
        AutomationResult
    """
    script = f'display alert "{message}"'

    if title:
        script += f' with title "{title}"'

    script += f' as "{alert_style}"'

    if buttons:
        script += f' buttons {buttons}'

    return run_applescript(script)


def choose_file(
    prompt: str = 'Choose a file',
    of_type: Optional[List[str]] = None,
    default_location: Optional[str] = None,
    multiple: bool = False,
) -> List[str]:
    """
    Show a file picker dialog.

    Args:
        prompt: Prompt text
        of_type: File types to allow
        default_location: Default directory
        multiple: Allow multiple selection

    Returns:
        List of selected file paths
    """
    script = 'set theFiles to '

    if multiple:
        script += 'choose file '
    else:
        script += 'choose file '

    script += f'with prompt "{prompt}"'

    if of_type:
        types = ', '.join(f'"{t}"' for t in of_type)
        script += f' of type {{ {types} }}'

    if default_location:
        script += f' default location "{default_location}"'

    if multiple:
        script += ' multiple selections allowed false'

    result = run_applescript(script)

    if result.success:
        return [f.strip() for f in result.output.split(', ')]

    return []


def choose_folder(
    prompt: str = 'Choose a folder',
    default_location: Optional[str] = None,
) -> str:
    """
    Show a folder picker dialog.

    Args:
        prompt: Prompt text
        default_location: Default directory

    Returns:
        Selected folder path
    """
    script = f'choose folder with prompt "{prompt}"'

    if default_location:
        script += f' default location "{default_location}"'

    result = run_applescript(script)

    if result.success:
        return result.output.strip()

    return ''


def run_shortcut(shortcut_name: str, input_text: Optional[str] = None) -> \
                 AutomationResult:
    """
    Run a Shortcuts shortcut.

    Args:
        shortcut_name: Name of the shortcut
        input_text: Optional input text

    Returns:
        AutomationResult
    """
    script = f'tell application "Shortcuts Events" to run shortcut \
              "{shortcut_name}"'

    if input_text:
        script += f' with input "{input_text}"'

    return run_applescript(script)
