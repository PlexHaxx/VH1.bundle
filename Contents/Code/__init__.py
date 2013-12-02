# VIDEO CLIP FOR BONUS CLIP OR SNEEK PEEK HAVE MULTIPLE PARTS

TITLE = 'VH1'
PREFIX = '/video/vh1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.vh1.com'
TOP_50 = 'http://www.vh1.com/shows/top_50_shows.jhtml'
VH1_MENU = 'http://www.vh1.com/sitewide/navigation/menubar_new.jhtml'
VH1_ALLMENU = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'
# Variables below uses the base url and either %20Full%20Episodes  or %20Bonus%20Clips but %s will not work with '-' in url so have to split into two
POPULAR_AJAX_PART1 = '/global/music/modules/mostPopular/module.jhtml?category=Videos%20-%20TV%20Show%20Videos%20-%20'
POPULAR_AJAX_PART2 = '&contentType=videos&howManyChartItems=25&fluxSort=numberOfViews:today:desc&displayPostedDate=true'
PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id=%s'
# THIS IS A LISTING FOR AWARDS SHOWS ON THE ALL SHOWS PAGE THAT HAVE SERIES.JHTML ENDINGS INSTEAD OF THE PROPER EVENTS NAME
SPECIAL_LIST = ["Do Something Awards 2013", "VH1 Divas 2012", "Critics' Choice Television Awards (2011)"]
# THIS IS A LISTING FOR AWARDS SHOWS THAT EITHER NO LONGER HAVE SITES OR THE LINKS ARE BAD
BAD_SHOW_LIST = ["17th Annual Critics' Choice Movie Awards", "2008 Hip Hop Honors", "2009 Hip Hop Honors", "2010 Hip Hop Honors", "VH1 Big In 2006 Awards", 
                "VH1 Divas Celebrates Soul", "Do Something Awards 2010", "Do Something Awards 2011", "Do Something Awards 2012","DIVAS (2010)", 
                "VH1 Divas (2009)", "You Oughta Know", "Critics' Choice Movie Awards (2011)", "Posted", "Music Festivals Coverage"]

SEARCH_URL = 'http://www.vh1.com/search/'

RE_SEASON  = Regex('.+(Season|Seas.) (\d{1,2}).+')
RE_EPISODE  = Regex('.+(Episode|Ep.) (\d{1,3})')
RE_PAGE = Regex('MTVN.UI.Paginate.totalNumPages = "(.+?)";')
####################################################################################################
# Set up containers for all possible objects
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  EpisodeObject.thumb = R(ICON)
  EpisodeObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(ProduceShows, title='VH1 Poplular Shows'), title='VH1 Popular Shows')) 
  oc.add(DirectoryObject(key=Callback(ProduceSpecials, title='VH1 Specials'), title='VH1 Specials')) 
  oc.add(DirectoryObject(key=Callback(VH1AllShows, title='VH1 Top 50 Shows', url=TOP_50), title='VH1 Top 50 Shows')) 
  oc.add(DirectoryObject(key=Callback(Alphabet, title='VH1 Shows A to Z'), title='VH1 Shows A to Z')) 
  oc.add(InputDirectoryObject(key=Callback(ShowSearch), title='Search for VH1 Shows', thumb=R(ICON), summary="Click here to search for shows", prompt="Search for the shows you would like to find"))
  oc.add(DirectoryObject(key=Callback(MostPopular, title='Most Popular Videos'), title='VH1 Most Popular Videos')) 
  #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.vh1", title=L("Search VH1 Videos"), prompt=L("Search for Videos")))
  return oc
