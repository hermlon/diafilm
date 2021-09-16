import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtGui import QPalette, QColor, QPixmap, QImage, QShortcut
from PySide6.QtCore import QThreadPool, QSize, Signal
import cv2
from videoworker import VideoWorker
from audioworker import AudioWorker
from settings import SettingsControls
from filesaver import Filesaver
from config import video_device

class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()

		self.setWindowTitle("diafilm")
		self.resize(900, 700)
		
		self.filesaver = Filesaver()

		main_layout = QVBoxLayout()

		preview = QHBoxLayout()
		
		self.last_shot = LiveImageView('lime')
		self.last_shot.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
		self.video = ToggleImageView('purple')
		self.video.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
		preview.addWidget(self.last_shot)
		preview.addWidget(self.video)

		main_layout.addLayout(preview)

		self.controls = SettingsControls()
		self.controls.switch_tabs.connect(self.video.show_view)

		main_layout.addWidget(self.controls)
		
		widget = QWidget()
		widget.setLayout(main_layout)
		self.setCentralWidget(widget)

		# initialize ThreadPool
		self.threadpool = QThreadPool()

		# start VideoWorker
		self.video_worker = VideoWorker(video_device, self.width()//2-50)
		self.video_worker.signals.update_preview.connect(self.update_preview)
		self.video_worker.signals.update_analysis.connect(self.update_analysis)

		self.video_worker.analyzer.new_image.connect(self.new_image)
		self.video_worker.analyzer.update_progress.connect(self.update_progress)
		self.controls.threshold_changed.connect(self.video_worker.set_threshold)
		self.controls.interval_changed.connect(self.video_worker.set_interval)
		
		self.threadpool.start(self.video_worker)
		
		self.audio_worker = AudioWorker()
		
		self.mute = False
		
		self.redo_shortcut = QShortcut(self)
		self.redo_shortcut.setKey('r')
		self.redo_shortcut.activated.connect(lambda: self.new_image(redo=True, manual=True))
		
		self.take_shortcut = QShortcut(self)
		self.take_shortcut.setKey('t')
		self.take_shortcut.activated.connect(lambda: self.new_image(manual=True))
		
		self.mute_shortcut = QShortcut(self)
		self.mute_shortcut.setKey('m')
		self.mute_shortcut.activated.connect(self.toggle_mute)
		
		self.run_shortcut = QShortcut(self)
		self.run_shortcut.setKey('s')
		self.run_shortcut.activated.connect(self.controls.run_button.toggle_shortcut)
		
	def toggle_mute(self):
		self.mute = not self.mute

	def closeEvent(self, event):
		self.video_worker.stop()

	def new_image(self, redo=False, manual=False):
		if not self.mute:
			self.audio_worker.start()
		self.last_shot.update(self.video_worker.get_last_preview())
		if not self.controls.is_paused() or manual:
			if not redo:
				self.controls.no += 1
			self.filesaver.save(self.controls.get_output_dir(), self.controls.get_prefix(), self.controls.no, self.video_worker.get_last_frame())
		
	def update_progress(self, progress, max_progress, status):
		self.controls.update_progress(progress, max_progress)
		pass

	def update_preview(self, frame):
		self.video.update_main(frame)

	def update_analysis(self, frame, percent):
		self.video.update_secondary(frame)
		self.controls.update_percentage(percent)


class LiveImageView(QLabel):

	def __init__(self, color):
		super().__init__()
		self.setAutoFillBackground(True)
		self.setScaledContents(True)

		palette = self.palette()
		palette.setColor(QPalette.Window, QColor(color))
		self.setPalette(palette)

	def update(self, frame):
		img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
		self.setPixmap(QPixmap.fromImage(img))
		
	def flash(self):
		white_frame = QPixmap()
		white_frame.fill()
		self.setPixmap(white_frame)

class ToggleImageView(LiveImageView):

	def __init__(self, color):
		super().__init__(color)
		self._main_view = True
		
	def get_pixmap(self):
		return super().pixmap

	def update_secondary(self, frame):
		if not self._main_view:
			super().update(frame)

	def update_main(self, frame):
		if self._main_view:
			super().update(frame)

	def show_view(self, show_main_view):
		self._main_view = show_main_view

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
