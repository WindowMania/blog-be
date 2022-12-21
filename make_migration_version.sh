#!/bin/bash

echo "set migration name"
read m_name

alembic revision -m "$m_name"