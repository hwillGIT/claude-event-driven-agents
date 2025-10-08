#!/opt/homebrew/bin/python3
"""
UserPromptSubmit hook - Enhance prompts with context
"""
import sys
import json

def main():
    try:
        input_data = json.load(sys.stdin)
        # For now, just pass through
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()