FROM python:latest

WORKDIR /app/tesis
COPY get_merge_landsat.py ./
COPY keys.json ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./get_merge_landsat.py"]