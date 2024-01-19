# pull official base image
FROM python:3.11

# set working directory
WORKDIR /usr/src/ai_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# install Python dependencies
RUN pip install -U cffi pip setuptools

# copy requirements and install
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# add app
COPY . .

CMD ["python3", "app/__init__.py"]