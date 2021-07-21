from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSlider, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal
from superqt import QLabeledRangeSlider

class SettingsControls(QWidget):

    switch_tabs = Signal(bool)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        run_button = RunButton()
        tabs = QTabWidget()
        tabs.currentChanged.connect(self.tab_changed)
        image_settings = ImageSettings()
        threshold_settings = ThresholdSettings()
        tabs.insertTab(0, image_settings, 'Image')
        tabs.insertTab(1, threshold_settings, 'Detection')
        main_layout.addWidget(run_button)
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

        # expose signals
        self.threshold_changed = threshold_settings.threshold_changed
        self.interval_changed = threshold_settings.interval_changed

        self.update_percentage = threshold_settings.update_percentage

    def tab_changed(self, index):
        if index == 0:
            self.switch_tabs.emit(True)
        elif index == 1:
            self.switch_tabs.emit(False)

class ImageSettings(QWidget):

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        brightness = QSlider(Qt.Horizontal)
        main_layout.addWidget(brightness)
        self.setLayout(main_layout)

class ThresholdSettings(QWidget):

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        threshold_label = QLabel("Black threshold")
        threshold = QSlider(Qt.Horizontal)
        threshold.setMinimum(0)
        threshold.setMaximum(255)

        # TODO: fix scrolling when hovering over labels
        interval_box = QHBoxLayout()
        interval_label = QLabel("Black percentage")
        self.percentage_label = QLabel()
        self.percentage_label.setAlignment(Qt.AlignRight)
        interval_box.addWidget(interval_label)
        interval_box.addStretch(1)
        interval_box.addWidget(self.percentage_label)

        interval = QLabeledRangeSlider(Qt.Horizontal)
        interval.setMinimum(0)
        interval.setMaximum(100)

        # expose signal
        self.threshold_changed = threshold.valueChanged
        self.interval_changed = interval.valueChanged

        main_layout.addWidget(threshold_label)
        main_layout.addWidget(threshold)
        main_layout.addSpacing(40)
        main_layout.addLayout(interval_box)
        main_layout.addWidget(interval)
        self.setLayout(main_layout)
        threshold.triggerAction(QSlider.SliderMove)

    def update_percentage(self, value):
        self.percentage_label.setText("{0:.0f} %".format(value*100))

class RunButton(QPushButton):

    def __init__(self):
        super().__init__()
        self.setCheckable(True)
