from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.exceptions import AirflowFailException
from env_variables import *
import extracting.checking_new_results as checking_new_results


def trigger_evaluator_primera(ti):
    """
    This function checks if new matches were found to scrape. If no new matches
    are found, it raises an AirflowFailException to stop further execution. If
    new matches are found, it proceeds to trigger the next DAG.

    Args:
        ti (TaskInstance): The TaskInstance object containing execution context
                           and information.

    Returns:
        None

    Raises:
        AirflowFailException: If no new matches are found to scrape.
    """
    result_primera = ti.xcom_pull(task_ids='evaluate_and_trigger_primera',
                                  key='trigger_evaluator')
    if result_primera is False:
        print('Result == False here the exception comes')
        raise AirflowFailException('-----NO NEW MATCHES TO SCRAPE-----')
    print('New matches to scrape, triggering next DAG...')


def trigger_evaluator_segunda(ti):
    """
    Triggers the next DAG if there are new matches to scrape.

    Args:
        ti (TaskInstance): The TaskInstance object containing context and
                           information about the task.

    Returns:
        None: This function does not return any value.

    Raises:
        AirflowFailException: If there are no new matches to scrape,
                              indicated by the result being False.

    Note:
        This function pulls a result from the 'evaluate_and_trigger_segunda'
        task using XCom. If the result is False, it raises an exception to
        halt further processing; otherwise, it proceeds to trigger the next
        DAG.
    """
    result_segunda = ti.xcom_pull(task_ids='evaluate_and_trigger_segunda',
                                  key='trigger_evaluator')
    if result_segunda is False:
        print('Result == False here the exception comes')
        raise AirflowFailException('-----NO NEW MATCHES TO SCRAPE-----')
    print('New matches to scrape, triggering next DAG...')


def trigger_evaluator_tercera(ti):
    """
    Checks if there are new matches to scrape and triggers the next DAG
    accordingly.

    This function pulls the result from the 'evaluate_and_trigger_tercera'
    task.
    If the result indicates no new matches, it raises an AirflowFailException
    to stop further processing. Otherwise, it proceeds to trigger the next DAG.

    Args:
        ti (TaskInstance): The TaskInstance object from Airflow.

    Returns:
        None

    Raises:
        AirflowFailException: If there are no new matches to scrape.
    """
    result_tercera = ti.xcom_pull(task_ids='evaluate_and_trigger_tercera',
                                  key='trigger_evaluator')
    if result_tercera is False:
        print('Result == False here the exception comes')
        raise AirflowFailException('-----NO NEW MATCHES TO SCRAPE-----')
    print('New matches to scrape, triggering next DAG...')


with DAG(
    dag_id="start_trigger_dag",
    schedule_interval="@daily",
    catchup=False,
    description='Primera,Segunda and Tercera FEB',
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime(2022, 11, 6)
        },
) as dag:

    evaluate_and_trigger_primera = PythonOperator(
        task_id="evaluate_and_trigger_primera",
        python_callable=checking_new_results.new_results,
        op_kwargs={'url': url_primera,
                   'file_path': file_path_primera}

    )

    evaluate_and_trigger_segunda = PythonOperator(
        task_id="evaluate_and_trigger_segunda",
        python_callable=checking_new_results.new_results,
        op_kwargs={'url': url_segunda, 'file_path': file_path_segunda}

    )

    evaluate_and_trigger_tercera = PythonOperator(
        task_id="evaluate_and_trigger_tercera",
        python_callable=checking_new_results.new_results,
        op_kwargs={'url': url_tercera, 'file_path': file_path_tercera}

    )

    should_trigger_primera = PythonOperator(
        task_id="should_trigger_primera",
        python_callable=trigger_evaluator_primera
    )

    should_trigger_segunda = PythonOperator(
        task_id="should_trigger_segunda",
        python_callable=trigger_evaluator_segunda
    )

    should_trigger_tercera = PythonOperator(
        task_id="should_trigger_tercera",
        python_callable=trigger_evaluator_tercera
    )

    trigger_dag_new_matchday_primera = TriggerDagRunOperator(
        task_id="trigger_dag_new_matchday_primera",
        trigger_dag_id="new_matchday_dag_primera_FEB",
    )

    trigger_dag_new_matchday_segunda = TriggerDagRunOperator(
        task_id="trigger_dag_new_matchday_segunda",
        trigger_dag_id="new_matchday_dag_segunda_FEB",
    )

    trigger_dag_new_matchday_tercera = TriggerDagRunOperator(
        task_id="trigger_dag_new_matchday_tercera",
        trigger_dag_id="new_matchday_dag_tercera_FEB",
    )

    evaluate_and_trigger_primera >> evaluate_and_trigger_segunda >> evaluate_and_trigger_tercera
    evaluate_and_trigger_primera >> should_trigger_primera >> trigger_dag_new_matchday_primera
    evaluate_and_trigger_segunda >> should_trigger_segunda >> trigger_dag_new_matchday_segunda
    evaluate_and_trigger_tercera >> should_trigger_tercera >> trigger_dag_new_matchday_tercera
