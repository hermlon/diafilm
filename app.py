import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtGui import QPalette, QColor, QPixmap, QImage
from PySide6.QtCore import QThreadPool, QSize, Signal
import cv2
from videoworker import VideoWorker
from settings import SettingsControls

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("autochrome")
        self.resize(900, 700)

        main_layout = QVBoxLayout()

        preview = QHBoxLayout()
        
        last_shot = LiveImageView('lime')
        last_shot.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.video = ToggleImageView('purple')
        self.video.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        preview.addWidget(last_shot)
        preview.addWidget(self.video)

        main_layout.addLayout(preview)

        self.controls = SettingsControls()
        self.controls.switch_tabs.connect(self.video.show_view)

        main_layout.addWidget(self.controls)
        
        last_pictures = QHBoxLayout()

        last_pictures.addWidget(LiveImageView('teal'))
        last_pictures.addWidget(LiveImageView('pink'))

        main_layout.addLayout(last_pictures)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # initialize ThreadPool
        self.threadpool = QThreadPool()

        # start VideoWorker
        self.video_worker = VideoWorker(0, self.width()//2-50)
        self.video_worker.signals.update_preview.connect(self.update_preview)
        self.video_worker.signals.update_analysis.connect(self.update_analysis)

        self.video_worker.analyzer.new_image.connect(self.new_image)
        self.video_worker.analyzer.update_progress.connect(self.update_progress)
        self.controls.threshold_changed.connect(self.video_worker.set_threshold)
        self.controls.interval_changed.connect(self.video_worker.set_interval)

        self.threadpool.start(self.video_worker)

    def closeEvent(self, event):
        self.video_worker.stop()

    def new_image(self):
        print('new image')

    def update_progress(self, progress, status):
        #print('progress: ' + str(progress))
        #print(status)
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

class ToggleImageView(LiveImageView):

    def __init__(self, color):
        super().__init__(color)
        self._main_view = True

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
