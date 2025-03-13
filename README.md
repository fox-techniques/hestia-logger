# Hestia Logger 

**A high-performance, structured logging system for Python applications.**  
Supports **async logging, ELK integration, structured JSON logs, and colorized console output.**

## Key Features

- **Structured JSON & Human-Readable Logs** (Optimized for ELK)  
- **Dynamic Metadata Support** (`user_id`, `request_id`, etc.)  
- **Application-Aware Logging** (`get_logger("my_app")`)  
- **Multi-Thread & Multi-Process Friendly** (`thread_id`, `process_id`)  
- **Colored Console Output** (`INFO` in green, `ERROR` in red, etc.)  
- **Internal Logger for Debugging the Logging System**  
- **Supports File Rotation & Future Cloud Integration**  

---

## Documentation

The full documentation is available on [GitHub Pages]().

---

##  Installation

```bash
pip install hestia-logger
```

##  Usage

**1. Basic Setup**

```python
from hestia_logger.core.custom_logger import get_logger

logger = get_logger("my_application")

logger.info("Application started successfully!")
logger.warning("This is a warning!")
logger.error("Something went wrong!")
logger.critical("System is down!!!")
```

**2. Adding Custom Metadata**

```python
logger = get_logger("my_application", metadata={"user_id": "12345", "request_id": "abcd-xyz"})

logger.info("User login successful")
```

## Log File Structure

Hestia Logger creates two main log files:


|File|	Format|	Purpose|
|---|---|---|
|**app.log**	|JSON	|Machine-readable (ELK)|
|**all.log**	|Text	|Human-readable debug logs|

## Log Colors (Console Output)

|Log Level|	Color|
|---|---|
|DEBUG|	🔵 Blue|
|INFO|	⚫ Black|
|WARNING|	🟡 Yellow|
|ERROR|	🔴 Red|
|CRITICAL|	🔥 Bold Red|

## Configuration

Hestia Logger supports environment-based configuration via .env or export:

```bash
# Environment Variables
ENVIRONMENT=local
LOG_LEVEL=INFO
```

## Example Log Output

### Console (Colorized) +  all.log (Text Format)

```yaml
2025-03-06 20:40:23 - my_application - INFO - Application started!
```

### app.log (JSON Format - ELK Ready)

```json
{
    "timestamp": "2025-03-06T20:40:23.286Z",
    "level": "INFO",
    "hostname": "server-1",
    "container_id": "N/A",
    "application": "my_application",
    "event": "Application started successfully!",
    "thread": 12345,
    "process": 56789,
    "uuid": "d3f5b2c1-4f27-46a8-b3d2-f4a7a5c3ef29",
    "metadata": {
        "user_id": "12345",
        "request_id": "abcd-xyz"
    }
}
```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/fox-techniques/hestia-logger/blob/main/LICENSE) file for details.