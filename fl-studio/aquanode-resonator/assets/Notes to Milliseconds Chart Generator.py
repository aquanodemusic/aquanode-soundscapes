# The following is a Python Code that creates a list of Note names, their frequencies and their time in milliseconds.

import math

def note_frequencies(reference_freq, note_names, octave_range):
    notes_info = []
    note_position = {
        "C ": -9, "C#": -8, "D ": -7, "D#": -6, "E ": -5, "F ": -4, "F#": -3,
        "G ": -2, "G#": -1, "A ": 0, "A#": 1, "B ": 2
    }
    for octave in octave_range:
        for note in note_names:
            noteposition = note_position[note] + (octave - 4) * 12
            frequency = reference_freq * (2 ** (noteposition / 12.0))
            milliseconds = 1000 / frequency
            notes_info.append([f"{note}{octave}", frequency, milliseconds])
    return notes_info

def print_note_details(note_details):
    for note, frequency, milliseconds in note_details: #.3f for 3 digits each
        print(f"Note: {note}, Frequency: {frequency:.3f} Hz, Time: {milliseconds:.7f} ms")

reference_freq = 440.0
note_names = ["C ", "C#", "D ", "D#", "E ", "F ", "F#", "G ", "G#", "A ", "A#", "B "]
octave_range = range(1, 9)

note_details = note_frequencies(reference_freq, note_names, octave_range)
print_note_details(note_details)