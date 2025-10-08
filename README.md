# Claude Code Event-Driven Agent System

An advanced event-driven agent architecture for Claude Code, featuring Redis-based message queuing, automated event processing, and deployment automation.

## 🚀 Features

- **Event-Driven Architecture**: Process events from multiple sources (Redis, RabbitMQ, file-based queues)
- **Specialized Agents**: Custom AI agents for specific tasks (event-processor, deployment, etc.)
- **Hooks System**: Lifecycle hooks for session management, command validation, and auto-formatting
- **Redis Integration**: Message queue system using Redis in Docker
- **Deployment Automation**: Complete CI/CD event processing with audit trails
- **Advanced Concurrency**: Async/await patterns inspired by modern Python architectures
- **Scalable Processing**: Handle hundreds of concurrent events efficiently

## 📁 Project Structure

```
.
├── .claude/                    # Claude Code configuration
│   ├── agents/                 # Custom AI agents
│   │   └── event-processor.md  # Event processing specialist
│   ├── hooks/                  # Lifecycle hooks
│   │   ├── check_events.py     # SessionStart hook for event checking
│   │   ├── bash_validator.py   # PreToolUse hook for command validation
│   │   └── python_formatter.py # PostToolUse hook for auto-formatting
│   ├── settings.json           # Claude Code settings and hook configuration
│   ├── event_trigger.py        # External event trigger script
│   └── message_queue_listener.py # Message queue listener
├── docs/                       # Documentation
│   ├── CONCURRENCY.md          # Concurrency architecture details
│   └── PERFORMANCE_GUIDE.md    # Performance optimization guide
├── infrastructure/             # Infrastructure components
│   └── redis/                  # Redis setup
│       ├── docker-compose.yml  # Redis container configuration
│       ├── start_redis.sh      # Redis startup script
│       └── redis_test.py       # Redis connection test
├── event-processing/           # Event processing artifacts
│   ├── deployments/            # Deployment event data
│   ├── logs/                   # Event processing logs
│   └── scripts/                # Generated deployment scripts
└── README.md                   # This file
```

## 🛠️ Setup

### Prerequisites

- Docker Desktop
- Python 3.x
- Claude Code CLI

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd projects
```

2. **Start Redis:**
```bash
cd infrastructure/redis
./start_redis.sh
```

3. **Test the setup:**
```bash
docker exec claude-redis redis-cli ping
# Should return: PONG
```

## 📨 Event Processing

### Sending Events

**Via Redis CLI:**
```bash
docker exec claude-redis redis-cli LPUSH claude_events \
  '{"type":"deployment","event_id":"123","payload":{"version":"v1.0"}}'
```

**Via Python script:**
```bash
python .claude/event_trigger.py deployment '{"version":"v1.0","environment":"staging"}'
```

**Via message queue listener:**
```bash
python .claude/message_queue_listener.py redis claude_events
```

### Event Types

- `deployment` - Trigger deployment workflows
- `test_failure` - Investigate and fix failing tests
- `code_review` - Analyze code changes
- `security_alert` - Triage security findings
- `scheduled_task` - Execute maintenance tasks

## 🎣 Hooks

The system includes several lifecycle hooks:

- **SessionStart**: Checks for pending events when Claude starts
- **PreToolUse**: Validates dangerous bash commands
- **PostToolUse**: Auto-formats Python files after editing
- **Stop**: Logs session completion

## 🤖 Custom Agents

### Event Processor Agent

Specialized agent for handling external events:

```bash
# Invoke directly
@agent-event-processor

# Or delegate from main session
"Use the event-processor agent to handle the deployment event"
```

## 📊 Monitoring

### Check Redis Queue:
```bash
docker exec claude-redis redis-cli LLEN claude_events
```

### View Logs:
```bash
docker logs claude-redis
```

### Redis Commander GUI:
```bash
docker-compose up -d redis-commander
# Access at: http://localhost:8081
```

## 🔧 Configuration

### Claude Settings
Edit `.claude/settings.json` to configure:
- Hook commands
- Allowed tools
- Model selection

### Redis Configuration
Edit `infrastructure/redis/docker-compose.yml` for:
- Port mappings
- Persistence settings
- Resource limits

## 📝 Examples

### Process a Deployment Event
```bash
# 1. Send event to Redis
docker exec claude-redis redis-cli LPUSH claude_events \
  '{"type":"deployment","event_id":"deploy_001","payload":{
    "version":"v2.0.0",
    "environment":"production",
    "triggered_by":"GitHub Actions"
  }}'

# 2. Start Claude session
claude --resume

# 3. Event will be automatically detected and can be processed
@agent-event-processor
```

## ⚡ Performance & Concurrency

### Concurrency Architecture
The system incorporates advanced Python concurrency patterns for optimal performance:

- **Async/Await Throughout**: Non-blocking I/O operations for maximum throughput
- **Event Loop Management**: Efficient task scheduling and execution
- **Parallel Processing**: Multiple events handled simultaneously without threading overhead
- **Queue-Based Distribution**: Redis ensures reliable, distributed event processing
- **Resource Efficiency**: Single process handles many concurrent operations

### Performance Optimizations
- **Non-Blocking Redis Operations**: Uses async Redis client for high-throughput messaging
- **Subprocess Management**: Shell commands execute asynchronously without blocking
- **Concurrent Tool Execution**: Multiple tools can run in parallel during event processing
- **Connection Pooling**: Maintains Redis connection pools for efficiency
- **Batched Event Processing**: Can process up to 5 events per session start

### Scalability Features
- **Horizontal Scaling**: Add more workers to handle increased load
- **Distributed Processing**: Events can be processed across multiple machines
- **Load Balancing**: Redis naturally distributes work across available workers
- **Fault Tolerance**: Failed events can be retried automatically
- **Zero Downtime**: Deploy updates without stopping event processing

## 🛡️ Security

- Command validation hooks prevent dangerous operations
- Docker isolation for Redis
- Audit logging for all event processing
- Rollback capabilities for deployments

## 📄 License

MIT

## 👥 Contributors

- Created with Claude Code
- Event-driven architecture powered by Redis

## 📚 Documentation

- [Concurrency Architecture](docs/CONCURRENCY.md) - Deep dive into async patterns and event processing
- [Performance Guide](docs/PERFORMANCE_GUIDE.md) - Optimization tips and benchmarks

## 🆘 Support

For issues or questions, please check:
- Claude Code documentation: https://docs.claude.com/
- Redis documentation: https://redis.io/docs/
- Project Issues: https://github.com/hwillGIT/claude-event-driven-agents/issues

---

Built with ❤️ using Claude Code's event-driven agent system