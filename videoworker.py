from PySide6.QtCore import QRunnable, Slot, QObject, Signal
import cv2

class VideoWorkerSignals(QObject):

    update_preview = Signal(object)

class VideoWorker(QRunnable):

    def __init__(self, camera_index, preview_size):
        super().__init__()
        self.preview_size = preview_size
        self.signals = VideoWorkerSignals()
        self.capture = cv2.VideoCapture(camera_index)

    @Slot()
    def run(self):
        while self.capture.isOpened():
            self.grab_preview()

    def grab_preview(self):
        ret_val, img = self.capture.read()
        preview = cv2.resize(img, self.preview_size, interpolation=cv2.INTER_AREA)
        frame_preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        self.signals.update_preview.emit(frame_preview)
