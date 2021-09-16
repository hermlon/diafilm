from PySide6.QtCore import QThread
from pydub import AudioSegment
from pydub.playback import play

class AudioWorker(QThread):

	def __init__(self):
		super().__init__()
		self.flash_sound =  AudioSegment.from_ogg("/usr/share/sounds/freedesktop/stereo/camera-shutter.oga")
		
	def run(self):
		play(self.flash_sound)