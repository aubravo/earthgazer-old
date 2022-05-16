FROM python:latest

WORKDIR /app/tesis
COPY get_merge_landsat.py ./
COPY keys.json ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt