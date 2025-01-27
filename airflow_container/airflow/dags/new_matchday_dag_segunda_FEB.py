from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from env_variables import *
import inserting_data.inserting_into_postgres as inserting_into_postgres
import inserting_data.insert_into_mongo as insert_into_mongo
import extracting.results_scraper as results_scraper
import extracting.evaluating as evaluating
import extracting.new_match_day as new_match_day


with DAG(
    dag_id='new_matchday_dag_segunda_FEB',
    schedule=None,
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 11, 6)
     }) as dag:

    evaluate_matchdays = PythonOperator(
        task_id="evaluate_matchdays",
        python_callable=evaluating.new_results,
        op_kwargs={'url': url_segunda, 'file_path': file_path_segunda}
    )

    scraping_results = PythonOperator(
        task_id='scraping_results',
        python_callable=results_scraper.results_scraper,
        op_kwargs={'url': url_segunda,
                   'postgres_connection': postgres_connection,
                   'category': second_category},
        do_xcom_push=True
    )

    uploading_results = PythonOperator(
        task_id='results_insert_data',
        python_callable=results_scraper.inserting_to_postgres,
        op_kwargs={'url': url_segunda,
                   'postgres_connection': postgres_connection,
                   'category': second_category},
        do_xcom_push=True
    )

    scraping_info = PythonOperator(
        task_id='scraping_match_info',
        python_callable=new_match_day.match_day,
        do_xcom_push=True
    )

    insert_into_postgres_players = PythonOperator(
            task_id='players_matches_stats_insert_data',
            python_callable=inserting_into_postgres.players_matches_stats_insert_data,
            op_kwargs={'url': url_segunda,
                       'postgres_connection': postgres_connection,
                       'category': second_category},
            do_xcom_push=True
        )

    with TaskGroup("uploading_match_data",
                   tooltip="""Task Group for inserting data
                              into mongo and postgres""") as uploading_info:

        upload_to_mongo = PythonOperator(
            task_id='upload_to_mongo',
            python_callable=insert_into_mongo.uploadtomongo,
            do_xcom_push=True
        )

        insert_into_postgres_teams = PythonOperator(
            task_id='teams_match_stats_insert_data',
            python_callable=inserting_into_postgres.teams_match_stats_insert_data,
            op_kwargs={'url': url_segunda,
                       'postgres_connection': postgres_connection,
                       'category': second_category},
            do_xcom_push=True
        )

        insert_into_postgres_match = PythonOperator(
            task_id='match_partials_insert_data',
            python_callable=inserting_into_postgres.match_partials_insert_data,
            op_kwargs={'url': url_segunda,
                       'postgres_connection': postgres_connection,
                       'category': second_category},
            do_xcom_push=True
        )

        insert_into_postgres_shootings = PythonOperator(
            task_id='shootings_insert_data',
            python_callable=inserting_into_postgres.shootings_insert_data,
            op_kwargs={'url': url_segunda,
                       'postgres_connection': postgres_connection,
                       'category': second_category},
            do_xcom_push=True
        )

        insert_into_postgres_available = PythonOperator(
            task_id='shooting_chart_availability_insert_data',
            python_callable=inserting_into_postgres.shooting_chart_availability_insert_data,
            op_kwargs={'url': url_segunda,
                       'postgres_connection': postgres_connection,
                       'category': second_category},
            do_xcom_push=True
        )

    trigger_dag_new_player_in_database = TriggerDagRunOperator(
            task_id="trigger_dag_new_player_in_database",
            trigger_dag_id="new_player_stage_team_in_database"
        )

    evaluate_matchdays >> scraping_results >> scraping_info
    scraping_info >> insert_into_postgres_players >> uploading_info
    uploading_info >> trigger_dag_new_player_in_database
    scraping_results >> uploading_results
