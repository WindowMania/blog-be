#!/bin/bash

poetry run uvicorn --host localhost --port 8000 src.app:app --reload