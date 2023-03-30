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
    tts = textToSpeech("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0", 200, 1)
    # tts.list_available_voices() #i sie wpierdala tu o wyżej key z rejestru.
    
    # Ładujemy jsona z reddita, można to z urla pobierać ale na czas devowania nie bede loadował cały czas ni?
    postsJson = json.load(open('posts_dev.json'))
    # postsJson = json.load(open('posts.json'))
    
    i = 0
    max_duration = 55
    for post in postsJson['data']['children']:
        postTitle = post['data']['title']
        postContent = post['data']['selftext']
        postText = postTitle + '. ' + postContent
        tts.say(postText, save=True, file_name=f'output{i}.mp3')
        
        clip = mp.VideoFileClip("hypnoclips/mc1.mp4")
        clip = mpvfx.resize(clip, height=1920)
        
        clip_w, clip_h = clip.size
        clip = mpvfx.crop(clip, x_center=clip_w/2, y_center=clip_h/2, width=1080, height=1920)
        
        audio = mp.AudioFileClip(f'output{i}.mp3')
        audioFileLength = audio.duration
        
        # divide audio into max_duration chunks
        audioChunks = []
        lastChunk = None
        
        chunkCount = audioFileLength // max_duration
        
        # remaining audio
        remainingAudio = audioFileLength % max_duration
        if remainingAudio > 0:
            lastChunk = audio.subclip(chunkCount*max_duration, chunkCount*max_duration + remainingAudio)
        
        for j in range(int(chunkCount)):
            audioChunks.append(audio.subclip(j*max_duration, (j+1)*max_duration))
            
        # for each audio chunk 
        for j, audioChunk in enumerate(audioChunks):
            availableLength = clip.duration - audioChunk.duration
            startTime = random.uniform(0, availableLength)
            clipFragment = clip.subclip(startTime, startTime + audioChunk.duration)
            clipFragment = clipFragment.set_audio(audioChunk)
            clipFragment = clipFragment.volumex(1)
            clipFragment.write_videofile(f'output/video{i}_{j}.mp4', fps=5, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False, verbose=False)
            
        if lastChunk:
            availableLength = clip.duration - lastChunk.duration
            startTime = random.uniform(0, availableLength)
            clipFragment = clip.subclip(startTime, startTime + lastChunk.duration)
            clipFragment = clipFragment.set_audio(lastChunk)
            clipFragment = clipFragment.volumex(1)
            clipFragment.write_videofile(f'output/video{i}_{j+1}.mp4', fps=5, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False, verbose=False)
            
        # clip = clip.subclip(0, audioFileLength) 
        
        # add audio to clip at startTime
        # clip = clip.set_audio(audio)
        # clip = clip.volumex(1) 
        
        # txt_clip = mp.TextClip(postTitle, font='impact', fontsize = 36, color = 'white', stroke_color='black', stroke_width=2, align='center', method='caption', bg_color='gray12', size=(640, 0))
        
        # save txt_clip
        # txt_clip.save_frame(f'output/{i}.png', t=0)
        
        # txt_clip = txt_clip.set_pos('center').set_duration(8)
        
        # video = mp.CompositeVideoClip([clip, txt_clip]) 
        # save the video
        # video.write_videofile(f'output/video{i}.mp4', fps=24, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False, verbose=False)
        
        i += 1
    
# HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
    
# json brany z url https://www.reddit.com/r/AmITheAssHole/top/.json?t=all&limit=2
    
    