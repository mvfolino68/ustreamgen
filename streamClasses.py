import logger
import os
import re
import tools

class Movie(object):
    def __init__(self, title, url, year=None, resolution=None, language=None):
        self.title = title.strip()
        self.url = url
        self.year = year
        self.resolution = resolution
        self.language = language

    def getFilename(self):
        filestring = [self.title.replace(':','-').replace('*','_').replace('/','_').replace('?','').replace('\\','_')]
        if self.year:
            year = self.year.replace('\\', '_')  # Replace backslashes
            filestring.append(year)
        else:
            self.year = "A"  
        if self.resolution:
            filestring.append(self.resolution)
        
        # Use os.path.join for creating paths
        cleaned_title = self.title.replace(':','-').replace('*','_').replace('/','_').replace('?','').replace('\\','_')
        folder_name = "{} - {}".format(cleaned_title, self.year)
        return os.path.join('movies', folder_name, ' - '.join(filestring) + ".strm")
    
    def makeStream(self):
        tools.makeStrm(self.getFilename(), self.url)

class Event(object):
    def __init__(self, title, url, eventtype, year=None, resolution=None, language=None):
        self.title = title.strip()
        self.url = url
        self.eventtype = eventtype
        self.year = year
        self.resolution = resolution
        self.language = language

    def getFilename(self):
        filestring = [self.clean_string(self.title.strip())]
        if self.resolution:
            filestring.append(self.resolution.strip())
        
        eventtype_cleaned = self.clean_string(self.eventtype.strip())
        filename = ' - '.join(filestring) + ".strm"
        
        return os.path.join('events', eventtype_cleaned, filename)
    
    def clean_string(self, string):
        return string.replace(':','-').replace('*','_').replace('/','_').replace('?','').replace('|','-').replace('\\','_')

    def makeStream(self):
        tools.makeStrm(self.getFilename(), self.url)


class TVEpisode(object):
    def __init__(self, showtitle, url, seasonnumber=None, episodenumber=None ,resolution=None, language=None, episodename=None, airdate=None):
        self.showtitle = showtitle
        self.episodenumber = episodenumber
        self.seasonnumber = seasonnumber
        self.url = url
        self.resolution = resolution
        self.language = language
        self.episodename = episodename
        self.airdate = airdate
        self.sXXeXX = self.format_season_episode()

    def format_season_episode(self):
        if self.seasonnumber is not None and self.episodenumber is not None:
            return "S{:02d}E{:02d}".format(int(self.seasonnumber), int(self.episodenumber))
        return ""

    def getFilename(self):
        showtitle_cleaned = self.clean_string(self.showtitle)
        
        filestring = [showtitle_cleaned]
        if self.airdate:
            filestring.append(self.airdate.strip())
        elif self.sXXeXX:
            filestring.append(self.sXXeXX.strip())
        if self.episodename:
            filestring.append(self.clean_string(self.episodename.strip()))
        if self.language:
            filestring.append(self.language.strip())
        if self.resolution:
            filestring.append(self.resolution.strip())
        
        filename = ' - '.join(filestring) + ".strm"
        
        if self.seasonnumber:
            season_folder = "Season {:02d}".format(int(self.seasonnumber))
            return os.path.join('tvshows', showtitle_cleaned, season_folder, filename)
        else:
            return os.path.join('tvshows', showtitle_cleaned, filename)
    
    def clean_string(self, string):
        return string.replace(':','-').replace('*','_').replace('/','_').replace('?','').replace('\'','_').replace('\\','_')

    def makeStream(self):
        tools.makeStrm(self.getFilename(), self.url)

