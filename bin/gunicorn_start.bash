#!/bin/bash

NAME="movincart"                                  # Name of the application
DJANGODIR=/home/ubuntu/movincart                  # Django project directory
SOCKFILE=/movincart/movincart_web/gunicorn.sock         # we will communicte using this unix socket
USER=movincart                                     # the user to run as
GROUP=movincart                                   # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=movincart.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=movincart.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
#if virtualenv exists
source /home/ubuntu/movincart_env/movincart_env/bin/activate

cd $DJANGODIR
#source ../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
#export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --bind=unix:$SOCKFILE


