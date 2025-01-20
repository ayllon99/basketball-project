create a sql_files folder with your schema.sql file
# Once the backup file is in the postgres_container (imported into var path) execute this:
psql -U "root -c "CREATE DATABASE cbmoron_database;"
psql -h "postgres_container" -p "5432" -U "root" -d "cbmoron_database" -f "/var/postgres_back_19-01-2025/19-01-2025-noroles-complete.sql"

# Airflow database backend
psql -U "root" -c "CREATE ROLE airflow WITH LOGIN PASSWORD 'airflow' SUPERUSER CREATEDB;"
psql -U "root" -c "CREATE DATABASE mydatabase OWNER airflow;"
psql -h "postgres_container" -p "5432" -U "root" -d "airflow" -f "/var/postgres_back_19-01-2025/airflow-db-back-19-01-2025.sql"