#######################################################################################
# This function produces a list of shows from the search results
# It uses the "All Results" section of the search and only returns those that end with series.jhtml
@route(PREFIX + '/showsearch')
def ShowSearch(query):
    oc = ObjectContainer(title1='VH1', title2='Show Search Results')
    url = SEARCH_URL + '?q=' + String.Quote(query, usePlus = True)
    html = HTML.ElementFromURL(url)
    for item in html.xpath('//div[contains(@class,"mtvn-item-content")]'):
        link = item.xpath('./div/a//@href')[0]
        # This make sure it only returns shows that are located at mtv.com
        if 'www.vh1.com/shows/' in link and link.endswith('series.jhtml'):
            title = item.xpath('./div/a//text()')[0]
            # The shows are listed by individual season in the show search so find season and send to sections
            if '/season_' in link:
              season = link.split('/season_')[1].split('/')[0]
            else:
              season = 1
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=link, thumb=R(ICON), season=int(season)), title = title))
    return oc

####################################################################################################
# This handles most popular from the ajax 
@route(PREFIX + '/mostpopular')
def MostPopular(title):
    oc = ObjectContainer(title2=title)
    pop_type = ["Full%20Episodes", "After%20Shows", "Bonus%20Clips"]
    url = BASE_URL + POPULAR_AJAX_PART1
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Most Popular Full Episodes", url=url + pop_type[0] + POPULAR_AJAX_PART2), title="Most Popular Full Episodes"))
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Most Popular Show Clips", url=url + pop_type[2] + POPULAR_AJAX_PART2), title="Most Popular Show Clips"))
    return oc
#####################################################################################
# For Producing Popular Shows 
@route(PREFIX + '/produceshows')
def ProduceShows(title):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(VH1_MENU, cacheTime = CACHE_1HOUR)

  for video in data.xpath('//*[text()="VH1 Shows"]/parent::li//a'):
    Log('entered for loop')
    url = video.xpath('.//@href')[0]
    if url.endswith('series.jhtml'):
      if not url.startswith('http://'):
        url = BASE_URL + url
      title = video.xpath('.//text()')[0]
      if '/season_' in url:
        oc.add(DirectoryObject(key=Callback(ShowCreateSeasons, title=title, url=url), title=title))
      elif 'shows/pop_up_video/' in url:
        oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))
      else:
        oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=R(ICON), url=url, season=0), title=title))

  oc.objects.sort(key = lambda obj: obj.title)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are shows to list right now.")
  else:
    return oc
#####################################################################################
# For Producing Specials 
@route(PREFIX + '/producespecials')
def ProduceSpecials(title):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(VH1_MENU, cacheTime = CACHE_1HOUR)

  for video in data.xpath('//*[text()="Specials"]/parent::li//a'):
    url = video.xpath('.//@href')[0]
    title = video.xpath('.//text()')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    if 'www.vh1.com' not in url:
      continue
    Log('the value of url is %s' %url)
    if url.endswith('series.jhtml'):
      oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=url, thumb=R(ICON), season=0), title = title))
    elif '/events/' in url:
      oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title = title))
    else:
      continue
      
  oc.objects.sort(key = lambda obj: obj.title)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are shows to list right now.")
  else:
    return oc
