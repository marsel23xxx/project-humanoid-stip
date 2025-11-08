#include <ATX2.h>

// RTRobot 32-Servo Controller B
// Mengontrol 21 servo untuk bagian bawah robot
// Protocol: ASCII, LF terminator ('\n'), 9600 baud
// Wiring: TXD1→RX, RXD1←TX, GND↔GND, 5V↔5V (logic only)

#define USB_BAUD   115200
#define SERVO_BAUD 9600
#define MARGIN_MS  300UL
#define MAX_SERVOS 21

String inbuf = "";

// ---------- Helpers ----------
void sendMove(uint8_t ch, uint16_t pos, uint16_t T, uint16_t D) {
  if (ch < 1 || ch > MAX_SERVOS) {
    Serial.print("ERROR: Channel out of range (1-");
    Serial.print(MAX_SERVOS);
    Serial.println(")");
    return;
  }
  
  char body[48];
  sprintf(body, "#%dP%dT%dD%d", ch, pos, T, D);
  
  // Debug output
  Serial.print("[B] TX: ");
  Serial.println(body);
  
  // Send to servo controller
  Serial1.print(body);
  Serial1.print('\n'); // LF only
}

// Wait for "OK" response
void waitOK(uint16_t T, uint16_t D) {
  unsigned long deadline = millis() + (unsigned long)T + (unsigned long)D + MARGIN_MS;
  String response = "";
  
  while (millis() < deadline) {
    while (Serial1.available()) {
      char c = (char)Serial1.read();
      response += c;
      
      if (response.indexOf("OK") != -1) {
        Serial.println("[B] OK received");
        return;
      }
    }
  }
  Serial.println("[B] WARNING: No OK response");
}

// Parse command dari Python
// Format: #<ch>P<pos>T<time>D<delay>
void parseCommand(String cmd) {
  cmd.trim();
  
  if (cmd.length() == 0) return;
  
  // Check if command starts with #
  if (cmd.charAt(0) != '#') {
    Serial.println("[B] ERROR: Command must start with #");
    return;
  }
  
  // Parse channel
  int pIdx = cmd.indexOf('P');
  int tIdx = cmd.indexOf('T');
  int dIdx = cmd.indexOf('D');
  
  if (pIdx == -1 || tIdx == -1 || dIdx == -1) {
    Serial.println("[B] ERROR: Invalid command format");
    return;
  }
  
  uint8_t channel = cmd.substring(1, pIdx).toInt();
  uint16_t position = cmd.substring(pIdx + 1, tIdx).toInt();
  uint16_t time = cmd.substring(tIdx + 1, dIdx).toInt();
  uint16_t delayTime = cmd.substring(dIdx + 1).toInt();
  
  // Validate values
  if (position < 500 || position > 2500) {
    Serial.println("[B] ERROR: Position must be 500-2500");
    return;
  }
  
  // Send command
  sendMove(channel, position, time, delayTime);
  waitOK(time, delayTime);
  
  Serial.println("[B] DONE");
}

// ---------- Setup ----------
void setup() {
  // USB Serial untuk komunikasi dengan Python
  Serial.begin(USB_BAUD);
  delay(200);
  
  // Serial1 untuk komunikasi dengan servo controller
  Serial1.begin(SERVO_BAUD);
  delay(200);
  
  Serial.println("=================================");
  Serial.println("Arduino ATX2 Controller B");
  Serial.println("Servo Controller: 21 servos");
  Serial.println("Lower body control");
  Serial.println("=================================");
  Serial.println("Ready to receive commands...");
  Serial.println();
}

// ---------- Loop ----------
void loop() {
  // Read command from USB Serial (Python)
  while (Serial.available()) {
    char c = (char)Serial.read();
    
    if (c == '\r' || c == '\n') {
      if (inbuf.length() > 0) {
        parseCommand(inbuf);
        inbuf = "";
      }
    } else {
      inbuf += c;
      if (inbuf.length() > 128) {
        Serial.println("[B] ERROR: Command too long");
        inbuf = "";
      }
    }
  }
  
  // Echo any servo controller responses
  while (Serial1.available()) {
    char c = (char)Serial1.read();
    Serial.write(c);
  }
}