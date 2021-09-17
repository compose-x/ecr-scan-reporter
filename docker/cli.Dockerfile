ARG ARCH=
ARG PY_VERSION=3.8
ARG BASE_IMAGE=public.ecr.aws/compose-x/python:${PY_VERSION}
ARG LAMBDA_IMAGE=public.ecr.aws/lambda/python:latest
FROM $BASE_IMAGE as builder

WORKDIR /opt
COPY ecr_scan_reporter /opt/ecr_scan_reporter
COPY pyproject.toml MANIFEST.in README.rst LICENSE /opt/
RUN python -m pip install pip -U; python -m pip install poetry; poetry build

FROM $BASE_IMAGE

ENV PATH=/app/.local/bin:${PATH}
COPY --from=builder /opt/dist/ecr_scan_reporter-*.whl ${LAMBDA_TASK_ROOT:-/app/}/
WORKDIR /app
RUN echo $PATH ; pip install pip -U --no-cache-dir && pip install wheel --no-cache-dir\
    && pip install *.whl --no-cache-dir;\
    yum upgrade -y;\
    yum autoremove -y; yum clean packages; yum clean headers; yum clean metadata; yum clean all; rm -rfv /var/cache/yum
WORKDIR /
ENTRYPOINT ["ecr_scan_reporter"]
