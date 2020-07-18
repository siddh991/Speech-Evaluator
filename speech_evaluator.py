from __future__ import division
from os import environ, path, listdir
import sys
import time
import wave
import audio_analyzer

''' ******************** speech_evaluator.py **********************
    This file takes in an audio file (or multiple files) and uses
    the automatic speech recognition (ASR) system CMUPocketSphinx
    to generate a transcription for the files, writes each of the
    results to a hypothesis file and reports the frequencies of the
    use of filler words ("um" and "uhh" for now) compared to the
    gold standard.
    ***************************************************************
'''

if __name__=='__main__':
    start = time.time()
    if len(sys.argv) == 2:
        # if one argument provided, it's a filename
        # and assume the data directory is the default data directory
        filename = sys.argv[1]
        audio_analyzer = audio_analyzer.Audio_Analyzer(filename)
        audio_analyzer.analyze_audio()
    else:
        print('ERROR: invalid # of arguement')

    end = time.time()
    print('time elapsed:', (end - start))
