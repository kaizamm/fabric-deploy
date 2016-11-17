#!/bin/bash
#Nginx: delete data in the cache
NGINX_HOME=$1
NGINX_DAEMON=$2

f=`ls "$1"/data | wc -l`
if ((f==0));then
        echo "cache is empty"
    exit 0
fi

pkill -9 nginx   && rm -rf "$1"/data/*
"${NGINX_DAEMON}" -s reload

