from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSlider, QLabel, QSizePolicy, QProgressBar, QFileDialog, QLineEdit
from PySide6.QtCore import Qt, Signal
from superqt import QLabeledRangeSlider

class SettingsControls(QWidget):

	switch_tabs = Signal(bool)

	def __init__(self):
		super().__init__()
		self.no = 0
		main_layout = QVBoxLayout()
		self.run_button = RunButton()
		self.dir_button = DirectoryButton()
		self.prefix_text = QLineEdit()
		self.prefix_text.setPlaceholderText("sub directory")
		self.prefix_text.textChanged.connect(self.reset_no)
		cooldown_bar = CooldownProgress()
		tabs = QTabWidget()
		tabs.currentChanged.connect(self.tab_changed)
		image_settings = ImageSettings()
		threshold_settings = ThresholdSettings()
		tabs.insertTab(0, image_settings, 'Image')
		tabs.insertTab(1, threshold_settings, 'Detection')
		control_bar = QHBoxLayout()
		control_bar.addWidget(self.run_button)
		control_bar.addWidget(self.dir_button)
		control_bar.addWidget(self.prefix_text)
		control_bar.addWidget(cooldown_bar)
		main_layout.addLayout(control_bar)

		main_layout.addWidget(tabs)
		self.setLayout(main_layout)

		# expose signals
		self.threshold_changed = threshold_settings.threshold_changed
		self.interval_changed = threshold_settings.interval_changed

		self.update_percentage = threshold_settings.update_percentage
		self.update_progress = cooldown_bar.update_progress
		
	def reset_no(self):
		self.no = 0

	def tab_changed(self, index):
		if index == 0:
			self.switch_tabs.emit(True)
		elif index == 1:
			self.switch_tabs.emit(False)
			
	def get_output_dir(self):
		return self.dir_button.dir_path
	
	def get_prefix(self):
		return self.prefix_text.text()
	
	def is_paused(self):
		return not self.run_button.checked
	
class ImageSettings(QWidget):

	def __init__(self):
		super().__init__()
		main_layout = QVBoxLayout()
		brightness = QSlider(Qt.Horizontal)
		#main_layout.addWidget(brightness)
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

		# initial values
		threshold.setValue(50)
		interval.setValue((10, 80))

	def update_percentage(self, value):
		self.percentage_label.setText("{0:.0f} %".format(value*100))

class RunButton(QPushButton):
	
	def toggleRun(self, checked):
		self.setText("recording" if checked else "paused")
		self.checked = checked

	def __init__(self):
		super().__init__()
		self.setCheckable(True)
		self.checked = False
		self.toggleRun(False)
		self.clicked.connect(self.toggleRun)
		
	def toggle_shortcut(self):
		self.animateClick()
		
class DirectoryButton(QPushButton):

	def __init__(self):
		super().__init__()
		self.setText("output directory")
		self.dir_path = ""
		self.clicked.connect(self.choose_dir)
		
	def choose_dir(self):
		self.dir_path = QFileDialog.getExistingDirectory()
		self.setText("..." + self.dir_path[-20:])
		
class CooldownProgress(QProgressBar):
	
	def update_progress(self, progress, max_progress):
		self.setMaximum(max_progress)
		self.setValue(progress)

	def __init__(self):
		super().__init__()
