# 📥 Installation

**HESTIA** uses the following dependencies which will be installed automatically:

1. **[`python-dotenv`](https://pypi.org/project/python-dotenv/)** – Loads environment variables from `.env`.  
2. **[`coloredlogs`](https://pypi.org/project/coloredlogs/)** – Provides colored log output for better readability.  
3. **[`elasticsearch`](https://pypi.org/project/elasticsearch/)** – Required for sending logs to Elasticsearch.  
4. **[`python-json-logger`](https://pypi.org/project/python-json-logger/)** – Formats logs as structured JSON (useful for Logstash & Kibana).  
5. **[`fastapi`](https://fastapi.tiangolo.com/)** – Likely used for exposing logs via an API endpoint.  
6. **[`requests`](https://pypi.org/project/requests/)** – Standard HTTP library for making API calls.  
7. **[`structlog`](https://pypi.org/project/structlog/)** – Enhances logging with structured data.  
8. **[`httpx`](https://pypi.org/project/httpx/)** – Async HTTP client (may be used for async logging or external APIs).  


## 🎭 Poetry 

We highly recommends using **Poetry** for its outstanding dependency management.

**To start a new project:**

```bash
poetry new my_project
cd my_project

```

This creates a structured Python project with `pyproject.toml`.

**Adding Poetry to an existing project:**

```bash
poetry init

```

Follow the interactive prompts to define project dependencies.

**Creating & Using a Virtual Environment:**

Poetry automatically creates and manages a virtual environment when installing dependencies. To explicitly create a virtual environment:

```bash
poetry env use python3

```

**Activate the virtual environment:**

```bash
poetry shell

```

**Check the environment:**

```bash
poetry env info

```

If you have an existing pyproject.toml, install all dependencies with:

```bash
poetry install

```

**Install HESTIA:**

Inside your project directory, run:

```bash
poetry add hestia-logger

```

---

## 📦 pip 

**HESTIA Asynchronous Logger** is published as a python package and can be installed with
`pip`, ideally by using a [virtual environment]. Open up a terminal and install with:

=== "Latest"

    ``` sh
    pip install hestia-logger
    ```

=== "1.x"

    ``` sh
    pip install hestia-logger=="1.*" # (1)!
    ```

    1.  **HESTIA** uses [semantic versioning].

        This will make sure that you don't accidentally [upgrade to the next
        major version], which may include breaking changes that silently corrupt
        your site. Additionally, you can use `pip freeze` to create a lockfile,
        so builds are reproducible at all times:

        ```
        pip freeze > requirements.txt
        ```

        Now, the lockfile can be used for installation:

        ```
        pip install -r requirements.txt
        ```

This will automatically install compatible versions of all dependencies. **HESTIA** always strives to support the latest versions, so there's no need to
install those packages separately.

---

## 🐙 GitHub

**HESTIA** can be directly used from [GitHub] by cloning the
repository into a subfolder of your project root which might be useful if you
want to use the very latest version:

```bash
git clone https://github.com/fox-techniques/hestia-logger.git
cd hestia-logger
pip install -e .

```

---

🤩 **CONGRAGULATIONS!** Continue to the **usage**. Let's keep going...🚀
