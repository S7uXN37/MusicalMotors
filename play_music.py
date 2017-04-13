import midi
# https://github.com/vishnubob/python-midi
import RPi.GPIO as GPIO
import threading
import time
import math

class MusicThread(threading.Thread):
    def setStep(self, step, pins=[35,31,33,29]):
        for i in range(0,4):
            GPIO.output(pins[i], step[i])
        #print step
    def __init__(self):
        super(MusicThread, self).__init__()
        self.daemon = True
        GPIO.setmode(GPIO.BOARD)
        for pin in [35,31,33,29]:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
	self._seq = [[0,0,1,1],
            [1,0,0,1],
            [1,1,0,0],
            [0,1,1,0]]
        self._delay = 5
	
        self._stop = threading.Event()
        self._start = threading.Event()
    def startNote(self, delay):
        self._delay = delay/1000.
        self._stop.clear()
        self._start.set()
    def stopNote(self):
        self._start.clear()
        self._stop.set()
    def run(self):
        while True:
            self._start.wait()
            self._start.clear()
            while not self._stop.isSet():
                for j in range(0, len(self._seq)):
                    self.setStep(self._seq[j])
                    time.sleep(self._delay)
            self._stop.clear()

def ticksToMs(ticks):
    return ticks * 60.0 / 1000.0 / 80.0
def pitchToDelay(pitch):
    freq = math.pow(2, (pitch-69)/12.0) * 440.0
    delay = 6.0 - 0.0093 * freq
    print(pitch, " - ", freq, "Hz - ", delay, "ms")
    return delay
pattern = midi.read_midifile('mary.mid')
last_event = time.time()
thread = MusicThread()
thread.start()

try:
    #thread.startNote(pitchToDelay(60))
    #time.sleep(5)
    #raise KeyboardInterrupt
    for track in pattern:
        track.make_ticks_rel()
        for event in track:
            if isinstance(event, midi.NoteOnEvent): # check that the current event is a NoteEvent, otherwise it won't have the method get_pitch() and we'll get an error
                pitch = event.get_pitch()
                thread.stopNote()
                thread.startNote(pitchToDelay(pitch))
            elif isinstance(event, midi.NoteOffEvent):
                thread.stopNote()
            time.sleep(ticksToMs(event.tick))
finally:
    for pin in [35,31,33,29]:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()
