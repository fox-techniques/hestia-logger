# Debugging Marathon: Key Findings and Lessons

## Overview

Our journey through async logging, structured logs, ELK integration, and colored console output was an intense but rewarding debugging process.
We've successfully built a robust, scalable, and structured logging system that ensures: 

- High-performance async logging
- Human-readable logs (all.log) & JSON logs (app.log)
- ELK (Elasticsearch, Logstash, Kibana) friendly logs
- Dynamic application names & metadata
- Thread-safe & process-aware logs
- Clean and colored console output

## Major Debugging Challenges & Fixes

➊ **LOG_LEVEL Not Taking Effect**

🚧 **Problem**

Despite setting LOG_LEVEL=INFO, DEBUG logs were still appearing.

🔧 **Fix**

- Applied LOG_LEVEL to root logger + all handlers
- Explicitly reset handlers (logging.root.handlers = []) before applying the level
- Ensured every logger inherited LOG_LEVEL correctly

➋ **Internal Logger File Was Created Even When Disabled**

🚧 **Problem**

Setting ENABLE_INTERNAL_LOGGER=false still created hestia_logger_internal.log, but it was empty.

🔧 **Fix**

- Introduced NullLogger to completely disable internal logging
- Prevented the file handler from attaching when logging was disabled
- Removed redundant checks for disabled (if it's off, it should not even exist!)

➌ **JSON Logs Were Not Structured Properly for ELK**

🚧 **Problem**

JSON logs were too basic (timestamp, level, message), lacking useful fields.

🔧 **Fix**

- Created a custom JSONFormatter(logging.Formatter) class
- Added hostname, container ID, process ID, thread ID, and UUID
- Introduced metadata (user_id, request_id, etc.) for better tracing
- Used ISO 8601 timestamps (datetime.utcnow().isoformat() + "Z") for ELK compatibility

➍ **Text Logs (all.log) Lacked Context**

🚧 **Problem**

The text log format was too simple and lacked context for debugging.

🔧 **Fix**

- Added hostname, container ID, process/thread ID, application name
- Ensured multi-threaded logs could be traced properly
- Kept a clean, readable structure without too much clutter

➎ **Colors in Log Files Didn’t Match the Console**

🚧 **Problem**

The console used colorlog.ColoredFormatter, but logs in all.log had raw ANSI escape codes (\x1b[31mERROR\x1b[0m).

🔧 **Fix**

- Used colored logs only for the console (console_handler)
- Kept plain-text formatting in all.log
- Ensured app.log remained pure JSON for ELK

➏ **get_logger(name) Did Not Pass Application Name to Logs**

🚧 **Problem**

Application names were not correctly embedded in logs.

🔧 **Fix**

- Modified get_logger(name) to store app name inside the logger
- Passed it dynamically into the JSONFormatter

## Lessons Learned

**1. Logging is NOT Just Printing Messages**

We learned that logging isn’t just about writing messages to a file—it’s about: 
- Structure (for machines & ELK)
- Readability (for humans & debugging)
- Performance (async, thread-safe logging)

**2. Colorlog is Awesome, But Not for Files**

Using colorlog made the console logs highly readable, but log files should remain clean.
Lesson:

- Use colors only for console_handler
- Use plain text & JSON for log files

**3. Structured Logging Is the Future**

Plain-text logs are fine for humans, but structured logs (JSON) allow:

-  Filtering logs by metadata (e.g., user_id, request_id)
-  Powerful ELK queries
-  Easier debugging & analytics

**4. Proper Logging Makes Debugging Easier**

By adding:
- Process ID & Thread ID, we solved multi-threaded log issues
- Metadata support, we can trace logs across services
- Structured logs, our logs are now searchable in ELK

**5. Debugging Requires Systematic Testing**

To solve our issues, we followed this debugging workflow:

- Isolate the problem (e.g., DEBUG logs appearing despite INFO)
- Reproduce it (change settings, test different use cases)
- Apply a fix, then test again
- Check logs (cat logs/all.log & cat logs/app.log)
- Ensure logs work for ELK, humans, and async systems

## Future Ideas & Improvements

- Auto-Rotate Logs

Problem: Our logs never rotate, meaning all.log & app.log grow indefinitely
Solution: Use RotatingFileHandler (maxBytes=10MB, backupCount=5) to rotate logs automatically.

- Add Trace ID Support

We already support metadata, but we could: 
- Generate a trace ID for each request
- Pass this trace ID through logs, requests, and services
- Improve distributed tracing for microservices

- Add Support for Cloud-Based Logging

Right now, logs only write to local files, but future support could include: 

- AWS CloudWatch
- Google Cloud Logging
- Datadog / New Relic
- Logstash / Elasticsearch Direct Ingestion

## Key Takeaways

- Logging is complex! Even when everything looks right, logs can be filtered, blocked, or lost.
- Always check if emit() is running. If emit() is never called, logs will NEVER be written.
- Python’s logging system sometimes filters logs before they reach handlers.
- Manually handling log records (handle(record)) can prevent logs from being lost.
- Debug step by step. Printing debug messages at each stage helped us pinpoint the issue.


💀 The 3 Major Issues That Kept Us Stuck

1️⃣ Misuse of asyncio for Logging

⛔ What Went Wrong?

    Logging in Python is inherently synchronous.
    We initially tried to make emit() fully async using asyncio.run(), but:
        asyncio.run() cannot be called from a running event loop, leading to crashes.
        When removed, _write_log() was never awaited, meaning logs were lost.
        Using create_task() helped, but tasks were not properly scheduled.
    Final Fix: Switched to a thread-based logging approach using queue.Queue() instead of asyncio.

🎯 Lesson Learned

    Async logging in logging.Handler is dangerous because logging is designed for synchronous operation.
    The best async logging solution is not asyncio, but a background thread handling file writes.

2️⃣ DEBUG Logs Were Being Filtered at Multiple Levels

⛔ What Went Wrong?

    Initially, handlers were not respecting LOG_LEVEL because:
        LOG_LEVEL was correctly set, but handlers had their own level settings (INFO by default).
        The root logger was still filtering out DEBUG logs, even though LOG_LEVEL=DEBUG.
    Final Fix:
        Explicitly set setLevel(LOG_LEVEL) for both root and handlers.
        Manually attached handlers before logging started.
        Printed handler levels during startup for verification.

🎯 Lesson Learned

    Setting LOG_LEVEL=DEBUG globally isn’t enough—handlers need to be explicitly configured to respect it.

3️⃣ Log Files Were Empty or Missing

⛔ What Went Wrong?

    app.log and all.log were empty because:
        _write_log() was not executing due to event loop issues.
        Handlers didn’t use the correct formatter (logs were stored in raw format).
        Log writes were being scheduled, but they never ran.
    Final Fix:
        Used a thread-based queue system to ensure logs are processed.
        Applied correct JSON and text formatters to app.log and all.log.
        Confirmed log files exist before running tests.

🎯 Lesson Learned

    Logs must be actively confirmed as being written.
    A queue-based system is better than relying on event loop scheduling.


💡 Key Takeaways & Lessons Learned

1️⃣ asyncio is Not a Good Fit for logging.Handler

- Python’s logging module is fundamentally synchronous.
- Thread-based logging (with a queue) is the best approach for async-like behavior.

2️⃣ The Root Logger Can Silently Filter Out Logs

- Setting LOG_LEVEL=DEBUG globally isn’t enough—each handler must also be set to DEBUG.
- Printing handler levels at startup helped catch this early.
- 
3️⃣ Log Writes Must Be Explicitly Verified

- A file appearing in the directory does NOT mean logs are actually being written.
- Using cat logs/app.log after every change was critical.

⏳ Why It Took So Long

1. Async logging is notoriously difficult to debug because tasks are scheduled but may never run.
2. Python’s logging module swallows errors, making it hard to see why logs were not appearing.
3. We fixed DEBUG logging multiple times, but handlers were still blocking logs.
4. Every test required multiple steps (configuring environment variables, checking log files, etc.).
5. The error messages were misleading (asyncio.run() cannot be called was a symptom, not the cause).
