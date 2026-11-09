# Hand Bot - Bras Robotique Contrôlé par Reconnaissance Gestuelle

## 🎯 But du Projet
Le **Hand Bot** est un système de main robotique qui reproduit les mouvements de votre propre main en temps réel. Grâce à la vision par ordinateur et à l'intelligence artificielle (hand tracking) capturée par votre webcam, le programme analyse vos gestes, et envoie via une connexion Bluetooth les commandes correspondantes à une carte Arduino qui actionne les servomoteurs d'une main articulée.

Il s'agit du projet éducatif et démonstratif idéal regroupant de l'impression 3D, de l'électronique (Arduino) et du développement logiciel (Python & IA) en une interface homme-machine très intuitive.

---

## 🛠️ Prérequis et Installation

### 1. Préparation Matérielle (Électronique)
- Branchez l'Arduino avec les 5 servomoteurs de la main robotique.
- Alimentez correctement la carte et assurez-vous que le module Bluetooth (HC-05) est sous tension.
- Téléversez le code C++ présent dans le dossier `arduino_code` (s'il n'y est pas déjà) sur votre Arduino via l'Arduino IDE.

### 2. Partie Logicielle (Ordinateur)
Le projet utilise Python et un environnement virtuel (`venv`) qui est généralement pré-configuré ou qu'il faudra instancier. 

Si ce n'est pas fait, lancez un terminal sous Linux pour installer les dépendances nécessaires à l'analyse vidéo.

```bash
# Activation de l'environnement virtuel (Linux/Mac)
source venv/bin/activate

# Installation des paquets nécessaires pour le traçage vidéo et la communication
pip install opencv-python mediapipe cvzone pyserial
```

---

## 🚀 Comment Lancer et Tester le Hand Bot

L'exécution du projet se fait en deux étapes. L'idéal est d'ouvrir deux terminaux disctincts depuis le répertoire racine `Bras-robotique-Tekbot` :

### Étape 1 : Connexion Bluetooth
La communication entre votre ordinateur et le contrôleur Arduino se fait par Bluetooth via le module HC-05.
Dans un premier terminal, exécutez le script de démarrage Bluetooth :

```bash
./start_hc05.sh
```
> **Note :** Ce script va automatiquement demander l'appairage avec le HC-05 (à travers l'adresse MAC `00:24:12:D0:13:55`) et il assurera une boucle de connexion continue sur le port virtuel `/dev/rfcomm0`. **Laissez ce terminal ouvert en arrière-plan.**

### Étape 2 : Lancement de l'Analyse Visuelle (Hand Tracking)
Une fois le composant Bluetooth stabilisé et connecté, depuis un second terminal, lancez la captation de la caméra et le module de reconnaissance en lançant :

```bash
./run_hand_tracking.sh
```
> **Note :** Ce script active automatiquement l'environnement virtuel et démarre `hand_tracking.py`.

### 🧪 Procède de Test
1. **Initialisation** : La webcam s'allumera et une fenêtre de rendu vidéo apparaîtra sur votre écran. Le terminal doit idéalement vous indiquer « ✓ Bluetooth connecté » ou avertir si le signal Bluetooth de la main est « hors ligne ». 
2. **Suivi des doigts** : Montrez votre main face à la caméra. Le programme MediaPipe détectera vos phalanges et transmettra, toutes les  0.08 millisecondes, la consigne aux servomoteurs en temps réel (l'index, le majeur, l'annulaire et l'auriculaire).
3. **Fermer la main** : Pliez vos doigts face à l'écran, vous devriez voir la main robotique réagir et reproduire le geste physique !
4. **Quitter** : Appuyez sur la touche **`q`** sur votre clavier dans la fenêtre d'image vidéo OpenCV pour arrêter la webcam et le script de tracking proprement.
