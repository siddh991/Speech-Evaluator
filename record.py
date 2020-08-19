from sys import byteorder
from array import array
from struct import pack
import select
import sys

import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os


''' *************************** record.py ******************************
    This file allows users to record themselves using the microphone of
    their local computer and saves the recorded file as 'demo.wav' in
    the data directory. Recording starts right after running the script
    and stops either if the user hits the 'Enter' key or is silent for
    a long period of time (i.e. if continuous silence time > SILENT_THRESHOLD)
    sources:
    *******************************************************************
'''

THRESHOLD = 300  # threshold for when to "tag" something as silent
SILENT_THRESHOLD = 30  # threshold for when to stop recording
CHUNK_SIZE = 1024
# FORMAT = pyaudio.paInt16
RATE = 16000  # sampling rate
AUDIO_DATADIR = "audio/audio_data/"
VIDEO_DATADIR = "video/video_data/"


class VideoRecorder():
    # Video class based on openCV
    def __init__(self):
        self.open = True
        self.device_index = 0
        self.fps = 20               # fps should be the minimum constant rate at which the camera can
        # capture images (with no decrease in speed over time; testing is required)
        self.fourcc = "mp4v"
        # video formats and sizes also depend and vary according to the camera used
        self.frameSize = (640, 480)
        self.video_filename = "temp_video.mp4"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_cap.set(3, 640)
        self.video_cap.set(4, 480)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(
            VIDEO_DATADIR + self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()
        self.video_frame = None

    # Video starts being recorded
    def record(self):
        timer_start = time.time()
        timer_current = 0
        
        while(self.open==True):
            ret, self.video_frame = self.video_cap.read()
            if (ret==True):
                self.video_out.write(self.video_frame)
                self.frame_counts += 1
                #time.sleep(0.16)
            
                # Uncomment the following three lines to make the video to be
                # displayed to screen while recording
                # gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
                # cv2.imshow('video_frame', gray)
                # cv2.waitKey(1)
            else:
                break
        
            # 0.16 delay -> 6 fps

    # Finishes the video recording therefore the thread to
    def stop(self):
        if self.open==True:	
            self.open=False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()	
        else: 
            pass

    # Launches the video recording function using a thread			
    def start(self):
        video_thread = threading.Thread(target=self.record, daemon = True)
        video_thread.start()


class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self):
        self.open = True
        self.rate = 16000
        self.frames_per_buffer = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                    channels=self.channels,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []
        self.r = array('h')
        
    def is_silent(self, snd_data):
        "Returns 'True' if below the 'silent' threshold"
        return max(snd_data) < THRESHOLD

    def normalize(self, snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)

        r = array('h')
        for i in snd_data:
            r.append(int(i*times))
        return r

    def trim(self, snd_data):
        "Trim the blank spots at the start and end"
        def _trim(snd_data):
            snd_started = False
            r = array('h')

            for i in snd_data:
                if not snd_started and abs(i)>THRESHOLD:
                    snd_started = True
                    r.append(i)

                elif snd_started:
                    r.append(i)
            return r

        # Trim to the left
        snd_data = _trim(snd_data)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data)
        snd_data.reverse()
        return snd_data

    def add_silence(self, snd_data, seconds):
        "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
        r = array('h', [0 for i in range(int(seconds*RATE))])
        r.extend(snd_data)
        r.extend([0 for i in range(int(seconds*RATE))])
        return r

    # Audio starts being recorded
    def record(self):
        num_silent = 0
        snd_started = False
        was_silent = False

        self.stream.start_stream()
        
        while(self.open == True):
            data = self.stream.read(self.frames_per_buffer) 
            if byteorder == 'big':
                data.byteswap()
            self.r.extend(data)
            self.audio_frames.append(data)

            silent = self.is_silent(data)

            if silent and snd_started:
                num_silent += 1
                was_silent = True
            elif not silent and not snd_started:
                self.snd_started = True
            elif not silent and was_silent:
                # reset num_silent if was silent but now talking again
                num_silent = 0
                was_silent = False
            
            if self.open==False:
                break

            
    # Finishes the audio recording therefore the thread too    
    def stop(self):
        if(self.open==True):
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            
            #self.audio_frames = self.normalize(self.r)
            #self.audio_frames = self.trim(self.r)
            #self.audio_frames = self.add_silence(self.audio_frames, 0.5)

            waveFile = wave.open(AUDIO_DATADIR + self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()
        else:
            pass
    
    # Launches the audio recording function using a thread
    def start(self):
        self.audio_thread = threading.Thread(target=self.record, daemon = True)
        self.audio_thread.start()


def start_AVrecording():			
    global video_thread
    global audio_thread
    
    video_thread = VideoRecorder()
    audio_thread = AudioRecorder()

    audio_thread.start()
    video_thread.start()


def stop_AVrecording():
    audio_thread.stop() 
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print("total frames " + str(frame_counts))
    print("elapsed time " + str(elapsed_time))
    print ("recorded fps " + str(recorded_fps))
    video_thread.stop() 


if __name__ == '__main__':
    print("*** please speak into the microphone ***\n")	
    start_AVrecording()  
    
    # time.sleep(5)

    # print('Press q to stop recording video')
    # while(True):
    #     gray = cv2.cvtColor(video_thread.video_frame, cv2.COLOR_BGR2GRAY)
    #     cv2.imshow('video_frame', gray)

    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    
    input("Press Enter to continue...")
    stop_AVrecording()
    print("Done")

    # extract_audio('./video_data/vid.mp4')
    # record_to_file(os.path.join(DATADIR,'demo.wav'))
    print("\n*** done - result written to demo.wav in the data directory ***")
