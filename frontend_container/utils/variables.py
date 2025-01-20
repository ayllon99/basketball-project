from dotenv import load_dotenv
import os


load_dotenv()

config = {
    'data_not_found_path': os.getenv('data_not_found_path'),
    'error_proc_data_path': os.getenv('error_proc_data_path'),
    'icon_path': os.getenv('icon_path'),
    'image_not_found_path': os.getenv('image_not_found_path'),

    'postgres_host': os.getenv('postgres_host'),
    'postgres_database': os.getenv('postgres_database'),
    'postgres_user': os.getenv('postgres_user'),
    'postgres_pass': os.getenv('postgres_pass'),

    'minio_host': os.getenv('minio_host'),
    'minio_port': os.getenv('minio_port'),
    'minio_api_key': os.getenv('minio_api_key'),
    'minio_pass_key': os.getenv('minio_pass_key'),
    'bucket_name': os.getenv('bucket_name')
}
