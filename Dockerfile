FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get clean

COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt --no-cache-dir

COPY src /src

RUN chmod 777 /src/runApp.sh && chmod +x /src/runApp.sh
CMD ["/src/runApp.sh"]


