import numpy as np
from enum import Enum
import sys

def MIDIEvent():
    class Type(Enum):
        def __init__(noteOFF, noteON, other):
            self.noteOFF = noteOFF
            self.noteON = noteON
            self.other = other
    nKey = 0
    nVelocity = 0
    nDeltaTick = 0

def MIDINote():
    nKey = 0
    nVelocity = 0
    nStartTime = 0
    nDuration = 0

def MIDITrack():
    # std::string sName;
	# std::string sInstrument;
	# std::vector<MidiEvent> vecEvents;
	# std::vector<MidiNote> vecNotes;
    nMaxNote = 64
    nMinNote = 64

class MIDIFile():
    class EventName(Enum):
        VoiceNoteOff = 0x80
        VoiceNoteOn = 0x90
        VoiceAftertouch = 0xA0
        VoiceControlChange = 0xB0
        VoiceProgramChange = 0xC0
        VoiceChannelPressure = 0xD0
        VoicePitchBend = 0xE0
        SystemExclusive = 0xF0
    
    class MetaEventName(Enum):
        MetaSequence = 0x00
        MetaText = 0x01
        MetaCopyright = 0x02
        MetaTrackName = 0x03
        MetaInstrumentName = 0x04
        MetaLyrics = 0x05
        MetaMarker = 0x06
        MetaCuePoint = 0x07
        MetaChannelPrefix = 0x20
        MetaEndOfTrack = 0x2F
        MetaSetTempo = 0x51
        MetaSMPTEOffset = 0x54
        MetaTimeSignature = 0x58
        MetaKeySignature = 0x59
        MetaSequencerSpecific = 0x7F

    def __init__(self, filename):
        parseFile(filename)
    
    def parseFile(filename):
        with open(filename,'r') as sys.stdin:
            t = int(input())
