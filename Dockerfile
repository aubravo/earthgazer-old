FROM python:latest

WORKDIR /app/tesis
RUN mkdir -p tmp
RUN mkdir -p res
COPY get_merge_landsat.py ./
COPY keys.json ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./get_merge_landsat.py"]