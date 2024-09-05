import re
import os
import shutil
def verifyURL(line):
  verifyurl  = re.compile('://').search(line)
  if verifyurl:
    return True
  return

def tvgTypeMatch(line):
  typematch = re.compile('tvg-type=\"(.*?)\"', re.IGNORECASE).search(line)
  if typematch:
    return typematch
  return

def eventMatch(line):
  eventmatch = re.compile('tvg-type=\"events\"', re.IGNORECASE).search(line)
  if eventmatch:
    return eventmatch
  return

def ufcwweMatch(line):
  ufcwwematch = re.compile('[U][f][c]|[w][w][e]|[r][i][d][i][c][u][l]', re.IGNORECASE).search(line)
  if ufcwwematch:
    return ufcwwematch
  return

def airDateMatch(line):
  datematch = re.compile('[1-2][0-9][0-9][0-9][ ][0-3][0-9][ ][0-1][0-9]|[1-2][0-9][0-9][0-9][ ][0-1][0-9][ ][0-3][0-9]').search(line)
  if datematch:
    return datematch
  return

def tvgNameMatch(line):
  namematch = re.compile('tvg-name=\"(.*?)\"', re.IGNORECASE).search(line)
  if namematch:
    return namematch
  return

def tvidmatch(line):
  tvidmatch = re.compile('tvg-ID=\"(.*?)\"', re.IGNORECASE).search(line)
  if tvidmatch:
    return tvidmatch
  return

def tvgLogoMatch(line):
  logomatch = re.compile('tvg-logo=\"(.*?)\"', re.IGNORECASE).search(line)
  if logomatch:
    return logomatch
  return

def tvgGroupMatch(line):
  groupmatch = re.compile('group-title=\"(.*?)\"', re.IGNORECASE).search(line)
  if groupmatch:
    return groupmatch
  return
      
def infoMatch(line):
  infomatch = re.compile('[,](?!.*[,])(.*?)$', re.IGNORECASE).search(line)
  if infomatch:
    return infomatch
  return

def getResult(re_match):
  return re_match.group().split('\"')[1]
      
def sxxExxMatch(line):
  tvshowmatch = re.compile('[s][0-9][0-9][e][0-9][0-9]|[0-9][0-9][x][0-9][0-9][ ][-][ ]|[s][0-9][0-9][ ][e][0-9][0-9]|[0-9][0-9][x][0-9][0-9]', re.IGNORECASE).search(line)
  if tvshowmatch:
    return tvshowmatch
  tvshowmatch = seasonMatch2(line)
  if tvshowmatch:
    return tvshowmatch
  tvshowmatch = episodeMatch2(line)
  if tvshowmatch:
    return tvshowmatch
  return

def tvgChannelMatch(line):
  tvgchnomatch = re.compile('tvg-chno=\"(.*?)\"', re.IGNORECASE).search(line)
  if tvgchnomatch:
    return tvgchnomatch
  tvgchannelid = re.compile('tvg-chno=\"(.*?)\"', re.IGNORECASE).search(line)
  if tvgchannelid:
    return tvgchannelid
  return

def yearMatch(line):
  yearmatch = re.compile('[(][1-2][0-9][0-9][0-9][)]').search(line)
  if yearmatch:
    return yearmatch
  return

def resolutionMatch(line):
  resolutionmatch = re.compile('HD|SD|720p WEB x264-XLF|WEB x264-XLF').search(line)
  if resolutionmatch:
    return resolutionmatch
  return

def episodeMatch(line):
  episodematch = re.compile('[e][0-9][0-9]|[0-9][0-9][x][0-9][0-9]', re.IGNORECASE).search(line)
  if episodematch:
    if episodematch.end() - episodematch.start() > 3:
      episodenumber = episodematch.group()[3:]
      #print(episodenumber,'E#')
    else:
      episodenumber = episodematch.group()[1:]
      #print(episodenumber,'E#')
    return episodenumber
  return

def episodeMatch2(line):
  episodematch = re.compile('[e][0-9][0-9]|[0-9][0-9][x][0-9][0-9]', re.IGNORECASE).search(line)
  if episodematch:
    return episodematch
  return

