
FROM python:3.10

# Cache dependencies installation
COPY ./pyproject.toml /engy/pyproject.toml

RUN pip install -e /engy

COPY ./src /engy/src

# Install required libraries
RUN pip install Flask Flask-CORS

COPY ./camera_app/ /app/

WORKDIR /app

CMD [ "python", "server.py" ]
