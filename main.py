import pyttsx3

from urllib.request import urlopen
import json

class textToSpeech:
    engine: pyttsx3.Engine
    
    def __init__(self, voice, rate: int, volume: float):
        self.engine = pyttsx3.init()
        if voice:
            self.engine.setProperty('voice', voice)
            
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
    def list_available_voices(self):
        voices: list = self.engine.getProperty('voices')
        
        for i, voice in enumerate(voices):
            print(f'{i}: {voice.name} {voice.age} - {voice.languages} - {voice.gender}, {voice.id}')
            
    def say(self, text: str, save: bool = False, file_name='output.mp3'):
        self.engine.say(text)
        self.engine.runAndWait()
        
        if save:
            self.engine.save_to_file(text, file_name)
            
        self.engine.runAndWait()
            

if __name__ == '__main__':
    tts = textToSpeech("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0", 165, 0.8)
    tts.list_available_voices()
    
    # postsJson = json.load(open('posts.json'))
    # for post in postsJson['data']['children']:
    #     postTitle = post['data']['title']
    #     postContent = post['data']['selftext']
    #     tts.say(postTitle)
    
    
# HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
    
# json brany z url https://www.reddit.com/r/AmITheAssHole/top/.json?t=all&limit=2
    
    