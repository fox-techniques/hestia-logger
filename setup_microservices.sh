#!/bin/bash
set -e  # Exit script if any command fails

###########################
# External Network Setup  #
###########################

# Define desired network parameters
NETWORK_NAME="elastic-net"
SUBNET="172.18.0.0/16"
GATEWAY="172.18.0.1"

# Function to check overlap between two subnets using Python's ipaddress module
check_overlap() {
    local subnet1=$1
    local subnet2=$2
    python - <<EOF
from ipaddress import ip_network
net1 = ip_network("$subnet1")
net2 = ip_network("$subnet2")
print(net1.overlaps(net2))
EOF
}

# Check if network exists and has attached resources
network_exists=$(docker network ls -q -f name="$NETWORK_NAME")
if [ -n "$network_exists" ]; then
    echo "🔍 Checking if '$NETWORK_NAME' has attached resources..."
    attached_containers=$(docker network inspect "$NETWORK_NAME" --format '{{range .Containers}}{{.Name}} {{end}}')
    if [ -z "$attached_containers" ]; then
        echo "🗑️ No containers attached to '$NETWORK_NAME'. Removing it..."
        docker network rm "$NETWORK_NAME"
        echo "✅ Network '$NETWORK_NAME' removed."
    else
        echo "⚠️ Network '$NETWORK_NAME' has attached containers: $attached_containers. Skipping removal."
    fi
fi

# Initialize conflict flag and details
conflict_found=0
declare -A conflicts

if [ -z "$(docker network ls -q -f name="$NETWORK_NAME")" ]; then
    echo "🔍 Scanning existing Docker networks for subnet conflicts with $SUBNET..."
    existing_networks=$(docker network ls -q)
    for net in $existing_networks; do
        net_name=$(docker network inspect "$net" --format '{{.Name}}')
        subnets=$(docker network inspect "$net" --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}')
        for existing_subnet in $subnets; do
            if [ -n "$existing_subnet" ]; then
                overlap=$(check_overlap "$SUBNET" "$existing_subnet")
                if [ "$overlap" == "True" ]; then
                    echo "⚠️ Conflict detected: Desired subnet $SUBNET overlaps with network '$net_name' (subnet: $existing_subnet)"
                    conflict_found=1
                    attached_containers=$(docker network inspect "$net" --format '{{range .Containers}}{{.Name}} (ID: {{.Name}}) {{end}}')
                    if [ -z "$attached_containers" ]; then
                        attached_containers="No containers attached."
                    fi
                    conflicts["$net_name"]="$existing_subnet | $attached_containers"
                fi
            fi
        done
    done

    if [ $conflict_found -eq 1 ]; then
        echo -e "\n❌ Failed to create network '$NETWORK_NAME' due to subnet overlaps."
        echo -e "\nConflicting network details:"
        for net in "${!conflicts[@]}"; do
            IFS='|' read -r conf_subnet conf_containers <<< "${conflicts[$net]}"
            echo "-------------------------------------------"
            echo "Network: $net"
            echo "Subnet: $conf_subnet"
            echo "Attached containers: $conf_containers"
            echo "-------------------------------------------"
        done
        echo -e "\nRecommendations:"
        echo "  • Either choose a different address space (e.g., change SUBNET to 172.19.0.0/16) OR"
        echo "  • Remove the conflicting network(s) if they are not needed."
        echo -e "\nTo remove a conflicting network (if no containers are using it), run:"
        for net in "${!conflicts[@]}"; do
            echo "    docker network rm $net"
        done
        exit 1
    fi

    echo "🌐 Creating external network '$NETWORK_NAME' with subnet '$SUBNET' and gateway '$GATEWAY'..."
    docker network create --driver bridge --subnet "$SUBNET" --gateway "$GATEWAY" "$NETWORK_NAME"
    if [ $? -eq 0 ]; then
        echo "✅ Network '$NETWORK_NAME' created successfully."
    else
        echo "❌ Failed to create network '$NETWORK_NAME'."
        exit 1
    fi
else
    echo "✅ Network '$NETWORK_NAME' already exists and will be reused."
fi

