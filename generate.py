from gtts import gTTS
from gtts.tokenizer import pre_processors
import gtts.tokenizer.symbols
     
import random
import moviepy.editor as mp
import moviepy.video.fx.all as mpvfx

from urllib.request import urlopen
import json

def createVideoClipFromChunk(clip, audioChunk, i, j):
    availableLength = clip.duration - audioChunk.duration
    startTime = random.uniform(0, availableLength)
    clipFragment = clip.subclip(startTime, startTime + audioChunk.duration)
    clipFragment = clipFragment.set_audio(audioChunk)
    clipFragment = clipFragment.volumex(1)
    clipFragment.write_videofile(f'output/video{i}_{j+1}.mp4', fps=2, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False)
            

if __name__ == '__main__':
    postsJson = json.load(open('posts_dev.json'))

    i:int = 0
    max_duration = 55
    
    abbreviations = {
        "aita": "Am I the A-hole?",
    }
        
    # append abbreviations to gtts.tokenizer.symbols.SUB_PAIRS
    gtts.tokenizer.symbols.SUB_PAIRS += [(k, v) for k, v in abbreviations.items()]
                    
    for post in postsJson['data']['children']:
        
        generate = True
        # check if post is already generated
        with open('generated.csv', 'r') as f:
            for line in f:
                if post['data']['id'] in line:
                    generate = False
    
        if not generate:
            continue
        
        postTitle = post['data']['title']
        postContent = post['data']['selftext']
        postText = postTitle + '. ' + postContent
        
        tts = gTTS(postText, lang='en', tld='us', slow=False)
        tts.save(f'output{i}.mp3')
        
        print(f'finished generating audio #{i}')
        
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
        # for j, audioChunk in enumerate(audioChunks):
        #     createVideoClipFromChunk(clip, audioChunk, i, j)
            
        if lastChunk:
            createVideoClipFromChunk(clip, lastChunk, i, j+1)
            
        # add post title;id;videonames to csv generated.csv
        # with open('generated.csv', 'a') as f:
        #     f.write(f'{post["data"]["id"]};{",".join([f"video{i}_{j+1}.mp4" for j in range(len(audioChunks))])};' + (f'video{i}_{j+2}.mp4' if lastChunk else '') + '\n')
            
        i += 1
        
        
    #     # --------------
    #     # --------------
    #     # --------------
    #     # --------------
    #     # TODO: dodać tekst do filmu, jutro
    #     # --------------
    #     # --------------
    #     # --------------
    #     # --------------
        
    #     # txt_clip = mp.TextClip(postTitle, font='impact', fontsize = 36, color = 'white', stroke_color='black', stroke_width=2, align='center', method='caption', bg_color='gray12', size=(1000, 0))
        
    #     # save txt_clip
    #     # txt_clip.save_frame(f'output/{i}.png', t=0)
        
    #     # txt_clip = txt_clip.set_pos('center').set_duration(8)
        
    #     # video = mp.CompositeVideoClip([clip, txt_clip]) 
        
    #     # save the video
    #     # video.write_videofile(f'output/video{i}.mp4', fps=24, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False, verbose=False)
        
    #     i += 1

# HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
# json brany z url https://www.reddit.com/r/AmITheAssHole/top/.json?t=all&limit=2