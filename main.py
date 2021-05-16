import numpy as np
from enum import Enum
import sys
import os


def MIDIEvent():
    class Type(Enum):
        noteOFF = 0
        noteON = 1
        other = 2

    # nKey = 0
    # nVelocity = 0
    # nDeltaTick = 0

    def __init__(self, note):
        self.type = note

    def __init__(self, note, noteID, vel, delta):
        self.type = note
        self.key = noteID
        self.velocity = vel
        self.deltaTick = delta


def MIDINote():
    nKey = 0
    nVelocity = 0
    nStartTime = 0
    nDuration = 0


class MIDITrack:
    # std::string sName;
    # std::string sInstrument;
    # std::vector<MidiEvent> vecEvents;
    # std::vector<MidiNote> vecNotes;

    def __init__(self, name, instrument, events, notes):
        self.name = name
        self.instrument = instrument
        self.events = events
        self.notes = notes

    nMaxNote = 64
    nMinNote = 64
    events = []
    notes = []


class MIDIFile:
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
        MIDIFile.parseFile(filename)

    tracks = []

    def parseFile(filename):
        n32 = 0
        n16 = 0

        with open(filename, "rb") as f:
            # print(int(input()))

            # we have to swap because MIDI is still stored in an older format
            # swapping a 32-bit integer
            def swap32(num):
                n = int.from_bytes(num, "big")
                return (
                    ((n >> 24) & 0xFF)
                    | ((n << 8) & 0xFF0000)
                    | ((n >> 8) & 0xFF00)
                    | ((n << 24) & 0xFF000000)
                )

            # swapping a 16-bit integer
            def swap16(num):
                n = int.from_bytes(num, "big")
                return (n >> 8) | (n << 8)

            # read a string of given size
            readString = lambda n: f.read(n)

            # reading an integer (value)
            # MIDI values are between the ranges 0-127
            # this means they only use 7 bits of the byte, but for values > 127
            # the MSB (left most bit) is set to 1, and we continue reading the next byte until the MSB = 0
            def readValue():
                # read the first byte
                num = f.read(1)
                nByte = 0

                nValue = int.from_bytes(num, "big")
                # check if MSB = 1
                if nValue & 0x80:
                    # get the last 7 LSBs
                    nValue = nValue & 0x7F
                    # read the next byte
                    num = f.read(1)
                    nByte = int.from_bytes(num, "big")
                    # add the next 7 bits of the next byte, shifting the first 7 bits to the left
                    nValue = (nValue << 7) | (nByte & 0x7F)
                    while nByte & 0x80:
                        # read the next byte
                        num = f.read(1)
                        nByte = int.from_bytes(num, "big")
                        # add the next 7 bits of the next byte, shifting the first 7 bits to the left
                        nValue = (nValue << 7) | (nByte & 0x7F)

                return nValue

            n32 = f.read(4)
            fileID = swap32(n32)
            n32 = f.read(4)
            headerLength = swap32(n32)
            n16 = f.read(2)
            nFormat = swap16(n16)
            n16 = f.read(2)
            traceChunks = swap16(n16)
            n16 = f.read(2)
            division = swap16(n16)

            print(fileID)
            print(headerLength)
            print(nFormat)
            print(traceChunks)
            print(division)

            for chunk in range(traceChunks):
                print("-------- NEW TRACK --------")
                n32 = f.read(4)
                trackID = swap32(n32)
                n32 = f.read(4)
                trackLength = swap32(n32)

                endTrack = False

                wallTime = 0
                previousState = 0
                events = []
                while not endTrack:
                    # the time difference between last note and current note is the delta
                    statusTimeDelta = readValue()
                    # the data can begin with an ID or instruction, to check which one it is, we check the status
                    num = f.read(1)
                    status = int.from_bytes(num, "big")

                    if status < 0x80:
                        status = previousState
                        # since we read the instruction byte, we need to bring it back on the stream so we can sync the values
                        f.seek(-1, os.SEEK_CUR)

                    if (status & 0xF0) == MIDIFile.EventName.VoiceNoteOff:
                        previousState = status
                        channel = status & 0x0F
                        noteID = f.read(1)
                        noteVelocity = f.read(1)

                        events.append(
                            MIDIEvent(
                                MIDIEvent.Type.noteOFF,
                                noteID,
                                noteVelocity,
                                statusTimeDelta,
                            )
                        )
                    elif (status & 0xF0) == MIDIFile.EventName.VoiceNoteOn:
                        previousState = status
                        channel = status & 0x0F
                        noteID = f.read(1)
                        num = f.read(1)
                        noteVelocity = int.from_bytes(num, "big")

                        if noteVelocity == 0:
                            events.append(
                                MIDIEvent(
                                    MIDIEvent.Type.noteOFF,
                                    noteID,
                                    noteVelocity,
                                    statusTimeDelta,
                                )
                            )
                        else:
                            events.append(
                                MIDIEvent(
                                    MIDIEvent.Type.noteON,
                                    noteID,
                                    noteVelocity,
                                    statusTimeDelta,
                                )
                            )
                    elif (status & 0xF0) == MIDIFile.EventName.VoiceControlChange:
                        previousState = status
                        channel = status & 0x0F
                        controlID = f.read(1)
                        controlValue = f.read(1)
                        # noteVelocity = int.from_bytes(num, "big")
                        events.append(MIDIEvent(MIDIEvent.Type.other))

                    elif (status & 0xF0) == MIDIFile.EventName.VoiceProgramChange:
                        previousState = status
                        channel = status & 0x0F
                        programID = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))

                    elif (status & 0xF0) == MIDIFile.EventName.VoiceChannelPressure:
                        previousState = status
                        channel = status & 0x0F
                        channelPressure = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))
                    
                    elif (status & 0xF0) == MIDIFile.EventName.VoicePitchBend:
                        previousState = status
                        channel = status & 0x0F
                        LS7B = f.read(1)
                        MS7B = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))
                    
                    elif (status & 0xF0) == MIDIFile.EventName.SystemExclusive:
                        previousState = 0

                        if (status == 0xFF):
                            # read meta message
                            type = f.read(1)
                            length = readValue()

                            # switch(type):

                        channel = status & 0x0F
                        LS7B = f.read(1)
                        MS7B = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))


demo = MIDIFile("bach_846.mid")
