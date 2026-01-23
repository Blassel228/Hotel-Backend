#!/usr/bin/env -S bash

set -e
python -m alembic upgrade head
python -m app.main
