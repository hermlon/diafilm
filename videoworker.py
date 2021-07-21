from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from enum import Enum
import cv2

class VideoWorkerSignals(QObject):

    update_preview = Signal(object)
    update_analysis = Signal(object, float)

class VideoWorker(QRunnable):

    def __init__(self, camera_index, preview_width):
        super().__init__()
        self.analyzer = VideoAnalyzer()
        self._enabled = True
        self.preview_width = preview_width
        self.signals = VideoWorkerSignals()
        self.capture = cv2.VideoCapture(camera_index)
        #self.capture = cv2.VideoCapture("test/test5.mp4")
        #yuyv vs mpeg?
        #self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
        #self.capture.set(cv2.CAP_PROP_EXPOSURE, 2)
        #self.capture.set(cv2.CAP_PROP_CONTRAST, 64)
        self._interval = (0.1, 0.7)
        self._threshold = 0

    def stop(self):
        self._enabled = False

    def set_threshold(self, value):
        self._threshold = value

    def set_interval(self, value):
        self._interval = (value[0]/100, value[1]/100)

    @Slot()
    def run(self):
        while self._enabled and self.capture.isOpened():
            self.grab_preview()

    def grab_preview(self):
        ret_val, img = self.capture.read()
        if ret_val:
            preview = cv2.resize(img, self.get_best_fit_size(img.shape), interpolation=cv2.INTER_AREA)
            frame_preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            try:
                self.signals.update_preview.emit(frame_preview)
                self.analyzer.frame(self.is_black(img, self._interval, self._threshold))
            except RuntimeError as e:
                # signals don't exist after closing main window
                pass
        else:
            print('no frame')

    def get_best_fit_size(self, img_size):
        return (self.preview_width, round(img_size[0]/img_size[1]*self.preview_width))

    def is_black(self, img, percent, val):
        # resize to preview size before analysis, faster but couples gui to analysis
        img = cv2.resize(img, self.get_best_fit_size(img.shape), interpolation=cv2.INTER_AREA)
        pixels = img.shape[0] * img.shape[1]
        threshold_img = self.threshold(img, val)
        percentage = 1 - cv2.countNonZero(threshold_img)/pixels
        #threshold_preview = cv2.resize(threshold_img, self.get_best_fit_size(img.shape), interpolation=cv2.INTER_AREA)
        threshold_preview = threshold_img
        threshold_preview = cv2.cvtColor(threshold_preview, cv2.COLOR_GRAY2RGB)
        self.signals.update_analysis.emit(threshold_preview, percentage)
        return percentage > percent[0] and percentage < percent[1]

    def threshold(self, img, val):
        bw = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        ret, thresh = cv2.threshold(bw, val, 255, cv2.THRESH_BINARY)
        return thresh

class VideoStatus(Enum):
    BLACK = 1
    PRE_CAPTURE = 2
    IDLE = 3


class VideoAnalyzer(QObject):

    update_progress = Signal(float, VideoStatus)
    new_image = Signal()

    def __init__(self):
        super().__init__()
        self._count_black = 0
        self._count_image = 0
        self._status = VideoStatus.IDLE
        self._min_black_seq = 2
        self._min_image_seq = 5 

    def frame(self, is_black):
        if self._status is VideoStatus.IDLE:
            if is_black:
                # first black
                self._status = VideoStatus.BLACK
                self._count_black = 1
        elif self._status is VideoStatus.BLACK:
            if is_black:
                # still black
                self._count_black += 1
            else:
                if self._count_black > self._min_black_seq:
                    # end of black phase
                    self._status = VideoStatus.PRE_CAPTURE
                    self._count_image = 1
                else:
                    # just a black flicker
                    self._status = VideoStatus.IDLE
                    self._count_black = 0
        elif self._status is VideoStatus.PRE_CAPTURE:
            if is_black:
                # abort to black
                self._status = VideoStatus.BLACK
                self._count_black = 1
            else:
                if self._count_image > self._min_image_seq:
                    self._status = VideoStatus.IDLE
                    self._count_image = 0
                    self._count_black = 0
                    self.new_image.emit()
                else:
                    self._count_image += 1
        self.update_progress.emit(self._count_image / self._min_image_seq, self._status)
