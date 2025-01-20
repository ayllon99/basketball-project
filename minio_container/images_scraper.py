from minio import Minio
import psycopg2
import pandas as pd
from seleniumwire import webdriver
import io


host = 'localhost'
conn = psycopg2.connect(
            dbname='cbmoron_database',
            host=host,
            user='root',
            password='root'
        )
cursor = conn.cursor()
cursor.execute("""
            SELECT player_id,player_name,player_link
            FROM players_info
                         """)

df = pd.DataFrame(cursor.fetchall())
df.columns = ['player_id', 'player_name', 'player_link']
cursor.close()
conn.close()

api_key = "1eTECadkp9l15cVUc3Kc"
pass_key = "TakZoqqGLlUN82ogGd1lG4AY3qccmNhmeuTpFRYb"
client = Minio(endpoint="localhost:9000",
               access_key=api_key,
               secret_key=pass_key,
               secure=False)
bucket_name = "player-image"

players_done = [int(obj.object_name.replace('.png', ''))
                for obj in client.list_objects(bucket_name)]
errors = [int(obj.object_name.replace('.txt', ''))
          for obj in client.list_objects("errors")]
done = players_done + errors
len(players_done)
len(errors)
len(done)
df = df[~df['player_id'].isin(done)]
left = len(df)

driver = webdriver.Chrome()

for index, row in df.iterrows():
    print('player_id in progress: ', row['player_id'])

    player_id = row['player_id']
    url = row['player_link']
    driver.get(url)
    foto_link = f'https://imagenes.feb.es/Foto.aspx?c={player_id}'
    try:
        for req in driver.requests:
            if req.url == foto_link:
                image_response = req.response.body
                content_length = int(req.response.headers
                                     .get('Content-Length'))
                break

        object_name = f"{player_id}.png"
        file = io.BytesIO(image_response)
        client.put_object(bucket_name, object_name,
                          data=file, length=content_length)
    except Exception:
        object_name = f"{player_id}.txt"
        data = b''
        data_stream = io.BytesIO(data)
        client.put_object('errors', object_name,
                          data=data_stream, length=len(data))
    left = left - 1
    print('images left: ', left)