####################################################################################################
# A to Z pull for VH1. But could be used with different sites. The # portion has bad links so removed it
@route(PREFIX + '/alphabet')
def Alphabet(title):
    oc = ObjectContainer(title2=title)
    for ch in list('#ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        url=VH1_ALLMENU + '?chars=' + ch
        oc.add(DirectoryObject(key=Callback(VH1AllShows, title=ch, url=url), title=ch))
    return oc
#####################################################################################
# This pulls from the VH1 archive All shows section and works for A-Z sorts of VH1 Shows
# THERE ARE LISTINGS FOR AWARDS SHOWS THAT NO LONGER HAVE SITES. 2010 HIP HOP HONORS AND 17TH ANNUAL CRITIC CHOICE AWARDS HAVE SITES, BUT LINKS ARE INCORRECT
@route(PREFIX + '/vh1allshows')
def VH1AllShows(title, url):
  oc = ObjectContainer(title2=title)
  #THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(url)
  if '?chars=' in url:
    xpath = '//div[@id="azshows_wrapper"]/div/div/a'
  else:
    xpath = '//tr[contains(@class,"Color")]/td/a'
  for video in data.xpath('%s' %xpath):
    url = video.xpath('.//@href')[0]
    title = video.xpath('.//text()')[0].strip()
    if not url.startswith('http://'):
      url = BASE_URL + url
    if title in BAD_SHOW_LIST:
      continue
    # The all shows section put series.jhtml on the end of all of the shows even the specials
    #if 'awards' not in url and 'events' not in url and 'divas_' not in url and 'you_oughta_know' not in url and '/festivals/' not in url and '/critics_choice' not in url and 'hip_hop_honors' not in url:
    if title not in SPECIAL_LIST and url.endswith('series.jhtml'):
      # Here the shows are listed by individual seasons. Specials here still have series.jhtml on them
      if '/season_' in url:
        season = url.split('/season_')[1]
        season = int(season.split('/')[0])
      else:
        season=1
      oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=url, season=season, thumb=R(ICON)), title = title))
    elif 'shows/pop_up_video/' in url:
      oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))
    else:
      #Need to take out the bad date and numbering on Critics Choice titles
      if "Critics' Choice" in title:
        title=title.split('(20')[0]
        if "Annual" in title:
          title=title.split('Annual ')[1]
      oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title = title))

  oc.objects.sort(key = lambda obj: obj.title)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no shows to list right now.")
  else:
    return oc
#######################################################################################
# This section handles shows that have a separate page for each season
# Shows that do not have an other season link will just produce all videos for all seasons
@route(PREFIX + '/showcreateseasons')
def ShowCreateSeasons(title, url):

  oc = ObjectContainer(title2=title)
  local_url = url.replace('series', 'seasons')
  #THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
  for video in data.xpath('//div[1]/ol/li/div[contains(@class,"title")]/a'):
    url = video.xpath('.//@href')[0]
    url = BASE_URL + url
    # since it hast to have season_ in url, they should all have a season number there
    season = url.split('season_')[1]
    season = int(season.replace('/series.jhtml', ''))
    title = video.xpath('./img//@alt')[0]
    if '&rsaquo;' in title:
      title = title.replace('&rsaquo;', '')
    thumb = video.xpath('./img//@src')[0]
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb

    oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=url, season=int(season)), title = title, thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

  oc.objects.sort(key = lambda obj: obj.title, reverse=True)
  
  if len(oc) < 1:
    # DO ANY MTV SHOWS HAVE OLD TABLE FORMAT?
    oc.add(DirectoryObject(key=Callback(ShowSections, title='All Videos', thumb=thumb, url=url, season=0), title='All Videos', thumb = thumb))
    return oc
    Log ('still no value for create season objects. Sending on to section function')
  else:
    return oc
#######################################################################################
# This function produces sections for each channel bases on the sections listed below Watch Video
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
  # This is for those shows that have sections listed below Watch Video
  for sections in data.xpath('//li[contains(@class,"-subItem")]/div/a'):
    sec_url = BASE_URL + sections.xpath('.//@href')[0]
    sec_title = sections.xpath('.//text()')[2].strip()
    oc.add(DirectoryObject(key=Callback(ShowVideos, title=sec_title, url=sec_url, season=season), title=sec_title, thumb=thumb))

  # For shows that do not have video section, we make sure they have videos and then produce one All Videos section
  if len(oc) < 1:
    section_nav = data.xpath('//ul[contains(@class,"section-nav")]//a//text()')
    if 'Watch Video' in section_nav:
      local_url = url.replace('series', 'video')
      oc.add(DirectoryObject(key=Callback(ShowVideos, title='All Videos', url=local_url, season=0), title='All Videos', thumb = thumb))
      return oc
    else:
      return ObjectContainer(header="Empty", message="This show has no videos.")
      Log ('still no value for video sections')
  else:
    return oc
