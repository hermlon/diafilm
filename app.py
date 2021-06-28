import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPalette, QColor

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        video = DiaMainImage('purple')
        main_layout.addWidget(video)
        
        last_pictures = QHBoxLayout()

        last_pictures.addStretch(1)
        last_pictures.addWidget(DiaSmallImage('teal'))
        last_pictures.addWidget(DiaSmallImage('pink'))

        main_layout.addLayout(last_pictures)


        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

class DiaMainImage(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class DiaSmallImage(QWidget):

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
