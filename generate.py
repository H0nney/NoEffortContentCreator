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

def createVideoClipFromChunk(mode, clip, audioChunk, videoIndex, chunkIndex):
    availableLength = clip.duration - audioChunk.duration
    startTime = random.uniform(0, availableLength)
    clipFragment = clip.subclip(startTime, startTime + audioChunk.duration)
    clipFragment = clipFragment.set_audio(audioChunk)
    clipFragment = clipFragment.volumex(1)
    if mode == 'dev':
        clipFragment.write_videofile(f'output/video{videoIndex}_{chunkIndex}.mp4', fps=2, codec='h264_nvenc', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False)
    else:
        clipFragment.write_videofile(f'output/video{videoIndex}_{chunkIndex}.mp4', fps=2, codec='h264_nvenc', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, write_logfile=False)
            

if __name__ == '__main__':
    # # # MODE is dev or prod # # #
    # # # # # # # # # # # # # # # # 
    mode = 'dev'  # # # # # # # # #
    # # # # # # # # # # # # # # # # 
    # # # MODE is dev or prod # # #
    
    postsJson = json.load(open('posts_dev.json'))

    i:int = 0
    
    abbreviations = {
        "aita": "Am I the bad one?",
        "AmItheAsshole": "AmItheA--hole",
    }
        
    gtts.tokenizer.symbols.SUB_PAIRS += [(k, v) for k, v in abbreviations.items()]
    
    min_duration = 0
    if mode == 'dev':
        min_duration = 2
    else:
        min_duration = 25
        
    for post in postsJson['data']['children']:
        print('---------------------------------')
        print(f'### Processing audio no.{i}')
        max_duration = 59 # Begin with 59, to be safe of shorts limit, substract title later
        
        generate = True
        
        # Check if post is already generated
        with open('generated.csv', 'r') as f:
            for line in f:
                if post['data']['id'] in line:
                    generate = False
    
        if not generate:
            print(f'### Post {i} already generated, skipping')
            i += 1
            continue
        
        postTitle = post['data']['title']
        postContent = post['data']['selftext']
        postSubreddit = post['data']['subreddit']
        
        # Plan for now: gtts has a limit of 100? characters per sentence, 
        # so we need to split the text into sentences 
        # and concatenate them into a single string co ty pierdolisz kopilot kurwa,
        # Tak jak wyżej ale musimy wygenerować serie audio z sensownymi breakpointami
        # a potem je połączyć w całość, reszta kodu bez zmian
        # to co, szukamy innego tts xDDDD
        # nie wyczymie
        
        if postSubreddit in abbreviations:
            postSubreddit = abbreviations[postSubreddit]
            
        # postText = postTitle + '. ' + postContent
        
        # Divide title and content into separate files
        if mode == 'dev':
            # tts = gTTS('Subskrybuj kanał HnyDEV żeby oglądać więcej pięknego kodu i słabych kobiet', lang='en', tld='us', slow=False)
            ttsTitle = gTTS('Example title to test generation.', lang='en', tld='us', slow=False)
            ttsContent = gTTS('Example content to test generation.', lang='en', tld='us', slow=False)
            ttsTitle.save(f'output{i}_title.mp3')
            ttsContent.save(f'output{i}_content.mp3')
        else:
            ttsTitle = gTTS(postTitle, lang='en', tld='us', slow=False)
            ttsContent = gTTS(postContent, lang='en', tld='us', slow=False)
            ttsTitle.save(f'output{i}_title.mp3')
            ttsContent.save(f'output{i}_content.mp3')
        
        print(f'### Finished generating audio no.{i}')
        
        clip = mp.VideoFileClip("hypnoclips/mc1.mp4")
        clip = mpvfx.resize(clip, height=1920)
        
        clip_w, clip_h = clip.size
        clip = mpvfx.crop(clip, x_center=clip_w/2, y_center=clip_h/2, width=1080, height=1920)
        
        audioTitle = mp.AudioFileClip(f'output{i}_title.mp3')
        audioContent = mp.AudioFileClip(f'output{i}_content.mp3')
        
        # Check if audio content length is longer than 180 seconds
        if audioContent.duration > 280:
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
                    ttsPart = gTTS(f'Part {partNo}', lang='en', tld='us', slow=False)
                    ttsPart.save(f'output{i}_part.mp3')
                    audioPart = mp.AudioFileClip(f'output{i}_part.mp3')
                    
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
                
                # Generate speech for part number
                ttsPart = gTTS(f'Part {lastChunkIndex}', lang='en', tld='us', slow=False)
                ttsPart.save(f'output{i}_part.mp3')
                audioPart = mp.AudioFileClip(f'output{i}_part.mp3')
                
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
            # audioTitle
            # audioContent
                
            
            
        if mode == 'prod':
            # add post title;id;videonames to csv generated.csv
            # probably need a better way to add videonames
            # A JSON what the hell am i thinking 2head 
            with open('generated.csv', 'a') as f:
                f.write(f'{post["data"]["id"]};{",".join([f"video{i}_{j+1}.mp4" for j in range(len(audioChunks))])};' + (f'video{i}_{lastChunkIndex}.mp4' if lastChunk else '') + '\n')
            
        i += 1

# HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
# json brany z url https://www.reddit.com/r/AmITheAssHole/top/.json?t=all&limit=2