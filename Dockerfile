FROM python:3.10-slim-bullseye

WORKDIR /opt/app-build
RUN python3 -m venv /opt/app-env

# install pinned dependencies from requirements.txt
COPY requirements.txt /opt/app-build
RUN /opt/app-env/bin/python -m pip install wheel
RUN /opt/app-env/bin/python -m pip install -r requirements.txt

WORKDIR /opt/app-run
ARG APP_VERSION
ENV APP_VERSION=$VERSION

COPY assets assets
COPY entrypoint.sh *.py .
RUN chmod a+x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/opt/app-run/entrypoint.sh"]
CMD ["run"]
