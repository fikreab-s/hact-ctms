#!/bin/bash
# =============================================================================
# OpenClinica CE — PostgreSQL Database Initialization
# Based on ParisZX/openclinica-docker-compose reference implementation.
# Creates 'clinica' role (SUPERUSER required) and 'openclinica' database.
# =============================================================================
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE ROLE clinica LOGIN ENCRYPTED PASSWORD '${OC_DB_PASSWORD:-change-me-oc-db-password}' SUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE;
    CREATE DATABASE openclinica WITH ENCODING='UTF8' OWNER=clinica;
EOSQL

echo "✅ OpenClinica database 'openclinica' created with SUPERUSER role 'clinica'."