def seasonMatch2(line):
  seasonmatch = re.compile('[s][0-9][0-9]', re.IGNORECASE).search(line)
  if seasonmatch:   
    return seasonmatch
  return

def seasonMatch(line):
  seasonmatch = re.compile('[s][0-9][0-9]|[0-9][0-9][x][0-9][0-9]', re.IGNORECASE).search(line)
  if seasonmatch:
    if seasonmatch.end() - seasonmatch.start() > 3:
      seasonnumber = seasonmatch.group()[:3]
      #print(seasonnumber,'s#')
    else:
      seasonnumber = seasonmatch.group()[1:]
      #print(seasonnumber,'s#')
    return seasonnumber
  return

def urlSeriesMatch(line):
  seriesmatch = re.compile('series\/', re.IGNORECASE).search(line)
  if seriesmatch:
    return seriesmatch
  return

def urlMovieMatch(line):
  seriesmatch = re.compile('movie\/', re.IGNORECASE).search(line)
  if seriesmatch:
    return seriesmatch
  return

def imdbCheck(line):
  imdbmatch = re.compile('[t][t][0-9][0-9][0-9]').search(line)
  if imdbmatch:
    return imdbmatch
  return

def parseMovieInfo(info):
  if ',' in info:
    info = info.split(',')
  if info[0] == "":
    del info[0]
  info = info[-1]
  if '#' in info:
    info = info.split('#')[0]
  if ':' in info:
    info = info.split(':')
    if resolutionMatch(info[0]):
      info = info[1]
    else:
      info = ':'.join(info)
  return info.strip()
     
def parseResolution(match):
  resolutionmatch = match.group().strip()
  if resolutionmatch == 'HD' or resolutionmatch == '720p WEB x264-XLF':
    return '720p'
  elif resolutionmatch == 'SD' or resolutionmatch == 'WEB x264-XLF':
    return '480p'
  return

def parseGroup(match):
  groupmatch = match.group().strip()
  groupparse = re.findall('group-title=\"(.*?)\"', groupmatch)
  return groupparse[0].replace('/','-')

def makeStrm(filename, url):
  try:
      path = os.path.dirname(filename)
      os.makedirs(path, exist_ok=True)
      streamfile = open(filename, "w+")
      streamfile.write(url)
      streamfile.close
      print("strm file created:", filename)
      streamfile.close()
  except:
    print ("Could not write:",filename)

def makeDirectory(directory):
  if not os.path.exists(directory):
    os.mkdir(directory)
  else:
    print("directory found:", directory)

def stripYear(title):
  yearmatch = re.sub('[(][1-2][0-9][0-9][0-9][)]|[1-2][0-9][0-9][0-9]', "", title)
  if yearmatch:
    return yearmatch.strip()
  return

def languageMatch(line):
  languagematch = re.compile('[|][A-Z][A-Z][|]', re.IGNORECASE).search(line)
  if languagematch:
    return languagematch
  return

def stripLanguage(title):
  languagematch = re.sub('[|][A-Z][A-Z][|]', "", title, flags=re.IGNORECASE)
  if languagematch:
    return languagematch.strip()
  return

def stripResolution(title):
  resolutionmatch = re.sub('HD|SD|720p WEB x264-XLF|WEB x264-XLF', "", title)
  if resolutionmatch:
    return resolutionmatch.strip()
  return

def stripSxxExx(title):
  sxxexxmatch = re.sub('[s][0-9][0-9][e][0-9][0-9]|[0-9][0-9][x][0-9][0-9][ ][-][ ]|[0-9][0-9][x][0-9][0-9]|[s][0-9][0-9][ ][e][0-9][0-9]', "", title, flags=re.IGNORECASE)
  if sxxexxmatch:
    return sxxexxmatch.strip()
  return

