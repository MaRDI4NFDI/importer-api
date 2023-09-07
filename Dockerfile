FROM python:3.8-slim

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential

WORKDIR /usr/src/app

COPY server ./server
COPY start.sh ./
COPY requirements.txt ./
COPY uwsgi.ini ./

RUN pip install -r requirements.txt --src /usr/local/src

COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh

EXPOSE 80
CMD ["./start.sh"]