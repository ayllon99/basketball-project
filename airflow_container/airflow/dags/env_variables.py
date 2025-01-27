from airflow.models import Variable

pre_teams_link = 'https://baloncestoenvivo.feb.es/Equipo.aspx?i='
pre_match_link = 'https://baloncestoenvivo.feb.es/Partido.aspx?p='
pre_player_link = 'https://baloncestoenvivo.feb.es/jugador'
json_shots_link = 'https://intrafeb.feb.es/LiveStats.API/api/v1/ShotChart'

mongo_user = 'root'
mongo_pass = 'root'
mongo_server = 'mongo-server'
mongo_port = 27017
mongo_database = 'CBM'
mongo_collection = 'temp'

minio_key = Variable.get(key='minio_key')
minio_pass_key = Variable.get(key='minio_pass_key')
minio_bucket = Variable.get(key='minio_bucket')

postgres_connection = 'cbmoron_dev'

first_category = 'primera_feb'
url_primera = Variable.get(key='url_primera_feb')
file_path_primera = 'dates_files/dates_primera.txt'

second_category = 'segunda_feb'
url_segunda = Variable.get(key='url_segunda_feb')
file_path_segunda = 'dates_files/dates_segunda.txt'

third_category = 'tercera_feb'
url_tercera = Variable.get(key='url_tercera_feb')
file_path_tercera = 'dates_files/dates_tercera.txt'
