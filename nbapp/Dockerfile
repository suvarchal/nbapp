# Use an official Python runtime as a parent image
FROM python:3.6-slim

COPY ./requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m nbuser
RUN groupadd docker
RUN usermod -aG docker nbuser


USER nbuser
ENV HOME=/home/nbuser
WORKDIR $HOME

COPY ./app.py $HOME/app.py
COPY ./static $HOME/static
COPY ./templates $HOME/templates
COPY ./boot.sh $HOME/boot.sh

EXPOSE 5000

#CMD ["gunicorn","-b 0.0.0.0:5000","-w 8","app:app"]
CMD ["./boot.sh"]
