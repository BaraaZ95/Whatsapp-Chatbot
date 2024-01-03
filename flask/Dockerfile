FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

LABEL MAINTAINER="Baraa Zaid <baraazaid95@protonmail.com>"
WORKDIR /src
COPY requirements.txt /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt
RUN pip install gunicorn
COPY . .

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "run:app"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

COPY --from=gloursdocker/docker / /

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "run:app"]
