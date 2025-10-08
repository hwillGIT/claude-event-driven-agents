#!/usr/bin/env python3
"""
PreToolUse hook to validate and potentially block dangerous bash commands
"""
import sys
import json
import re

# Dangerous command patterns
DANGEROUS_PATTERNS = [
    (r'rm\s+.*-[rf]', "Potentially destructive rm command"),
    (r'sudo\s+rm', "Sudo rm command blocked"),
    (r'chmod\s+777', "Dangerous permission change"),
    (r'dd\s+if=.*of=/dev', "Direct disk write operation"),
    (r'mkfs', "Filesystem format command"),
    (r'>\s*/dev/sd', "Writing directly to disk device"),
    (r'curl.*\|\s*bash', "Piping curl to bash is dangerous"),
    (r'wget.*\|\s*sh', "Piping wget to shell is dangerous"),
]

# Commands that require confirmation
CONFIRM_PATTERNS = [
    (r'git\s+push.*--force', "Force push detected"),
    (r'git\s+reset\s+--hard', "Hard reset will lose changes"),
    (r'npm\s+publish', "Publishing to npm registry"),
    (r'docker\s+rm.*-f', "Force removing docker containers"),
]

def validate_command(command):
    """Validate bash command for security issues"""

    # Check for dangerous patterns
    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, reason

    # Check for patterns requiring confirmation
    for pattern, warning in CONFIRM_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            # In automated mode, allow with warning
            print(f"⚠️  Warning: {warning}", file=sys.stderr)

    return True, None

def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name")
        tool_input = input_data.get("tool_input", {})

        if tool_name == "Bash":
            command = tool_input.get("command", "")

            is_safe, reason = validate_command(command)

            if not is_safe:
                output = {
                    "permissionDecision": "deny",
                    "reason": f"Command blocked: {reason}"
                }
                print(json.dumps(output))
                sys.exit(0)

        # Allow the operation
        sys.exit(0)

    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()