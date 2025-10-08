#!/opt/homebrew/bin/python3
"""
SessionStart hook to check for pending events from external sources
"""
import sys
import json
import os
import subprocess
from pathlib import Path

def check_redis_events():
    """Check Redis for pending events using docker exec"""
    try:
        # Check if Redis container is running
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=claude-redis', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if 'claude-redis' not in result.stdout:
            return []

        # Get pending events from queue (up to 5)
        events = []
        for _ in range(5):
            result = subprocess.run(
                ['docker', 'exec', 'claude-redis', 'redis-cli', 'RPOP', 'claude_events'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0 or not result.stdout.strip() or result.stdout.strip() == '(nil)':
                break

            try:
                event_data = json.loads(result.stdout.strip())
                events.append(event_data)
            except json.JSONDecodeError:
                continue

        return events
    except Exception as e:
        print(f"Redis check error: {e}", file=sys.stderr)
        return []

def check_file_events(cwd):
    """Check for event files in project directory"""
    event_dir = Path(cwd) / '.claude' / 'events'
    events = []

    if event_dir.exists():
        for event_file in event_dir.glob('*.json'):
            try:
                with open(event_file, 'r') as f:
                    event = json.load(f)
                    events.append(event)
                # Remove processed event file
                event_file.unlink()
            except Exception:
                pass

    return events

def main():
    try:
        input_data = json.load(sys.stdin)
        cwd = input_data.get('cwd', os.getcwd())

        all_events = []

        # Check multiple event sources
        all_events.extend(check_redis_events())
        all_events.extend(check_file_events(cwd))

        if all_events:
            # Add events to session context
            context = "\n## 🔔 Pending External Events\n\n"
            context += "The following events require processing:\n\n"

            for i, event in enumerate(all_events, 1):
                context += f"### Event {i}\n"
                context += f"- **Type**: {event.get('type', 'unknown')}\n"
                context += f"- **ID**: {event.get('event_id', 'N/A')}\n"
                context += f"- **Timestamp**: {event.get('timestamp', 'N/A')}\n"

                if 'payload' in event:
                    context += f"- **Payload**:\n```json\n{json.dumps(event['payload'], indent=2)}\n```\n"

                context += "\n"

            context += "\nUse @agent-event-processor or process these events as needed.\n"

            print(context)

        sys.exit(0)

    except Exception as e:
        # Don't block session start on errors
        print(f"Error checking events: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()