# VIDEO CLIP FOR BONUS CLIP OR SNEEK PEEK HAVE MULTIPLE PARTS

TITLE = 'VH1'
PREFIX = '/video/vh1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.vh1.com'
VH1_MENU = 'http://www.vh1.com/sitewide/navigation/menubar_new.jhtml'
VH1_ALLMENU = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'
SEARCH_URL = 'http://www.vh1.com/search/'
SERIES_VIDEOS = 'http://www.vh1.com/global/music/modules/video/shows/?seriesID=%s'
PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id='
# The two variables below uses the base url and either %20Full%20Episodes  or %20Bonus%20Clips but %s will not work with '-' in url so have to split into two
POPULAR_AJAX_PART1 = '/global/music/modules/mostPopular/module.jhtml?category=Videos%20-%20TV%20Show%20Videos%20-%20'
POPULAR_AJAX_PART2 = '&contentType=videos&howManyChartItems=25&fluxSort=numberOfViews:today:desc&displayPostedDate=true'

# THIS IS A LISTING FOR AWARDS SHOWS OR SPECIALS ON THE ALL SHOWS PAGE THAT WE WANT TO PRODUCE VIDEOS FOR BUT 
# BECAUSE THEY HAVE ENDED EVERY LINK WITH SERIES.JHTML INSTEAD OF CORRECT URL FOR A SPECIAL (/EVENT/) WE HAVE TO CHECK FOR THEM AND PULL THEM OUT
SPECIAL_LIST = ["Do Something Awards 2013", "VH1 Divas 2012", "Critics' Choice Television Awards (2011)", "The Best Super Bowl Concert Ever",
                "VH1 Super Bowl Blitz"]
# THIS IS A LISTOF ANY SHOWS OR SPECIALS IN THE ALL SHOWS PAGE THAT GIVE AN ERROR
BAD_ARCHIVE_LIST = ["VH1 Classic Main Format", "VH1 Classic", "ANOTHER SHOW"]

RE_SERIES_ID = Regex("var seriesID = '(\d+)';")
RE_SEASON  = Regex('.+(Season|Seas.) (\d{1,2}).+')
RE_EPISODE  = Regex('.+(Episode|Ep.) (\d{1,3})')
RE_VIDID = Regex('(\d{7})')
####################################################################################################
# Set up containers for all possible objects
def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ShowMain, title='VH1 Shows'), title='VH1 Shows')) 
    oc.add(DirectoryObject(key=Callback(ProduceCarousels, title='VH1 Videos', url=BASE_URL+'/video/'), title='VH1 Videos')) 
    #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.vh1", title=L("Search VH1 Videos"), prompt=L("Search for Videos")))
    return oc
#####################################################################################
@route(PREFIX + '/showmain')
def ShowMain(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(ProduceCarousels, title='VH1 Current Shows', url=BASE_URL+'/shows/'), title='VH1 Current Shows')) 
    oc.add(DirectoryObject(key=Callback(ProduceShows, title='VH1 Poplular Shows'), title='VH1 Popular Shows'))  
    oc.add(DirectoryObject(key=Callback(Alphabet, title='VH1 Shows A to Z'), title='VH1 Shows A to Z')) 
    oc.add(InputDirectoryObject(key=Callback(ShowSearch), title='Search for VH1 Shows', summary="Click here to search for shows", prompt="Search for the shows you would like to find"))
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
            oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=link), title = title))
    return oc

