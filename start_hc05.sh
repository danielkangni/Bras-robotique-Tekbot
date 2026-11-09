#!/bin/bash

echo "Démarrage de la connexion HC-05..."

# Nettoyer les anciennes connexions
sudo killall rfcomm 2>/dev/null
sudo rfcomm release /dev/rfcomm0 2>/dev/null

sleep 1

MAC="00:24:12:D0:13:55"

# Boucle de reconnexion automatique
while true; do
    echo "Connexion en cours à $MAC..."
    sudo rfcomm connect /dev/rfcomm0 $MAC 1
    echo "Connexion perdue, reconnexion dans 2 secondes..."
    sleep 2
done
