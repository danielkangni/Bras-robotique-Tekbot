#!/bin/bash
# ─────────────────────────────────────────────
#  Lancement du hand tracking + main robotique
# ─────────────────────────────────────────────

# Vérifier que le port Bluetooth est disponible
if [ ! -e /dev/rfcomm0 ]; then
    echo "⚠  /dev/rfcomm0 non trouvé."
    echo "   Lance d'abord start_hc05.sh dans un autre terminal :"
    echo "   ./start_hc05.sh"
    echo ""
    echo "   Démarrage quand même en mode test caméra..."
fi

# Active l'environnement virtuel
source venv/bin/activate

# Lance le hand tracking
python hand_tracking.py