#####################################################################################
# For Producing Section titles for the Video and Shows page
@route(PREFIX + '/producecarousels')
def ProduceCarousels(title, url):
    oc = ObjectContainer(title2=title)
    # THIS DATA PULL IS USED BY THE MOREVIDEOS FUNCTION
    local_url = url
    data = HTML.ElementFromURL(local_url)
    for video in data.xpath('//div[contains(@class, "mdl-carousel animate")]'):
        try: show_type = video.xpath('./@id')[0]
        except: show_type = None
        # The video page does not have links but the show pages does
        if not show_type:
            title = video.xpath('.//h2/span/a/text()')[0]
            url = video.xpath('.//h2/span/a/@href')[0]
            if not url.startswith('http://'):
                url = BASE_URL + url
            oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url), title=title))
        else:
            title = video.xpath('.//h2/span//text()')[0]
            oc.add(DirectoryObject(key=Callback(MoreVideos, title=title, url=local_url, show_type=show_type), title = title))
      
    # We add the Most Popular Videos to the end of the directory for Videos
    if local_url.endswith('video/'):
        oc.add(DirectoryObject(key=Callback(MostPopular, title='Most Popular Videos'), title='VH1 Most Popular Videos')) 

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
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
#########################################################################################
# This will produce the items in the carousel sections for the video page
@route(PREFIX + '/morevideos')
def MoreVideos(title, url, show_type):
    oc = ObjectContainer(title2=title)
    show_title=title
    # THIS DATA PULL IS UESED TWICE ONCE TO GET SECTIONS AND ONCE TO GET VIDEOS IN EACH SECTION
    data = HTML.ElementFromURL(url)
    for video in data.xpath('//div[@id="%s"]//li[@class="carouselItem "]' %show_type):
        vid_url = video.xpath('.//a/@href')[0]
        if not vid_url.startswith('http://'):
            vid_url = BASE_URL + vid_url
        title = video.xpath('.//div[@class="long"]//text()')[0]
        try: date = Datetime.ParseDate(video.xpath('.//i[@class="date"]//text()')[0].split('Posted ')[1])
        except: date = None
        thumb = video.xpath('.//img/@src')[0].split('?')[0]
        if not thumb.startswith('http://'):
            thumb = BASE_URL + thumb
      
        if 'Show Clips' in show_title:
            vid_id = RE_VIDID.search(vid_url).group(1)
            vid_url = PLAYLIST + vid_id
            # send to videopage function
            oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb))
        else:
            oc.add(VideoClipObject(url = vid_url, title = title, originally_available_at = date, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
#####################################################################################
# For Producing Popular Shows 
@route(PREFIX + '/produceshows')
def ProduceShows(title):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(VH1_MENU, cacheTime = CACHE_1HOUR)

  for video in data.xpath('//*[text()="VH1 Shows"]/parent::li//a'):
    url = video.xpath('.//@href')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    title = video.xpath('.//text()')[0]
    if url.endswith('series.jhtml'):
      if 'shows/pop_up_video/' in url:
        oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))
      else:
        oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url), title=title))
    elif '/celebrity/' in url:
      oc.add(DirectoryObject(key=Callback(BlogPlayer, title=title, url=url), title = title))
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
    for ch in list('#ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        url=VH1_ALLMENU
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
    if title=='#':
        title='no'
    for video in data.xpath('//div[@id="shows-%s"]/div[@class="col"]/a' %title.lower()):
        url = video.xpath('.//@href')[0]
        title = video.xpath('.//text()')[0].strip()
        if title in BAD_ARCHIVE_LIST:
            continue
        if not url.startswith('http://'):
            url = BASE_URL + url
        # The all shows section put series.jhtml on the end of all links including specials so the URL is incorrect for them
        if title not in SPECIAL_LIST and url.endswith('series.jhtml'):
            if 'shows/pop_up_video/' in url:
                oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))
            else:
                if '/season_' in url:
                    season = url.split('/season_')[1]
                    season = int(season.split('/')[0])
                else:
                    season=1
                vid_url = url.replace('series', 'video')
                oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=vid_url + '?filter=', thumb=R(ICON), season=int(season), show_url=vid_url), title = title))
        else:
           #Need to pre-code "Super Bowl" and send to JSON function
            if "The Best Super Bowl Concert Ever" in title or "VH1 Super Bowl Blitz" in title:
                url = 'http://www.vh1.com/events/super_bowl_blitz/includes/leap2/dataSources/instantReplay/instant-replay.jhtml?format=application/json'
                oc.add(DirectoryObject(key=Callback(SpecialJSON, title=title, url=url), title = title))
            # All the rest go to the VideoPage() function but some have adjustments
            else:             
                #Need to pre-code "Philly 4th of July Jam"
                if "Philly 4th Of July Jam" in title:
                    url = PLAYLIST + '1709553'
                 # All other Critics' Choice Movie Awards are either 404 errors or go to a series page
                else:
                    if "Critics' Choice Movie Awards" in title:
                        title = "17th Annual Critics' Choice Movie Awards"
                    #Need to get the proper url for the videos for the rest since it puts series on the end and we need the video page
                    url = SpecialFix(url)
                oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no shows to list right now.")
    else:
        return oc
