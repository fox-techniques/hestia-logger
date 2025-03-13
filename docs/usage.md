# 📄 Usage Guide

This guide provides **simple examples** to demonstrate how to use Hestia Logger in:

1. **Python during development**  
2. **Running inside a container**  

---


=== "Script Example"

     Create a file example.py:

     ```python title="script_example.py" linenums="1"
     from hestia_logger import get_logger

     # Get a logger instance
     logger = get_logger("development")

     # Log messages with different levels
     logger.debug("This is a DEBUG log")
     logger.info("Application started successfully")
     logger.warning("Low disk space warning")
     logger.error("Failed to connect to database")
     logger.critical("System is down!")

     ```

     Run the Script

     ```bash
     poetry run python example.py

     ```

     
=== "Decorator Example"

     
     **HESTIA** Logger provides a **decorator** to automatically log function execution.

     ```python title="example_decorator.py" linenums="1"

     from hestia_logger import get_logger
     from hestia_logger.decorators import log_execution

     # Initialize the logger
     logger = get_logger("decorator")

     @log_execution
     def add_numbers(a, b):
     """Adds two numbers and returns the result."""
     return a + b

     @log_execution
     def simulate_task():
     """Simulates a task that takes time."""
     import time
     time.sleep(2)
     return "Task completed!"

     # Call the functions
     if __name__ == "__main__":
     result = add_numbers(5, 10)
     logger.info(f"Result: {result}")

     task_status = simulate_task()
     logger.info(f"Task Status: {task_status}")
     ```