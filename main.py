import numpy as np
from enum import Enum
import sys
import os


class MIDIEvent:
    class Type(Enum):
        noteOFF = 0
        noteON = 1
        other = 2

    # nKey = 0
    # nVelocity = 0
    # nDeltaTick = 0

    def __init__(self, note, noteID=None, vel=None, delta=None):
        if delta == None:
            self.type = note
        else:
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

    def __init__(self):
        self.name = ""
        self.instrument = ""
        self.events = []
        self.notes = []

    def setName(self, name):
        self.name = name

    def setInstrument(self, inst):
        self.instrument = inst

    nMaxNote = 64
    nMinNote = 64


class MIDIFile:
    EventName = {
        "VoiceNoteOff": 0x80,
        "VoiceNoteOn": 0x90,
        "VoiceAftertouch": 0xA0,
        "VoiceControlChange": 0xB0,
        "VoiceProgramChange": 0xC0,
        "VoiceChannelPressure": 0xD0,
        "VoicePitchBend": 0xE0,
        "SystemExclusive": 0xF0,
    }

    class ModeMessages(Enum):
        ALL_SOUND_OFF = 0x78
        RESET_ALL_CONTROLLERS = 0x79
        LOCAL_CONTROL = 0x7A
        ALL_NOTES_OFF = 0x7B
        OMNI_MODE_OFF = 0x7C
        OMNI_MODE_ON = 0x7D
        MONO_MODE_ON = 0x7E
        SystemExclusive = 0x7F

    MetaEventName = {
        "MetaSequence": 0x00,
        "MetaText": 0x01,
        "MetaCopyright": 0x02,
        "MetaTrackName": 0x03,
        "MetaInstrumentName": 0x04,
        "MetaLyrics": 0x05,
        "MetaMarker": 0x06,
        "MetaCuePoint": 0x07,
        "MetaChannelPrefix": 0x20,
        "MetaPort": 0x21,
        "MetaEndOfTrack": 0x2F,
        "MetaSetTempo": 0x51,
        "MetaSMPTEOffset": 0x54,
        "MetaTimeSignature": 0x58,
        "MetaKeySignature": 0x59,
        "MetaSequencerSpecific": 0x7F,
    }

    def __init__(self, filename):
        MIDIFile.parseFile(filename)

    tracks = []
    m_nTempo = 0
    m_nBPM = 0

    def parseFile(filename):
        n32 = 0
        n16 = 0

        with open(filename, "rb") as f:
            # f = f.read()
            # print(f.read())

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

            fileID = f.read(4)
            headerLength = int.from_bytes(f.read(4), "big")
            nFormat = int.from_bytes(f.read(2), "big")
            trackChunks = int.from_bytes(f.read(2), "big")
            division = int.from_bytes(f.read(2), "big")

            print(fileID)
            print(headerLength)
            print(nFormat)
            print(trackChunks)
            print(division)

            for chunk in range(trackChunks):
                endTrack = False
                wallTime = 0
                previousState = 0
                temp = 0
                events = []

                trackID = f.read(4)
                trackLength = int.from_bytes(f.read(4), "big")

                print("-------- NEW TRACK --------")
                print(trackID)
                print("track length: " + str(trackLength))

                MIDIFile.tracks.append(MIDITrack())

                # loop till the end of the track
                while not endTrack:
                    # the time difference between last note and current note is the delta
                    statusTimeDelta = readValue()
                    # print("time difference: " + str(statusTimeDelta))

                    # the data can begin with an ID or instruction, to check which one it is, we check the status
                    num = f.read(1)
                    status = int.from_bytes(num, "big")

                    # if status == 0:
                    #     if int.from_bytes(f.read(1), "big") == 0:
                    #         print("break at " + str(int.from_bytes(f.read(1), "big")))
                    #         break
                    #     else:
                    #         f.seek(-1, os.SEEK_CUR)

                    if status < 0x80:
                        print("running status! " + str(status & 0xF0))
                        status = previousState
                        if previousState < 0x80:
                            status = temp
                        # since we read the instruction byte, we need to bring it back on the stream so we can sync the values
                        f.seek(-1, os.SEEK_CUR)
                        print("running status!" + str(temp))

                    if (status & 0xF0) == MIDIFile.EventName["VoiceNoteOff"]:
                        # print("in voice note on")
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
                    elif (status & 0xF0) == MIDIFile.EventName["VoiceNoteOn"]:
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
                    elif (status & 0xF0) == MIDIFile.EventName["VoiceAftertouch"]:
                        previousState = status
                        key = status & 0x0F
                        keyPressure = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))
                    elif (status & 0xF0) == MIDIFile.EventName["VoiceControlChange"]:
                        previousState = status
                        channel = status & 0x0F
                        controlID = f.read(1)
                        controlValue = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))

                    elif (status & 0xF0) == MIDIFile.EventName["VoiceProgramChange"]:
                        previousState = status
                        channel = status & 0x0F
                        programID = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))

                    elif (status & 0xF0) == MIDIFile.EventName["VoiceChannelPressure"]:
                        previousState = status
                        channel = status & 0x0F
                        channelPressure = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))

                    elif (status & 0xF0) == MIDIFile.EventName["VoicePitchBend"]:
                        previousState = status
                        channel = status & 0x0F
                        LS7B = f.read(1)
                        MS7B = f.read(1)
                        events.append(MIDIEvent(MIDIEvent.Type.other))

                    elif (status & 0xF0) == MIDIFile.EventName["SystemExclusive"]:
                        temp = previousState
                        previousState = 0

                        if status == 0xFF:
                            # read meta message
                            n = f.read(1)
                            type = int.from_bytes(n, "big")
                            length = readValue()

                            if type == MIDIFile.MetaEventName["MetaSequence"]:
                                print("Sequence number: " + f.read(1) + " " + f.read(1))
                            elif type == MIDIFile.MetaEventName["MetaText"]:
                                print("Text: " + readString(length))
                            elif type == MIDIFile.MetaEventName["MetaCopyright"]:
                                print("Copyright: " + readString(length))
                            elif type == MIDIFile.MetaEventName["MetaTrackName"]:
                                MIDIFile.tracks[chunk].setName(readString(length))
                                print("Name: " + str(MIDIFile.tracks[chunk].name))
                            elif type == MIDIFile.MetaEventName["MetaInstrumentName"]:
                                MIDIFile.tracks[chunk].setInstrument(readString(length))
                                print(
                                    "Instrument: " + MIDIFile.tracks[chunk].instrument
                                )
                            elif type == MIDIFile.MetaEventName["MetaLyrics"]:
                                print("Lyrics: " + readString(length))
                            elif type == MIDIFile.MetaEventName["MetaMarker"]:
                                print("Marker: " + readString(length))
                            elif type == MIDIFile.MetaEventName["MetaCuePoint"]:
                                print("Cue: " + readString(length))
                            elif type == MIDIFile.MetaEventName["MetaChannelPrefix"]:
                                print("Prefix: " + str(f.read(1)))
                            elif type == MIDIFile.MetaEventName["MetaEndOfTrack"]:
                                endTrack = True
                            elif type == MIDIFile.MetaEventName["MetaSetTempo"]:
                                if MIDIFile.m_nTempo == 0:
                                    num = f.read(1)
                                    n = int.from_bytes(num, "big")
                                    MIDIFile.m_nTempo |= n << 16
                                    num = f.read(1)
                                    n = int.from_bytes(num, "big")
                                    MIDIFile.m_nTempo |= n << 8
                                    num = f.read(1)
                                    n = int.from_bytes(num, "big")
                                    MIDIFile.m_nTempo |= n << 0
                                    MIDIFile.m_nBPM = 60000000 / MIDIFile.m_nTempo
                                    print(
                                        "Tempo: "
                                        + str(MIDIFile.m_nTempo)
                                        + " ("
                                        + str(MIDIFile.m_nBPM)
                                        + "bpm)"
                                    )
                            elif type == MIDIFile.MetaEventName["MetaSMPTEOffset"]:
                                print(
                                    "SMPTE: H:"
                                    + str(f.read(1))
                                    + " M:"
                                    + str(f.read(1))
                                    + " S:"
                                    + str(f.read(1))
                                    + " FR:"
                                    + str(f.read(1))
                                    + " FF:"
                                    + str(f.read(1))
                                )
                            elif type == MIDIFile.MetaEventName["MetaTimeSignature"]:
                                n1 = f.read(1)
                                num = f.read(1)
                                n2 = int.from_bytes(num, "big")
                                print(
                                    "Time Signature: "
                                    + str(int.from_bytes(n1, "big"))
                                    + "/"
                                    + str(2 << n2)
                                )
                                n1 = f.read(1)
                                num = f.read(1)
                                print(
                                    "Clocks Per Metronome Tick: "
                                    + str(int.from_bytes(n1, "big"))
                                )
                                print(
                                    "Number of 1/32 notes per 24 MIDI clocks: "
                                    + str(int.from_bytes(num, "big"))
                                )
                            elif type == MIDIFile.MetaEventName["MetaKeySignature"]:
                                print(
                                    "Key Signature: "
                                    + str(int.from_bytes(f.read(1), "big"))
                                )
                                print(
                                    "Minor Key: "
                                    + str(int.from_bytes(f.read(1), "big"))
                                )
                            elif type == MIDIFile.MetaEventName["MetaPort"]:
                                # print("Meta Port")
                                print("Meta Port: " + str(f.read(1)))
                            elif (
                                type == MIDIFile.MetaEventName["MetaSequencerSpecific"]
                            ):
                                print("Sequencer Specific: " + readString(length))
                            else:
                                print("Unrecognised meta event: " + str(type))

                        if status == 0xF0:
                            print("System Executive Begins" + readString(readValue()))
                        if status == 0xF7:
                            print("System Executive Ends" + readString(readValue()))
                    else:
                        print(
                            "Unrecognised Status Byte: "
                            + str(status)
                            + " "
                            + str(previousState)
                            + " "
                            + str(temp)
                        )


demo = MIDIFile("meanwoman.mid")
