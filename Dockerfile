# syntax=docker/dockerfile:1

FROM python:3.11-alpine

WORKDIR /gxiba

RUN apk add --update make cmake gcc g++ gfortran py3-numpy cython

COPY requirements_docker.txt requirements_docker.txt

RUN pip3 install -r requirements_docker.txt

COPY . .

CMD ["python3", "-c", "print('SUCCESSFUL BUILD')" ]