def parseEpisode(title):
  airdate = airDateMatch(title)
  titlelen = len(title)
  showtitle, episodetitle, language = None, None, None
  if airdate:
    showtitle = title[:airdate.start()].strip()
    if airdate.end() != titlelen:
      episodetitle = title[airdate.end():].strip()
    return [showtitle,episodetitle,airdate.group()]
  seasonepisode = sxxExxMatch(title)
  if seasonepisode:
    print(seasonepisode)
    if seasonepisode.end() - seasonepisode.start() > 6 or len(seasonepisode.group()) == 5:
      
      episodetitle = title[seasonepisode.end():].strip()
      seasonnumber = seasonMatch(title)
      episodenumber = episodeMatch(title)
      showtitle = title[:seasonepisode.start()]
      languagem = languageMatch(showtitle)
      if languagem:
        language = languagem.group().strip('|')
        showtitle = showtitle[languagem.end():]
        language2 = languageMatch(showtitle)
        if language2:
          showtitle = showtitle[:language2.start()]
          season = seasonMatch2(showtitle)
          if season:
            showtitle = showtitle[:season.start()]
    else:
      seasonnumber = seasonMatch(title)
      episodenumber = episodeMatch(title)
      showtitle = stripSxxExx(title)
    return [showtitle, episodetitle, seasonnumber, episodenumber, language]
  
def compare_and_update(dcmp, uid, gid):
    for name in dcmp.diff_files:
        print("STREAM CHANGE -  %s - UPDATING" % (name))
        left_path = os.path.join(dcmp.left, name)
        right_path = os.path.join(dcmp.right, name)
        if os.path.isdir(left_path):
            shutil.copytree(left_path, right_path, dirs_exist_ok=True)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
        elif os.path.isfile(left_path):
            shutil.copy2(left_path, right_path)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
    for name in dcmp.left_only:
        left_path = os.path.join(dcmp.left, name)
        right_path = os.path.join(dcmp.right, name)
        if os.path.isdir(left_path):
            print("NEW STREAM DIRECTORY - %s - CREATING" % (name))
            shutil.copytree(left_path, right_path, dirs_exist_ok=True)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
        elif os.path.isfile(left_path):
            print("NEW STREAM FILE - %s - CREATING" % (name))
            shutil.copy2(left_path, right_path)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
    for name in dcmp.right_only:
        right_path = os.path.join(dcmp.right, name)
        if os.path.isdir(right_path):
            print("directory NO LONGER EXISTS - %s - DELETING" % (name))
            shutil.rmtree(right_path)
        if os.path.isfile(right_path) and name.endswith(".strm"):
            print("file NO LONGER EXISTS - %s - DELETING" % (name))
            os.remove(right_path)
    for sub_dcmp in dcmp.subdirs.values():
        compare_and_update(sub_dcmp, uid, gid)

def compare_and_update_events(dcmp, uid, gid):
    for name in dcmp.diff_files:
        print("STREAM CHANGE -  %s - UPDATING" % (name))
        left_path = os.path.join(dcmp.left, name)
        right_path = os.path.join(dcmp.right, name)
        if os.path.isdir(left_path):
            shutil.copytree(left_path, right_path, dirs_exist_ok=True)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
        elif os.path.isfile(left_path):
            shutil.copy2(left_path, right_path)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
    for name in dcmp.left_only:
        left_path = os.path.join(dcmp.left, name)
        right_path = os.path.join(dcmp.right, name)
        if os.path.isdir(left_path):
            print("NEW STREAM DIRECTORY - %s - CREATING" % (name))
            shutil.copytree(left_path, right_path, dirs_exist_ok=True)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
        elif os.path.isfile(left_path):
            print("NEW STREAM FILE - %s - CREATING" % (name))
            shutil.copy2(left_path, right_path)
            os.chown(right_path, uid, gid)
            os.chmod(right_path, 0o777)
    for name in dcmp.right_only:
        right_path = os.path.join(dcmp.right, name)
        if os.path.isfile(right_path) and name.endswith(".strm"):
            print("EVENT NO LONGER EXISTS - %s - DELETING" % (name))
            os.remove(right_path)
    for sub_dcmp in dcmp.subdirs.values():
        compare_and_update_events(sub_dcmp, uid, gid)

def printArray(args):
    argcount =1
    for arg in args:
        print ('argument ',argcount,': ',arg)
        argcount=argcount+1
