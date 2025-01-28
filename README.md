# Basketball Data Project

A containerized basketball data analytics platform that leverages multiple services to collect, process, store, and visualize basketball player and match data.

## Overview

This project is designed to automate and manage basketball data workflows using Docker containers. The platform includes ETL pipelines, data storage, web scraping, and data visualization, all orchestrated and monitored using modern containerization and orchestration tools.

## Architecture

The project consists of the following Docker containers, each with a specific role:

### Containers and Ports

1. **Airflow Container**
   - **Port Mapping:** `8080:8080`
   - **Role:** Manages and schedules ETL (Extract, Transform, Load) pipelines for data processing.

2. **Frontend Container**
   - **Port Mapping:** `2425:5000`
   - **Role:** Provides a web interface for users to analyze and visualize basketball player performance and match statistics.

3. **MinIO Container**
   - **Port Mapping:**
    -- ***Server:*** `9000:9000`
    -- ***UI:*** `9090:9090`

   - **Role:** Object storage for player images and other static assets.

4. **MongoDB Container**
   - **Port Mapping:**
    -- ***Server:*** `27017:27017`
    -- ***Mongo Express:*** `8081:8081`
   - **Role:** Stores shooting statistics for each match. Each document represents a different match.

5. **Postgres Container**
   - **Port Mapping:**
    -- ***Server:*** `5432:5432`
    -- ***PgAdmin4:*** `5050:80`
   - **Role:** Relational database for storing structured data about players, matches, and teams.

6. **Selenium Container**
   - **Port Mapping:**
    -- ***Selenium hub:*** `4444:4444`
    -- ***Publish port:*** `4442:4442`
    -- ***Suscribe port:*** `4443:4443`
   - **Role:** Used for web scraping to extract basketball data from external sources.

7. **Monitoring Container**
   - **Tools:** Prometheus and Grafana
   - **Role:** Monitors the health and performance of all containers and services.

## Features

- **ETL Pipelines:** Automated data processing workflows using Airflow.
- **Data Storage:** Combination of relational (Postgres) and NoSQL (MongoDB) databases for structured and semi-structured data.
- **Object Storage:** MinIO for storing player images and other files.
- **Web Scraping:** Selenium for extracting data from external websites.
- **Data Visualization:** Frontend interface using Taipy framework for users to analyze player and match data.
- **Monitoring:** Comprehensive monitoring using Prometheus and Grafana.

## Setup and Installation

1. **Prerequisites**
   - Docker installed on your system.
   - Docker Compose installed for orchestrating multiple containers.

2. **Clone the Repository**

   ```bash
   git clone https://github.com/ayllon99/basketball-project.git
   cd basketball-project
   ```

3. **Create a Docker Network**

   ```bash
   docker network create principal_network
   ```

4. **Build and Run Containers**
    Recomended compose each container one by one starting by postgres_container

   ```bash
   docker-compose up -d
   ```

5. **Access the Services**
   - **Airflow:** `http://localhost:8080`
   - **Frontend:** `http://localhost:2425`
   - **MinIO:** `http://localhost:9090`
   - **Mongo Express:** `http://localhost:8081`
   - **pgAdmin:** `http://localhost:5050`
   - **Selenium:** `http://localhost:4444`
   - **Prometheus:** `TBD`
   - **Grafana:** `TBD`

## Monitoring

The project includes Prometheus and Grafana for monitoring the health and performance of all containers. You can access the Grafana dashboard at `TBD` and Prometheus at `TBD`.

## Troubleshooting

- **Port Conflicts:** Ensure that the ports listed in the `docker-compose.yml` file are not in use by other services.
- **Service Startup Issues:** Check the logs for each container using `docker logs <container-name>`.
- **Network Issues:** Verify that all containers are connected to the `principal_network` network.

## Future Enhancements

- **Internationalization:** Add new pipelines to get data from more countries and leagues. (Extracting data only from Spain at this moment)
- **Scalability:** Implement horizontal scaling for the MongoDB and Postgres containers.
- **Backup and Recovery:** Add automated backup and recovery mechanisms for the databases.
- **Security:** Implement proper authentication and authorization for all services.
- **CI/CD:** Set up a CI/CD pipeline for automated testing and deployment.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss the changes.
