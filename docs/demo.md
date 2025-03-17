# 🎥 Demo

This guide walks you through setting up HESTIA as a microservice that:

✅ Logs structured events in JSON format.
✅ Process logs with Logstash. 
✅ Streams logs to Elasticsearch for centralized storage.
✅ Visualizes logs in Kibana & Grafana.
✅ Runs inside Docker & Kubernetes.


## 🎬 A Glance on HESTIA

>>>>>>> Screenshots of mounted place, kibana, and grafana


## 3.1 Start Services



chmod +x setup_microservices.sh
./setup_microservices.sh


docker-compose up -d

🔹 3.2 Start Hestia Logger Microservice

uvicorn app:app --host 0.0.0.0 --port 8000

🔹 3.3 Test Logging

curl http://localhost:8000/

🔹 3.4 Verify Logs in Kibana

    Open http://localhost:5601
    Go to "Stack Management" → "Index Patterns"
    Add hestia-logs-* as the index pattern.
    View logs in Discover.

🔹 3.5 Connect Grafana to Elasticsearch

    Open http://localhost:3000 (default: admin/admin).
    Add Elasticsearch as a data source.
    Set Index Pattern = hestia-logs-*.
    Create dashboards to visualize logs.

🎯 Summary

✅ Hestia Logger logs requests in structured format.
✅ Elasticsearch stores logs.
✅ Kibana visualizes logs in real-time.
✅ Grafana provides dashboards for analysis.


``` mermaid

graph TD
    A[Main Application (main.py)]
    B[Logging Decorator (log_execution in decorators.py)]
    C[Custom Logger (get_logger in core/custom_logger.py)]
    D[Service Loggers (api_service, database_service)]
    E[Global App Logger]
    F[Internal Logger (hestia_internal_logger in internal_logger.py)]
    G[Request Logger (requests_logger.py)]
    H[Logging Middleware (middleware.py)]
    I[Console Handler]
    J[File Handler (JSONFormatter)]
    K[Rotating File Handler (for internal logs)]

    A -->|calls| B
    B -->|retrieves| C
    C -->|creates| D
    B -->|logs events to| E
    A -->|logs internal events to| F
    A -->|triggers| G
    A -->|triggers| H
    G --> I
    G --> J
    H --> I
    H --> J
    F --> K

```


``` mermaid
graph LR
  A[Start] --> B{Error?};
  B -->|Yes| C[Hmm...];
  C --> D[Debug];
  D --> B;
  B ---->|No| E[Yay!];
```