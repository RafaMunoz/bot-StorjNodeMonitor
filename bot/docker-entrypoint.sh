#!/bin/sh
set -e

if [[ -z $TELEGRAM_TOKEN ]]; then
	echo "A TELEGRAM_TOKEN is required to run this container."
	exit 1
fi

if [[ -z $URI_MONGODB ]]; then
	echo "A URI_MONGODB is required to run this container."
	exit 1
fi

/usr/sbin/crond -b -l 9

exec "$@"
