#!/bin/bash

uvicorn --host 127.0.0.1 --port 8000 src.app:app --reload