#######################################################################################
# This function produces seasons for each show based on the format
@route(PREFIX + '/showseasons', season=int)
def ShowSeasons(title, url):
    oc = ObjectContainer(title2=title)
    local_url = url.replace('series', 'video')
    content = HTTP.Request(local_url).content
    data = HTML.ElementFromString(content)
    thumb = data.xpath('//a[@href="series.jhtml"]/img/@src')[0]
    series_id = RE_SERIES_ID.search(content).group(1)
    section_nav = data.xpath('//ul[contains(@class,"section-nav")]/li[not(contains(@class,"subItem"))]//a//text()')
    # Make sure the show has videos
    if 'Watch Video' in section_nav:
        # Check for season
        season_list = data.xpath('//*[@id="videolist_id"]/option')
        if len(season_list)> 0:
            for season in season_list:
                season_title = season.xpath('.//text()')[0]
                season_url = BASE_URL + season.xpath('./@value')[0]
                season = season_title.split('Season ')[1]
                oc.add(DirectoryObject(key=Callback(ShowSections, title=season_title, url=season_url, season=season, thumb=thumb, show_url=local_url), title=season_title, thumb=thumb))
        else:
            # These could manually be broken up by season but you risk losing some videos that may not have the Season listed in the title 
            # We set the season to zero so that each season will be picked up properly
            # The SERIES_VIDEOS does not work on mtv but it does here on VH1
            season_url = SERIES_VIDEOS %series_id
            season_url = season_url + '&filter='
            oc.add(DirectoryObject(key=Callback(ShowSections, title='All Seasons', url=season_url, season=0, thumb=thumb, show_url=local_url), title='All Seasons', thumb=thumb))

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
#######################################################################################
# This function produces sections for shows with old table format
@route(PREFIX + '/showsection', season=int)
def ShowSections(title, thumb, url, season, show_url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(show_url, cacheTime = CACHE_1HOUR)
    # To send shows directly to this function first, we need to check for videos
    video_check = data.xpath('//li//a[text()="Watch Video"]')
    if video_check:
        sub_list = data.xpath('//li[contains(@class,"-subItem")]/div/a')
        # This is for those shows that have sections listed below Watch Video
        for section in sub_list:
            section_filter = section.xpath('./@href')[0].split('filter=')[1]
            sec_url = url + section_filter
            sec_title = section.xpath('.//text()')[2].strip()
            oc.add(DirectoryObject(key=Callback(ShowVideos, title=sec_title, url=sec_url, season=season), title=sec_title, thumb=thumb))

        # Add a section that shows all videos
        oc.add(DirectoryObject(key=Callback(ShowVideos, title='All Videos', url=url, season=season), title='All Videos', thumb = thumb))

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos for this show.")
    else:
        return oc
#################################################################################################################
# This function produces videos from the table layout used by show video pages
# This function picks up all videos in all pages even without paging code
@route(PREFIX + '/showvideo', season=int)
def ShowVideos(title, url, season):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url)
    for video in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
        # If the link does not have a mainuri, it will not play through the channel with the url service, so added a check for that here
        title = video.xpath('.//@maintitle')[0]
        thumb = video.xpath('./meta[@itemprop="thumbnail"]//@content')[0].split('?')[0]
        if not thumb:
            thumb = video.xpath('.//li[contains(@id,"img")]/img//@src')[0]
        if not thumb.startswith('http:'):
            thumb = BASE_URL + thumb
        vid_url = BASE_URL + video.xpath('.//@mainurl')[0]
        desc = video.xpath('.//@maincontent')[0]

        # HERE WE CHECK TO SEE IF THE VIDEO IS A VIDEO CLIP PLAYLIST THAT NEEDS TO HAVE THE PARTS PRODUCED
        # THIS IS USED TO PROCESS SPECIALS BUT IN VH1, ALL VIDEO CLIPS ARE PLAYLIST WITH THE URL IN THE FORMAT OF "/video/play.jhtml?id=1706039" 
        # ALMOST ALL BONUS CLIPS, SHOW CLIPS, ETC LISTED FOR EACH SHOW ON VH1 CONTAIN MULTIPLE VIDEOS
        # And the current URL service will not pick up these parts if playlist is not in the title
        if '?id=' in vid_url:
            vid_id = RE_VIDID.search(vid_url).group(1)
            vid_url = PLAYLIST + vid_id
            # send to videopage function
            oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb))
        else:
            date = video.xpath('.//@mainposted')[0]
            if 'hrs ago' in date:
                date = Datetime.Now()
            else:
                date = Datetime.ParseDate(date)
            episode = video.xpath('.//li[@class="list-ep"]//text()')[0]
            if episode.isdigit()==False or season==0:
                (new_season, episode) = SeasEpFind(episode, title)
            else:
                new_season = season
            oc.add(EpisodeObject(
                url = vid_url, 
                season = int(new_season),
                index = int(episode),
                title = title, 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON)),
                originally_available_at = date,
                summary = desc
            ))
    
    if len(oc) < 1:
        Log ('no value for objects')
        # Found some old VH1 shows that use an old table setup so added an addtional pull for those old formats here
        try:
            for video in data.xpath('//table[@class="video-list"]/tr'):
                try: vid_url = video.xpath('./td[@class="r-title"]/a//@href')[0]
                except: continue
                if not vid_url.startswith('http://'):
                    vid_url = BASE_URL + vid_url
                title = video.xpath('./td[@class="r-title"]/a//text()')[0]
                if '?id=' in vid_url:
                    vid_id = RE_VIDID.search(vid_url).group(1)
                    vid_url = PLAYLIST + vid_id
                    # send to videopage function
                    oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title))
                else:
                    try: episode = int(video.xpath('./td[@class="r-ep"]//text()')[0])
                    except: episode = 0
                    date = Datetime.ParseDate(video.xpath('./td[@class="r-date"]//text()')[0])
                    oc.add(EpisodeObject(url = vid_url, season = season, index = episode, title = title, originally_available_at = date))
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
        link = item.xpath('.//a[@itemprop="url"]//@href')[0]
        if not link.startswith('http:'):
            link = BASE_URL + link
        # When there isn't an image, they provide a default image
        try: image = item.xpath('.//img[@itemprop="thumbnail"]//@src')[0]
        # When there isn't an image, they provide a default image
        except: image = BASE_URL + item.xpath('.//img//@src')[0]
        try: video_title = item.xpath('.//a//text()')[0].strip()
        # This is used by Most Popular Full Episodes to get title all others use the anchor text
        except: video_title = item.xpath('.//img[@itemprop="thumbnail"]//@alt')[0]
        # The only way to get the title consistently is to get all text fields and combine them since each type of page arranges the title differently
        if not video_title:
            video_title_list = item.xpath('.//a//text()')
            video_title = ' '.join(video_title_list).replace('\n', '')
            # This cleans up the title a little bit if it has Video: in it
            try: video_title = video_title.split('Video:')[1].strip()
            except: pass
        try:
            # The VH1 most popular pulls have the show and/or the episode title in two different locations
            # and sometimes have new lines in the middle of them so need to strip that away here
            title = item.xpath('./p[@class="deck"]//text()')[0].strip()
            title = title.replace('\n', '')
            video_title = '%s  %s' %(title,video_title)
        except:
            pass
        # here we want to see if there is an episode and season info for the video
        (season, episode) = SeasEpFind(episode='--', title=video_title)
        (season, episode) = (int(season), int(episode))
        try: date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
        except: date = ''
        if 'hrs ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)

        # HERE WE CHECK TO SEE IF THE VIDEO IS A VIDEO CLIP PLAYLIST THAT NEEDS TO HAVE THE PARTS PRODUCED
        # But skip those that start with the playlist url since they are already processed
        if '?id=' in link or ('#id=' in link and not PLAYLIST in url):
            vid_id = RE_VIDID.search(link).group(1)
            vid_url = PLAYLIST + vid_id
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
# In VH1, these seem to always have an episode number but occasionally have the word Episode or Season in the title
@route(PREFIX + '/seasepfind')
def SeasEpFind(episode, title):

    #Log('the value of title is %s' %title)
    try:
        test_ep = int(episode)
    except:
        try: episode = RE_EPISODE.search(title).group(2)
        except: episode = '0'
    if len(episode) > 2:
        new_season = episode[0]
    else:
        try: new_season = RE_SEASON.search(other_info).group(2)
        except: new_season = '1'
    
    #Log('the value of season is %s and episode is %s' %(season, episode))
    return (new_season, episode)
