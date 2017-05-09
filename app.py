import pyaudio
import wave
import pyttsx
import json
import urllib2
import time

import led

from os import path
import speech_recognition as sr

import requests

def post(url, data):
	return requests.post(url, data)

led.pin_setup()
led.pin_toggle(led.EYES_PIN)

tts_engine = pyttsx.init()


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()
r = sr.Recognizer()
r.energy_threshold = 0

URL = "https://secret-sierra-38946.herokuapp.com/questions/"

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
				rate=RATE, input=True,
				frames_per_buffer=CHUNK)
print("recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	data = stream.read(CHUNK, exception_on_overflow=False)
	frames.append(data)

print("finished recording")

led.pin_toggle(led.HEAD_PIN)

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

print('Saved audio...')

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "file.wav")

with sr.AudioFile(AUDIO_FILE) as source:
	audio = r.record(source)

	try:
		text = r.recognize_google(audio)		
		print(text)
		
		if text.encode('ascii', 'ignore') == 'hello':				
			tts_engine.say('Greetings!')
			tts_engine.runAndWait()
		else:
			req = urllib2.Request(URL)
			req.add_header('Content-Type', 'application/json')
		
			response = urllib2.urlopen(req, json.dumps({"question": text + '?'}))
			answer = json.loads(response.read())
			answerText = answer['answer']
			print('Answer: ', answerText)
		
			tts_engine.say(answerText)
			tts_engine.runAndWait()
	except sr.UnknownValueError:
		tts_engine.say("I could not understand you.")
		tts_engine.runAndWait()
	except sr.RequestError as e:
		print("Error; {0}".format(e))
		
led.pin_off(led.HEAD_PIN)
time.sleep(1)
led.pin_off(led.EYES_PIN)
