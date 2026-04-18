# =============================================================================
# OpenClinica CE — Docker Configuration
# Uses the community-maintained piegsaj/openclinica image (OC 3.13)
# which includes Tomcat + OpenClinica WAR pre-deployed.
#
# OC 3.13 has the same SOAP Web Services API as 3.17:
#   - StudyService, StudySubjectService, EventService, DataImportService
#   - CDISC ODM export, audit trails, e-signatures
#
# We customize it with our own datainfo.properties for HACT DB config.
# =============================================================================
FROM piegsaj/openclinica:oc-3.13

LABEL maintainer="HACT CTMS Team"
LABEL description="OpenClinica Community Edition on Tomcat (HACT integration)"

# Copy our custom datainfo.properties template
COPY datainfo.properties /opt/openclinica/datainfo.properties

# Copy entrypoint script
COPY entrypoint.sh /opt/openclinica/entrypoint.sh
RUN chmod +x /opt/openclinica/entrypoint.sh

# Create data directory
RUN mkdir -p ${CATALINA_HOME}/openclinica.data \
    && chmod 755 ${CATALINA_HOME}/openclinica.data

EXPOSE 8080

ENTRYPOINT ["/opt/openclinica/entrypoint.sh"]