###########################
# Directory & File Setup  #
###########################

# Detect OS (Linux or Windows)
OS="$(uname -s)"
if [[ "$OS" == "Linux" ]]; then
    USER_HOME="$HOME"
elif [[ "$OS" =~ ^(MINGW|CYGWIN|MSYS) ]]; then
    USER_HOME="$(cygpath -u "$USERPROFILE")"
else
    echo "❌ Unsupported OS: $OS"
    exit 1
fi

# Define required directories for mounting
HLOG_DIR="$USER_HOME/docker/hestia-logs"
LOGSTASH_CONFIG_DIR="$USER_HOME/docker/logstash-config"
GRAFANA_DATA_DIR="$USER_HOME/docker/grafana-data"
LOGSTASH_CONFIG="$LOGSTASH_CONFIG_DIR/logstash.conf"

# Function to check and create directories
check_and_create_dir() {
    local DIR="$1"
    if [ ! -d "$DIR" ]; then
        echo "📁 Creating directory: $DIR"
        mkdir -p "$DIR"
    else
        echo "✅ Directory exists: $DIR"
    fi
}

# Function to check and fix permissions for directories
check_and_fix_permissions() {
    local DIR="$1"
    if [[ "$OS" == "Linux" ]]; then
        if [ ! -w "$DIR" ]; then
            echo "🔑 Fixing permissions on Linux for: $DIR"
            sudo chmod -R 755 "$DIR"
            sudo chown -R "$USER:$(id -gn)" "$DIR"
        else
            echo "✅ Permissions are correct: $DIR"
        fi
    elif [[ "$OS" =~ ^(MINGW|CYGWIN|MSYS) ]]; then
        echo "🔑 Windows detected, applying permissions: $DIR"
        icacls "$(cygpath -w "$DIR")" /grant "$USERNAME:R" /T > /dev/null 2>&1
        echo "✅ Permissions applied: $DIR"
    fi
}

# Function to copy and fix logstash.conf permissions
copy_and_fix_logstash() {
    if [ -f "./logstash.conf" ]; then
        echo "ℹ️ Copying updated logstash.conf from repository to $LOGSTASH_CONFIG..."
        cp ./logstash.conf "$LOGSTASH_CONFIG"
        echo "🔒 Fixing permissions for Logstash config: $LOGSTASH_CONFIG"
        chmod 600 "$LOGSTASH_CONFIG"
        echo "✅ Logstash config updated and permissions fixed: $(ls -l "$LOGSTASH_CONFIG")"
    else
        echo "❌ logstash.conf not found in repository. Please add it to your project."
        echo "You can create it with the following content:"
        echo "-------------------------------------------"
        cat <<EOL
input {
  file {
    path => "/var/logs/hestia/app.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}
output {
  elasticsearch {
    hosts => ["http://es01:9200", "http://es02:9200"]
    index => "hestia-logs"
    ilm_enabled => false
  }
  stdout { codec => rubydebug }
}
EOL
        echo "-------------------------------------------"
        echo "Save this as 'logstash.conf' in your project directory and rerun the script."
        exit 1
    fi
}

# Check and create directories
for DIR in "$HLOG_DIR" "$LOGSTASH_CONFIG_DIR" "$GRAFANA_DATA_DIR"; do
    check_and_create_dir "$DIR"
    check_and_fix_permissions "$DIR"
done

# Always copy and fix logstash.conf
copy_and_fix_logstash

echo "🎉 Setup complete! Mounted volumes:"
echo "  - Hestia Logs: $HLOG_DIR"
echo "  - Logstash Config: $LOGSTASH_CONFIG_DIR"
echo "  - Grafana Data: $GRAFANA_DATA_DIR"

###########################
# Docker Compose Startup  #
###########################

# Check if docker-compose.yml exists in current directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in current directory!"
    exit 1
fi

echo "🚀 Starting Docker Compose..."
if ! docker compose up --build -d; then
    echo "❌ Failed to start Docker Compose!"
    exit 1
fi

# Stop Docker Compose instructions
echo "🏁 To stop the microservices, run:"
echo "   docker compose down"