class rawStreamList(object):
  def __init__(self, filename):
    self.log = logger.Logger(__file__, log_level=logger.LogLevel.DEBUG)
    self.streams = {}
    self.filename = filename
    self.readLines()
    self.parseLine()

  def readLines(self):
    self.lines = [line.rstrip('\n') for line in open(self.filename, encoding="UTF-8")]
    return len(self.lines)
 
  def parseLine(self):
    linenumber=0
    for j in range(len(self.lines)):
      numlines = len(self.lines)
      if linenumber >= numlines:
        return 0
      if not linenumber:
        linenumber = 0
      thisline = self.lines[linenumber]
      nextline = self.lines[linenumber + 1]
      firstline = re.compile('EXTM3U', re.IGNORECASE).search(thisline)
      if firstline or thisline.startswith('#EXT-X-SESSION-DATA'):
        linenumber += 1
        continue
      thisline=thisline.replace("#","")
      print("THISLINE:", thisline)
      if thisline[0] == "#" and nextline[0] == "#":
        if tools.verifyURL(self.lines[linenumber+2]):
          self.log.write_to_log(msg=' '.join(["raw stream found:", str(linenumber),'\n', ' '.join([thisline, nextline]),self.lines[linenumber+2]]))
          self.parseStream(' '.join([thisline, nextline]),self.lines[linenumber+2])
          linenumber += 3
          #self.parseLine(linenumber)
        else:
          self.log.write_to_log(msg=' '.join(['Error finding raw stream in linenumber:', str(linenumber),'\n', ' '.join(self.lines[linenumber:linenumber+2])]))
          linenumber += 1
          #self.parseLine(linenumber)
      elif tools.verifyURL(nextline):
        self.log.write_to_log(msg=' '.join(["raw stream found: ", str(linenumber),'\n', '\n'.join([thisline,nextline])]))
        self.parseStream(thisline, nextline)
        linenumber += 2
        #self.parseLine(linenumber)

  def parseStreamType(self, streaminfo, streamURL):
    moviematch = tools.urlMovieMatch(streamURL)
    if moviematch:
      return 'vodMovie'

    seriesmatch = tools.urlSeriesMatch(streamURL)
    if seriesmatch:
      return 'vodTV'
  
    eventmatch = tools.eventMatch(streaminfo)
    if eventmatch:
      return 'live'
    
    ufcwwematch = tools.ufcwweMatch(streaminfo)
    if ufcwwematch:
      return 'live'
    
    typematch = tools.tvgTypeMatch(streaminfo)    
    if typematch:
      streamtype = tools.getResult(typematch)
      if streamtype == 'tvshows':
        return 'vodTV'
      if streamtype == 'movies':
        return 'vodMovie'
      if streamtype == 'live':
        return 'live'
    
    idmatch = tools.tvidmatch(streaminfo)
    if idmatch:
      return 'live'

    channelmatch = tools.tvgChannelMatch(streaminfo)
    if channelmatch:
      return 'live'
    
    logomatch = tools.tvgLogoMatch(streaminfo)
    if logomatch:
      return 'live'
    
    tvshowmatch = tools.sxxExxMatch(streaminfo)
    if tvshowmatch:
      return 'vodTV'
    
    airdatematch = tools.airDateMatch(streaminfo)
    if airdatematch:
      return 'vodTV'

    tvgnamematch = tools.tvgNameMatch(streaminfo)
    if tvgnamematch:
      if not tools.imdbCheck(tools.getResult(tvgnamematch)):
        return 'live'
    return 'vodMovie'


  def parseStream(self, streaminfo, streamURL):
    streamtype = self.parseStreamType(streaminfo, streamURL)
    if streamtype == 'vodTV':
      self.parseVodTv(streaminfo, streamURL)
    elif streamtype == 'vodMovie':
      self.parseVodMovie(streaminfo, streamURL)
    else:
      self.parseLiveStream(streaminfo, streamURL)
  
  def parseVodTv(self, streaminfo, streamURL):
    #print(streaminfo)
    title = tools.infoMatch(streaminfo)
    if title:
      title = tools.parseMovieInfo(title.group())
    resolution = tools.resolutionMatch(streaminfo)
    if resolution:
      resolution = tools.parseResolution(resolution)
      #print(resolution)
      title = tools.stripResolution(title)
    episodeinfo = tools.parseEpisode(title)
    if episodeinfo:
      if len(episodeinfo) == 3:
        showtitle = episodeinfo[0]
        airdate = episodeinfo[2]
        episodename = episodeinfo[1]
        episode = TVEpisode(showtitle, streamURL, resolution=resolution, episodename=episodename, airdate=airdate)
      else:
        showtitle = episodeinfo[0]
        episodename = episodeinfo[1]
        seasonnumber = episodeinfo[2]
        episodenumber = episodeinfo[3]
        language = episodeinfo[4]
        episode = TVEpisode(showtitle, streamURL, seasonnumber=seasonnumber, episodenumber=episodenumber, resolution=resolution, language=language, episodename=episodename)
      print(episode.__dict__, 'TVSHOW')
      print(episode.getFilename())
      episode.makeStream()
    else:
      print("NOT FOUND: ",streaminfo)
   
  
  def parseLiveStream(self, streaminfo, streamURL):
    #print(streaminfo, "LIVETV")
    title = tools.parseMovieInfo(streaminfo)
    resolution = tools.resolutionMatch(streaminfo)
    eventtype = tools.tvgGroupMatch(streaminfo)
    if eventtype:
      eventtype = tools.parseGroup(eventtype)
    if resolution:
      resolution = tools.parseResolution(resolution)
    year = tools.yearMatch(streaminfo)
    if year:
      title = tools.stripYear(title)
      year = year.group().strip()
    language = tools.languageMatch(title)
    if language:
      title = tools.stripLanguage(title)
      language = language.group().strip()
    eventstream = Event(title, streamURL,eventtype=eventtype, year=year, resolution=resolution, language=language)
    print(eventstream.__dict__, "EVENT")
    print(eventstream.getFilename())
    eventstream.makeStream()

  def parseVodMovie(self, streaminfo, streamURL):
    #todo: add language parsing for |LA| and strip it
    title = tools.parseMovieInfo(streaminfo)
    resolution = tools.resolutionMatch(streaminfo)
    if resolution:
      resolution = tools.parseResolution(resolution)
    year = tools.yearMatch(streaminfo)
    if year:
      title = tools.stripYear(title)
      year = year.group().strip()
    language = tools.languageMatch(title)
    if language:
      title = tools.stripLanguage(title)
      language = language.group().strip()
    moviestream = Movie(title, streamURL, year=year, resolution=resolution, language=language)
    print(moviestream.__dict__, "MOVIE")
    print(moviestream.getFilename())
    moviestream.makeStream()
