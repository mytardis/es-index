FROM python:3.7

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

RUN pip install -U pip

RUN pip install -r requirements.txt

CMD ["python", "index.py", "--rebuild"]
