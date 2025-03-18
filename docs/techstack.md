# 💻 Tech Stack

When designing a logging and monitoring stack, we needed a **robust, scalable, and efficient** system that can **process, store, visualize, and analyze logs** effectively. Below is the reasoning behind our choices:

---


## **🛢️ Fluent Bit**

🔸 Purpose: **The Lightweight Log Forwarder**

- **Lightweight and Fast:** Consumes fewer resources than Logstash, making it ideal for containerized environments.
- **Efficient Log Forwarding:** Fluent Bit collects and forwards logs from Hestia Logger, system logs, and applications.
- **Built-in Processing Capabilities:** Supports basic filtering, transformation, and parsing before sending logs to storage.
- **Seamless Integration with Elasticsearch:** Natively supports Elasticsearch output, ensuring smooth data ingestion.

**Alternatives Considered:**

- **Logstash** – More powerful for complex log transformations but heavier on resource usage.
- **Filebeat** – Extremely efficient for forwarding logs but lacks processing capabilities like Fluent Bit.

**🏅 Why Fluent Bit Won?**

- **Lightweight** and optimized for containers (low memory footprint).
- **Built-in support for JSON**, structured logs, and multiple input sources.
- **Perfect balance between performance and flexibility** for log forwarding.
- **Works natively with Elasticsearch**, simplifying our architecture.

---

## **🔍 Elasticsearch**

🔸 Purpose:  **The Log Storage & Search Engine**

**Why we chose Elasticsearch?**

- Elasticsearch is a **distributed search and analytics engine**, optimized for storing and querying logs efficiently.
- Provides **full-text search**, meaning we can easily search for specific logs.
- Supports **indexing and real-time querying**, allowing logs to be searchable as soon as they arrive.
- Handles **large-scale data storage**, making it future-proof for expanding logging needs.

**Alternatives Considered:**

- **MongoDB** – Could store logs but lacks efficient log searching and indexing.
- **PostgreSQL** – A strong relational database, but not optimized for log storage.
- **Loki (Grafana)** – Better for structured logs but lacks strong full-text search.

**🏅 Why Elasticsearch Won?**

- **Designed for handling and searching logs at scale.**  
- **Built-in indexing and near real-time search.**  
- **Seamless integration with Logstash and Kibana.**  

---

## **📊 Kibana** 

🔸 Purpose:  **The Log Visualization Tool**

**Why we chose Kibana?**

- Kibana provides a **powerful UI** to search and explore logs stored in Elasticsearch.
- Includes **Discover, Dashboards, and Alerts**, making log analysis easier.
- Allows **real-time monitoring** of logs with customizable filters and views.

**Alternatives Considered:**

- **Grafana (directly with Elasticsearch)** – Good but lacks native log search and filtering.
- **Graylog** – A dedicated log analysis tool, but more complex than Kibana.

**🏅 Why Kibana Won?**

- **Best tool for interactive log exploration and search.**  
- **Easy to set up with Elasticsearch.**  
- **Built-in dashboards for monitoring log trends.**  

---

## **🎨 Grafana**

🔸 Purpose: **Advanced Monitoring & Dashboards**

**Why we chose Grafana?**
- Grafana **extends our log monitoring capabilities** by allowing custom dashboards.
- **Supports multiple data sources**, including Elasticsearch, Prometheus, and more.
- Provides **rich visualizations** like time-series graphs, alerts, and heatmaps.
- **More advanced alerting and dashboarding than Kibana.**

**Alternatives Considered:**

- **Kibana (only)** – Can visualize logs but lacks advanced monitoring.
- **Loki (with Grafana)** – Good for structured logs, but we wanted full-text search.

**🏅 Why Grafana Won?**

- **More flexible than Kibana for monitoring dashboards.**  
- **Supports multiple data sources, making it future-proof.**  
- **Custom alerting, allowing proactive monitoring of logs.**  

---

## Summary

✔ **Logstash** - Ingests and processes logs.  
✔ **Elasticsearch** - Stores and indexes logs.  
✔ **Kibana** - Enables log search and visualization.  
✔ **Grafana** - Provides advanced monitoring and dashboards.  

**🎯 Together, these tools create a full observability and log management solution.**
