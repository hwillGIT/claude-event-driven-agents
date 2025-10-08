#!/usr/bin/env python3
"""
PostToolUse hook to auto-format Python files after editing
"""
import sys
import json
import subprocess
import os

def format_python_file(file_path):
    """Format Python file with black or autopep8"""

    # Try black first
    try:
        result = subprocess.run(
            ['black', '--quiet', file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Formatted with black"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Try autopep8 as fallback
    try:
        result = subprocess.run(
            ['autopep8', '--in-place', '--aggressive', file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Formatted with autopep8"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return False, "No formatter available"

def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name")
        tool_input = input_data.get("tool_input", {})

        if tool_name in ["Write", "Edit"]:
            file_path = tool_input.get("file_path", "")

            if file_path.endswith('.py') and os.path.exists(file_path):
                success, message = format_python_file(file_path)

                if success:
                    print(f"✅ {message}: {file_path}", file=sys.stderr)
                else:
                    print(f"ℹ️  {message}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        # Don't block on formatting errors
        print(f"Formatting error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()