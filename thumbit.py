from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageDraw, ImageFont
import StringIO
import re
import os
from decimal import Decimal

def getThumbnailAt(timestring,filename):
    p = Popen(["ffmpeg","-ss",timestring,"-i",filename,"-f","image2","-frames:v","1","-c:v","png","-loglevel","8","-"],stdout=PIPE)
    pout = p.communicate()
    img = Image.open(StringIO.StringIO(pout[0]))
    return img

def getThumbnalsInterval(filename,interval):
    totalThumbs = getVideoDuration(filename)//interval
    imageList = []
    seektime = 0
    for n in range(0,totalThumbs):
        seektime += interval
        hours = seektime // 3600
        minutes = (seektime % 3600) // 60
        seconds = seektime % 60
        timestring = `hours`+":"+`minutes`+":"+`seconds`
        img = getThumbnailAt(timestring,filename)
        imageList.append(img)
    return imageList

def getVideoDuration(filename):
    # p = Popen(["ffmpeg","-i",filename,"2>&1","|","awk","'/Duration/ {split($2,a,\":\");print a[1]*3600+a[2]*60+a[3]}'"],stdout=PIPE)
    p = Popen(["ffmpeg","-i",filename],stdout=PIPE, stderr=STDOUT)
    pout = p.communicate()
    matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", pout[0], re.DOTALL).groupdict()
    hours = Decimal(matches['hours'])
    minutes = Decimal(matches['minutes'])
    seconds = Decimal(matches['seconds'])
    duration= 3600*hours + 60*minutes + seconds
    return duration

def shrinkThumbs(imageList,maxsize):
    totalThumbs = len(imageList)
    for i in range(0, totalThumbs):
        imageList[i].thumbnail(maxsize)
    return imageList

def makeGrid(imageList,column):
    totalThumbs = len(imageList)
    row = (totalThumbs//column)
    if (totalThumbs % column) > 0:
        row += 1
    width = imageList[0].width
    height = imageList[0].height
    sheet = Image.new(imageList[0].mode,(width*column,height*row))
    for i in range(0,column):
        for j in range(0,row):
            if j*column+i >= totalThumbs:
                break
            sheet.paste(imageList[j*column+i],(width*i,height*j))
    return sheet

def makeHeader(filename,grid,resolution):
    filesize = os.stat(filename).st_size / 1048576.0
    width = resolution[0]
    height = resolution[1]
    duration = getVideoDuration(filename)
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    timestring = ("{:4n}".format(hours))+":"+("{:2n}".format(minutes))+":"+("{:2n}".format(seconds))

    fnt = ImageFont.truetype('Cabin-Regular-TTF.ttf', 15)
    header = Image.new(grid.mode, (grid.width,100), (0,0,0,0))
    d = ImageDraw.Draw(header)
    d.text((10,10), "File Name: "+filename, font=fnt,fill=(255,255,255,0))
    d.text((10,30), "File Size: "+("{:10.6f}".format(filesize))+" MB", font=fnt,fill=(255,255,255,0))
    d.text((10,50), "Resolution: "+`width`+"x"+`height`, font=fnt,fill=(255,255,255,0))
    d.text((10,70), "Duration: "+timestring, font=fnt,fill=(255,255,255,0))
    return header

def makeSheetInterval(filename, interval, maxsize):
    thumbsList = getThumbnalsInterval(filename,interval)
    resol = thumbsList[0].size
    thumbsList = shrinkThumbs(thumbsList,maxsize)
    column = 5
    grid = makeGrid(thumbsList,column)
    header = makeHeader(filename,grid,resol)
    sheet = Image.new(grid.mode,(grid.width,grid.height+header.height))
    sheet.paste(header,(0,0))
    sheet.paste(grid,(0,header.height))
    sheet.show()
    print(thumbsList[0].mode)

print("Hi there")

makeSheetInterval("in.mp4",5,(220,220))
