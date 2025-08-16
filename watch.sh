#!/bin/sh


# Ejecutar watchmedo para monitorear cambios
watchmedo auto-restart \
    --directory=./ \
    --pattern="*.py" \
    --recursive \
    --ignore-patterns="*.pyc;.git/*;env/*;__pycache__/*" \
    -- python run_server.py
