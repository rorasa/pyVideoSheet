# pyVideoSheet
Python video thumbnail contact sheet creator.

pyVideoSheet is designed for efficiency and simplicity, allowing users to create video contact sheets rapidly.
pyVideoSheet can be used as a standalong command-line application and as an includable package.

## Dependencies

pyVideoSheet requires the following softwares and packages to work:

* Python (Of course! pyVideoSheet is written in Python 2.7 though)
* Python Image Library (PIL) 
* FFmpeg

### Basic instruction on how to install dependencies

#### Python
Because pyVideoSheet is written in Python, therefore there must be a valid Python installed to use pyVideoSheet.

Python package for any platform can be downloaded from https://www.python.org/downloads/

#### Python Image Library (PIL)
There are many ways to install PIL, but here we would recommend to use [Pillow](https://pypi.python.org/pypi/Pillow/3.0.0), a nice and easy folk of PIL.
To install Pillow, run this command
```
easy_install Pillow
```
More details instruction on how to install Pillow can be found in Pillow's [documentation](https://pillow.readthedocs.org/en/3.0.x/index.html).

#### FFmpeg
FFmpeg is a cross-platform media solution that pyVideoSheet uses as the primary way to interact with a video.
pyVideoSheet requires a working FFmpeg to work.

You can get the latest FFmpeg from its website https://www.ffmpeg.org/download.html . 
Because compiling FFmpeg properly is quite tricky, we'd recommend you to stick to the pre-built packages unless you really need otherwise.

Please note that FFmpeg must be included in the system search path for pyVideoSheet to work correctly.
You can test this by running
```
ffmpeg -h
```
If you can see FFmpeg's help, it should work alright. Otherwise please check how to add FFmpeg to search path in its [documentations](https://www.ffmpeg.org/documentation.html)

## Installing pyVideoSheet

1. Get the latest version of pyVideoSheet.
   This can be done by either using git:
   
   ```
   git clone https://github.com/rorasa/pyVideoSheet.git
   ```
   
   or by downloading the zip archive https://github.com/rorasa/pyVideoSheet/archive/master.zip and extract it.
2. Go into the downloaded directory
   ```
   cd pyVideoSheet-<version>
   ```
3. Install the package
   ```
   python setup.py install
   ```
   
## Using pyVideoSheet as a standalone application

pyVideoSheet can be used as a command-line application. This provides a quick and easy way to create contact sheets.
The best thing about being a command-line application, as opposed to a GUI one, is the ease of writing a batch script for it, 
especially when one has to work with lots of videos. 

Example of how to create a contact sheet for a video, run this command
```
python -m pyVideoSheet.create video-file.mp4
```
This executes *create* utility of pyVideoSheet to create a contact sheet for *video-file.mp4* named *video-file.png*, using default options.
Customisation options can be added using optional flags.

There are many customisation options, as follows:

Options | Example | Description
--------|---------|-------------
-h, --help | --help | Display pyVideoSheet's instruction on command-line
-o, --output | -o out.png | Specify contact sheet's filename
-n, --number | -n 30 | Specify total number of thumbnails. Each thumbnail is at equidistant apart. The default option is -n 20. This option cannot be use with --interval.
-i, --interval | -i 300 | Specify fixed interval between each thumbnails. Total number of thumbnail is vary. This option cannot be use with --number.
-c, --column | -c 6 | Specify number of column of the thumbnail grid. The default is -c 5.
--notime | --notime | Remove thumbnail's timestamp.
--header | --header 120 | Specify the height of description header in pixels. The default is 100.
-t, --thumbsize | -t 300 250 | Specify the maximum size of thumbnail. Thumbnails will retain its aspect ratio. The default is -t 220 220.
--textcolour | --textcolour 255 255 0 0 | Specify description's text colour in RGBA format.
--bgcolour | --bgcolour 255 255 0 0 | Specify description's text colour in RGBA format.
--font | --font font-file.ttf 12 | Specify description's font and font size. Support any TrueType font.
--preview | --preview | Preview the contact sheet on default image viewer.

## Using pyVideoSheet as a package

pyVideoSheet can be imported into any Python project, allowing a quick and flexible way to create a video contact sheet programatically.

### Examples
First example shows how to create a simple contact sheet for *video-name.mp4*
```python
import pyVideoSheet as pvs

vid = pvs.Video("video-name.mp4")
vsheet = pvs.Sheet(vid)
vsheet.makeSheetByNumber(20)
vsheet.sheet.save("sheet.png")
```
This results in a default contact sheet. 

The next example shows the full customisation capability of pyVideoSheet.
```python
import pyVideoSheet as pvs

vid = pvs.Video("video-name.mp4") # create Video object
vidLength = vid.getVideoDuration() # get video duration in seconds

# create a 5x6 grid contact sheet with blue text without timestamp
vsheet1 = pvs.Sheet(vid) # create Sheet object
vsheet1.setProperty('gridColumn',6) # set 6 columns
vsheet1.setProperty('textColour',(0,0,255,0)) # set text to blue
vsheet1.setProperty('timestamp',False) # disable timestamp

sheet_1 = vsheet1.makeSheetByNumber(30) # create contact sheet of 5 times 6 columns
sheet_1.save('grid_example.png') # save with PIL save()

vsheet1.sheet.show() # preview with PIL show(). The created sheet is kept as Sheet.sheet variable.

# create a single row preview with black text on white background
vsheet2 = pvs.Sheet(vid) # create Sheet object
vsheet2.setProperty('gridColumn',1) # set 1 columns
vsheet2.setProperty('textColour',(0,0,0,0)) # set text to black
vsheet2.setProperty('backgroundColour',(255,255,255,0)) # set background to white
vsheet2.setProperty('maxThumbSize',(500,500)) # allow larger thumbnails

sheet_2 = vsheet2.makeSheetByInterval(600) # create one thumbnail every 10 minutes
sheet_2.show()

vsheet2.sheet.save('column_example.png') # save with PIL save()
```

### Video class

Video class represents a video object. 
It contains information regarding each specific video as well as providing low level interaction between Python and video.

####Video class functions

**Video(*file*)**

Constructor of Video class. 
- **Parameter**: **file**—a file name string of video (including its path).
- **Return**: A Video object.

**getFileSize()**

Get file size of the video in MB.
- **Return**: File size in MB.

**getVideoDuration()**

Get duration of the video in seconds.
- **Return**: Duration in seconds.

**getFrameAt(*seektime*)**

Capture a frame at *seektime* seconds from the beginning.
- **Parameter**: **seektime**—time in seconds.
- **Return**: A PIL Image object.

**makeThumbnails(*interval*)**

Create a list of frames captured at every fixed *interval*.
- **Parameter**: **interval**—time in seconds.
- **Return**: A List of PIL Image objects.

**shrinkThumbs(*maxSize*)**

Reduce the resolution of Video.thumbnails.
- **Parameter**: **maxSize**—a tuple of (maxWidth, maxHeight).
- **Return**: Video.thumbnails.

### Sheet class

Sheet class handles the creation of contact sheet.
Contact sheet's customisation can be done by setting Sheet class's properties.

####Sheet class functions

**Sheet(*Video*)**

Constructor of Sheet class.
- **Parameter**: **Video**—a Video object.
- **Return**: A Sheet object.

**setProperty(*prop*,*value*)**

Set customisation options of Sheet.
- **Parameter**: **prop**—a property string.
                 **value**—a property value

Property string | Default Property Value | Description
----------------|----------------|-------------
'font' | ('Cabin-Regular-TTF.ttf', 15) | Set description's font and font size. Takes value as a tuple of font file name (string) and font size (integer).
'backgroundColour' | (0,0,0,0) | Set header's background colour. Takes value as a tuple containing 4 value for RGBA colour.
'textColour' | (255,255,255,0) | Set description's text colour. Takes value as a tuple containing 4 value for RGBA colour.
'headerSize' | 100 | Set header's height in pixels.
'gridColumn' | 5 | Set number of thumbnail columns in the grid.
'maxThumbSize' | (220,220) | Set maximum width and height of each thumbnail. The thumbnail will always retain its aspect ratio. Takes value as a tuple of max width and max height.
'timestamp' | True | Enable thumbnail timestamp. Takes boolean as its value.

**makeSheetByInterval(*interval*)**

Create a contact sheet. Each thumbnail is created at fixed *interval*. 
The total number of thumbnails is vary by the video duration divided by *interval*.
- **Parameter**: **interval**—a time in seconds.
- **Return**: A PIL Image object.

**makeSheetByNumber(*number*)**

Create a contact sheet. The total number of thumbnails is fixed.
Each thumbnail is created at the interval defined by the video duration divided by *number*.
- **Parameter**: **number**—a number of thumbnails.
- **Return**: A PIL Image object.

## Supporting formats

pyVideoSheet works based upon PIL and FFmpeg, thus the supporting formats are set by these dependencies.
Most commonly used video formats (such as mp4, avi, mov *etc.*) should work with FFmpeg, thus should work with pyVideoSheet.
Most encoding should be supported as well (including MPEG-2, Xvid, h264). 
For more information on FFmpeg supported formats, please check [FFmpeg documentation](https://www.ffmpeg.org/documentation.html)
Most image formats (including JPEG and PNG) should also work as an output format.

## License and development information
### License
pyVideoSheet source, including this document, is distributed under Mozilla Public License 2.0. Please refer to LICENSE file for information.

### Developer
pyVideoSheet is created and maintained by [Wattanit Hotrakool](https://github.com/rorasa).
You can reach the developer directly through [twitter](https://www.twitter.com/rorasa).

### Development log

30 October 2015
- Converted into a python package with setup script.

28 October 2015
- Converted into a executable module (legacy)

27 October 2015
- First working version
