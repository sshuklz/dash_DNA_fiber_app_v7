#!/bin/bash
set -e

source /opt/app-env/bin/activate

if [[ "$1" = 'run' ]]; then
    exec gunicorn DNAfibAPPv3:server -b 0.0.0.0:8000 --workers=4 --capture-output --log-file -
else
    exec "$@"
fi


