from __future__ import division
import sys
import os
import re

''' ************************ audio_util.py ***************************
    This file contains methods that help analyze the transcriptions
    obtained from the audio files. Assuming we already have the
    hypothesis file, we can read in the text file, process it to remove
    additional unwanted information in the file, and count filler words
    ******************************************************************
'''

def read_file(hypdir, filename):
    ''' Takes in a file name and reads it in as a list of words
        Assuming the file is space delimited and is one continuous
        line of text
    '''
    filepath = os.path.join(hypdir, filename)
    with open(filepath, 'r') as f:
        return f.read().split()

def preprocess_segments(segments):
    ''' Preprocesses the segments to remove numbers after words, <sil>, <s>, </s>,
        [NOISE] and return a new list with the cleaned up data
        i.e. new list returned will only contain the words spoken
    '''
    new_list = []
    for word in segments:
        if not (word == '<sil>' or word == '<s>' or word == '</s>' or word == '[NOISE]'):
            if "(" in word:
                new_list.append(word.split("(")[0])
            else:
                new_list.append(word)
    return new_list

def filler_words(segments, filler='[SPEECH]'):
    ''' Takes in a list of the hypothesis segments and an optional parameter as
        the filler word to search for and returns the % of the filler word's
        occurrence. The default filler word to search for is 'um' or 'uh',
        represented as "[SPEECH]" in the hypothesis files.
        This function assumes that the segments passed in is already cleaned up
        (only contains words spoken, no <s>, </s>, <sil>, or [NOISE])
    '''
    if not filler == '[SPEECH]':
        filler = filler.lower()

    num_filler = segments.count(filler)
    total_words = len(segments)
    print('total_words:', total_words)
    if filler == '[SPEECH]':
        filler = 'um or uh' # for better printing in the results
    print('number of ', filler,'said:', num_filler)
    percent = num_filler/total_words
    print('percent of filler words', percent)
    print('compared to TED standard frequency of filler words (0.005589%)...')
    compare_to_standard(percent, 0.005589) # gold standard is hard coded into the program right now
    return percent

def compare_to_standard(percent, standard):
    ''' This function takes in the percentage of the user's usage of filler
        words and compares it with the gold standard and prints out a
        message informing the user their performance against the standard
    '''
    if percent < standard:
        print('GOOD JOB. You don\'t use many filler words.')
    else:
        print('Keep practicing! You still use too many filler words')


def sylco(word):
    def syl(word):
        exception_add = ['serious','crucial']
        exception_del = ['fortunately','unfortunately']
        co_one = ['cool','coach','coat','coal','count','coin','coarse','coup','coif','cook','coign','coiffe','coof','court']
        co_two = ['coapt','coed','coinci']
        pre_one = ['preach']
        syls = 0 #added syllable number
        disc = 0 #discarded syllable number
        #1) if letters < 3 : return 1
        if len(word) <= 3 :
            syls = 1
            return syls
        #2) if doesn't end with "ted" or "tes" or "ses" or "ied" or "ies", discard "es" and "ed" at the end.
        # if it has only 1 vowel or 1 set of consecutive vowels, discard. (like "speed", "fled" etc.)
        if word[-2:] == "es" or word[-2:] == "ed" :
            doubleAndtripple_1 = len(re.findall(r'[eaoui][eaoui]',word))
            if doubleAndtripple_1 > 1 or len(re.findall(r'[eaoui][^eaoui]',word)) > 1 :
                if word[-3:] == "ted" or word[-3:] == "tes" or word[-3:] == "ses" or word[-3:] == "ied" or word[-3:] == "ies" :
                    pass
                else :
                    disc+=1
        #3) discard trailing "e", except where ending is "le"
        le_except = ['whole','mobile','pole','male','female','hale','pale','tale','sale','aisle','whale','while']
        if word[-1:] == "e" :
            if word[-2:] == "le" and word not in le_except :
                pass
            else :
                disc+=1
        #4) check if consecutive vowels exists, triplets or pairs, count them as one.
        doubleAndtripple = len(re.findall(r'[eaoui][eaoui]',word))
        tripple = len(re.findall(r'[eaoui][eaoui][eaoui]',word))
        disc+=doubleAndtripple + tripple
        #5) count remaining vowels in word.
        numVowels = len(re.findall(r'[eaoui]',word))
        #6) add one if starts with "mc"
        if word[:2] == "mc" :
            syls+=1
        #7) add one if ends with "y" but is not surrouned by vowel
        if word[-1:] == "y" and word[-2] not in "aeoui" :
            syls +=1
        #8) add one if "y" is surrounded by non-vowels and is not in the last word.
        for i,j in enumerate(word) :
            if j == "y" :
                if (i != 0) and (i != len(word)-1) :
                    if word[i-1] not in "aeoui" and word[i+1] not in "aeoui" :
                        syls+=1
        #9) if starts with "tri-" or "bi-" and is followed by a vowel, add one.
        if word[:3] == "tri" and word[3] in "aeoui" :
            syls+=1
        if word[:2] == "bi" and word[2] in "aeoui" :
            syls+=1
        #10) if ends with "-ian", should be counted as two syllables, except for "-tian" and "-cian"
        if word[-3:] == "ian" :
        #and (word[-4:] != "cian" or word[-4:] != "tian") :
            if word[-4:] == "cian" or word[-4:] == "tian" :
                pass
            else :
                syls+=1
        #11) if starts with "co-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.
        if word[:2] == "co" and word[2] in 'eaoui' :
            if word[:4] in co_two or word[:5] in co_two or word[:6] in co_two :
                syls+=1
            elif word[:4] in co_one or word[:5] in co_one or word[:6] in co_one :
                pass
            else :
                syls+=1
        #12) if starts with "pre-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.
        if word[:3] == "pre" and word[3] in 'eaoui' :
            if word[:6] in pre_one :
                pass
            else :
                syls+=1
        #13) check for "-n't" and cross match with dictionary to add syllable.
        negative = ["doesn't", "isn't", "shouldn't", "couldn't","wouldn't"]
        if word[-3:] == "n't" :
            if word in negative :
                syls+=1
            else :
                pass
        #14) Handling the exceptional words.
        if word in exception_del :
            disc+=1
        if word in exception_add :
            syls+=1
        # calculate the output
        return numVowels - disc + syls
    if (word == '<sil>' or word == '<s>' or word == '</s>' or word == '[NOISE]' or word == '[SPEECH]'):
        return 0
    elif "(" in word:
        return syl(word.split("(")[0].lower())
    else:
        return syl(word.lower())


if __name__=='__main__':
    DATADIR = sys.argv[1] #directory to read the hypothesis files from
    # assumes the directory provided only contains text files of the hypotheses
    for f in os.listdir(DATADIR):
        if not f.startswith('.') and os.path.isfile(os.path.join(DATADIR, f)):
            print('file is:', f)
            filename = os.path.join(DATADIR, f)
            read = read_file(filename) # original segments
            preprocessed = preprocess_segments(read) # only spoken words
            print('\n*********** FILE: ', f, '****************')
            ums = filler_words(preprocessed)
            #likes = filler_words(preprocessed, 'like') #<-- inaccurate
            silences = filler_words(read, '<sil>')
            print('% of "um"s said ([\'SPEECH\'])', ums)
            #print '% of "like"s said', likes
            print('% of "<sil>"', silences)