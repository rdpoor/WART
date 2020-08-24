#include "wart.h"

void setup() {
  Serial1.begin(115200); // serial port for PWM
  while (!Serial1) {
    ; // wait for serial port to connect.
  }
}

void loop() {
  Serial1.write(wart, sizeof(wart));
}
