import mido
from lib import mtof
from lib import consts

#Handles input from MIDI devices, translating MIDI info into note-on, note-off, frequency, and velocity values
class MIDI_device:
    def __init__(self, device_name = consts.DEVICE_NAME):
        self._device_name = device_name
        self._input = None
        self.connectController()
        self._mtof = mtof.mtof()

    #Handle incoming messages using callback
    def handleMessage(self, message):
        self.processMIDI(message)

    def close(self):
        if self._input:
            self._input.close()

    #Find the correct device if possible    
    def connectController(self) -> bool:
        matching_ports = [port for port in mido.get_input_names() if self._device_name in port]
        if matching_ports:
            self._input = mido.open_input(matching_ports[0], callback=self.handleMessage)
            return True
        else:
            raise ValueError("No connected devices matching", self._device_name)
        
    #For parent class, this function just prints the MIDI information.
    #See the Synth subclass implementation for actual usasge
    def processMIDI(self, message: mido.Message = None):

        if message == None:
            raise TypeError("processMIDI got None (expected mido.Message)")
        
        if message.type == 'note_on':
            print(f"Note ON: {message.note}, Velocity: {message.velocity}")
        elif message.type == 'note_off':
            print(f"Note OFF: {message.note}, Velocity: {message.velocity}")
        elif message.type == 'control_change':
            print(f"Control Change: {message.control}, Value: {message.value}")