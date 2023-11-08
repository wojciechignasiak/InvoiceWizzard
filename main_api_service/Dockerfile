#pull official base image
FROM python:3.11-alpine

# set working directory
WORKDIR /usr/src/main_api_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apk update \
    && apk upgrade
RUN apk add bash

RUN apk add py3-argon2-cffi py3-six
RUN apk add gcc musl-dev libffi-dev && \
    pip install -U  cffi pip setuptools

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# add app
COPY . .

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod a+x /usr/src/main_api_service/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["sh", "/usr/src/main_api_service/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]