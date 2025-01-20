# Once the schema file is in the postgres_container (imported into var path) execute this:
psql -U "root -c "CREATE DATABASE basketball_database;"

psql -h "postgres_container" -p "5432" -U "root" -d "basketball_database" -f "/var/database_schema.sql"

# Airflow database backend
psql -U "root" -c "CREATE ROLE airflow WITH LOGIN PASSWORD 'airflow' SUPERUSER CREATEDB;"

psql -U "root" -c "CREATE DATABASE airflow OWNER airflow;"
