FROM python:3.13-slim AS builder

RUN pip install "uv==0.1.25"
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip compile pyproject.toml --output-file=requirements.txt

FROM python:3.13-slim AS runtime

RUN pip install "uv==0.1.25"

WORKDIR /app
COPY . .

RUN uv pip install --system -r requirements.txt

RUN pip uninstall -y uv && rm -rf /root/.cache/uv

RUN chmod +x ./app-start.sh

EXPOSE 8000
CMD ["./app-start.sh"]