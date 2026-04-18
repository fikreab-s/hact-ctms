#!/bin/bash
# =============================================================================
# OpenClinica CE — Container Entrypoint
# Substitutes environment variables into datainfo.properties, then starts Tomcat.
# The piegsaj/openclinica image already has the WAR deployed at:
#   /usr/local/tomcat/webapps/OpenClinica/
# =============================================================================
set -e

PROPS_DIR="${CATALINA_HOME}/webapps/OpenClinica/WEB-INF/classes"
PROPS_FILE="${PROPS_DIR}/datainfo.properties"

# Check if OC WAR is already deployed
if [ -d "${CATALINA_HOME}/webapps/OpenClinica/WEB-INF" ]; then
    echo "✅ OpenClinica WAR is deployed."
else
    echo "⏳ Waiting for OpenClinica WAR deployment..."
    for i in $(seq 1 30); do
        if [ -d "${CATALINA_HOME}/webapps/OpenClinica/WEB-INF" ]; then
            echo "✅ OpenClinica WAR deployed."
            break
        fi
        if [ "$i" -eq 30 ]; then
            echo "⚠️ WAR not yet deployed — starting Tomcat anyway (it will auto-deploy)."
        fi
        sleep 2
    done
fi

# Substitute environment variables into datainfo.properties
if [ -f "/opt/openclinica/datainfo.properties" ] && [ -d "$PROPS_DIR" ]; then
    echo "📝 Configuring datainfo.properties..."
    sed "s|\${OC_DB_PASSWORD}|${OC_DB_PASSWORD:-change-me-oc-db-password}|g" \
        /opt/openclinica/datainfo.properties > "$PROPS_FILE"
    echo "✅ datainfo.properties configured."
else
    echo "⚠️ Skipping datainfo.properties config (template or target dir not found)."
fi

# Create data directory if needed
mkdir -p "${CATALINA_HOME}/openclinica.data" 2>/dev/null || true

echo "🚀 Starting OpenClinica on Tomcat..."
exec catalina.sh run
