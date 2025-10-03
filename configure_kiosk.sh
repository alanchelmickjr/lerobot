#!/bin/bash

# Configure Ubuntu system for kiosk/console setup to prevent automatic sleep and screen lock

echo "Setting idle-delay to 0 to prevent session idle timeout"
gsettings set org.gnome.desktop.session idle-delay 0

echo "Disabling screen lock"
gsettings set org.gnome.desktop.screensaver lock-enabled false

echo "Masking sleep targets to prevent system sleep, suspend, hibernate, and hybrid-sleep"
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

echo "Verifying settings..."

echo "Idle delay: $(gsettings get org.gnome.desktop.session idle-delay)"
echo "Screen lock enabled: $(gsettings get org.gnome.desktop.screensaver lock-enabled)"

echo "Sleep targets status:"
systemctl list-units --type=target --state=masked | grep -E "(sleep|suspend|hibernate|hybrid-sleep)" || echo "No masked sleep targets found"

echo "Configuration completed. The system should now not sleep or lock the screen automatically."