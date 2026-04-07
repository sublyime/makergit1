#!/usr/bin/env bash
set -e

DB_NAME="makergit"
DB_USER="postgres"
DB_PASSWORD="NatEvan12!!"
DB_HOST="localhost"
DB_PORT="5432"
SCHEMA_FILE="$(dirname "$0")/db/schema.sql"
MIGRATION_FILE="$(dirname "$0")/db/migration.sql"

if ! command -v psql >/dev/null 2>&1; then
  echo "psql is not installed or not on PATH. Install PostgreSQL client tools first."
  exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d "|" -f 1 | grep -qw "$DB_NAME"; then
  echo "Database '$DB_NAME' already exists. Applying migration..."
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
else
  echo "Creating database '$DB_NAME'..."
  createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"

  echo "Applying initial schema from $SCHEMA_FILE..."
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"
fi

echo "Setup complete. Connector string:"
echo "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
unset PGPASSWORD
