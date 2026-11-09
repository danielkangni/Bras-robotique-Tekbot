import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.components.containers import landmark as mp_landmark
import serial
import time
import urllib.request
import os

# ─────────────────────────────────────────────
#  MODÈLE MEDIAPIPE (Tasks API)
# ─────────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Téléchargement du modèle hand_landmarker.task ...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("✓ Modèle téléchargé")

# ─────────────────────────────────────────────
#  CONFIGURATION BLUETOOTH
# ─────────────────────────────────────────────
BT_PORT     = "COM3"
BT_BAUDRATE = 9600
BT_TIMEOUT  = 1

# ─────────────────────────────────────────────
#  CONNEXION BLUETOOTH
# ─────────────────────────────────────────────
bt = None
try:
    bt = serial.Serial(BT_PORT, BT_BAUDRATE, timeout=BT_TIMEOUT)
    time.sleep(2)
    print(f"✓ Bluetooth connecté sur {BT_PORT}")
except Exception as e:
    print(f"✗ Bluetooth non disponible ({e})")
    print("  Le programme continue SANS envoi Bluetooth (mode test caméra)")

# ─────────────────────────────────────────────
#  CAMÉRA
# ─────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la caméra")
    exit(1)
print("✓ Caméra ouverte")

# ─────────────────────────────────────────────
#  DÉTECTEUR DE MAIN (Tasks API)
# ─────────────────────────────────────────────
base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
options = mp_vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.8,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    running_mode=mp_vision.RunningMode.VIDEO
)
detector = mp_vision.HandLandmarker.create_from_options(options)

# Indices landmarks
FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [3, 6, 10, 14, 18]
FINGER_NAMES = ["Pouce", "Index", "Majeur", "Annulaire", "Auriculaire"]

# Connexions pour dessiner le squelette de la main
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),       # Pouce
    (0,5),(5,6),(6,7),(7,8),       # Index
    (0,9),(9,10),(10,11),(11,12),  # Majeur
    (0,13),(13,14),(14,15),(15,16),# Annulaire
    (0,17),(17,18),(18,19),(19,20),# Auriculaire
    (5,9),(9,13),(13,17)           # Paume
]

def draw_landmarks(img, landmarks):
    h, w = img.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(img, pts[a], pts[b], (0, 200, 200), 2)
    for pt in pts:
        cv2.circle(img, pt, 5, (255, 255, 255), -1)
        cv2.circle(img, pt, 5, (0, 150, 255), 1)

def fingers_up(landmarks, handedness="Right"):
    fingers = []
    # Pouce : comparaison horizontale
    if handedness == "Right":
        fingers.append(1 if landmarks[FINGER_TIPS[0]].x < landmarks[FINGER_PIPS[0]].x else 0)
    else:
        fingers.append(1 if landmarks[FINGER_TIPS[0]].x > landmarks[FINGER_PIPS[0]].x else 0)
    # Autres doigts : tip.y < pip.y = levé
    for i in range(1, 5):
        fingers.append(1 if landmarks[FINGER_TIPS[i]].y < landmarks[FINGER_PIPS[i]].y else 0)
    return fingers

SEND_INTERVAL = 0.08
last_send_time = 0
start_time = time.time()

print("─────────────────────────────────────")
print("  Contrôle main robotique  |  'q' pour quitter")
print("─────────────────────────────────────")

while True:
    ok, img = cap.read()
    if not ok:
        print("Erreur: frame caméra perdue")
        break

    # Timestamp en ms pour le mode VIDEO
    timestamp_ms = int((time.time() - start_time) * 1000)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    servo_vals = None

    if result.hand_landmarks:
        landmarks  = result.hand_landmarks[0]
        handedness = result.handedness[0][0].display_name if result.handedness else "Right"

        draw_landmarks(img, landmarks)
        fingers = fingers_up(landmarks, handedness)

        all_servo = [0 if f == 1 else 180 for f in fingers]
        servo_vals = [all_servo[1], all_servo[2], all_servo[3], all_servo[4]]

        # ── Affichage ─────────────────────────────────────────────────
        y = 40
        for i, name in enumerate(FINGER_NAMES):
            color = (0, 255, 0) if fingers[i] == 1 else (0, 100, 255)
            cv2.putText(img, f"{name}: {all_servo[i]}deg",
                        (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
            y += 35

        # ── Envoi Bluetooth ───────────────────────────────────────────
        now = time.time()
        if bt and (now - last_send_time) >= SEND_INTERVAL:
            msg = f"{servo_vals[0]},{servo_vals[1]},{servo_vals[2]},{servo_vals[3]}\n"
            try:
                bt.write(msg.encode())
                if bt.in_waiting:
                    ack = bt.readline().decode(errors="ignore").strip()
                    if ack:
                        print(f"  Arduino: {ack}")
                last_send_time = now
                print(f"→ Envoyé: {msg.strip()}")
            except Exception as e:
                print(f"✗ Erreur envoi BT: {e}")
                

    # ── Statut BT ─────────────────────────────────────────────────────
    status = "BT OK" if bt else "BT HORS LIGNE"
    cv2.putText(img, status, (img.shape[1] - 160, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0) if bt else (0, 0, 255), 2)

    cv2.imshow("Main Robotique - Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ─────────────────────────────────────────────
#  NETTOYAGE
# ─────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
detector.close()
if bt:
    bt.close()
print("Programme terminé")
