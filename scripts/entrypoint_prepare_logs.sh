#!/bin/bash

mkdir -p /app/materials/logs /app/users/logs
touch /app/materials/logs/reports.log /app/users/logs/reports.log
chown -R userdj:groupdjango /app/materials/logs /app/users/logs
