from enum import Enum
import os

"""
    This is a simple parser for a MIDI file that outputs a human readable text file of the instruction in the file
    It is an adaptation of the parser created by Javidx9 (OneLoneCoder), hence the credit of the logic of this parser is completely for him
    You can read the source code for their parser, written in C++ at https://github.com/OneLoneCoder/olcPixelGameEngine/blob/master/Videos/OneLoneCoder_PGE_MIDI.cpp
    It will be helpful for further explanation, and to compare how both languages compare when parsing
    If you want more information on the MIDI file format and OneLoneCoder's code, I recommend watching https://www.youtube.com/watch?v=040BKtnDdg0
    It includes their detailed explanations for the source code and the basis of the logic

    For a breakdown of the MIDI file components, i.e. the instructions, I recommend the reading http://personal.kent.edu/~sbirch/Music_Production/MP-II/MIDI/midi_file_format.htm#midi_event
    It includes an extensive list of voice messages, mode messages as well as system instructions

    This parser essentially identifies 3 main features in a MIDI file:
        - The Tracks in a file
        - The events in a track
        - The notes used by a track
    These are all identified as classes, and objects of these classes will be used to create the structure of the MIDI file as we parse
"""

# This recognises the events in a MIDI track
# The type of events inclde: playing a note, stopping a note, or another system executive instruction
class MIDIEvent:

    # defining an enumeration on the type of MIDI events
    class Type(Enum):
        noteOFF = 0
        noteON = 1
        other = 2

    # A MIDI event has the following features
    # Type = The type of event (from the above enumeration)
    # Key = The note being played
    # velocity = the speed of the note in the track
    # deltaTick = the time difference between this and the previous event
    def __init__(self, note, noteID=0, vel=0, delta=0):
        self.type = note
        self.key = noteID
        self.velocity = vel
        self.deltaTick = delta

    def __repr__(self):
        return (
            "\nEvent Type: "
            + str(self.type)
            + " Key: "
            + str(self.key)
            + " Velocity: "
            + str(self.velocity)
            + " delta tick: "
            + str(self.deltaTick)
        )


# recognises a note in a track in the MIDI file
# the features of the note is identified by noting when a note On and note Off event arrive
class MIDINote:
    # a note in MIDI has the following features
    # key = The note
    # velocity = the speed of the note
    # startTime = when the note begins
    # duration = how long the note is played for
    def __init__(self, k, vel, start, dur):
        self.key = k
        self.velocity = vel
        self.startTime = start
        self.duration = dur

    def __repr__(self):
        return (
            "\n\t Key: "
            + str(self.key)
            + " Velocity: "
            + str(self.velocity)
            + "start time: "
            + str(self.startTime)
            + " duration: "
            + str(self.duration)
        )


# recognises a track in the MIDI file
# a track has a minimum and maximum note, which is initialised is 64 as a base value
class MIDITrack:
    maxNote = 64
    minNote = 64

    # The features in a note are as follows:
    # name = a name given to a track, if any
    # instrument = an instrument specified for a track, if any
    # events = the list of events in the note
    # notes = the list of notes and the duration
    def __init__(self):
        self.name = ""
        self.instrument = ""
        self.events = []
        self.notes = []

    def __repr__(self):
        temp = (
            ("\nTrack Name: " + str(self.name))
            + ("\nTrack Instrument: " + str(self.instrument))
            + ("\nTrack Events:")
        )
        for eve in self.events:
            temp = temp + repr(eve)
        temp = temp + ("\nTrack Notes:")
        for n in self.notes:
            temp = temp + repr(n)
        return temp

    def setName(self, name):
        self.name = name

    def setInstrument(self, inst):
        self.instrument = inst

    def setEvents(self, eve):
        self.events = eve


