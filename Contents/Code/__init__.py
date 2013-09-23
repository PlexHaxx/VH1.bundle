# NEED TO SEE IF WE CAN CUT DOWN SPECIALS SECTION AND EPISODE AND SEASON FIND
# at least tough love is not separating full episodes and clips
TITLE = 'VH1'
PREFIX = '/video/vh1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.vh1.com'
VIDEO = 'http://www.vh1.com/video/'
VH1_MENU = 'http://www.vh1.com/sitewide/navigation/menubar_new.jhtml'
VH1_ALLMENU = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'
SEARCH_URL = 'http://www.vh1.com/search/video/'
# Variables below uses the base url and either %20Full%20Episodes  or %20Bonus%20Clips but %s will not work with '-' in url so have to split into two
POPULAR_AJAX_PART1 = '/global/music/modules/mostPopular/module.jhtml?category=Videos%20-%20TV%20Show%20Videos%20-%20'
POPULAR_AJAX_PART2 = '&contentType=videos&howManyChartItems=25&fluxSort=numberOfViews:today:desc'
MTV_PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id=%s'

RE_SEASON  = Regex('.+Season (\d{1,2}).+')
RE_SEASON_ALSO  = Regex('.+Seas. (\d{1,2}).+')
RE_EPISODE  = Regex('.+Ep. (\d{1,3})')
RE_EPISODE_ALSO  = Regex('.+Episode (\d{1,3})')
####################################################################################################
# Set up containers for all possible objects
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  #EpisodeObject.thumb = R(ICON)
  #EpisodeObject.art = R(ART)
  #VideoClipObject.thumb = R(ICON)
  #VideoClipObject.art = R(ART)

  #HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(ShowMain, title='VH1 Shows'), title='VH1 Shows')) 
  oc.add(DirectoryObject(key=Callback(VideoMain, title='VH1 Videos'), title='VH1 Videos')) 
  #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
  oc.add(InputDirectoryObject(key=Callback(SearchVideos, title='Search VH1 Videos'), title='Search VH1 Videos', summary="Click here to search videos", prompt="Search for the videos you would like to find"))
  return oc
#####################################################################################
# This is the submenu for all vh1 videos
@route(PREFIX + '/showmain')
def ShowMain():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(ProduceShows, title='VH1 Shows', sort_type='shows'), title='VH1 Shows')) 
  oc.add(DirectoryObject(key=Callback(ProduceShows, title='VH1 Specials', sort_type='specials'), title='VH1 Specials')) 
  oc.add(DirectoryObject(key=Callback(Alphabet, title='VH1 Shows A to Z'), title='VH1 Shows A to Z')) 
  return oc
####################################################################################################
# This is the submenu for all vh1 videos
@route(PREFIX + '/videomain')
def VideoMain(title):
  oc = ObjectContainer()
  vid_type = ["episodes", "shows", "music", "news"]
  oc.add(DirectoryObject(key=Callback(VideoCarousel, title='Full Episodes', vid_type=vid_type[0]), title='Full Episodes'))
  oc.add(DirectoryObject(key=Callback(VideoCarousel, title='Sneak Peeks, Show Clips & Extras', vid_type=vid_type[1]), title='Sneak Peeks, Show Clips & Extras'))
  oc.add(DirectoryObject(key=Callback(VideoCarousel, title='VH1 News', vid_type=vid_type[3]), title='VH1 News'))
  oc.add(DirectoryObject(key=Callback(MostPopular, title='Most Popular Videos'), title='VH1 Most Popular Videos')) 
  return oc
####################################################################################################
# This handles most popular from the ajax 
# ARE THERE AFTERSHOWS FOR VH1???
@route(PREFIX + '/mostpopular')
def MostPopular(title):
    oc = ObjectContainer(title2=title)
    pop_type = ["Full%20Episodes", "After%20Shows", "Bonus%20Clips"]
    url = BASE_URL + POPULAR_AJAX_PART1
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Most Popular Full Episodes", url=url + pop_type[0] + POPULAR_AJAX_PART2), title="Most Popular Full Episodes"))
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Most Popular Show Clips", url=url + pop_type[2] + POPULAR_AJAX_PART2), title="Most Popular Show Clips"))
    return oc
