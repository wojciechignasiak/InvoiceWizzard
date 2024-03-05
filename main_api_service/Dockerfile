# pull official base image
FROM python:3.11

# set working directory
WORKDIR /usr/src/main_api_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    musl-dev \
    libffi-dev \
    bash \
    git \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# install Python dependencies
RUN pip install -U cffi pip setuptools

# copy requirements and install
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
