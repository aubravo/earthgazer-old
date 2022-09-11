from ubuntu:22.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install python3.10 python3-pip default-jdk curl
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV SPARK_HOME="/usr/local/lib/python3.10/dist-packages/pyspark"
RUN echo "JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))" >> ~/.bash.rc
RUN geopyspark install-jar

