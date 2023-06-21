from html2image import Html2Image
hti = Html2Image(browser_executable='chromium/GoogleChromePortable64/App/Chrome-bin/chrome.exe')
     
import os
import random
from datetime import datetime, timedelta
import moviepy.editor as mp
import moviepy.video.fx.all as mpvfx

from time import sleep
from tiktok_tts.main import main as tiktok_tts
import json

def createVideoClipFromChunk(mode, clip, audioChunk, videoIndex, chunkIndex):
    availableLength = clip.duration - audioChunk.duration
    startTime = random.uniform(0, availableLength)
    clipFragment = clip.subclip(startTime, startTime + audioChunk.duration)
    clipFragment = clipFragment.set_audio(audioChunk)
    clipFragment = clipFragment.volumex(1)
    clipFragment.write_videofile(f'output/video{videoIndex}_{chunkIndex}.mp4', fps=30, codec='h264_nvenc', audio_codec='aac', temp_audiofile='temp/temp-audio.m4a', remove_temp=True, write_logfile=False, bitrate='4500k', logger=None)


import selenium.webdriver as webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'
firefoxDriver = 'geckodriver.exe'

def upload_videos():
    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M")
    
    # open log.json and iterate through posts
    with open('log.json', 'r') as f:
        offset_m = 20
        data = json.load(f)
        for post in data['posts']:
            postId = post['id']
            postTitle = post['title']
            postIndex = post['index']
            postParts = post['parts']
            
            for i in range(postParts):
                schedule_time = datetime.now() + timedelta(minutes=offset_m)
                schedule_time = schedule_time.strftime("%d/%m/%Y, %H:%M")
                print(f'### Uploading video {postIndex}_{i+1}, scheduled at {schedule_time}')
                offset_m += 20
    

