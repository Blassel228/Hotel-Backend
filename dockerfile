FROM python:3.13-slim as builder

# Install uv
RUN pip install uv==0.1.25

ENV UV_CACHE_DIR=/tmp/uv_cache

WORKDIR /core

COPY pyproject.toml uv.lock ./

RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv venv /core/.venv && \
    . /core/.venv/bin/activate && \
    uv pip install --cache-dir=${UV_CACHE_DIR} -r requirements.txt

FROM python:3.13-slim as runtime

ENV VIRTUAL_ENV=/core/.venv \
    PATH="/core/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . .

RUN chmod +x ./app-start.sh

CMD ["./app-start.sh"]