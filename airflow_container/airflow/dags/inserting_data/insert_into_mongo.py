from pymongo import MongoClient
from ..env_variables import *


def uploadtomongo(ti):
    """
    Uploads scraped match data to a MongoDB database.

    This function pulls match IDs and their corresponding data from Airflow's
    XCom system.
    It then connects to a MongoDB instance and inserts the data into a
    temporary collection.

    Args:
        ti (TaskInstance): The TaskInstance object containing the context for
                           the task.

    Returns:
        None

    Raises:
        Exception: If there is an error inserting data into MongoDB.
    """
    match_ids = ti.xcom_pull(task_ids='scraping_match_info', key='match_ids')
    print(f'match_ids = {match_ids}')
    for match_id in match_ids:
        data = ti.xcom_pull(task_ids='scraping_match_info',
                            key=f'{match_id}_data_mongo')
        try:
            print(f'Uploading to mongo match_id={match_id}')
            client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@{mongo_server}:{mongo_port}/")
            db = client[f"{mongo_database}"]
            collection = db[f"{mongo_collection}"]
            document = {f'{match_id}': data}
            collection.insert_one(document)
            print(f"Match_id= {match_id} Document inserted into {collection}")
        except Exception as e:
            print(f"Error inserting to mongo match_id= {match_id}")
            print(e)
