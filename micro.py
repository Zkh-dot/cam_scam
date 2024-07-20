# Author: Alexey Slokva <Alesha72003@ya.ru>
import os
import string
import random
from multiprocessing import Process
import subprocess
from time import sleep
from abstract_classes import devices

class MicroScam(devices):
	def __init__(self, micid, noiseFile):
		self.micid = micid
		self.virtualname = 'Virtual' + ''.join(random.choices(string.ascii_uppercase, k=5))
		print(f"RUN pactl load-module module-null-sink sink_name={self.virtualname}")
		self.mainpid = str(subprocess.check_output(f"pactl load-module module-null-sink sink_name={self.virtualname}", shell=True), "UTF-8")
		self.pid = None
		self.proc = None
		if not os.path.isfile(noiseFile):
			raise RuntimeError("Noise file not found")
		self.noiseFile = noiseFile
		self.unfreeze()

	def unfreeze(self):
		if not self.pid:
			print(f"RUN pactl load-module module-loopback sink={self.virtualname} source={self.micid} latency_msec=1")
			self.pid = str(subprocess.check_output(f"pactl load-module module-loopback sink={self.virtualname} source={self.micid} latency_msec=1", shell=True), "UTF-8")
		if self.proc:
			self.proc.terminate()
			self.proc = None


	def freeze(self):
		if self.pid:
			os.system(f"pactl unload-module {self.pid}")
			self.pid = None
		if not self.proc:
			env = os.environ.copy()
			env.update({"PULSE_SINK": self.virtualname})
			self.proc = subprocess.Popen(["cvlc", "-R", self.noiseFile], env=env, start_new_session=True)

	def __del__(self):
		print(f"RUN pactl unload-module {self.mainpid}")
		os.system(f"pactl unload-module {self.mainpid}")
		if self.pid:
			print(F"RUN pactl unload-module {self.pid}")
			os.system(f"pactl unload-module {self.pid}")
		if self.proc:
			self.proc.terminate()

if __name__ == "__main__":
	test = MicroScam("alsa_input.pci-0000_00_1f.3.analog-stereo", "/home/alesha/test.wav")
	print("loopback mode")
	sleep(60)
	print("freeze mode")
	test.freeze()
	print("test")
	sleep(15)
	test.unfreeze()
	print("loopback mode again")
	sleep(15)