#####################################################################################
# For Producing All Shows 
@route(PREFIX + '/produceshows')
def ProduceShows(title, sort_type):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(VH1_MENU)

  for video in data.xpath('//ul[@class="submenu"]/li/ul/li/a'):
    url = video.xpath('.//@href')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    title = video.xpath('.//text()')[0]
    # THE GETTHUMB FUNCTION PRODUCES IMAGES BUT SLOW DOWN PULL SO IN THIS VERSION 
    # USED THE OPTION OF ADDING THEM AS CALLBACKS TO DIRECTORYOBJECTS PER MIKE'S SUGGESTION

    if sort_type=='shows':
      if 'series.jhtml' in url and 'super_bowl' not in url:
      # Would prefer to use a content check for Other Seasons since some shows do not have /season in url but it slows down the pull
        if '/season_' in url:
          oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url), title=title, thumb=Callback(GetThumb, url=url)))
        elif 'pop_up_video' in url:
        # POP UP VIDEOS PRODUCING ERROR
          oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title=title, thumb=Callback(GetThumb, url=url)))
        else:
          oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=R(ICON), url=url, season=1), title=title, thumb=Callback(GetThumb, url=url)))
      else:
        pass

    else:
      if '/events/' in url or  'super_bowl' in url:
        if 'do_something' in url:
          video_url = url + 'video_photos.jhtml'
        elif 'series.jhtml' in url:
          video_url = url.replace('series.jhtml', 'video.jhtml')
        else:
          video_url = url + 'videos.jhtml'
        oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=video_url), title = title, thumb=Callback(GetThumb, url=video_url)))
      else:
        pass

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
    for ch in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        oc.add(DirectoryObject(key=Callback(VH1AllShows, ch=ch), title=ch))
    return oc
#####################################################################################
# This pulls from the VH1 archive All shows section and works for A-Z sorts of VH1 Shows
# THERE ARE LISTINGS FOR AWARDS SHOWS THAT NO LONGER HAVE SITES. 2010 HIP HOP HONORS AND 17TH ANNUAL CRITIC CHOICE AWARDS HAVE SITES, BUT LINKS ARE INCORRECT
@route(PREFIX + '/vh1allshows')
def VH1AllShows(ch):
  oc = ObjectContainer(title2=ch)
  local_url = VH1_ALLMENU + '?chars=' + ch
  #THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1DAY)
  for video in data.xpath('//div[@id="azshows"]/div/div/div[contains(@style,"float")]/div'):
    url = video.xpath('./a//@href')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    title = video.xpath('./a//text()')[0]
    # THE GETTHUMB FUNCTION PRODUCES IMAGES BUT SLOW DOWN PULL SO IN THIS VERSION 
    # USED OPTION OF ADDING THEM AS CALLBACKS TO DIRECTORYOBJECTS PER MIKE'S SUGGESTION 
    thumb = R(ICON)
    if 'series.jhtml' in url and 'awards' not in url and '/divas/' not in url and '/festivals/' not in url and 'critics_choice' not in url and 'hip_hop_honors' not in url:
      # Here the shows are listed by individual seasons but still need to send to ShowCreateSeason if _season not in url. Specials here still have series.jhtml on them
      if '/season_' in url:
        season = url.split('/season_')[1]
        season = season.split('/')[0]
        oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=url, season=int(season)), title = title, thumb = Callback(GetThumb, url=url)))
      else:
        oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=url, season=1), title = title, thumb = Callback(GetThumb, url=url)))
    else:
      oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title = title, thumb=Callback(GetThumb, url=url)))

  oc.objects.sort(key = lambda obj: obj.title)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no shows to list right now.")
  else:
    return oc
