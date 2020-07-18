from __future__ import division
from pocketsphinx.pocketsphinx import *
from pocketsphinx import AudioFile
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
#MODELDIR = "/Users/rishabh.patni/opt/anaconda3/lib/python3.6/site-packages/pocketsphinx/model"
DATADIR = "audio_data" #wav files
HYPDIR = "audio_data/hypothesis" # stores test hypotheses

class Audio_Analyzer():

    def __init__(self, filename):
        self.filename = filename
        self.hyp_filename = 'hypothesis-'+self.filename.split('.')[0]+'.txt'
        # create a decoder
        self.config = Decoder.default_config()
        self.config.set_string('-audio_file', path.join(DATADIR, self.filename))
        self.config.set_string('-hmm', path.join(MODELDIR, 'en-us'))
        self.config.set_string('-lm', path.join(MODELDIR, 'en-us.lm.bin'))
        self.config.set_string('-dict', path.join(MODELDIR, 'cmudict-en-us.dict'))

    def write_hypothesis(self, outfile, segments):
        ''' Writes the hypothesis file'''
        with open(path.join(HYPDIR, outfile), 'w') as o:
            for word in segments:
                o.write(word+' ')
        o.close()

    def complexity(self):
        read = read_file(HYPDIR, self.hyp_filename) # original segments
        preprocessed = preprocess_segments(read) # only spoken words
        word_count = len(preprocessed)
        letter_count = sum([len(word) for word in preprocessed])
        complexity = letter_count / word_count
        print('complexity: ', complexity)

    def decode(self):
        ''' Decode streaming data.'''
        decoder = Decoder(self.config)
        decoder.start_utt()

        stream = open(path.join(DATADIR, self.filename),'rb')

        while True:
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
            else:
                break
        decoder.end_utt()
        segments = [seg.word for seg in decoder.seg()]
        f = self.hyp_filename
        print ('Best hypothesis segments: ', [seg.word for seg in decoder.seg()])
        self.write_hypothesis(f, segments)
        return segments

    def speed(self):
        fps = 100
        audio = AudioFile()
        for phrase in audio:
            print('-' * 28)
            print('| %5s |  %3s  |  %3s  |   %4s   |' % ('start', 'end', 'duration', 'word'))
            print('-' * 28)
            for s in phrase.seg():
                print('| %4ss | %4ss | %4ss | %8s |' % (s.start_frame / fps, s.end_frame / fps, round(s.end_frame / fps - s.start_frame / fps, 2), s.word))
            print('-' * 28)


    def file_in_correct_format(self):
        ''' Checks if the provided file is in the correct format
            (i.e. mono channel with a sampling rate of 16000).
            returns True if it is in the correct format and False
            if it isn't. Also prints out an error message if the
            file is not in the correct format
        '''
        wf = wave.open(path.join(DATADIR, self.filename), 'rb')
        # get information about the audio file provided
        channels = wf.getnchannels()
        rate = wf.getframerate()

        # print error message if the format of provided file is incorrect
        if not channels == 1 or not rate == 16000:
            return False
        return True

    def analyze_audio(self):
        if self.file_in_correct_format():
            segments = self.decode()
            self.speed()
            new_list = preprocess_segments(segments)
            print('\n************* RESULTS ****************')
            filler_words(new_list)
            self.complexity()

        else:
            raise Invalid_Audio_File_Format
