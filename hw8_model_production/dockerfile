FROM python:3.8-slim AS compile-image

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /opt/titanic_model
COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python setup.py install && \
    rm -rf /opt/titanic_model/build /opt/titanic_model/dist /opt/titanic_model/titanic_model.egg-info && \
    python /opt/titanic_model/titanic_model.py train /opt/titanic_model/configs/model_config.yaml

FROM python:3.8-slim AS build-image

COPY --from=compile-image /opt/venv /opt/venv
COPY --from=compile-image /opt/titanic_model /opt/titanic_model

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /opt/titanic_model
