from pymongo import MongoClient


def uploadtomongo(ti):
    match_ids = ti.xcom_pull(task_ids='scraping_match_info', key='match_ids')
    print(f'match_ids = {match_ids}')
    for match_id in match_ids:
        data = ti.xcom_pull(task_ids='scraping_match_info',
                            key=f'{match_id}_data_mongo')
        try:
            print(f'Uploading to mongo match_id={match_id}')
            client = MongoClient("mongodb://root:root@mongo-server:27017/")
            db = client["CBM"]
            collection = db["temp"]
            document = {f'{match_id}': data}
            collection.insert_one(document)
            print(f"Match_id= {match_id} Document inserted into {collection}")
        except Exception as e:
            print(f"Error inserting to mongo match_id= {match_id}")
            print(e)
