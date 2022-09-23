## Install application locally

```
python3 -m venv py3-env
source py3-env/bin/activate
pip install -r requirements.txt
```

Launch the application using the built in Dash development server.

```
python3 DNAfibAPPv3.py
```

## Build and run locally with Docker

Build the docker image (``--platform=linux/amd64`` required only for M1/2 macs)

```
export TAG=$(git describe --tags --dirty)
docker build . --platform=linux/amd64 -t fiber:latest -t fiber:$TAG --build-arg APP_VERSION=$TAG
```

Run the application from the image:

```
docker run --platform=linux/amd64 --rm -p 8000:8000 fiber:latest
```

