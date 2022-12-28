# syntax=docker/dockerfile:1

FROM ubuntu:jammy

WORKDIR /gxiba

RUN apt-get install gfortran gcc

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-c", "print('SUCCESSFUL BUILD')" ]