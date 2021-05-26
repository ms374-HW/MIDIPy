# MIDIPy

This is a simple parser for a MIDI file that outputs a human readable text file of the instruction in the file. It is an adaptation of the parser created by Javidx9 (OneLoneCoder), hence the credit of the logic of this parser is completely for them. This version only checks for another instruction. You can read the source code for their parser, <a href="https://github.com/OneLoneCoder/olcPixelGameEngine/blob/master/Videos/OneLoneCoder_PGE_MIDI.cpp" target="_blank">written in C++</a> </br></br>

## Background

It will be helpful for further explanation, and to compare how both languages compare when parsing. </br>
If you want more information on the MIDI file format and OneLoneCoder's code, I recommend watching <a href="https://www.youtube.com/watch?v=040BKtnDdg0" target="_blank">their video. </a> It includes their detailed explanations for the source code and the basis of the logic </br></br>

## Pre-requisites

- Language = Python 3.7
- Libraries = OS, Enum

## MIDI File

For a breakdown of the MIDI file components, i.e. the instructions, I recommend the reading <a href="http://personal.kent.edu/~sbirch/Music_Production/MP-II/MIDI/midi_file_format.htm#midi_event" target="_blank">this webpage. </a> It includes an extensive list of voice messages, mode messages as well as system instructions. </br></br>

## Parser

This parser essentially identifies 3 main features in a MIDI file:

- The Tracks in a file
- The events in a track
- The notes used by a track

These are all identified as classes, and objects of these classes will be used to create the structure of the MIDI file as we parse

## How to use this file

### Example Run

To run the file on the example MIDI File [1], simply fork and download the repository and click run on your IDE or run the command:

```
python3 main.py
```

### Using your own MIDI file

You can easily replace this with another MIDI file, by changing the path to your MIDI file in line 512:

```
demo = MIDIFile("your_file_path.mid")
```

### Using your own MIDI file

You can view the graph of the notes in the track, with every track represented as its own color in the generated file 'music.png', the graph for the sample MIDI file has been given

## Future

Since this is a simple parser, more work can be done in the output to make it more understandable and intuitive. An interesting prospect can be visualising the events in the track.

</br> </br>
[1]: http://www.piano-midi.de/bach.htm
