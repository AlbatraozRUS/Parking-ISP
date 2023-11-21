FROM python:3.9

COPY . /app/
WORKDIR /app/

RUN apt-get update && \
	apt-get install -y locales && \
	sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
	dpkg-reconfigure --frontend=noninteractive locales

RUN pip install aiogram==2.25.1

ENV TG_TOKEN=6204595239:AAF0TMF7tTM4vfDi5ZuR-a4elY8BDLasVzM

CMD [ "python", "Run.py"]