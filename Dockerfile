FROM python:3.11-buster

ENV WORKDIR_PATH /usr/src/app
ENV DOCKER 1
ARG USER_CONTAINER
ARG ENV_FOR_DYNACONF
ARG SECRET_KEY


RUN mkdir -p $WORKDIR_PATH
WORKDIR $WORKDIR_PATH
RUN apt-get update -y && apt-get install vim nano -y && pip install pipenv

COPY --chmod=0444 ./Pipfile* ./
RUN pipenv install --deploy --system --clear

COPY --chmod=0444 . .
RUN find $WORKDIR_PATH -type d -exec chown $USER_CONTAINER:$USER_CONTAINER {} \;
RUN find $WORKDIR_PATH -type d -exec chmod 755 {} \;

#HEALTHCHECK --interval=5m --timeout=10s \
#  CMD python healthcheck_probe.py


USER $USER_CONTAINER
CMD python manage.py runserver 0.0.0.0:8000
