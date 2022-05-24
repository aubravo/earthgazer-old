FROM python:latest

WORKDIR /app/gxiba
RUN mkdir -p tmp
RUN mkdir -p res
COPY landsat_merge.py ./
COPY keys.json ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./landsat_merge.py"]