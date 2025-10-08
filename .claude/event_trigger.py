#!/usr/bin/env python3
"""
External event trigger for Claude Code agents
Usage: python event_trigger.py <event_type> <event_data>
"""
import sys
import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

def trigger_claude_agent(event_type, event_data, use_headless=False):
    """
    Trigger Claude Code agent with event data

    Args:
        event_type: Type of event (deployment, test_failure, etc.)
        event_data: JSON string or dict with event details
        use_headless: If True, run in headless mode
    """

    # Parse event data if string
    if isinstance(event_data, str):
        try:
            event_data = json.loads(event_data)
        except json.JSONDecodeError:
            event_data = {"raw_data": event_data}

    # Create event object
    event = {
        "event_id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "payload": event_data
    }

    if use_headless:
        # Trigger Claude in headless mode
        prompt = f"""
        Process this external event:

        Event Type: {event_type}
        Event ID: {event['event_id']}

        Event Data:
        {json.dumps(event_data, indent=2)}

        Use @agent-event-processor to handle this event appropriately.
        """

        result = subprocess.run([
            'claude', '-p', prompt,
            '--allowedTools', 'Read,Write,Bash',
            '--output-format', 'stream-json'
        ], capture_output=True, text=True)

        return result.stdout

    else:
        # Save event to file for next session
        event_dir = Path.cwd() / '.claude' / 'events'
        event_dir.mkdir(parents=True, exist_ok=True)

        event_file = event_dir / f"{event['event_id']}.json"
        with open(event_file, 'w') as f:
            json.dump(event, f, indent=2)

        print(f"Event saved: {event_file}")
        print("Event will be processed in next Claude session")
        return str(event_file)

def main():
    if len(sys.argv) < 3:
        print("Usage: python event_trigger.py <event_type> <event_data> [--headless]")
        sys.exit(1)

    event_type = sys.argv[1]
    event_data = sys.argv[2]
    use_headless = '--headless' in sys.argv

    result = trigger_claude_agent(event_type, event_data, use_headless)
    print(result)

if __name__ == '__main__':
    main()