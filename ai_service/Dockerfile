# pull official base image
FROM python:3.12

# set working directory
WORKDIR /usr/src/ai_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-pol \
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
RUN chmod a+x /usr/src/ai_service/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["sh", "/usr/src/ai_service/entrypoint.sh"]

CMD ["python3", "app/__init__.py"]