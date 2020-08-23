##
# @file: wart.py
#
# @brief Convert a .WAV file to a "WART" PWM format file
#
# This python script reads a .wav file and emits a array of bytes in C format
# that encode the audio in pulse-width modulation (PWM) format.  To play the
# resulting data, output the array to a UART through a low-pass filter.
#
# Synopsis:
#
#   python [arguments]
#
# where arguments can be:
#
#   -i <infile>  default wart.wav
#   -o <outfile> default wart.h
#
# Note 1: As written, the input file MUST be 8 bit unsigned, mono channel.
# Note 2: The output file is designed to be output with a buad rate that is 10x
#         the sample rate of the input file.  For example, if the input file has
#         a sample rate of 11520 Hz, the UART should be configured for 115200
#         baud.
#
# @author R. D. Poor <rdpoor@gmail.com>
#
# @date August 2020

import wave
import os

class Wart(object):

    SYMBOLS = [
        0b00000000,   # 0.1 duty cycle
        0b10000000,   # 0.2 duty cycle
        0b11000000,   # 0.3 duty cycle
        0b11100000,   # 0.4 duty cycle
        0b11110000,   # 0.5 duty cycle
        0b11111000,   # 0.6 duty cycle
        0b11111100,   # 0.7 duty cycle
        0b11111110,   # 0.8 duty cycle
        0b11111111,   # 0.9 duty cycle
        ]

    # Convert a uint8_t to one of the 9 PWM symbols
    SAMPLE_MAP = [0] * 256

    def __init__(self, options):
        self.options = options
        self.init_sample_map()

    def convert_file(self):
        with wave.open(self.options.infile, mode='rb') as wavi:
            with open(self.wart_h_filename(), "w") as f:
                self.generate_c_file(wavi, f)

    def wart_h_filename(self):
        if self.options.outfile != None:
            return self.options.outfile
        root, ext = os.path.splitext(self.options.infile)
        return root + ".h"

    def generate_c_file(self, wavi, f):
        self.write_c_preamble(wavi, f)
        while True:
            bytes = wavi.readframes(32)
            if len(bytes) == 0: break
            self.process_c_line(bytes, f)
        self.write_c_postamble(wavi, f)

    def write_c_preamble(self, wavi, f):
        print("#ifndef _WART_H_\r\n" +
              "#define _WART_H_\r\n\r\n" +
              "#include <stdint.h>\r\n\r\n" +
              "const uint8_t wart[] = {", file=f)

    def process_c_line(self, bytes, f):
        mapped = ['0x{:02x},'.format(self.map_sample(b)) for b in bytes]
        print('  ' + ''.join(mapped), file=f)

    def write_c_postamble(self, wavi, f):
        print("};\r\n" +
              "#endif // #ifndef _WART_H_", file=f)

    def map_sample(self, b):
        return self.SAMPLE_MAP[b]

    def init_sample_map(self):
        for i in range(256):
            j = self.lerp(i, 0, 256, 0, len(self.SYMBOLS))
            # print(i, j)
            self.SAMPLE_MAP[i] = self.SYMBOLS[int(j)]

    @classmethod
    def lerp(cls, x, x0, x1, y0, y1):
        return y0 + (x-x0)*(y1-y0)/(x1-x0)

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="WART converter")

    parser.add_argument('-i', '--infile', default="wart.wav",
                        help='input wav file')
    parser.add_argument('-o', '--outfile',
                        help='output h file')
    options = parser.parse_args()

    Wart(options).convert_file()