#######################################################################################
# This section handles seasons that have a different url for each season
@route(PREFIX + '/showseasons')
def ShowSeasons(title, url):

  oc = ObjectContainer(title2=title)
  local_url = url.replace('series', 'seasons')
  if not local_url.startswith('http://'):
    local_url = BASE_URL + local_url
  #THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url, cacheTime=CACHE_1DAY)
  for video in data.xpath('//div[1]/ol/li/div[contains(@class,"title")]/a'):
    url = video.xpath('.//@href')[0]
    url = BASE_URL + url
    if '/season_' in url:
      season = url.split('season_')[1]
      season = int(season.replace('/series.jhtml', ''))
    else:
      season = 1
    title = video.xpath('./img//@alt')[0]
    #if '&rsaquo;' in title:
      #title = title.replace('&rsaquo;', '')
    # WOULD LIKE TO ADD A SEASON NUMBERS TO THE TITLE THAT DO NOT HAVE A NUMBER HERE. Redneck Vacation is one
    #if 'Season' not in url and 'rwrr_challenge/' not in url and 'real_world/' not in url:
      #title = title + ' Season ' + season
    thumb = video.xpath('./img//@src')[0]
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb

    oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=url, season=int(season)), title = title, thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

  #oc.objects.sort(key = lambda obj: obj.title, reverse=True)
  if len(oc) < 1:
    Log ('still no value for season objects')
    return ObjectContainer(header="Empty", message="There are no seasons to list right now.")
  else:
    return oc
#######################################################################################
# This section handles specials that do not have a traditional show structure. We use ID numbers to produce sections for these specials
# then use those IDS with the MTV_PLAYLIST to get the playlist
# ALL SHOWS THAT ARE PRODUCED ARE WORKING NOW, BUT COULD LOOK AT ADDING VH1 STORYTELLERS AND MTV UNPLUGGED AND CTITICS TV AWARDS
@route(PREFIX + '/specialsections')
def SpecialSections(title, url):

  oc = ObjectContainer(title2=title)
  # The Philly Jam Special does not have any way to pull ids so we have to hard coded the id for this special
  if 'phillyjam' in url:
    section_list = ['1709553']
  else:
    section_list = GetIds(url)
    # Check to see if multiple pages here
    # VH1 DIVAS HAVE MULTIPLE PAGES
    pagination = Pagination(url)
    while pagination:
      #send next page url to get ids
      page_list = GetIds(pagination)
      #append section list to include any ids on that page
      section_list = section_list + page_list
      #see if there is a url for next page 
      pagination = Pagination(pagination)

  # Since this is just pulling thumb for one show, it should not slow down function
  thumb = Callback(GetThumb, url=url)
  for ids in section_list:
    #it appears that is a little faster to pull the title from the Playlist than the MRSS and allows use of viedopage function for results
    # THIS DATA PULL IS ALSO USED BY THE SPECIAL VIDEOS FUNCTION
    id_url = MTV_PLAYLIST %ids
    data = HTML.ElementFromURL(id_url)
    try:
      title = data.xpath('//h3/span/text()')[0]
      oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=id_url), title=title, thumb=thumb))
    except:
      pass

  #oc.objects.sort(key = lambda obj: obj.title)
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no special videos to list right now.")
  else:
    return oc
#######################################################################################
# This function produces sections for each channel. 
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season):
  oc = ObjectContainer(title2=title)
  #first see if there are any videos for this show 
  url = url.replace('series', 'video')
  data = HTML.ElementFromURL(url)
  sections = data.xpath('//ul[@class=" section-nav"]/li/div/a//text()')
  Log('the value of sections is %s' %sections)
  if 'Watch Video' in sections:
    if '/season_' not in url:
      # add thumb for those without seasons
      try:
        thumb = data.xpath('//ol[contains(@class, "photo-alt")]/li/div/a/img//@src')[0]
        if not thumb.startswith('http://'):
          thumb = BASE_URL + thumb
      except:
        pass
    else:
      pass
    if 'Full Episodes' in sections:
      oc.add(DirectoryObject(key=Callback(ShowVideos, title='Full Episodes', section_id='fulleps', url=url, season=season), title='Full Episodes', thumb=thumb))
    if 'Show Clips' in sections:
      oc.add(DirectoryObject(key=Callback(ShowVideos, title='Show Clips', section_id='showclips', url=url, season=season), title='Show Clips', thumb=thumb))
    oc.add(DirectoryObject(key=Callback(ShowVideos, title='All Videos', section_id='', url=url, season=season), title='All Videos', thumb=thumb))
  else:
    pass

  if len(oc) < 1:
    Log ('still no value for video objects')
    return ObjectContainer(header="Empty", message="There are no videos available for this show right now.")
  else:
    return oc
