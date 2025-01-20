# To access website:
user: admin
password: pass

# Setting up mongo server
Create database CBM

Create collection shootings
# Copy volume to volume
docker run -it --rm -v docker_mongodb_mongodb_data_volume:/old -v mongo-server-volume:/new busybox sh -c 'cp -r /old/* /new/'
