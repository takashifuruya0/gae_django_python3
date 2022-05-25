FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN apt update && apt dist-upgrade -y && apt clean
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /src/gae
WORKDIR /src/gae
ENTRYPOINT ["python3", "manage.py", "daily_tweet"]
