class InvalidAudioFileFormat(Exception):
    def __init__(self):
        self.message = "File provided is not in the correct format. Please provide a mono channel file with a sampling rate of 16000"
        super().__init__(self.message)