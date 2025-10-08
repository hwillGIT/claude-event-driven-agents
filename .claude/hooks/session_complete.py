#!/opt/homebrew/bin/python3
"""
Stop hook - Run when session completes
"""
import sys
import json
from datetime import datetime

def main():
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get('session_id', 'unknown')

        # Log session completion
        print(f"Session {session_id} completed at {datetime.now()}", file=sys.stderr)

        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()