#!/bin/bash
set -e
echo "EXECUTING DB-INIT SCRIPT..."

# Check if database exists
if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw codeAgent; then
    echo "Database 'codeAgent' already exists, skipping creation"
else
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE DATABASE codeAgent;
EOSQL
fi

echo "Database initialization completed successfully!"