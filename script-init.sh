#!/bin/bash
cd /home/simop/api-dados-extraidos-sesdf

gunicorn --bind 0.0.0.0:5003 wsgi:app
