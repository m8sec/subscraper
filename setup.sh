#!/usr/bin/env bash

# Author: m8r0wn
# Script: setup.sh

# Description:
# SubScraper setup script to verify all required packages
# are installed on the system.

#Check if Script run as root
if [[ $(id -u) != 0 ]]; then
	echo -e "\n[!] Setup script needs to run as root\n\n"
	exit 0
fi

echo -e "\n[*] Starting SubScraper setup script"
apt-get install python3 -y
pip3 install -r requirements.txt
