from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageDraw, ImageFont
import StringIO
import re
import os
from decimal import Decimal

class Video:
    def __init__(self,filename):
        self.filename = filename
        self.filesize = self.getFileSize()
        example = self.getFrameAt(0)
        self.resolution = example.size
        self.mode = example.mode
        self.duration = self.getVideoDuration()
        self.thumbnails = []
        self.thumbsize = self.resolution
        self.thumbcount = 0

    def getFileSize(self):
        return os.stat(self.filename).st_size / 1048576.0

    def getVideoDuration(self):
        p = Popen(["ffmpeg","-i",self.filename],stdout=PIPE, stderr=STDOUT)
        pout = p.communicate()
        matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", pout[0], re.DOTALL).groupdict()
        hours = Decimal(matches['hours'])
        minutes = Decimal(matches['minutes'])
        seconds = Decimal(matches['seconds'])
        duration= 3600*hours + 60*minutes + seconds
        return duration

    def getFrameAt(self,seektime):
        hours = int(seektime // 3600)
        minutes = int((seektime % 3600) // 60)
        seconds = int(seektime % 60)
        timestring = `hours`+":"+`minutes`+":"+`seconds`
        p = Popen(["ffmpeg","-ss",timestring,"-i",self.filename,"-f","image2","-frames:v","1","-c:v","png","-loglevel","8","-"],stdout=PIPE)
        pout = p.communicate()
        img = Image.open(StringIO.StringIO(pout[0]))
        return img

    def makeThumbnails(self,interval):
        totalThumbs = self.duration//interval
        thumbsList = []
        seektime = 0
        for n in range(0,totalThumbs):
            seektime += interval
            img = self.getFrameAt(seektime)
            thumbsList.append(img)
        self.thumbnails = thumbsList
        self.thumbcount = len(thumbsList)
        return thumbsList

    def shrinkThumbs(self,maxsize):
        if self.thumbcount==0:
            return
        for i in range(0, self.thumbcount):
            self.thumbnails[i].thumbnail(maxsize)
        self.thumbsize = self.thumbnails[0].size
        return self.thumbnails

class VidSheet:
    def __init__(self, video):
        self.font = ImageFont.truetype('Cabin-Regular-TTF.ttf', 15)
        self.backgroundColour = (0,0,0,0)
        self.textColour = (255,255,255,0)
        self.headerSize = 100
        self.gridColumn = 5
        self.maxThumbSize = (220,220)

        self.video = video

    def setProperty(self,prop,value):
        if prop == 'font':
            self.font = ImageFont.truetype(value[0], value[1])
        elif prop == 'backgroundColour':
            self.backgroundColour = value
        elif prop == 'textColour':
            self.textColour = value
        elif prop == 'headerSize':
            self.headerSize = value
        elif prop == 'gridColumn':
            self.gridColumn = value
        elif prop == 'maxThumbSize':
            self.maxThumbSize = value
        else:
            raise Exception('Invalid VidSheet property')

    def makeGrid(self):
        column = self.gridColumn
        row = self.video.thumbcount//column
        if (self.video.thumbcount % column) > 0:
            row += 1
        width = self.video.thumbsize[0]
        height = self.video.thumbsize[1]
        grid = Image.new(self.video.mode,(width*column,height*row))
        for i in range(0,column):
            for j in range(0,row):
                if j*column+i >= self.video.thumbcount:
                    break
                grid.paste(self.video.thumbnails[j*column+i],(width*i,height*j))
        self.grid = grid
        return grid

    def makeHeader(self):
        width = self.video.resolution[0]
        height = self.video.resolution[1]
        duration = self.video.duration
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        timestring = ("{:4n}".format(hours))+":"+("{:2n}".format(minutes))+":"+("{:2n}".format(seconds))

        header = Image.new(self.grid.mode, (self.grid.width,self.headerSize), self.backgroundColour)
        d = ImageDraw.Draw(header)
        d.text((10,10), "File Name: "+self.video.filename, font=self.font,fill=self.textColour)
        d.text((10,30), "File Size: "+("{:10.6f}".format(self.video.filesize))+" MB", font=self.font,fill=self.textColour)
        d.text((10,50), "Resolution: "+`width`+"x"+`height`, font=self.font,fill=self.textColour)
        d.text((10,70), "Duration: "+timestring, font=self.font,fill=self.textColour)
        self.header = header
        return header

    def makeSheetByInterval(self,interval):
        self.video.makeThumbnails(interval)
        self.video.shrinkThumbs(self.maxThumbSize)
        self.makeGrid()
        self.makeHeader()
        self.sheet = Image.new(self.grid.mode,(self.grid.width,self.grid.height+self.header.height))
        self.sheet.paste(self.header,(0,0))
        self.sheet.paste(self.grid,(0,self.header.height))
        return self.sheet

    def makeSheetByNumber(self,numOfThumbs):
        interval = (self.video.duration/numOfThumbs)
        return self.makeSheetByInterval(interval)


print("Hi there")

video = Video("in.mp4")
sheet = VidSheet(video)
sheet.setProperty('textColour',(0,255,0,0))
sheet.makeSheetByNumber(15).show()
