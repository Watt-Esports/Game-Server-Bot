#!/bin/bash

# Check if the user is root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

# Update the system and install required packages
echo "Updating the system and installing required packages..."
DEBIAN_FRONTEND=noninteractive apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y lib32gcc-s1 curl tmux

# Create a steam user if it doesn't exist
if ! id -u steam > /dev/null 2>&1; then
    echo "Creating 'steam' user..."
    useradd -m steam
fi

# Switch to steam user
echo "Switching to 'steam' user..."
su - steam << 'EOF'

# Download SteamCMD
echo "Downloading SteamCMD..."
mkdir -p ~/steamcmd
cd ~/steamcmd
if [ ! -f steamcmd_linux.tar.gz ]; then
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" -o steamcmd_linux.tar.gz
fi
tar -xzf steamcmd_linux.tar.gz

# Install the CSGO server
echo "Installing CSGO server..."
./steamcmd.sh +force_install_dir ~/csgo_server +login anonymous +app_update 740 validate +quit

# Download the required library
echo "Downloading the required library..."
wget -O ~/csgo_server/bin/libgcc_s.so.1 "https://github.com/ValveSoftware/csgo-osx-linux/raw/master/bin/linux64/libgcc_s.so.1"

# Create the server.cfg file
echo "Creating server configuration file..."
mkdir -p ~/csgo_server/csgo/cfg
cat > ~/csgo_server/csgo/cfg/server.cfg << EOL
# Your server configuration settings
EOL

# Create the start script
echo "Creating the start script..."
cat > ~/start_csgo.sh << EOL
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

EOL
chmod +x ~/csgo_server/start.sh

echo "CSGO server installation complete."
echo "To start the server, run '~/csgo_server/start.sh' as the 'steam' user."
echo "Remember to update the rcon_password, sv_password, and tv_relaypassword in the server.cfg and gotv.cfg files."

EOF

exit 0