#################################################################################################################
# This function produces videos from the table layout used by show video pages for all three networks
# This function picks up all videos in all pages even without paging code
@route(PREFIX + '/showvideos', season=int)
def ShowVideos(title, section_id, url, season):
  oc = ObjectContainer(title2=title)
  if section_id:
    local_url = url + '?filter=' + section_id
  else:
    local_url = url
  # NOT SURE IF THIS PULL IS THE SAME SINCE FILTER ON END BUT SIMILAR TO CREATE SEASON FUNCTION FOR MISC VIDEO 
  data = HTML.ElementFromURL(local_url)
  for video in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
    other_info = video.xpath('.//@maintitle')[0]
    episode = video.xpath('./ul/li[@class="list-ep"]//text()')[0]
    if episode == '--' or episode == 'Special':
      episode = 0
      all_season = 0
    else:
      if len(episode) > 2:
        all_season = int(episode[0])
      else:
        all_season = 0
      episode = int(episode)
    title = video.xpath('./meta[@itemprop="name"]//@content')[0]
    if not title:
      title = other_info
    thumb = video.xpath('./meta[@itemprop="thumbnail"]//@content')[0].split('?')[0]
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb
    vid_url = video.xpath('./meta[@itemprop="url"]//@content')[0]
    if not vid_url.startswith('http://'):
      vid_url = BASE_URL + vid_url
    desc = video.xpath('./meta[@itemprop="description"]//@content')[0]
    date = video.xpath('./ul/li[@class="list-date"]//text()')[0]
    if 'hrs ago' in date:
      try:
        date = Datetime.Now()
      except:
        date = ''
    else:
      date = Datetime.ParseDate(date)

    oc.add(EpisodeObject(
      url = vid_url, 
      season = all_season,
      index = episode,
      title = title, 
      thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
      originally_available_at = date,
      summary = desc
    ))
  #oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  if len(oc) < 1:
    Log ('no value for objects')
    # Found some old VH1 shows that use an old table setup so added a pull for that here
    try:
      for video in data.xpath('//tr[@class="row"]'):
      #for video in data.xpath('//tr'):
        url = video.xpath('./td[@class="r-title"]/a//@href')[0]
        if not url.startswith('http://'):
          url = BASE_URL + url
        episode = int(video.xpath('./td[@class="r-ep"]//text()')[0])
        title = video.xpath('./td[@class="r-title"]/a//text()')[0]
        date = Datetime.ParseDate(video.xpath('./td[@class="r-date"]//text()')[0])
        oc.add(EpisodeObject(url = url, season = season, index = episode, title = title, originally_available_at = date))
    except:
      pass
  
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no %s videos to list right now." %section_id)
  else:
    return oc
