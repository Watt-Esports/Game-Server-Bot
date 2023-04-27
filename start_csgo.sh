#!/bin/bash
cd /home/steam/csgo_server/

screen_name="csgo_server"
server_info="Game: CS:GO | Game Type: 0 | Game Mode: 1 | Map Group: mg_active | Map: de_dust2 | Max Players: 12 | Tick Rate: 128 | GOTV Enabled: 1 | GOTV Auto Record: 1 | GOTV Delay: 90 | GOTV Max Clients: 10"

screen -dmS "$screen_name" ./srcds_run -game csgo -usercon +game_type 0 +game_mode 1 +mapgroup mg_active +map de_dust2 +servercfgfile server.cfg -maxplayers_override 12 -tickrate 128 +tv_enable 1 +tv_autorecord 1 +tv_adelay 90 +tv_maxclients 10 +exec gotv.cfg > test_screen_output.txt 2>&1

# Wait for a moment to allow the screen session to start
sleep 1

# Get the PID of the screen session
screen_pid=$(screen -ls | awk -v name="$screen_name" '$0 ~ name { gsub("[^0-9]", "", $1); print $1 }')

if [ -n "$screen_pid" ]; then
    echo "Screen session name: $screen_name"
    echo "Screen session PID: $screen_pid"
    echo "Server information: $server_info"
    echo "Server started successfully in a detached screen."
else
    echo "Failed to start the server in a detached screen."
fi