#######################################################################################
# This function produces videos from a blog like best week ever
# IT ONLY PLAYS THE LATEST FULL EPISODE
@route(PREFIX + '/blogplayer')
def BlogPlayer(title, url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    # To send shows directly to this function first, we need to check for videos
    video_list = data.xpath('//article')
    for video in video_list:
        try: mgid = video.xpath('./section/div/@data-content-uri')[0]
        except: continue
        vid_title = video.xpath('./header/h3/a/@title')[0]
        date = video.xpath('.//span[@class="entry-date"]//text()')[0].split('|')[0]
        date = Datetime.ParseDate(date.strip())
        url = video.xpath('./header/h3/a/@href')[0]
        # need to manipulate the url
        id_num = mgid.split('id=')[1]
        Log('the value of mgid is %s' %mgid)
        if 'videolist' in mgid:
            new_url = 'http://www.vh1.com/video/playlist.jhtml?id=' + id_num
        else:
            new_url = 'http://www.vh1.com/video/play.jhtml?id=' + id_num
        summary_list = video.xpath('./section/p//text()')
        summary = ' '.join(summary_list)
        thumb = video.xpath('.//img/@src')[0]
        oc.add(VideoClipObject(url=new_url, title=vid_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

    # Paging
    try:
        next_link = data.xpath('.//ul/li[@class="bpn-next-link"]/a/@href')[0]
        oc.add(NextPageObject(key = Callback(BlogPlayer, title=title, url=next_link), title = L("Next Page ...")))
    except:
        pass

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no sections for this show.")
    else:
        return oc
#####################################################################################
# For Specials with JSON
# This is the new format they are using. Right now it is only used for Super Bowl, but may be used with others in the future.
@route(PREFIX + '/specialjson')
def SpecialJSON(title, url):
    oc = ObjectContainer(title2=title)
    content = HTTP.Request(url).content
    content = content.replace('{"interface":{"data":{"item":', '').replace('},"disabled":true}}', '')
    json = JSON.ObjectFromString(content)
    for items in json:
        # have to first check that it is a valid entry so we use the thumb field
        try: thumb = BASE_URL + items['images']['img']['src']
        except: continue
        # date my be today so we need to check before doing the Datetime.ParseDate()
        date = items['datePublished']
        if 'today' in date or 'hrs ago' in date:
            date = Datetime.Now()
        else:
            try: date = Datetime.ParseDate(date)
            except: date = None
        oc.add(VideoClipObject(
            url = BASE_URL + items['link'],
            title = items['name'],
            duration = Datetime.MillisecondsFromString(items['duration']),
            thumb=Resource.ContentsOfURLWithFallback(url=thumb),
            originally_available_at=date
        ))
    return oc
#####################################################################################
# This is for finding the video link for specials. This will go to the Redirected page and look for a video section link, otherwise it pulls the new url address
@route(PREFIX + '/specialfix')
def SpecialFix(url):
    data = HTML.ElementFromURL(url)

    vid_url = None
    for video in data.xpath('//ul[@id="navlist"]/li/a'):
        title = video.xpath('.//text()')[0]
        if 'Video' in title or 'VIDEO' in title:
            vid_url = video.xpath('.//@href')[0]
            if not vid_url.startswith('http:'):
                vid_url =  BASE_URL + vid_url
                
    if not vid_url:
        try: vid_url = BASE_URL + video.xpath('//div[@id="nav_logo"]/a/@href')[0]
        except: vid_url = url

    return vid_url
