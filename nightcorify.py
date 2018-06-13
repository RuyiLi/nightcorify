# Script made by Huckzel
# https://github.com/Huckzel/nightcorify

import numpy as np

from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

def speedup_audio(sound_array, factor):
    indices = np.round(np.arange(0, len(sound_array), factor))
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[indices.astype(int)]

def prepare_audio(file_name, rate=44100, speedup=1.3):
    audio = AudioFileClip(file_name)
    data = audio.to_soundarray(fps=rate)
    data = speedup_audio(data, speedup)
    return AudioArrayClip(data, fps=rate)

def nightcorify(source_file, destination_file):
    audio = prepare_audio(source_file)
    audio.write_audiofile(destination_file)