#########################################################################################
# This will produce the videos playlist for videos with ids from url anchors on any each page on vh1
@route(PREFIX + '/specialsections')
def SpecialSections(title, url):
  oc = ObjectContainer(title2=title)
  # The Philly Jam Special does not have any way to pull ids so we have to hard coded the id for this special
  if 'phillyjam' in url:
    vid_id = '1709553'
    vid_url = PLAYLIST %vid_id
    oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title))
  else:
    # This seems to work better and give more results from the front page vs going to the video page
    section_list=[]
    data = HTML.ElementFromURL(url)
    try:
      thumb = data.xpath('//link[@rel="image_src"]//@href')[0]
    except:
      try:
        thumb = data.xpath('//meta[@property="og:image"]//@content')[0]
      except:
        thumb = R(ICON)
    for video in data.xpath('//a[contains(@href,"/video/") and contains(@href,"#id=")]'):
      vid_id = video.xpath('.//@href')[0].split('#id=')[1]
      if vid_id in section_list:
        continue
      playlist_url = PLAYLIST %vid_id
      # A second url pull is the only way to ensure we get the right title for the playlist
      html = HTML.ElementFromURL(playlist_url)
      # The playlist page for this could just be blank
      try:
        title = html.xpath('//h3/span//text()')[0]
        oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=playlist_url), title=title, thumb=thumb))
        section_list.append(vid_id)
      except:
        pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to list right now.")
  else:
    return oc
#################################################################################################################
# This function produces videos from the table layout used by show video pages
# This function picks up all videos in all pages even without paging code
@route(PREFIX + '/showvideos', season=int)
def ShowVideos(title, url, season):
  oc = ObjectContainer(title2=title)
  if 'series.jhtml' in url:
    local_url = url.replace('series', 'video')
  else:
    local_url = url
  data = HTML.ElementFromURL(local_url)
  for video in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
    # If the link does not have a mainuri, it will not play through the channel with the url service, so added a check for that here
    title = video.xpath('.//@maintitle')[0]
    episode = video.xpath('.//li[@class="list-ep"]//text()')[0]
    seas_ep = SeasEpFind(episode, title, season)
    episode = int(seas_ep[0])
    new_season = int(seas_ep[1])
    thumb = video.xpath('./meta[@itemprop="thumbnail"]//@content')[0].split('?')[0]
    if not thumb:
      thumb = video.xpath('.//li[contains(@id,"img")]/img//@src')[0]
    if not thumb.startswith('http:'):
      thumb = BASE_URL + thumb
    vid_url = BASE_URL + video.xpath('.//@mainurl')[0]
    desc = video.xpath('.//@maincontent')[0]
    date = video.xpath('.//@mainposted')[0]
    if 'hrs ago' in date:
      date = Datetime.Now()
    else:
      date = Datetime.ParseDate(date)

    # HERE WE CHECK TO SEE IF THE VIDEO IS A VIDEO CLIP PLAYLIST THAT NEEDS TO HAVE THE PARTS PRODUCED
    # THIS IS USED TO PROCESS SPECIALS BUT IN VH1, ALL VIDEO CLIPS ARE PLAYLIST WITH THE URL IN THE FORMAT OF "/video/play.jhtml?id=1706039" 
    # ALMOST ALL BONUS CLIPS, SHOW CLIPS, ETC LISTED FOR EACH SHOW ON VH1 CONTAIN MULTIPLE VIDEOS
    if '?id=' in vid_url:
      vid_id = vid_url.split('?id=')[1]
      vid_url = PLAYLIST %vid_id
      # send to videopage function
      oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb))
    else:
      oc.add(EpisodeObject(
        url = vid_url, 
        season = new_season,
        index = episode,
        title = title, 
        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON)),
        originally_available_at = date,
        summary = desc
      ))

  # The site currently orders the videos by most recent but may need to use it later
  #oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)
  if len(oc) < 1:
    Log ('no value for objects')
    # Found some old VH1 shows that use an old table setup so added a pull for that here
    try:
      for video in data.xpath('//table[@class="video-list"]/tr'):
        try:
          url = video.xpath('./td[@class="r-title"]/a//@href')[0]
        except:
          continue
        if not url.startswith('http://'):
          url = BASE_URL + url
        try:
          episode = int(video.xpath('./td[@class="r-ep"]//text()')[0])
        except:
          episode = 0
        title = video.xpath('./td[@class="r-title"]/a//text()')[0]
        date = Datetime.ParseDate(video.xpath('./td[@class="r-date"]//text()')[0])
        oc.add(EpisodeObject(url = url, season = season, index = episode, title = title, originally_available_at = date))
    except:
      pass
  
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to list right now.")
  else:
    return oc
