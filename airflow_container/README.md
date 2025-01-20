Dates from dates_file are detected automatically so I don't need to set them
each change of stage.
-------------------------------------------------------------------------------
modify from airflow.cfg:
# Variable: AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
sql_alchemy_conn = postgresql://airflow:airflow@postgres_container:5432/airflow
# Variable: AIRFLOW__CORE__DAGS_FOLDER
dags_folder = /opt/airflow/dags
# Variable: AIRFLOW__CORE__EXECUTOR
executor = LocalExecutor
# Variable: AIRFLOW__CORE__TEST_CONNECTION
test_connection = Enabled
# Variable: AIRFLOW__CORE__ENABLE_XCOM_PICKLING
enable_xcom_pickling = True
---------------------------------------------------
In airflow folder create dags folder for your dags
---------------------------------------------------
In webserver user: admin password: (standalone_admin_password.txt)
