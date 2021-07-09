# WART
WART Audio: Play encoded .WAV files with just a UART and a speaker

Question: Since a UART can only generate ones and zeros (or high and low voltages), how can you use it to play audio?

Answer: Use the UART as a pulse width modulator.

## Short Form:

WART Audio uses a UART as a simple Pulse Width Modulator (PWM).  Sending a stream of 0x00 bytes, you get a 10% duty cycle because the stop bit is always true.  Similarly, a stream of 0xff bytes gets you a 90% duty cycle because the start bit is always false.  Between those two extremes, you can use the UART to generate nine different levels of PWM.  After you put its output through a low-pass filter, this is equivalent to a 3.17 bit DAC -- not high-fidelity by any means, but even the simplest microcontoller can use this approach to play passable audio.

The script [wart.py](https://github.com/rdpoor/WART/blob/master/wart.py) converts a .wav file into a C-formatted byte array that you incorporate into your microcontroller code.  Just a few lines of code are enough to play the array out of the serial port, which you connect to a speaker with an appropriate driver and -- voila -- you get audio.

## Using a UART to generate PWM

This graphic shows how you can use an ordinary UART to generate Pulse Width Modulated signals.  The UART is configured for standard `8-n-1` encoding, meaning that each transmitted byte begins with one start bit (always low), followed by eight data bits (least significant bit transmitted first), and ending with one stop bit (always high).  

![WART Encoding](https://github.com/rdpoor/WART/blob/master/images/WART2.png "WART Encoding")


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
  Serial1.begin(115200); // Use Serial1 TXD for PWM output
  while (!Serial1) {
    ; // wait for serial port to connect.
  }
}

void loop() {
  Serial1.write(wart, sizeof(wart));
}
```

## The Teensy 3.2 Schematic
Since the Teensy's UART output lacks sufficient oomph (that's a technical term) to power a speaker, a simple transistor driver will do the job.  There are many more sophisticated approaches you could take (use an H bridge to double the effective power, use a real low-pass filter), but this simplistic approach is in keeping with WART's "quick and easy" philosophy.

![WART Schematic](https://github.com/rdpoor/WART/blob/master/images/WART.png "WART Schematic")

Here's how it looks on a solderless breadboard:

![WART Layout](https://github.com/rdpoor/WART/blob/master/images/IMG_0561.JPG "WART Layout")

And here's a closeup showing the resistor and transistor drive circuitry:

![WART Closeup](https://github.com/rdpoor/WART/blob/master/images/IMG_0573.JPG "WART Closeup")

## To create your own WART audio system

The following steps assume that you're using the Arduino application and a Teensy 3.2, but the general concepts should work with just about any IDE and processor.

### Assemble the hardware

In our example, we used a Teensy 3.2 board, but WART Audio will work with just about any microcontroller.  The only requirements are:
- it must have enough program space to hold the sample array
- it must have a UART capable of 115200 baud rate
- its serial driver must be capable of writing bytes to the UART without interruption

Using the schematic shown above as a guide, build the speaker driver.  It requires one 10K resistor, a general purpose NPN transistor and 5V source.

### Prepare the firmware

Assuming that you're using the Arduino application, create a new sketch with [the code listed above](https://github.com/rdpoor/WART/blob/master/wart.ino).

### Prepare your audio file

Use Audacity or sox or your favorite audio tool to create a file with the following properties:
- Number of Channels:1 (Mono)
- Sampling Rate: 11520
- Encoding: .WAV 8 bit unsigned

For best results, make sure the sound file has been normalized for maximum dynamic range. 
The following steps assume the resulting file is named `my_sound.wav`, but of
course you can name it whatever you like.

### Convert the file

- [Download the wart.py python script](https://github.com/rdpoor/WART/blob/master/wart.py) from the github repository.
- In a shell script, invoke `python wart.py -i <path_to_my_sound>/my_sound.wav` -o wart.h

This will create wart.h -- similar to what's shown above -- in the current directory.

### Build and run the Arduino sketch

Move the `wart.h` file into the same directory as the `wart.ino` sketch.  Then 
launch the Arduino application, open the `wart.ino` sketch, then compile and run it.

### Impatient?

Skip the steps about preparing and converting an audio file, and use the `wart.h` file
already in the project to test your hardware.  Management assumes no responsibility for 
compaints from your neighbors!
