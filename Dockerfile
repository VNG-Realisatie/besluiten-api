# Stage 1 - Compile needed python dependencies
FROM python:3.9-alpine AS build
RUN apk --no-cache add \
    gcc \
    musl-dev \
    pcre-dev \
    linux-headers \
    postgresql-dev \
    python3-dev \
    # libraries installed using git
    git \
    # lxml dependencies
    libxslt-dev \
    # pillow dependencies
    jpeg-dev \
    openjpeg-dev \
    zlib-dev

WORKDIR /app

COPY ./requirements /app/requirements
RUN pip install -r requirements/production.txt
# Don't copy source code here, as changes will bust the cache for everyting
# below


# Stage 2 - build frontend
FROM mhart/alpine-node:16 AS frontend-build

WORKDIR /app

COPY ./*.json /app/
RUN npm install

COPY ./*.js ./.babelrc /app/
COPY ./build /app/build/

COPY src/brc/sass/ /app/src/brc/sass/
RUN npm run build


# Stage 3 - Prepare CI tests image
FROM build AS jenkins

RUN apk --no-cache add \
    postgresql-client

COPY --from=build /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=build /app/requirements /app/requirements

RUN pip install -r requirements/ci.txt --exists-action=s

# Stage 3.2 - Set up testing config
COPY ./setup.cfg /app/setup.cfg
COPY ./bin/runtests.sh /runtests.sh

# Stage 3.3 - Copy source code
COPY --from=frontend-build /app/src/brc/static/bundles /app/src/brc/static/bundles

COPY ./src /app/src
ARG COMMIT_HASH
ENV GIT_SHA=${COMMIT_HASH}

RUN mkdir /app/log && rm /app/src/brc/conf/test.py
CMD ["/runtests.sh"]


# Stage 4 - Build docker image suitable for execution and deployment
FROM python:3.9-alpine AS production
RUN apk --no-cache add \
    ca-certificates \
    mailcap \
    make \
    musl \
    pcre \
    postgresql \
    # lxml dependencies
    libxslt \
    # pillow dependencies
    jpeg \
    openjpeg \
    zlib \
    nodejs

COPY --from=build /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=build /usr/local/bin/sphinx-build /usr/local/bin/sphinx-build
# required for swagger2openapi conversion
COPY --from=frontend-build /app/node_modules /app/node_modules

# Stage 4.2 - Copy source code
WORKDIR /app
COPY ./bin/docker_start.sh /start.sh
RUN mkdir /app/log

COPY --from=frontend-build /app/src/brc/static/bundles /app/src/brc/static/bundles

COPY ./src /app/src
COPY ./docs /app/docs
ARG COMMIT_HASH
ENV GIT_SHA=${COMMIT_HASH}

ENV DJANGO_SETTINGS_MODULE=brc.conf.docker

ARG SECRET_KEY=dummy

# build docs
RUN make -C docs html

# Run collectstatic, so the result is already included in the image
RUN python src/manage.py collectstatic --noinput

EXPOSE 8000
CMD ["/start.sh"]
