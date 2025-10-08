#!/usr/bin/env python3
"""
Test Redis connection and demonstrate event queue usage
"""
import json
import sys
import time

def test_redis():
    """Test Redis connection and basic operations"""
    try:
        import redis
    except ImportError:
        print("❌ Redis Python client not installed")
        print("Install with: pip install redis")
        return False

    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)

        # Test connection
        r.ping()
        print("✅ Redis connection successful!")

        # Test basic operations
        print("\n📝 Testing basic operations:")

        # Set/Get
        r.set('test_key', 'Hello Claude!')
        value = r.get('test_key').decode('utf-8')
        print(f"  SET/GET: {value}")

        # Queue operations
        event = {
            'type': 'test_event',
            'payload': {
                'message': 'This is a test event',
                'timestamp': time.time()
            }
        }

        r.lpush('claude_events', json.dumps(event))
        print(f"  QUEUE: Pushed test event to 'claude_events'")

        # Check queue length
        queue_len = r.llen('claude_events')
        print(f"  LENGTH: {queue_len} events in queue")

        # Pop event
        popped = r.rpop('claude_events')
        if popped:
            event_data = json.loads(popped)
            print(f"  POP: Retrieved event type '{event_data['type']}'")

        # Pub/Sub test
        print("\n📡 Testing Pub/Sub:")
        pubsub = r.pubsub()
        pubsub.subscribe('claude_channel')

        # Publish a message
        r.publish('claude_channel', json.dumps({
            'type': 'pubsub_test',
            'message': 'Hello from Redis Pub/Sub!'
        }))
        print("  Published test message to 'claude_channel'")

        # Cleanup
        r.delete('test_key')
        pubsub.close()

        print("\n✅ All Redis tests passed!")
        return True

    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nMake sure Redis is running:")
        print("  docker-compose up -d redis")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_redis()
    sys.exit(0 if success else 1)