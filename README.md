# WART
WART Audio: Play encoded .WAV files with just a UART and a speaker

## Short Form:

WART Audio uses a UART as a simple Pulse Width Modulator (PWM).  Sending a stream of 0x00 bytes, you get a 10% duty cycle (because the stop bit is always true).  Similarly, a stream of 0xff bytes gets you a 90% duty cycle (because the start bit is always false).  Overall, you can use the UART to generate nine different levels of PWM.  After you put its output through a low-pass filter, this is equivalent to a 3.17 bit DAC -- not high-fidelity by any means, but even the smallest microcontoller can use this approach to play passable audio.

The script [wart.py](https://github.com/rdpoor/WART/blob/master/wart.py) converts a .wav file into a C-formatted byte array that you incorporated into your microcontroller code.  Just a few lines of code are enough to play the array out of the serial port, which you connect to a speaker with an appropriate driver and -- voila -- you get audio.

## wart.h 
The output of the python script is a C-compliant `wart.h` file that looks something like this:

```c
#ifndef _WART_H_
#define _WART_H_

#include <stdint.h>

const uint8_t wart[] = {
0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xe0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xe0,0xf0,0xf0,0xf0,
0xf0,0xe0,0xe0,0xe0,0xe0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf0,0xf8,0xf8,0xf0,0xf8,0xf8,0xf0,0xf0,0xf0,0xf0,0xf0,
...
0xf8,0xf8,0xf8,0xf0,0xf8,0xf8,0xf8,0xf0,0xf0,0xf0,0xf0,0xf0,0xfc,0xf8,0xf0,0xf8,0xfc,0xfc,0xf8,0xf8,0xf8,0xf0,0xf0,0xf0,0xe0,0xc0,0xf0,0xf8,0xe0,0xc0,0xe0,0xe0,
0xe0,0xf0,0xe0,0xe0,0xe0,0xf0,0xf8,0xf0,0xe0,0xe0,0xe0,0xf0,0xf0,0xf8,0xf0,0xf0,0xf0,0xf8,0xfc,0xf8,0xf8,0xf8,0xf0,0xe0,0xe0,0xe0,0xc0,0xe0,0xf0,0xe0,0xe0,0xf0,
0xf0,0xf0,0xf8,0xf8,0xf0,0xf0,0xf0,0xf0,0xe0,0xe0,0xc0,0xc0,0xe0,0xf0,0xf8,0xe0,0xc0,0xe0,0xf0,0xf0,0xf0,0xe0,0xc0,0xc0,0xf0,0xf0,0xc0,0xc0,0xf0,0xf0,0xf0,0xf0,
0xf0,0xf0,0xf8,0xf8,0xf0,0xe0,0xf0,0xf8,0xf0,0xf0,0xe0,0xc0,0xe0,0xf0,0xf8,0xfc,0xf0,0xf0,0xf8,0xfc,0xf8,0xf8,0xf8,0xf0,0xf0,0xf8,0xf8,0xe0,0xe0,0xf0,0xf8,0xf0,
};
#endif // #ifndef _WART_H_
```

## Arduino Sketch

The following sketch is all that's needed to play a WART-encoded file.  Note that in this case, we're using the `Serial1` object whose transmit data appears on pin 3 of the Teensy 3.2 board.  (The regular `Serial` object outputs over the USB connection.)

```c
// file: wart.ino
#include "wart.h"

void setup() {
  Serial1.begin(115200); // User Serial1 TXD for PWM output
  while (!Serial1) {
    ; // wait for serial port to connect.
  }
}

void loop() {
  Serial1.write(wart, sizeof(wart));
}
```

## The Teensy 3.2 Schematic
Since the Teensy's UART output lacks sufficient oomph (that's a technical term) to power a speaker, a simple transitor driver will do the job.  There are many more sophisticated approaches you could take (use an H bridge to double the effective power, use a real low-pass filter), but this simplistic approach is in keeping with the quick and simple WART philosophy.

![WART Schematic](https://github.com/rdpoor/WART/blob/master/images/WART.png "WART Schematic")
