import time,aiohttp,asyncio,os,shutil
from segmenter import create_segmented_file
from fastapi import FastAPI
# from pytubefix import YouTube
from music_stream_size_api import get_stream
from math import ceil,floor
from concurrent.futures import ThreadPoolExecutor
app = FastAPI()
a=time.time()
Aud_list=[]
total_received=0
File_name="song.mp3"
OUTPUT_DIR = "segmented_file"
audio_path= f"{OUTPUT_DIR}/{File_name}"
def create_throttles(size):
    mb=1024*1024
    if size>=mb:
        if ceil(size / mb)>=16:
            return 16
        else:
            return ceil(size / mb)
    else:
        return 1

def range_list(audio_segment_list,file_size, parts):
    end=0
    start=0
    segment_size=floor(file_size / parts)
    for i in range(parts):
        end=end+(segment_size-1)
        if i!=parts-1:
            audio_segment_list.append((start,end))
        else:
            end = file_size
            audio_segment_list.append((start, end))
        start=end+1
async def download_chunk(session, start, stop, url):

    headers = {"Range": f"bytes={start}-{stop}"}
    async with session.get(url, headers=headers) as response:
        downloaded=await response.read()
        return downloaded

async def download_segments(data_parts, streaming_url, segment_list):
    chunks = []
    tasks = []
    print("Downloading...")
    async with aiohttp.ClientSession() as session:
        for i in range(data_parts):
            start=segment_list[i][0]
            stop=segment_list[i][1]
            tasks.append(asyncio.create_task(download_chunk(session,start,stop,streaming_url)))
        results=await asyncio.gather(*tasks)
        chunks.extend(results)
    with open(f"{audio_path}", "wb") as f:
        for chunk in chunks:
            f.write(chunk)

def runner(file_throttles, file_stream,file_segment_list):
    asyncio.run(download_segments(file_throttles, file_stream,file_segment_list))
@app.get('/download')
def download_audio(url:str):
    # yt=YouTube(url)
    # streams=yt.streams
    # for stream in streams.filter(only_audio=True):
    #     audio_resolution = stream.itag, f"{stream.filesize} Bytes"
    #     Aud_list.append(audio_resolution)
    # print(f"Resolutions: {Aud_list}")
    # audio_select=int(input("Choose Audio Quality:")) #--> for quality selection only
    #------X-----X---> for quality selection
    # audio_resolution=streams.filter(only_audio=True).filter().first().itag,streams.filter(only_audio=True).filter().first().filesize
    # audio_stream=streams.filter().get_by_itag(Aud_list[audio_select - 1][0]).url #--> for quality selection
    # total_size=Aud_list[audio_select-1][1] #--> for quality selection
    # audio_stream = streams.filter().get_by_itag(audio_resolution[0]).url
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    audio_segment_list=[]
    result=get_stream(url)
    audio_resolution=result["stream"],result["size"]
    audio_stream=audio_resolution[0]
    with ThreadPoolExecutor() as executor:
        #t2=executor.submit(create_throttles,Aud_list[audio_select-1][1]) #--> for quality selection
        t2 = executor.submit(create_throttles, audio_resolution[1])
    audio_throttles=t2.result()

    with ThreadPoolExecutor() as executor:
        #executor.submit(range_list,Aud_list[audio_select-1][1], audio_throttles) #--> for quality selection
        executor.submit(range_list, audio_segment_list,audio_resolution[1], audio_throttles)

    with ThreadPoolExecutor() as executor:
        executor.submit(runner,audio_throttles, audio_stream,audio_segment_list)
    b=time.time()
    create_segmented_file()
    print("Finished")
    print("Time Taken:",b-a,"sec")
    return {"url": "http://127.0.0.1:5000"}
