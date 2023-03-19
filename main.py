import pyttsx3
import random
import moviepy.editor as mp
import moviepy.video.fx.all as mpvfx

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
        # self.engine.say(text)
        
        if save:
            self.engine.save_to_file(text, file_name)
            
        self.engine.runAndWait()
            

if __name__ == '__main__':
    tts = textToSpeech("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0", 185, 1)
    # tts.list_available_voices() #i sie wpierdala tu o wyżej key z rejestru.
    
    # Ładujemy jsona z reddita, można to z urla pobierać ale na czas devowania nie bede loadował cały czas ni?
    postsJson = json.load(open('posts.json'))
    
    i = 0
    for post in postsJson['data']['children']:
        postTitle = post['data']['title']
        postContent = post['data']['selftext']
        postText = postTitle + '. ' + postContent
        tts.say(postText, save=True, file_name=f'output{i}.mp3')
        
        clip = mp.VideoFileClip("hypnoclips/1.mp4")
        clip = mpvfx.resize(clip, height=1920)
        
        clip_w, clip_h = clip.size
        clip = mpvfx.crop(clip, x_center=clip_w/2, y_center=clip_h/2, width=720, height=1280)
        
        audio = mp.AudioFileClip(f'output{i}.mp3')
        audioFileLength = audio.duration
        
        # audio.set_duration(5) #for debugging
        
        clipLength = clip.duration
        availableLength = clipLength - audioFileLength
        startTime = random.randint(0, int(availableLength))
        
        clip = clip.subclip(0, audioFileLength) 
        
        # add audio to clip at startTime
        clip = clip.set_audio(audio)
        clip = clip.volumex(1) 
        
        txt_clip = mp.TextClip(postTitle, font='impact', fontsize = 36, color = 'white', stroke_color='black', stroke_width=2, align='center', method='caption', bg_color='gray12', size=(640, 0))
        # save txt_clip
        # txt_clip.save_frame(f'output/{i}.png', t=0)
        
        txt_clip = txt_clip.set_pos('center').set_duration(8)
        # txt_clip = txt_clip.set_pos('center').set_duration(5) #for debugging
        
        video = mp.CompositeVideoClip([clip, txt_clip]) 
        # save the video
        video.write_videofile(f'output/video{i}.mp4', fps=24, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False, verbose=False)
        
        i += 1
    
# HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
    
# json brany z url https://www.reddit.com/r/AmITheAssHole/top/.json?t=all&limit=2
    
    