from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageDraw, ImageFont
import StringIO
import re
import os
import argparse
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
        timestring = self.getTimeString(seektime)
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

    def getTimeString(self,seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        timestring = `hours`+":"+`minutes`+":"+`seconds`
        return timestring

class Sheet:
    def __init__(self, video):
        self.font = ImageFont.truetype('Cabin-Regular-TTF.ttf', 15)
        self.backgroundColour = (0,0,0,0)
        self.textColour = (255,255,255,0)
        self.headerSize = 100
        self.gridColumn = 5
        self.maxThumbSize = (220,220)
        self.timestamp = True

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
        elif prop == 'timestamp':
            self.timestamp = value
        else:
            raise Exception('Invalid Sheet property')

    def makeGrid(self):
        column = self.gridColumn
        row = self.video.thumbcount//column
        if (self.video.thumbcount % column) > 0:
            row += 1
        width = self.video.thumbsize[0]
        height = self.video.thumbsize[1]
        grid = Image.new(self.video.mode,(width*column,height*row))
        d = ImageDraw.Draw(grid)
        seektime = 0
        for j in range(0,row):
            for i in range(0,column):
                if j*column+i >= self.video.thumbcount:
                    break
                grid.paste(self.video.thumbnails[j*column+i],(width*i,height*j))
                if self.timestamp==True:
                    seektime += self.vid_interval
                    ts = self.video.getTimeString(seektime)
                    d.text((width*i,height*j),ts,font=self.font,fill=self.textColour)
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
        d.text((10,10), "File Name: "+os.path.basename(self.video.filename), font=self.font,fill=self.textColour)
        d.text((10,30), "File Size: "+("{:10.6f}".format(self.video.filesize))+" MB", font=self.font,fill=self.textColour)
        d.text((10,50), "Resolution: "+`width`+"x"+`height`, font=self.font,fill=self.textColour)
        d.text((10,70), "Duration: "+timestring, font=self.font,fill=self.textColour)
        self.header = header
        return header

    def makeSheetByInterval(self,interval):
        self.vid_interval = interval
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
        self.vid_interval = interval
        return self.makeSheetByInterval(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create thumbnail contact sheet from a video.')
    parser.add_argument('filename',help='Input video filename.')
    parser.add_argument('--output','-o',default=None, metavar='<output_file>',help='Specift output video filename.')
    parser.add_argument('--interval', '-i', type=int, default=None, metavar='<sec>',help='Create thumnnails at fixed interval. Each thumbnail is <sec> seconds apart.')
    parser.add_argument('--number', '-n', type=int, default=None, metavar='<num>',help='Create total of <num> thumbnails. Each thumbnail is at equidistant apart.')
    parser.add_argument('--column','-c',type=int,default=None, metavar='<num>', help='Specify number of column of thumbnail sheet.')
    parser.add_argument('--notime', action='count', help='Remove thumbnail timestamp.')
    parser.add_argument('--header',type=int,default=None, metavar='<size>', help='Specify height of description header.')
    parser.add_argument('--thumbsize','-t', nargs=2,type=int,default=None, metavar=('<width>','<height>'), help='Specify maximum size of a thumbnail. The thumbnails will keep its aspect ratio unchanged.')
    parser.add_argument('--textcolour',nargs=4,type=int,default=None, metavar=('<r>','<g>','<b>','<a>'), help='Specify text colour of description. Colour is specify in RGBA format.')
    parser.add_argument('--bgcolour',nargs=4,type=int,default=None, metavar=('<r>','<g>','<b>','<a>'), help='Specify background colour of contact sheet. Colour is specify in RGBA format.')
    parser.add_argument('--font',nargs=2,default=None, metavar=('<fontfile>','<size>'), help='Specify font of description. Any truetype font are supported.')
    parser.add_argument('--preview', action='count', help='Preview the result contact sheet.')
    args = parser.parse_args()

    video = Video(args.filename)
    sheet = Sheet(video)

    count = 20
    mode = 'number'
    if args.interval != None:
        mode = 'interval'
        count = args.interval
    if args.number != None:
        mode = 'number'
        count = args.number
    if args.column != None:
        c = args.column
        if c < 1:
            c = 1
        sheet.setProperty('gridColumn',c)
    if args.header != None:
        c = args.header
        if c<85:
            c=85
        sheet.setProperty('headerSize',c)
    if args.notime != None:
        sheet.setProperty('timestamp',False)
    if args.thumbsize != None:
        thumbsize = (args.thumbsize[0],args.thumbsize[1])
        sheet.setProperty('maxThumbSize',thumbsize)
    if args.textcolour != None:
        colour = (args.textcolour[0],args.textcolour[1],args.textcolour[2],args.textcolour[3])
        sheet.setProperty('textColour',colour)
    if args.bgcolour != None:
        colour = (args.bgcolour[0],args.bgcolour[1],args.bgcolour[2],args.bgcolour[3])
        sheet.setProperty('backgroundColour',colour)
    if args.font != None:
        font = (args.font[0],int(args.font[1]))
        sheet.setProperty('font',font)

    if mode=='number':
        sheet.makeSheetByNumber(count)
    else:
        sheet.makeSheetByInterval(count)

    if args.output != None:
        sheet.sheet.save(args.output)
    else:
        sheet.sheet.save(args.filename[:-3]+'png')

    if args.preview != None:
        sheet.sheet.show()
