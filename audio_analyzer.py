from __future__ import division
from pocketsphinx.pocketsphinx import *
from os import environ, path, listdir
import sys
import time
import wave
from audio_util import *
from exceptions import *

''' ******************** speech_to_text.py ************************
    This file takes in an audio file (or multiple files) and uses 
    the automatic speech recognition (ASR) system CMUPocketSphinx
    to generate a transcription for the files, writes each of the 
    results to a hypothesis file and reports the frequencies of the
    use of filler words ("um" and "uhh" for now) compared to the 
    gold standard.
    ***************************************************************
'''

MODELDIR = "/anaconda3/envs/speech-evaluator/lib/python3.6/site-packages/pocketsphinx/model"
DATADIR = "audio_data" #wav files
HYPDIR = "audio_data/hypothesis" # stores test hypotheses

class Audio_Analyzer():

    def __init__(self):
        # create a decoder
        self.config = Decoder.default_config()
        self.config.set_string('-hmm', path.join(MODELDIR, 'en-us'))
        self.config.set_string('-lm', path.join(MODELDIR, 'en-us.lm.bin'))
        self.config.set_string('-dict', path.join(MODELDIR, 'cmudict-en-us.dict'))

    def write_hypothesis(self, outfile, segments):
        ''' Writes the hypothesis file'''
        with open(path.join(HYPDIR, outfile), 'w') as o:
            for word in segments:       
                o.write(word+' ')  
        o.close()  
        
    def decode(self, datadir, filename):
        ''' Decode streaming data.'''
        decoder = Decoder(self.config)
        decoder.start_utt()
        
        stream = open(path.join(datadir,filename),'rb')
        
        while True:
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
            else:
                break
        decoder.end_utt()
        segments = [seg.word for seg in decoder.seg()]
        f = 'hypothesis-'+filename.split('.')[0]+'.txt'
        print ('Best hypothesis segments: ', [seg.word for seg in decoder.seg()])
        self.write_hypothesis(f, segments)
        return segments
    
    def file_in_correct_format(self, filename):
        ''' Checks if the provided file is in the correct format 
            (i.e. mono channel with a sampling rate of 16000).
            returns True if it is in the correct format and False 
            if it isn't. Also prints out an error message if the 
            file is not in the correct format
        '''
        wf = wave.open(filename, 'rb')
        # get information about the audio file provided
        channels = wf.getnchannels()
        rate = wf.getframerate()
        
        # print error message if the format of provided file is incorrect
        if not channels == 1 or not rate == 16000:
            return False
        return True
    
    def analyze_audio(self, filename):
        if self.file_in_correct_format(path.join(DATADIR, filename)):
            segments = self.decode(DATADIR, filename)
            new_list = preprocess_segments(segments)
            print('\n************* RESULTS ****************')
            filler_words(new_list)
            
        else:
            raise Invalid_Audio_File_Format
