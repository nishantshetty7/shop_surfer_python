#!/bin/sh

gunicorn shop_surfer_python.wsgi:application -b 0.0.0.0:80