#########################################################################################
# This function is for searches
@route(PREFIX + '/searchvideos')
def SearchVideos(title, query='', page_url=''):
  oc = ObjectContainer(title2=title)
  if query:
    local_url = SEARCH_URL + '?q=' + String.Quote(query, usePlus = False)  + '&page=1'
  else:
    local_url = SEARCH_URL + page_url
  data = HTML.ElementFromURL(local_url)
  for item in data.xpath('//ul/li[contains(@class,"mtvn-video ")]'):
    link = item.xpath('./div/a//@href')[0]
    if not link.startswith('http://'):
      link = BASE_URL + link
    image = item.xpath('./div/a/span/img//@src')[0]
    if not image.startswith('http://'):
      image = BASE_URL + image
    try:
      video_title = item.xpath('./div/a/text()')[2].strip()
    except:
      video_title = item.xpath('./div/div/a/text()')[0]
    if not video_title:
      try:
        video_title = item.xpath('./div/a/span/span/text()')[0]
        video_title2 = item.xpath('./div/a/span/em/text()')[0]
        video_title = video_title + ' ' + video_title2
      except:
        video_title = ''
    try:
      date = item.xpath('./p/span/em//text()')[0]
      if date.startswith('Music'):
        date = item.xpath('./p/span/em//text()')[1]
    except:
      date = ''
    if 'hrs ago' in date:
      try:
        date = Datetime.Now()
      except:
        date = ''
    else:
      date = Datetime.ParseDate(date)

    oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))
  # This goes through all the pages of a search
  # After first page, the Prev and Next have the same page_url, so have to check for
  try:
    page_type = data.xpath('//a[contains(@class,"pagination")]//text()')
    x = len(page_type)-1
    if 'Next' in page_type[x]:
      page_url = data.xpath('//a[contains(@class,"pagination")]//@href')[x]
      oc.add(NextPageObject(
        key = Callback(SearchVideos, title = title, page_url = page_url), 
        title = L("Next Page ...")))
    else:
      pass
  except:
    pass

  #oc.objects.sort(key = lambda obj: obj.index, reverse=True)

  if len(oc)==0:
    return ObjectContainer(header="Sorry!", message="No video available in this category.")
  else:
    return oc
####################################################################################################
# This produces videos for most popular for vh1 and for specials
# This function works with the ajax and global module pages
@route(PREFIX + '/videopage', page=int)
def VideoPage(url, title, page=1):
  oc = ObjectContainer(title2=title)
  if '?' in url:
    local_url = url + '&page=' + str(page)
  else:
    local_url = url + '?page=' + str(page)
  # THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url)
  for item in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
    link = item.xpath('./div/a//@href')[0]
    if not link.startswith('http://'):
      link = BASE_URL + link
    image = item.xpath('./div/a/img//@src')[0]
    if not image.startswith('http://'):
      image = BASE_URL + image
    if '70x53' in image:
      image = image.replace('70x53', '140x105.jpg')
    video_title = item.xpath('./div/meta[@itemprop="name"]//@content')[0].strip()
    video_title = video_title.replace('\n', '')
    try:
      # The VH1 most popular pulls have the name of the show and the episode in two different locations
      # and have lots of spaces and new lines in the middle of them so need to strip that away here
      title = item.xpath('./p[@class="deck"]//text()')[0].strip()
      title = title.replace('  ', '')
      title = title.replace('\n', '')
      video_title = title + ' ' + video_title
    except:
      pass
    if video_title == None or len(video_title) == 0:
      video_title = item.xpath('div/a/img')[-1].get('alt')
    try:
      date = item.xpath('./p/span/time[@itemprop="datePublished"]//text()')[0]
    except:
      date = ''
    if 'hrs ago' in date:
      try:
        date = Datetime.Now()
      except:
        date = ''
    else:
      date = Datetime.ParseDate(date)

    oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))

  #oc.objects.sort(key = lambda obj: obj.index, reverse=True)

  if len(oc)==0:
    return ObjectContainer(header="Sorry!", message="No video available in this category.")
  else:
    return oc
#################################################################################################################
# This function creates a list of the unique ids for specials pages
@route(PREFIX + '/getids')
def GetIds(url):

  section_list = []
  data = HTML.ElementFromURL(url)
  # The best place to get the ids are from the uri for the links so we check for that first
  for ids in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
    try:
      # This below handles series like vh1 super bowl that do not have a mainuri
      id_num = ids.xpath('.//@mainurl')[0]
    except:
      # This below handles vh1 divas and do somethign awards and need #id= off end
      id_num = ids.xpath('./div/a//@href')[0]
    if 'id=' in id_num:
      id_num = id_num.split('id=')[1]
    else:
      pass
    # make sure it is a 7 digit number could even add int check
    if len(id_num) == 7:
      if id_num not in section_list:
        section_list.append(id_num)
    else:
      pass
  return section_list
