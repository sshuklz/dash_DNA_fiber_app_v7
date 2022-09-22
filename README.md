## Build and run locally with Docker

```
export TAG=0.1
# export TAG=$(git describe --tags --dirty)
docker build . --platform=linux/amd64 -t fiber:latest -t fiber:$TAG --build-arg APP_VERSION=$TAG
docker run --platform=linux/amd64 --rm -p 8000:8000 fiber:latest
```
