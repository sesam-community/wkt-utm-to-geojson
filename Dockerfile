FROM python:3-alpine
MAINTAINER Baard H. Rehn Johansen "baard.johansen@sesam.io"

COPY ./service /service

RUN apk update
RUN apk add --update build-base
RUN apk add --update geos-dev --repository http://dl-3.alpinelinux.org/alpine/edge/testing/
RUN pip install -r /service/requirements.txt

EXPOSE 5000/tcp
ENTRYPOINT ["python"]
CMD ["./service/service.py"]