#################################################################################################################
# This function checks to see if there are multiple pages and produces the url for the next page
@route(PREFIX + '/pagination')
def Pagination(url):

  data = HTML.ElementFromURL(url)
  try:
    page_url = data.xpath('//div[@class="pagintation"]/a[@class="page-next"]//@href')[0]
    page_url = BASE_URL + page_url
  except:
    page_url = ''
  return page_url

#############################################################################################################################
# This is a function to pull the thumb image from a page. 
# We first try the top of the page if it isn't there, we can pull an image from the video page side block
@route(PREFIX + '/gethumb')
def GetThumb(url):
  # NEED TO BE AWARE OF OTHER PULLS TO THIS URL AND MAKE SURE THEY ARE ALL THE SAME CACHE
  if 'series.jhtml' in url and 'pop_up_video' not in url:
    local_url = url.replace('series', 'video')
  else:
    local_url = url
  try:
    page = HTML.ElementFromURL(local_url)
  except:
    thumb = None
    pass
  try:
    thumb = page.xpath('//ol[contains(@class, "photo-alt")]/li/div/a/img//@src')[0].split('?')[0]
  except:
    try:
      thumb = page.xpath("//head//meta[@property='og:image']//@content")[0].split('?')[0]
    except:
      thumb = None
  if thumb:
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb
    return Redirect(thumb)
  else:
    return Redirect(R(ICON))
#########################################################################################
# This will produce the carousels for vh1 video page the choices for videos are episodes, shows, music and news
# Teh music section has a different setup and since this is for shows, not using it
# THE MAIN SHOW PAGE CAROUSELS HAVE A COMPLETELY DIFFERENT SETUP, MOSTLY INCLUDE BLOGS, AND ARE AVAILABLE ELSEWHERE THEREFORE THEY WILL NOT BE USED
@route(PREFIX + '/videocarousel')
def VideoCarousel(title, vid_type):
  oc = ObjectContainer(title2=title)
  # for shows there is no id and there is a space after carouselItem
  #THIS DATA PULL IS UNIQUE
  data = HTML.ElementFromURL(VIDEO)
  for video in data.xpath('//div[@id="%s-carousel"]/div/ol/li[contains(@class,"carouselItem")]' %vid_type):
    vid_url = video.xpath('./div/a//@href')[0]
    if not vid_url.startswith('http://'):
      vid_url = BASE_URL + vid_url
    title = video.xpath('./div/a/div/div[@class="long"]//text()')[0]
    thumb = video.xpath('./div/span/a/img//@src')[0].split('?')[0]
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb
    date = Datetime.ParseDate(video.xpath('./div/i//text()')[0].split()[1])
    oc.add(VideoClipObject(
      url = vid_url, 
      title = title, 
      thumb = thumb,
      originally_available_at=date
      ))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to list right now.")
  else:
    return oc
#########################################################################################
# This will produce the videos listed in the top image block for each page on vh1
@route(PREFIX + '/producemarquee')
def ProduceMarquee(title, url, show_type):
  oc = ObjectContainer(title2=title)
  #THIS DATA PULL WILL MOST LIKELY NEVER BE UNIQUE AND ALWAYS BE USED ELSEWHERE
  data = HTML.ElementFromURL(url)
  for video in data.xpath('//ul/li[@class="marquee_images"]'):
    id = video.xpath('.//@id')[0]
    vid_url = video.xpath('./div/a//@href')[0]
    if not vid_url.startswith('http://'):
      vid_url = BASE_URL + vid_url
    thumb = video.xpath('./div/a/img//@src')[0].split('?')[0]
    #if not thumb.startswith('http://'):
      #thumb = BASE_URL + thumb
    title = video.xpath('./div/a/img//@alt')[0]
    # Here we use the id from above to directly access the more detailed hidden title
    summary = data.xpath('//div[@class="marquee_bg"]/div[contains(@id,"%s"]/p//text()' &id)[0]
    oc.add(VideoClipObject(
      url = vid_url, 
      title = title, 
      thumb = thumb,
      summary = summary
      ))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to list right now.")
  else:
    return oc
