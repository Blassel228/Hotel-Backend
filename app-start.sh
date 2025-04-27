#!/usr/bin/env -S bash

set -e
alembic upgrade head
python -m app.main