if __name__ == '__main__':
    upload_videos()
    exit()
    
    # # # MODE is dev or prod # # #
    # # # # # # # # # # # # # # # # 
    mode = 'prod'  # # # # # # # # #
    # # # # # # # # # # # # # # # # 
    # # # MODE is dev or prod # # #
    
    postsJson = json.load(open('posts.json'))

    i:int = 0
    generatedCount:int = 0
    
    abbreviations = {
        "AITA": "Am I the bad one?",
        "AmItheAsshole": "AmItheA--hole",
    }
        
    min_duration = 0
    if mode == 'dev':
        min_duration = 2
    else:
        min_duration = 25
        
    for post in postsJson['data']['children']:
        print('---------------------------------')
        print(f'### Processing audio no.{i}')
        max_duration = 58 # Begin with 58, to be safe of shorts limit, substract title later
        
        generate = True
        
        postId = post['data']['id']
        # Check if post is already generated in log.json posts
        if os.path.exists('log.json'):
            with open('log.json', 'r') as f:
                log = json.load(f)
                for generatedPost in log['posts']:
                    if generatedPost['id'] == postId:
                        generate = False
                        break
    
        if not generate:
            print(f'### Post {i} already generated, skipping')
            i += 1
            continue
        
        if not 'data' in post:
            print('### Post data not found, skipping')
            i += 1
            continue
        
        postTitle = post['data']['title']
        postContent = post['data']['selftext']
        # if post content longer than 3000 characters, skip
        if len(postContent) > 3000:
            print('### Post text too long, skipping')
            i += 1
            continue
        
        postSubreddit = post['data']['subreddit']
        
        # check title and content for abbreviations
        for k, v in abbreviations.items():
            postTitle = postTitle.replace(k, v)
            postContent = postContent.replace(k, v)
                
        textPath = f'temp/text_title{i}.txt'
        with open(textPath, 'w') as f:
            f.write(postTitle)
            
        textContentPath = f'temp/text_content{i}.txt'
        with open(textContentPath, 'w') as f:
            f.write(postContent + f'. Thank you for listening. Leave a like!')
            
        if postSubreddit in abbreviations:
            postSubreddit = abbreviations[postSubreddit]
            
        # Grab sessionid from sessionid.txt
        # SessionID is required to generate audio
        with open('sessionid.txt', 'r') as f:
            sessionid = f.read()

        # Divide title and content into separate files
        if mode == 'dev':
            tiktok_tts('en_us_001', 'pregenerated/exampleTitle.txt', sessionid, f'temp/output{i}_title.mp3')
            tiktok_tts('en_us_001', 'pregenerated/exampleContent.txt', sessionid, f'temp/output{i}_content.mp3')
        else:
            tiktok_tts('en_us_001', textPath, sessionid, f'temp/output{i}_title.mp3')
            tiktok_tts('en_us_001', textContentPath, sessionid, f'temp/output{i}_content.mp3')
        
        print(f'### Finished generating audio no.{i}')
        
        clip = mp.VideoFileClip("backgrounds/parkour_1440.mp4")
        clip = mpvfx.resize(clip, height=1920)
        
        clip_w, clip_h = clip.size
        clip = mpvfx.crop(clip, x_center=clip_w/2, y_center=clip_h/2, width=1080, height=1920)
        
        audioTitle = mp.AudioFileClip(f'temp/output{i}_title.mp3')
        audioContent = mp.AudioFileClip(f'temp/output{i}_content.mp3')
        # Audiocontent is generating with annoying glitch at the end.
        audioContent = audioContent.subclip(0, audioContent.duration - 0.12)
        
        # Check if audio content length is longer than X seconds
        if audioContent.duration > 170:
            with open('log.json', 'r') as f:
                data = json.load(f)
                # add post to json
                data['posts'].append({ 'id': postId, 'title': postTitle, 'subreddit': postSubreddit, 'status': 'lengthcap', 'index' : i })

            with open('log.json', 'w') as f:
                json.dump(data, f, indent=4) 
                  
            print(f'### Audio content too long, skipping post {i}')
            i += 1
            continue
        
        audioTitleLength = audioTitle.duration  
        audioContentLength = audioContent.duration
        
        # Divide audio into max_duration chunks
        audioChunks = []
        lastChunk = None
        
        # Substract title length from max_duration
        max_duration -= audioTitleLength
        print(f'### Max duration: {max_duration} seconds')
        
        # Check if total audio length is longer than max_duration
        if audioContentLength > max_duration:
            print(f'### Audio content too long, splitting into chunks')
        
            chunkCount:int = audioContentLength // max_duration
            remainingAudio = audioContentLength - chunkCount*max_duration
            print(f'### Chunk count: {int(chunkCount)}, remaining audio: {remainingAudio} seconds')
            
            if remainingAudio > 0 and chunkCount > 0:
                lastChunk = audioContent.subclip(chunkCount*max_duration, chunkCount*max_duration + remainingAudio)
                
            for j in range(int(chunkCount)):
                audioChunks.append(audioContent.subclip(j*max_duration, (j+1)*max_duration))
                
            for j, audioChunk in enumerate(audioChunks):
                if mode == 'dev':
                    print('Skipping to last chunk for debug')
                else:
                    partNo = j+1
                    hti.screenshot(
                        # url params as title;part;subreddit
                        url=f'C:/Users/HNY/Desktop/YTShortsBot/html/titlebar.html?title={postTitle}&part={partNo}&subreddit={postSubreddit}',
                        size=(1080, 1920),
                        save_as=f'titlebar{i}_{partNo}.png',
                    )
                    
                    print(f'### Generating chunk: post {i}, part {partNo}')
                    
                    # Generate speech for part number
                    audioPart = mp.AudioFileClip(f'pregenerated/part{partNo}.mp3')
                    
                    # Add title, content and part number to one audio file
                    generatedChunk = mp.concatenate_audioclips([audioTitle, audioPart, audioChunk])
                    
                    # Generate titlebar and add it to video
                    titleBar = mp.ImageClip(f'titlebar{i}_{partNo}.png').set_duration(clip.duration)
                    video = mp.CompositeVideoClip([clip, titleBar]) 
                    
                    createVideoClipFromChunk(mode, video, generatedChunk, i, partNo)
                
            if lastChunk:
                lastChunkIndex = len(audioChunks) + 1
                hti.screenshot(
                    # url params as title;part;subreddit
                    url=f'C:/Users/HNY/Desktop/YTShortsBot/html/titlebar.html?title={postTitle}&part={lastChunkIndex}&subreddit={postSubreddit}',
                    size=(1080, 1920),
                    save_as=f'titlebar{i}_{lastChunkIndex}.png',
                )
                
                print(f'### Generating last chunk: post {i}, part {lastChunkIndex}')
                
                audioPart = mp.AudioFileClip(f'pregenerated/part{lastChunkIndex}.mp3')
                
                # Add title, content and part number to one audio file
                generatedChunk = mp.concatenate_audioclips([audioTitle, audioPart, lastChunk])
                
                # Generate titlebar and add it to video
                titleBar = mp.ImageClip(f'titlebar{i}_{lastChunkIndex}.png').set_duration(clip.duration)
                video = mp.CompositeVideoClip([clip, titleBar]) 
                
                createVideoClipFromChunk(mode, video, generatedChunk, i, lastChunkIndex)
            else:
                print('### No last chunk to generate')
        else:
            # Check if audio content is longer than min_duration
            if audioContentLength < min_duration:
                print(f'### Audio content too short, skipping post {i}')
                i += 1
                continue
            
            print(f'### Generating single chunk: post {i}, no parts')
            # generate video using audioTitle and Content
            
            hti.screenshot(
                # url params as title;part;subreddit
                url=f'C:/Users/HNY/Desktop/YTShortsBot/html/titlebar.html?title={postTitle}&subreddit={postSubreddit}',
                size=(1080, 1920),
                save_as=f'titlebar{i}.png',
            )
            
            # Add title, content and part number to one audio file
            generatedAudio = mp.concatenate_audioclips([audioTitle, audioContent])
            
            # Generate titlebar and add it to video
            titleBar = mp.ImageClip(f'titlebar{i}.png').set_duration(clip.duration)
            video = mp.CompositeVideoClip([clip, titleBar]) 
            
            createVideoClipFromChunk(mode, video, generatedAudio, i, 0)
            
        if mode == 'prod':
            print(f'### Adding post {i} to JSON LOG')
            
            # Add post to log.json
            with open('log.json', 'r') as f:
                data = json.load(f)
                data['posts'].append({ 'id': postId, 'title': postTitle, 'subreddit': postSubreddit, 'status': 'generated', 'index' : i })

            with open('log.json', 'w') as f:
                json.dump(data, f, indent=4)    
                
            generatedCount += 1
            print(f'### Current count: {generatedCount}')
                
            
        # Cleanup has to be manual. Some bug that i can't be bothered to fix is riddling it.
        if generatedCount >= 3:
            upload_videos()
            break
        
        i += 1

# Json History
# https://www.reddit.com/r/amitheasshole/top/.json?t=all&limit=200
# https://www.reddit.com/r/talesfromtechsupport/top/.json?t=all&limit=200