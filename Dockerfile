FROM python:3.8

RUN mkdir -p /gxiba/src

WORKDIR /gxiba/src

COPY requirements.txt /gxiba/src
RUN pip install --no-cache-dir -r requirements.txt

COPY . /gxiba/src

CMD ["python", "setup.py"]