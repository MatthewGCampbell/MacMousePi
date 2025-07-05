// The quadrature waveform phases
const bool waveform1[] = {HIGH, LOW, LOW, HIGH};
const bool waveform2[] = {HIGH, HIGH, LOW, LOW};

// GPIOs for X and Y quadrature outputs (Macintosh mouse signals)
const int xGPIOs[] = {5, 6};
const int yGPIOs[] = {4, 3};

// GPIO for left mouse button output (active low)
const int clickOutGPIO = 2;

// GPIO for activity LED
const int ledPin = 13;

// Quadrature state indexes
int xIdx = 0;
int yIdx = 0;

// Pending steps to feed out smoothly
volatile int xPending = 0;
volatile int yPending = 0;

// LED timing
unsigned long ledOnTime = 0;
const unsigned long ledFlashDuration = 20; // milliseconds

void setup() {
  Serial.begin(115200);      // USB serial for debug
  Serial1.begin(115200);     // UART serial to Raspberry Pi

  // Set up quadrature outputs
  pinMode(xGPIOs[0], OUTPUT); // X1
  pinMode(xGPIOs[1], OUTPUT); // X2
  pinMode(yGPIOs[0], OUTPUT); // Y1
  pinMode(yGPIOs[1], OUTPUT); // Y2
  pinMode(clickOutGPIO, OUTPUT); // Mouse button

  // Set up LED pin
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); // LED off initially

  // Initialize quadrature outputs to idle high
  digitalWrite(xGPIOs[0], HIGH);
  digitalWrite(xGPIOs[1], HIGH);
  digitalWrite(yGPIOs[0], HIGH);
  digitalWrite(yGPIOs[1], HIGH);
  digitalWrite(clickOutGPIO, HIGH); // Button released

  Serial.println("Macintosh quadrature mouse emulator ready! Listening on Serial1");
}

void loop() {
  processSerial();
  updateLED();  // handle LED timing

  if (xPending != 0) {
    int direction = (xPending > 0) ? 1 : -1;
    xIdx = (xIdx + direction) % 4;
    if (xIdx < 0) xIdx += 4;
    writeQuadrature(xGPIOs, xIdx);
    xPending += (xPending > 0) ? -1 : 1;
    delayMicroseconds(120); // adjust for speed/smoothness
  }

  if (yPending != 0) {
    int direction = (yPending > 0) ? 1 : -1;
    yIdx = (yIdx + direction) % 4;
    if (yIdx < 0) yIdx += 4;
    writeQuadrature(yGPIOs, yIdx);
    yPending += (yPending > 0) ? -1 : 1;
    delayMicroseconds(120); // adjust for speed/smoothness
  }
}

void processSerial() {
  static String input = "";
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    if (c == '\n') {
      parseCommand(input);
      input = "";
    } else {
      input += c;
    }
  }
}

void parseCommand(String cmd) {
  cmd.trim();

  if (cmd.startsWith("X:")) {
    int delta = cmd.substring(2).toInt();
    int scaled = scaleDelta(delta);
    xPending += scaled;
    flashLED();
  } else if (cmd.startsWith("Y:")) {
    int delta = cmd.substring(2).toInt();
    int scaled = scaleDelta(delta);
    yPending += scaled;
    flashLED();
  } else if (cmd.startsWith("BTN:")) {
    int btnState = cmd.substring(4).toInt();
    digitalWrite(clickOutGPIO, btnState ? LOW : HIGH); // Active low: LOW=pressed
    flashLED();
  }
}

int scaleDelta(int delta) {
  int absDelta = abs(delta);
  int sign = (delta > 0) ? 1 : -1;
  int scaled;

  if (absDelta < 5) {
    scaled = absDelta;  // precise moves: 1x
  } else if (absDelta < 15) {
    scaled = absDelta * 1.5;  // small-to-medium moves: 1.5x
  } else if (absDelta < 40) {
    scaled = absDelta * 3;    // medium-to-large moves: 3x
  } else {
    scaled = absDelta * 5;    // very large moves: 5x
  }

  return sign * scaled;
}

void writeQuadrature(const int gpios[], int idx) {
  digitalWrite(gpios[0], waveform1[idx % 4]);
  digitalWrite(gpios[1], waveform2[idx % 4]);
}

void flashLED() {
  digitalWrite(ledPin, HIGH);
  ledOnTime = millis();
}

void updateLED() {
  if (ledOnTime != 0 && (millis() - ledOnTime) >= ledFlashDuration) {
    digitalWrite(ledPin, LOW);
    ledOnTime = 0; // reset timer
  }
}