# the MIDI file class
class MIDIFile:

    # The following dictionaries are used to identify specific MIDI event and meta instructions
    # for more information on these events, visit: http://personal.kent.edu/~sbirch/Music_Production/MP-II/MIDI/midi_file_format.htm#midi_event
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

    # this includes the tracks and the tempo and BPM of the file
    tracks = []
    tempo = 0
    bpm = 0
    temp = ""

    def __init__(self, filename):
        MIDIFile.parseFile(filename)

    # A function that parses the file
    def parseFile(filename):
        # MIDI files are a sequence of bytes
        with open(filename, "rb") as f:

            # read a string of given size
            readString = lambda n: str(f.read(n))

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

            # read File information
            fileID = f.read(4)
            headerLength = int.from_bytes(f.read(4), "big")
            nFormat = int.from_bytes(f.read(2), "big")
            trackChunks = int.from_bytes(f.read(2), "big")
            division = int.from_bytes(f.read(2), "big")

            # add to the temp
            MIDIFile.temp = (
                "\nFile ID: "
                + str(fileID)
                + " header length: "
                + str(headerLength)
                + " format: "
                + str(nFormat)
                + " Number of Tracks: "
                + str(trackChunks)
                + " number of divisions: "
                + str(division)
            )

            # print(fileID)
            # print(headerLength)
            # print(nFormat)
            # print(trackChunks)
            # print(division)

            # parsing every track
            for chunk in range(trackChunks):
                endTrack = False
                wallTime = 0
                previousState = 0
                events = []

                # creating an track object for the file
                MIDIFile.tracks.append(MIDITrack())

                # reading the ID and length of the track
                trackID = f.read(4)
                trackLength = int.from_bytes(f.read(4), "big")

                MIDIFile.temp = (
                    MIDIFile.temp
                    + ("\n-------- NEW TRACK --------")
                    + "\nTrack ID: "
                    + str(trackID)
                    + "\nTrack Length: "
                    + str(trackLength)
                    + "\n"
                )

                print("\n-------- NEW TRACK --------")
                # loop till the end of the track
                while not endTrack:
                    # the time difference between last note and current note is the delta
                    statusTimeDelta = readValue()

                    # the data can begin with an ID or instruction, to check which one it is, we check the status
                    num = f.read(1)
                    status = int.from_bytes(num, "big")

                    # if it begins with an instruction
                    if status < 0x80:
                        # set the previous status as the current status
                        status = previousState
                        # since we read the instruction byte, we need to bring it back on the stream so we can sync the values
                        f.seek(-1, os.SEEK_CUR)

                    # parse to read the instruction and identify it
                    if (status & 0xF0) == MIDIFile.EventName["VoiceNoteOff"]:
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

                        # if the veloctiy is 0, that means the note isnt being played
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
                                n1 = 0
                                n = int.from_bytes(f.read(1), "big")
                                n1 |= n << 16
                                n = int.from_bytes(f.read(1), "big")
                                n1 |= n << 8
                                n = int.from_bytes(f.read(1), "big")
                                n1 |= n << 0
                                MIDIFile.bpm = 60000000 / n1
                                if n1 != MIDIFile.tempo:
                                    MIDIFile.tempo = n1
                                    print(
                                        "Tempo: "
                                        + str(MIDIFile.tempo)
                                        + " ("
                                        + str(MIDIFile.bpm)
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
                                print("Meta Port")
                                f.read(1)
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
                        print("Unrecognised Status Byte: " + str(status))

                # add the list of events to the track
                MIDIFile.tracks[chunk].setEvents(events)

            # creating list of notes used in every track
            for track in MIDIFile.tracks:
                wallTime = 0
                processedNotes = []  # notes that are being processed
                notes = []  # notes that have been processed

                for eve in track.events:
                    # getting the total time since
                    wallTime = wallTime + eve.deltaTick

                    if eve.type == MIDIEvent.Type.noteON:
                        processedNotes.append(
                            MIDINote(eve.key, eve.velocity, wallTime, 0)
                        )
                    # if a note has ended
                    elif eve.type == MIDIEvent.Type.noteOFF:

                        def findNote(noteList):
                            for n in noteList:
                                if n.key == eve.key:
                                    return n

                        # finding the note when it began
                        note = findNote(processedNotes)

                        if note:
                            processedNotes.remove(note)
                            # getting duration
                            note.duration = wallTime - note.startTime
                            notes.append(note)

                            # checking minimum and maximum of a note in a track
                            track.minNote = min(
                                track.minNote, int.from_bytes(note.key, "big")
                            )
                            track.maxNote = min(
                                track.maxNote, int.from_bytes(note.key, "big")
                            )
                # Setting the track's notes
                track.notes = notes

    def __repr__(self):
        for track in self.tracks:
            if track.name != "":
                MIDIFile.temp = MIDIFile.temp + repr(track)
        return MIDIFile.temp


demo = MIDIFile("bach_846.mid")
script = repr(demo)
f = open("openedMIDI.txt", "w")
f.write(script)
f.close()
