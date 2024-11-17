FROM python:3.12-alpine

WORKDIR /app

RUN pip install --upgrade pip

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app

CMD ["flask", "run", "--host=0.0.0.0"]