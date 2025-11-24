FROM apache/airflow:2.8.1

# Switch to root only for system packages
USER root

# Install Java
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Switch back to airflow user for pip install
USER airflow

# Install Python packages (Airflow requires pip install as airflow)
RUN pip install --no-cache-dir pyspark==3.5.1 delta-spark
