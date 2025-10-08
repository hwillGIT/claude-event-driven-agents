#!/usr/bin/env python3
"""
Message queue listener that triggers Claude Code agents
Supports Redis, RabbitMQ, and file-based queues
"""
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class BaseQueueListener:
    """Base class for queue listeners"""

    def __init__(self, queue_name, project_dir=None):
        self.queue_name = queue_name
        self.project_dir = project_dir or Path.cwd()
        self.running = True

    def process_message(self, message):
        """Process a message from the queue"""
        try:
            # Parse message
            if isinstance(message, str):
                data = json.loads(message)
            else:
                data = message

            event_type = data.get('type', 'unknown')
            event_payload = data.get('payload', {})

            print(f"[{datetime.now()}] Processing event: {event_type}")

            # Trigger Claude agent
            prompt = f"""
            Process this message queue event:

            Queue: {self.queue_name}
            Event Type: {event_type}
            Timestamp: {datetime.now().isoformat()}

            Event Payload:
            {json.dumps(event_payload, indent=2)}

            Delegate to @agent-event-processor if complex processing is needed.
            Otherwise, handle the event directly based on its type.
            """

            result = subprocess.run([
                'claude', '-p', prompt,
                '--project-dir', str(self.project_dir),
                '--allowedTools', 'Read,Write,Bash',
                '--output-format', 'stream-json'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Event processed successfully")
            else:
                print(f"❌ Event processing failed: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            print(f"Error processing message: {e}")
            return False

    def listen(self):
        """Start listening to the queue"""
        raise NotImplementedError("Subclasses must implement listen()")

    def stop(self):
        """Stop the listener"""
        self.running = False

class RedisQueueListener(BaseQueueListener):
    """Redis queue listener using LPOP"""

    def __init__(self, queue_name, project_dir=None, host='localhost', port=6379):
        super().__init__(queue_name, project_dir)
        import redis
        self.redis = redis.Redis(host=host, port=port, db=0)

    def listen(self):
        print(f"📡 Listening to Redis queue: {self.queue_name}")

        while self.running:
            try:
                # Block for 1 second waiting for message
                message = self.redis.blpop(self.queue_name, timeout=1)

                if message:
                    _, data = message
                    self.process_message(data.decode('utf-8'))

            except KeyboardInterrupt:
                print("\n🛑 Stopping Redis listener...")
                break
            except Exception as e:
                print(f"Redis error: {e}")
                time.sleep(5)

class RedisPubSubListener(BaseQueueListener):
    """Redis Pub/Sub listener"""

    def __init__(self, channel_name, project_dir=None, host='localhost', port=6379):
        super().__init__(channel_name, project_dir)
        import redis
        self.redis = redis.Redis(host=host, port=port, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channel_name)

    def listen(self):
        print(f"📡 Listening to Redis channel: {self.queue_name}")

        for message in self.pubsub.listen():
            if not self.running:
                break

            if message['type'] == 'message':
                self.process_message(message['data'].decode('utf-8'))

class RabbitMQListener(BaseQueueListener):
    """RabbitMQ queue listener"""

    def __init__(self, queue_name, project_dir=None, host='localhost'):
        super().__init__(queue_name, project_dir)
        import pika
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        """RabbitMQ callback"""
        success = self.process_message(body.decode('utf-8'))

        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Requeue on failure
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def listen(self):
        print(f"📡 Listening to RabbitMQ queue: {self.queue_name}")

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
            auto_ack=False
        )

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\n🛑 Stopping RabbitMQ listener...")
            self.channel.stop_consuming()
            self.connection.close()

class FileQueueListener(BaseQueueListener):
    """File-based queue listener (watches a directory for JSON files)"""

    def __init__(self, queue_dir, project_dir=None):
        queue_dir = Path(queue_dir)
        super().__init__(str(queue_dir), project_dir)
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def listen(self):
        print(f"📡 Watching directory: {self.queue_dir}")

        processed_dir = self.queue_dir / 'processed'
        processed_dir.mkdir(exist_ok=True)

        while self.running:
            try:
                # Check for new JSON files
                for event_file in self.queue_dir.glob('*.json'):
                    print(f"Found event file: {event_file.name}")

                    with open(event_file, 'r') as f:
                        data = f.read()

                    success = self.process_message(data)

                    if success:
                        # Move to processed directory
                        event_file.rename(processed_dir / event_file.name)
                    else:
                        # Move to error directory
                        error_dir = self.queue_dir / 'error'
                        error_dir.mkdir(exist_ok=True)
                        event_file.rename(error_dir / event_file.name)

                time.sleep(5)  # Check every 5 seconds

            except KeyboardInterrupt:
                print("\n🛑 Stopping file watcher...")
                break
            except Exception as e:
                print(f"File watcher error: {e}")
                time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description='Message queue listener for Claude Code')
    parser.add_argument('type', choices=['redis', 'redis-pubsub', 'rabbitmq', 'file'],
                       help='Queue type')
    parser.add_argument('queue', help='Queue/channel name or directory path')
    parser.add_argument('--host', default='localhost', help='Queue server host')
    parser.add_argument('--port', type=int, help='Queue server port')
    parser.add_argument('--project-dir', help='Project directory for Claude')

    args = parser.parse_args()

    try:
        if args.type == 'redis':
            listener = RedisQueueListener(
                args.queue,
                args.project_dir,
                args.host,
                args.port or 6379
            )
        elif args.type == 'redis-pubsub':
            listener = RedisPubSubListener(
                args.queue,
                args.project_dir,
                args.host,
                args.port or 6379
            )
        elif args.type == 'rabbitmq':
            listener = RabbitMQListener(
                args.queue,
                args.project_dir,
                args.host
            )
        elif args.type == 'file':
            listener = FileQueueListener(
                args.queue,
                args.project_dir
            )

        listener.listen()

    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install required packages:")
        print("  pip install redis  # for Redis")
        print("  pip install pika   # for RabbitMQ")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()