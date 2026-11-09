#include <SoftwareSerial.h>
#include <Servo.h>

SoftwareSerial bluetooth(2, 3);

Servo servoIndex;       // Pin 9  — monté à l'envers
Servo servoMajeur;      // Pin 8
Servo servoAnnulaire;   // Pin 7
Servo servoPetitDoigt;  // Pin 6

String data = "";

void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600);

  servoIndex.write(180);     // index inversé → 180 = ouvert // max = 0 || config de base 180
  servoMajeur.write(0);     // max = 75                                 || config de base 75
  servoAnnulaire.write(180);// max = 0                                  || config de base 0
  servoPetitDoigt.write(0);  // max =  180                              || config de base 180

  servoIndex.attach(9);
  servoMajeur.attach(8);
  servoAnnulaire.attach(7);
  servoPetitDoigt.attach(6);

  Serial.println("=== Main robotique - 4 servos ===");
  Serial.println("En attente de connexion Bluetooth...");
}

void parseAndSetAngles(String input) {
  input.trim();

  int comma1 = input.indexOf(',');
  int comma2 = input.indexOf(',', comma1 + 1);
  int comma3 = input.indexOf(',', comma2 + 1);

  if (comma1 > 0 && comma2 > 0 && comma3 > 0) {
    // Python envoie : 0 = doigt levé, 180 = doigt baissé
    int angleIndex      = constrain(input.substring(0, comma1).toInt(), 0, 180);
    int angleMajeur     = constrain(input.substring(comma1 + 1, comma2).toInt(), 0, 180);
    int angleAnnulaire  = constrain(input.substring(comma2 + 1, comma3).toInt(), 0, 180);
    int anglePetitDoigt = constrain(input.substring(comma3 + 1).toInt(), 0, 180);

    // Index    : inversé,  0→180  à  180→0
    servoIndex.write(map(angleIndex, 0, 180, 180, 0));

    // Majeur   : course limitée, 0→0  à  180→75
    servoMajeur.write(map(angleMajeur, 0, 180, 0, 75));

    // Annulaire: inversé,  0→180  à  180→0
    servoAnnulaire.write(map(angleAnnulaire, 0, 180, 180, 0));

    // Auriculaire: normal, 0→0  à  180→180
    servoPetitDoigt.write(map(anglePetitDoigt, 0, 180, 0, 180));

    Serial.print("✓ Reçu: ");
    Serial.println(input);
    bluetooth.println("OK");

  } else {
    Serial.println("✗ Format invalide");
    bluetooth.println("ERREUR");
  }
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (data.length() > 0) {   // ← ignorer si vide
        parseAndSetAngles(data);
      }
      data = "";
    } else if (c != '\r') {
      data += c;
      if (data.length() > 30) data = "";
    }
  }
}