####################################################################################################
# This produces videos for most popular as well for video playlist broken down with the Playlist URL
# THIS FUNCTION DOES SEEM TO TAKE LONGER TO PROCESS THE VIDEOS. MRSS COULD BE USED FOR PLAYLIST BUT NOT FOR MOST POPULAR
@route(PREFIX + '/videopage')
def VideoPage(url, title):
  oc = ObjectContainer(title2=title)
  # THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(url)
  for item in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
    link = BASE_URL + item.xpath('.//a[@itemprop="url"]//@href')[0]
    try:
      image = item.xpath('.//img[@itemprop="thumbnail"]//@src')[0]
    # When there isn't an image, they provide a default image
    except:
      image = BASE_URL + item.xpath('.//img//@src')[0]
    try:
      video_title = item.xpath('.//img[@itemprop="thumbnail"]//@alt')[0]
    except:
      video_title = item.xpath('.//a//text()')[0].strip()
    try:
      # The VH1 most popular pulls have the show and/or the episode title in two different locations
      # and sometimes have new lines in the middle of them so need to strip that away here
      title = item.xpath('./p[@class="deck"]//text()')[0].strip()
      title = title.replace('\n', '')
      video_title = '%s  %s' %(title,video_title)
    except:
      pass
    # here we want to see if there is an episode and season info for the video
    seas_ep = SeasEpFind(episode='--', other_info=video_title, season=0)
    episode = int(seas_ep[0])
    season = int(seas_ep[1])
    try:
      date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
    except:
      date = ''
    if 'hrs ago' in date:
      date = Datetime.Now()
    else:
      date = Datetime.ParseDate(date)

    # HERE WE CHECK TO SEE IF THE VIDEO IS A VIDEO CLIP PLAYLIST THAT NEEDS TO HAVE THE PARTS PRODUCED
    if '?id=' in link:
      vid_id = link.split('?id=')[1]
      vid_url = PLAYLIST %vid_id
      # send to videopage function
      oc.add(DirectoryObject(key=Callback(VideoPage, title=video_title, url=vid_url), title=video_title, thumb=image))
    else:
      if episode > 0:
        oc.add(EpisodeObject(url=link, title=video_title, season=season, index=episode, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))
      else:
        oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))

  if len(oc)==0:
    return ObjectContainer(header="Sorry!", message="No video available in this category.")
  else:
    return oc
###########################################################################################
# This function is used to pull the season and episodes for shows 
# In VH1, these seem to always have an episode number but occasionally have the word Episode in the title
@route(PREFIX + '/seasepfind')
def SeasEpFind(episode, other_info, season):

  #Log('the value of other_info is %s' %other_info)
  try:
    test_ep = int(episode)
  except:
    try:
      episode = RE_EPISODE.search(other_info).group(2)
    except:
      episode = '0'
  if season==0:
    if len(episode) > 2:
      new_season = episode[0]
    else:
      try:
        new_season = RE_SEASON.search(other_info).group(2)
      except:
        new_season = '1'
  else:
    new_season = season
    
  seas_ep=[episode, new_season]
  #Log('the value of seas_ep is %s' %seas_ep)
  return seas_ep
