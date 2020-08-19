from __future__ import division
from pocketsphinx.pocketsphinx import *
from pocketsphinx import AudioFile
from os import environ, path, listdir
import sys
import time
import wave
from audio.audio_util import *
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

MODELDIR = "./audio/model"
DATADIR = "./audio/audio_data" #wav files
HYPDIR = "./audio/audio_data/hypothesis" # stores test hypotheses

class Audio_Analyzer():

    def __init__(self, filename):
        self.filename = filename
        self.hyp_filename = 'hypothesis-'+self.filename.split('.')[0]+'.txt'
        
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

    def complexity(self, hypothesis):
        word_count = len(hypothesis)
        letter_count = sum([len(word) for word in hypothesis])
        complexity = letter_count / word_count
        print('complexity: ', complexity)

    def filler_words(self, hypothesis, filler='[SPEECH]'):
        ''' Takes in a list of the hypothesis segments and an optional parameter as 
            the filler word to search for and returns the % of the filler word's
            occurrence. The default filler word to search for is 'um' or 'uh', 
            represented as "[SPEECH]" in the hypothesis files. 
            This function assumes that the segments passed in is already cleaned up
            (only contains words spoken, no <s>, </s>, <sil>, or [NOISE])
        '''
        if not filler == '[SPEECH]':
           filler = filler.lower()
        
        num_filler = hypothesis.count(filler)
        total_words = len(hypothesis)
        print('total_words:', total_words)
        if filler == '[SPEECH]':
            filler = 'um or uh' # for better printing in the results
        print('number of ', filler,'said:', num_filler)
        percent = num_filler/total_words
        print('Percent of filler words: ', percent)
        print('compared to TED standard frequency of filler words (0.005589%)...')
        compare_to_standard(percent, 0.005589) # gold standard is hard coded into the program right now
        return percent

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
        config = {
            'verbose': False,
            'audio_file': path.join(DATADIR, self.filename),
            'hmm': path.join(MODELDIR, 'en-us'),
            'lm': path.join(MODELDIR, 'en-us.lm.bin'),
            'dict': path.join(MODELDIR, 'cmudict-en-us.dict')
        }

        audio = AudioFile(**config)
        for phrase in audio:
            print('-' * 28)
            print('| %5s |  %3s  |  %8s  |  %18s  |   %4s   |' % ('start', 'end', 'duration', 'syllables per word', 'word'))
            print('-' * 28)
            for s in phrase.seg():
                print('| %4ss | %4ss | %4ss | %4s | %8s |' % (s.start_frame / fps, s.end_frame / fps, round(s.end_frame / fps - s.start_frame / fps, 2), round(sylco(s.word)), s.word))

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
            hypothesis = self.decode()
            preprocessed_hypothesis = preprocess_segments(hypothesis)
            print('\n************* RESULTS ****************')
            self.filler_words(preprocessed_hypothesis)
            self.filler_words(hypothesis, '<sil>')
            self.complexity(preprocessed_hypothesis)
            self.speed()

        else:
            raise InvalidAudioFileFormat
