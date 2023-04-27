#!/bin/bash
screen_name="csgo_server"
screen_pid=$(screen -ls | awk -v name="$screen_name" '$0 ~ name { gsub("[^0-9]", "", $1); print $1 }')

if [ -n "$screen_pid" ]; then
    echo "Killing screen session: $screen_name with PID: $screen_pid"
    kill -SIGTERM "$screen_pid"
    echo "Screen session killed."
else
    echo "No screen session with the name '$screen_name' was found."
fi
