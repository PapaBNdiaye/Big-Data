FROM ubuntu:22.04

USER root

# Installe Java 17, Hadoop, Python3
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk wget python3 python3-pip && \
    wget https://archive.apache.org/dist/hadoop/core/hadoop-2.7.4/hadoop-2.7.4.tar.gz && \
    tar -xzf hadoop-2.7.4.tar.gz -C /opt && \
    rm hadoop-2.7.4.tar.gz

RUN pip install pandas numpy pyarrow hdfs jupyter duckdb pyspark

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop-2.7.4
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

WORKDIR /app
COPY main.py /app/

EXPOSE 9870 8088

CMD ["python3", "main.py"]
CMD ["python3", "main.py"]
