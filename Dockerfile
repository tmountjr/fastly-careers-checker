FROM python:3.9-alpine

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN echo "0 0 * * * /usr/local/bin/python /app/main.py >> /proc/1/fd/1 2>> /proc/1/fd/2" >> /etc/crontabs/root

WORKDIR /app
COPY main.py /app/main.py
COPY manifest.json /app/manifest.json
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "/entrypoint.sh" ]