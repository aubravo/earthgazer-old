# syntax=docker/dockerfile:1

FROM python:3.11-alpine

WORKDIR /gxiba

RUN apk add --update make cmake gcc g++ gfortran py3-numpy cython

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-c", "print('SUCCESSFUL BUILD')" ]