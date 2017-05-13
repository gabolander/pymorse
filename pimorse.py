#!/usr/bin/env python
import time
import sys, getopt, os, re

BeepPin = 11    # pin11
# MotorPin1   = 11    # pin11
# MotorPin2   = 12    # pin12
# MotorEnable = 13    # pin13

# I define some vars that I treat as constants ...

DOT_MS_LEN=0.08     # "BASE" DOT LENGTH: This is the main 'dot' length which all
                    # the other delay/durations are based on.
                    # Decrease it, to make it playing faster.
                    # Increase it, to make it slower.
                    # Don't touch other DASH_* DELAY_* values instead, because
                    # they are multipliers of DOT_MS_LEN.
DASH_MS_LEN=(DOT_MS_LEN*3)
DELAY_MS_DOTS=(DOT_MS_LEN*1)
DELAY_MS_LETTERS=(DOT_MS_LEN*3)
DELAY_MS_WORDS=(DOT_MS_LEN*5)

# Global vars
default_msg = "Hello, world!"

Kalfav = [ 'A','B','C','D','E','F','G','H','I','J',
            'K','L','M','N','O','P','Q','R','S','T',
            'U','V','W','X','Y','Z', ## Alphabet chars
            '1','2','3','4','5','6','7','8','9','0',' ', ## Numbers + space
            '.',',',':','?','=','-','(',')','"','\'','/','_','@','!' ## Symbols
        ]

Kmorsev = [
    ".-","-...","-.-.","-..",".","..-.","--.","....","..",".---",
    "-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-",
    "..-","...-",".-- ","-..-","-.--","--..", # Alphabet chars
    ".----","..---","...--","....-",".....",
    "-....","--...","---..","----.","-----"," ", # Numbers + space
    ".-.-.-","--..--","---...","..--..","-...-","-....-","-.--.",
    "-.--.-",".-..-.",".----.","-..-.","..--.-",".--.-.","-.-.--" # Symbols
    ]

Simulate = False
Dot_ms_len = 0.08
DEBUG = False

def soundmorse(seq):
    global Simulate, Dot_ms_len, DEBUG
    if not(Simulate):
        import RPi.GPIO as GPIO
    if seq==" ":
        time.sleep(DELAY_MS_WORDS)
        return 1
    Index=0
    while Index<len(seq):
        sign=seq[Index]
        if not(Simulate):
            GPIO.output(BeepPin, GPIO.LOW)
        if sign=='-':
            #if DEBUG:
            #    print "time.sleep(",DASH_MS_LEN,")"
            time.sleep(DASH_MS_LEN)
        else:
            #if DEBUG:
            #    print "time.sleep(",DOT_MS_LEN,")"
            time.sleep(DOT_MS_LEN)
        if not(Simulate):
            GPIO.output(BeepPin, GPIO.HIGH)

        time.sleep(DELAY_MS_DOTS)
        Index=Index+1
    # Delay at end of letter
    time.sleep(DELAY_MS_LETTERS-DELAY_MS_DOTS)
    return 1

def morse_decode(letter):
    Index=0
    maxindex=len(Kalfav)
    for kalfa in Kalfav:
        if kalfa == letter:
            break
        else:
            Index=Index+1
    if Index>=maxindex:
        return ""
    else:
        return Kmorsev[Index]

def setup():
    global Simulate, Dot_ms_len

    if Dot_ms_len != 0.08:
        tmp = re.findall(r"[-+]?\d*\.\d+|\d+", Dot_ms_len)
        # print "Found in Dot_ms_len : [", tmp[0], "] " # GABODebug
        if len(tmp)==0:
            print "Float not found in 'dot' parameter.  The value of 0.08 has been restored."
            Dot_ms_len=0.08
        else:
            Dot_ms_len=float(tmp[0])
            if Dot_ms_len < 0.05 or Dot_ms_len > 0.2:
                print "required DOT_MS_LEN out of bounds. The value of 0.08 has been restored."
                Dot_ms_len=0.08

        DOT_MS_LEN=Dot_ms_len
        DASH_MS_LEN=(DOT_MS_LEN*3)
        DELAY_MS_DOTS=(DOT_MS_LEN*1)
        DELAY_MS_LETTERS=(DOT_MS_LEN*3)
        DELAY_MS_WORDS=(DOT_MS_LEN*5)

    if not(Simulate):
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)        # Numbers GPIOs by physical location
        GPIO.setup(BeepPin, GPIO.OUT)   # Set BeepPin's mode is output
        GPIO.output(BeepPin, GPIO.HIGH) # Set BeepPin high(+3.3V) to off beep

def loop():
    global DEBUG
    while True:
            message = raw_input("Enter a message to transmit (\""+default_msg+"\" default message, \"STOP\" to exit) : " )
            if message == "STOP":
                break

            if message == "":
                message = default_msg

            if DEBUG:
                print "message: ", message
            Index=0
            while Index<len(message):
                letter=message.upper()[Index]
                morseseq=morse_decode(letter)
                if DEBUG:
                    print "letter: ", letter, " morse seq: ", morseseq
                soundmorse(morseseq)
                Index=Index+1
            print '\n'

def destroy():
    global Simulate, Dot_ms_len
    if not (Simulate):
        import RPi.GPIO as GPIO
        GPIO.output(BeepPin, GPIO.HIGH)    # beep off
        GPIO.cleanup()                     # Release resource

def usage():
    print os.path.basename(os.path.basename(sys.argv[0])), "[options]"
    print
    print "Options: "
    print " -h | --help       Shows this help"
    print " -s | --simulate   Allow to test program without RaspberriPI"
    print " -d <dot_lenth>  "
    print " --dot=<dot_lenth> Length in seconds of dots (default=0.08) "
    print " -D | --debug      Add more verbosity to program "
    print


def main(argv):
    global Simulate, Dot_ms_len, DEBUG

    try:
      opts, args = getopt.getopt(argv,"hsd:D",["help","simulate","dot=","debug"])
    except getopt.GetoptError:
      print os.path.basename(os.path.basename(sys.argv[0]))+' Error: Usage: '
      usage()
      sys.exit(2)
    for opt, arg in opts:
      if opt in ("-h", "--help" ):
         usage()
         sys.exit()
      elif opt in ("-d", "--dot"):
         Dot_ms_len = arg
      elif opt in ("-s", "--simulate"):
         Simulate = True
      elif opt in ("-D", "--debug" ):
         DEBUG = True

    if not(Simulate):
        import RPi.GPIO as GPIO
    # print 'Press Ctrl+C to end the program...'
    setup()
    try:
        loop()
        destroy()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

if __name__ == '__main__':     # Program start from here
    main(sys.argv[1:])

# ex: ts=4 sts=4 sw=4 ai nohls mouse-=a ft=python et:
# ex: tabstop=4 softtabstop=4 shiftwidth=4 autoindent mouse-=a filetype=python expandtab:
