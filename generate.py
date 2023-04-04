from gtts import gTTS
from gtts.tokenizer import pre_processors
import gtts.tokenizer.symbols
from html2image import Html2Image
hti = Html2Image(browser_executable='chromium/GoogleChromePortable64/App/Chrome-bin/chrome.exe')
     
import random
import moviepy.editor as mp
import moviepy.video.fx.all as mpvfx

# from urllib.request import urlopen
import json

def createVideoClipFromChunk(mode, clip, audioChunk, i, j):
    availableLength = clip.duration - audioChunk.duration
    startTime = random.uniform(0, availableLength)
    clipFragment = clip.subclip(startTime, startTime + audioChunk.duration)
    clipFragment = clipFragment.set_audio(audioChunk)
    clipFragment = clipFragment.volumex(1)
    if mode == 'dev':
        clipFragment.write_videofile(f'output/video{i}_{j+1}.mp4', fps=3, codec='h264_nvenc', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False)
    else:
        clipFragment.write_videofile(f'output/video{i}_{j+1}.mp4', fps=30, codec='h264_nvenc', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False)
            

if __name__ == '__main__':
    # # # # # # # # # # # # # # # # 
    # # # # # # # # # # # # # # # # 
    # # # MODE is dev or prod # # #
    # # # # # # # # # # # # # # # # 
    mode = 'prod'  # # # # # # # # #
    # # # # # # # # # # # # # # # # 
    # # # MODE is dev or prod # # #
    # # # # # # # # # # # # # # # # 
    # # # # # # # # # # # # # # # # 
    
    postsJson = json.load(open('posts_dev.json'))

    i:int = 0
    max_duration = 55
    
    abbreviations = {
        "aita": "Am I the A-hole?",
        "AmItheAsshole": "AmItheA--hole",
    }
        
    gtts.tokenizer.symbols.SUB_PAIRS += [(k, v) for k, v in abbreviations.items()]

    for post in postsJson['data']['children']:
        generate = True
        # check if post is already generated
        with open('generated.csv', 'r') as f:
            for line in f:
                if post['data']['id'] in line:
                    generate = False
    
        if not generate:
            i += 1
            continue
        
        postTitle = post['data']['title']
        postContent = post['data']['selftext']
        postSubreddit = post['data']['subreddit']
        if postSubreddit in abbreviations:
            postSubreddit = abbreviations[postSubreddit]
            
        postText = postTitle + '. ' + postContent
        
        if mode == 'dev':
            tts = gTTS('Quick text for testing', lang='en', tld='us', slow=False)
        else:
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
        
        remainingAudio = audioFileLength % max_duration
        if remainingAudio > 0:
            lastChunk = audio.subclip(chunkCount*max_duration, chunkCount*max_duration + remainingAudio)
            
        for j in range(int(chunkCount)):
            audioChunks.append(audio.subclip(j*max_duration, (j+1)*max_duration))
            
        for j, audioChunk in enumerate(audioChunks):
            if mode == 'dev':
                print('Skipping to last chunk for debug')
            else:
                hti.screenshot(
                    # Tu kurwa wsadzasz path do htmla i chuj mnie to obchodzi bo juz zmeczon mocno
                    url=f'C:/Users/HNY/Desktop/YTShortsBot/html/titlebar.html?title={postTitle}&part={j+1}&subreddit={postSubreddit}',
                    size=(1080, 1920),
                    save_as=f'titlebar{i}.png',
                )
                print(f'screened titlebar{i}.png, part {j}')
            
                titleBar = mp.ImageClip(f'titlebar{i}.png').set_duration(clip.duration)
                video = mp.CompositeVideoClip([clip, titleBar]) 
                
                createVideoClipFromChunk(mode, video, audioChunk, i, j)
            
        if lastChunk:
            hti.screenshot(
                # url params as title;part;subreddit
                url=f'C:/Users/HNY/Desktop/YTShortsBot/html/titlebar.html?title={postTitle}&part={j+1}&subreddit={postSubreddit}',
                size=(1080, 1920),
                save_as=f'titlebar{i}.png, part {j+1}',
            )
            print(f'screened titlebar{i}.png')
            
            titleBar = mp.ImageClip(f'titlebar{i}.png').set_duration(clip.duration)
            video = mp.CompositeVideoClip([clip, titleBar]) 
            createVideoClipFromChunk(mode, video, lastChunk, i, j+1)
            
        if mode == 'prod':
            # add post title;id;videonames to csv generated.csv
            # probably need a better way to add videonames
            with open('generated.csv', 'a') as f:
                f.write(f'{post["data"]["id"]};{",".join([f"video{i}_{j+1}.mp4" for j in range(len(audioChunks))])};' + (f'video{i}_{j+2}.mp4' if lastChunk else '') + '\n')
            
        i += 1

# HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
# json brany z url https://www.reddit.com/r/AmITheAssHole/top/.json?t=all&limit=2