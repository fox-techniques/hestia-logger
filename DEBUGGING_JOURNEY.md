## HESTIA Logger + Logstash + Elasticsearch + Kibana + Grafana Debugging Journey

### **Step 1: Setting Up Hestia Logger**

- First, we deployed `hestia-logger` using Docker Compose.
- Mounted `/home/anova/docker/hestia-logs` to `/var/logs/hestia` inside the container.
- Verified logs were being written to `/home/anova/docker/hestia-logs/app.log` using:
  
  ```bash
  ls -lh /home/anova/docker/hestia-logs
  tail -f /home/anova/docker/hestia-logs/app.log
  ```

- Sent a manual log to test logging:


  docker exec -it hestia-logger python -c "
  from hestia_logger.core.custom_logger import get_logger
  logger = get_logger('demo')
  logger.info({'event': 'test_log', 'message': 'Hello from Hestia!'})
  "

- Confirmed logs were written successfully.


### **Step 2: Deploying Logstash and Initial Debugging**

- Added Logstash to `docker-compose.yml`, mounting the same log directory.
- Initially, Logstash kept **crashing with JRuby-related errors**.
- Found the key issue: **Logstash was trying to read container Cgroups** but failing inside Docker.
- Attempted to disable Cgroups using:

  - LS_CGROUPS_ENABLED=false

  but the issue persisted.
- Fully disabled Cgroups by adding:

  - LS_CGROUPS_HIERARCHY_OVERRIDE="/"
  - LS_CGROUPS_PATH_OVERRIDE="/"
  - LOGSTASH_SKIP_CGROUPS_CHECK=true

- Also disabled JMX:

  - LS_JAVA_OPTS=-Xms256m -Xmx512m -Dlog4j2.disable.jmx=true

- Rebuilt and restarted Logstash:

  docker compose up --build -d

- Successfully launched Logstash after these changes.


### **Step 3: Checking If Logstash was Sending Logs**

- Checked if Logstash was running:

  docker ps | grep logstash

- Verified logs:

  docker logs logstash --tail 50

- Initially, Logstash was not sending logs to Elasticsearch.
- Checked if the index existed in Elasticsearch:

  curl -X GET "http://localhost:9200/_cat/indices?v"

- The index `hestia-logs` was missing, so we created it manually:

  curl -X PUT "http://localhost:9200/hestia-logs"

- After restarting Logstash:

  docker restart logstash

- Verified logs were now being sent to Elasticsearch:

  curl -X GET "http://localhost:9200/hestia-logs/_search?pretty"



### **Step 4: Deploying Kibana for Log Visualization**
- Added Kibana to `docker-compose.yml` and restarted the stack:

  docker compose up --build -d

- Checked if Kibana was running:

  docker ps | grep kibana

- Opened Kibana:

  http://localhost:5601

- Created a Data View in Kibana:
  - Went to **Stack Management → Data Views**
  - Created a Data View named `hestia-logs`
  - Selected `@timestamp` as the time field

- Opened **Discover** and confirmed logs were visible.


### **Step 5: Deploying Grafana for Dashboarding**

- Added Grafana to `docker-compose.yml` and restarted:

  docker compose up --build -d

- Checked if Grafana was running:

  docker ps | grep grafana

- Opened Grafana:

  http://localhost:3000

- Logged in with:
  - **Username:** admin
  - **Password:** admin

- Added **Elasticsearch as a Data Source**:
  - Went to **Settings → Data Sources**
  - Selected **Elasticsearch**
  - Entered **http://elasticsearch:9200** as the URL
  - Used `hestia-logs` as the index pattern

- Created a visualization:
  - **X-Axis:** `@timestamp`
  - **Y-Axis:** Count of logs
  - **Grouped by:** `level.keyword`

- Saved the visualization and added it to a new dashboard.


## **Final Result**

- **Hestia Logger** is correctly writing logs.
- **Logstash** is processing logs and sending them to Elasticsearch.
- **Elasticsearch** is storing logs in the `hestia-logs` index.
- **Kibana** is visualizing logs in Discover and Dashboards.
- **Grafana** is providing advanced monitoring with real-time dashboards.

**System is fully functional!**
