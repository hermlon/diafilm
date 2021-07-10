import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPalette, QColor, QPixmap, QImage
from PySide6.QtCore import QThreadPool
import cv2
from videoworker import VideoWorker

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("autochrome")

        main_layout = QVBoxLayout()

        video = MainImage('purple')
        main_layout.addWidget(video)
        
        last_pictures = QHBoxLayout()

        last_pictures.addStretch(1)
        last_pictures.addWidget(SmallImage('teal'))
        last_pictures.addWidget(SmallImage('pink'))

        main_layout.addLayout(last_pictures)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # initialize ThreadPool
        self.threadpool = QThreadPool()

        # start VideoWorker
        video_worker = VideoWorker(0, (100, 100))
        video_worker.signals.update_preview.connect(video.update)

        self.threadpool.start(video_worker)

    def closeEvent(self, event):
        # TODO: somehow send signal to VideoWorker to make it stop
        event.accept()


class MainImage(QLabel):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def update(self, frame):
        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(img))


class SmallImage(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
