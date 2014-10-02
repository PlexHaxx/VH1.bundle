TITLE = 'VH1'
PREFIX = '/video/vh1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.vh1.com'
SHOWS_AZ = 'http://www.vh1.com/include/series/azFilter?startingCharac=%s&template=/shows/home2/modules/azFilter&resultSize=50'
ALL_VID_AJAX = 'http://www.vh1.com/include/shows/seasonAllVideosAjax?id=%s&seasonId=%s&start=0&resultSize=1000&template=/shows/platform/watch/modules/seasonRelatedPlaylists'
FULL_EP_AJAX = '&filter=fullEpisodes'

RE_SEASON  = Regex('(Season|Seas.) ?(\d{1,2})')
RE_EPISODE  = Regex('(Episode|Ep.) ?(\d{1,3})')
RE_VIDID = Regex('(\d{7})')
# episode regex for new show format
RE_EXX = Regex('/e(\d+)')

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
    oc.add(DirectoryObject(key=Callback(ProduceCarousels, title="Videos", url='http://www.vh1.com/video/'), title="Videos"))
    #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.vh1", title=L("Search VH1 Videos"), prompt=L("Search for Videos")))
    return oc
#####################################################################################
@route(PREFIX + '/showmain')
def ShowMain(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(ProduceShows, title='VH1 Poplular Shows'), title='VH1 Popular Shows'))  
    oc.add(DirectoryObject(key=Callback(Alphabet, title='VH1 Shows A to Z'), title='VH1 Shows A to Z')) 
    return oc
#####################################################################################
# For Producing Popular Shows form main show page
@route(PREFIX + '/produceshows') 
def ProduceShows(title):
    oc = ObjectContainer(title2=title)
    local_url = url=BASE_URL+'/shows/'
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)

    for video in data.xpath('//section[@id="sec-popshows"]//div[contains(@class,"promo-block")]'):
        url = video.xpath('./a/@href')[0]
        if not url.startswith('http://'):
            url = BASE_URL + url
        title = video.xpath('.//div[@class="header"]/span//text()')[0].strip()
        thumb = video.xpath('.//div[contains(@class, "thumb")]/@data-src')[0] + '?width=470&height=264'
        # Two shows in the list still use the old format, Hollywood Exes and VH1 News
        if '/celebrity/' in url:
            oc.add(DirectoryObject(key=Callback(BlogPlayer, title=title, url=url), title = title, thumb = Resource.ContentsOfURLWithFallback(url=thumb)))
        else:
            oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url, thumb = thumb), title=title, thumb = Resource.ContentsOfURLWithFallback(url=thumb)))

    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
        return oc
#####################################################################################
# For Producing a to z list of shows
@route(PREFIX + '/alphabet')
def Alphabet(title):
    oc = ObjectContainer(title2=title)
    for ch in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        url=SHOWS_AZ %ch
        oc.add(DirectoryObject(key=Callback(ShowsAZ, title=ch, url=url), title=ch))
    return oc
#####################################################################################
# For Producing a to z list of shows
@route(PREFIX + '/showsaz')
def ShowsAZ(title, url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    for items in data.xpath('//ul/li/a'):
        url = BASE_URL + items.xpath('./@href')[0]
        title = items.xpath('.//text()')[0]
        if url=='#':
            continue
        if 'series.jhtml' in url:
            if 'shows/pop_up_video/' in url:
                oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))
            # These shows are blogs so we send them to the blog player
            elif '/best_week_ever/' in url or '/the_gossip_table/' in url:
                if '/celebrity/category/' not in url:
                    url_name = url.split('shows/')[1].split('/')[0]
                    url_name = url_name.replace('_', '-')
                    url = 'http://www.vh1.com/celebrity/category/%s/' %url_name
                oc.add(DirectoryObject(key=Callback(BlogPlayer, title=title, url=url), title = title))
            else:
                vid_url = url.replace('series', 'video')
                oc.add(DirectoryObject(key=Callback(ShowOldVideos, title=title, url=vid_url), title=title))
        else:
            oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url), title=title))
    return oc
#######################################################################################
# This function produces sections for shows with new format
@route(PREFIX + '/showseasons')
def ShowSeasons(title, url, thumb=''):
    oc = ObjectContainer(title2=title)
    if url.endswith('series.jhtml'):
        local_url = url.replace('series', 'video')
        oc.add(DirectoryObject(key=Callback(ShowOldVideos, title='All Videos', url=local_url), title='All Videos', thumb=thumb))
    else:
        local_url = url + 'video/'
        html = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
        new_season_list = html.xpath('//span[@id="season-dropdown"]//li/a')
        if len(new_season_list)> 0:
            for section in new_season_list:
                title = section.xpath('./span//text()')[0].strip().title()
                season = int(title.split()[1])
                season_id = section.xpath('./@data-id')[0]
                oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=local_url, season=season, season_id=season_id), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
        else:
            oc.add(DirectoryObject(key=Callback(ShowSections, title='All Seasons', thumb=thumb, url=local_url, season=0), title='All Seasons', thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    return oc
#######################################################################################
# This function produces sections for new show format
# LOOK INTO THE FACT THAT IT SHOWS FULL EPISODE INFO EVEN IF FULL EPISODES IS NOT AN OPTION
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season, season_id=''):
    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    section_list = html.xpath('//span[@id="video-filters-dropdown"]//li/a')
    #Log('the value of section_list is %s' %section_list)
    for section in section_list:
        id = section.xpath('./@data-seriesid')[0]
        url = BASE_URL + section.xpath('./@href')[0]
        section_title = section.xpath('./span/text()')[0].title()
        new_url = ALL_VID_AJAX
        if season_id:
            new_url = new_url %(id, season_id)
            if 'Full Episodes' in section_title:
                new_url = new_url + FULL_EP_AJAX
        else:
            new_url = url
        oc.add(DirectoryObject(key=Callback(ShowVideos, title=section_title, url=new_url, season=season), title=section_title, thumb=thumb))
        
    # This handles pages that do not have the new format that still come through this function
    if len(oc) < 1:
        Log ('still no value for objects')
        oc.add(DirectoryObject(key=Callback(ShowOldVideos, title='All Videos', url=url), title='All Videos', thumb=thumb))
    return oc
#######################################################################################
# This function produces videos for the new show format
# FOR NOW I HAVE CHOSEN TO NOT SHOW RESULTS THAT HAVE "NOT AVAILABLE" BUT INCLUDE THOSE THAT GIVE A DATE FOR WHEN IT WILL BE AVAILABLE
@route(PREFIX + '/showvideos', season=int, start=int)
def ShowVideos(title, url, season):

    oc = ObjectContainer(title2=title)
    try: data = HTML.ElementFromURL(url)
    except: return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    video_list = data.xpath('//div[contains(@class,"grid-item")]')
    for video in video_list:
        try: vid_avail = video.xpath('.//div[@class="message"]//text()')[0]
        except: vid_avail = 'Now'
        # Full episodes have a sub-header field for the title but all videos have a second header hidden text
        try: vid_title = video.xpath('.//div[@class="sub-header"]/span//text()')[0].strip()
        except: vid_title = video.xpath('.//div[@class="header"]/span[@class="hide"]//text()')[0].strip()
        thumb = video.xpath('.//div[@class=" imgDefered"]/@data-src')[0]
        seas_ep = video.xpath('.//div[@class="header"]/span//text()')[0].strip()
        if vid_avail == 'not available':
            continue
        if vid_avail == 'Now':
            vid_type = video.xpath('./@data-filter')[0]
            # Skip full episodes for Android Clients
            if vid_type=="FullEpisodes" and Client.Platform in ('Android'):
                continue
            #Found one that does not have a anchor code on it so put the in a try/except
            try: vid_url = video.xpath('./a/@href')[0]
            except: continue
            # One descriptions is blank and gives an error
            try: desc = video.xpath('.//div[contains(@class,"deck")]/span//text()')[0].strip()
            except: desc = None
            other_info = video.xpath('.//div[@class="meta muted"]/small//text()')[0].strip()
            duration = Datetime.MillisecondsFromString(other_info.split(' - ')[0])
            date = Datetime.ParseDate(video.xpath('./@data-sort')[0])
            try: episode = int(RE_EXX.search(seas_ep).group(1))
            except: episode = None
            # This creates a url for playlists of video clips
            if '#id=' in url:
                id_num = RE_VIDID.search(vid_url).group(1)
                new_url = BUILD_URL + id_num
                vid_url = new_url

            oc.add(EpisodeObject(
                url = vid_url, 
                season = season,
                index = episode,
                title = vid_title, 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
                originally_available_at = date,
                duration = duration,
                summary = desc
            ))
        else:
            avail_date = vid_avail.split()[1]
            avail_title = 'NOT AVAILABLE UNTIL %s' %avail_date
            desc = '%s - %s' %(seas_ep, vid_title)
            oc.add(PopupDirectoryObject(key=Callback(NotAvailable, avail=vid_avail), title=avail_title, summary=desc, thumb=thumb))
      
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos available to watch." )
    else:
        return oc
####################################################################################################
# This produces videos for the old style of show video pages
@route(PREFIX + '/showoldvideos')
def ShowOldVideos(url, title):
    oc = ObjectContainer(title2=title)
    try: data = HTML.ElementFromURL(url)
    except: return ObjectContainer(header="404 Error", message="The URL the website has given for this show is invalid and therefore videos cannot be found.")
    for item in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
        link = BASE_URL + item.xpath('./@mainurl')[0]
        video_title = item.xpath('./@maintitle')[0]
        image = item.xpath('./meta[@itemprop="thumbnail"]/@content')[0].split('?')[0]
        date = item.xpath('./@mainposted')[0]
        desc = item.xpath('./@maincontent')[0]
        # Some videos are locked or unavailable but still listed on the site
        # most have 'class="quarantineDate"' in, the description, but not all so using the text also
        if 'quarantineDate' in desc or 'Not Currently Available' in desc:
            continue
        if 'hrs ago' in date or 'today' in date or 'hr ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)
        # Skip full episodes and videos with parts for Android Clients
        if Client.Platform in ('Android') and 'playlist.jhtml' in link:
            continue
        # check for episode
        episode = item.xpath('.//li[@class="list-ep"]//text()')[0]
        if episode and episode.isdigit()==True:
            season = int(episode[0])
            episode = int(episode)
        else:
            episode = 0
            season = 0

        oc.add(EpisodeObject(
            url=link,
            title=video_title,
            season=season,
            index=episode,
            summary=desc,
            originally_available_at=date,
            thumb=Resource.ContentsOfURLWithFallback(url=image)
        ))

    if len(oc) < 1:
        Log ('no value for objects')
        # Found some old VH1 shows that use an old table setup so added an addtional pull for those old formats here
        try:
            for video in data.xpath('//table[@class="video-list"]/tr'):
                try: vid_url = video.xpath('./td[@class="r-title"]/a/@href')[0]
                except: continue
                if not vid_url.startswith('http://'):
                    vid_url = BASE_URL + vid_url
                title = video.xpath('./td[@class="r-title"]/a//text()')[0]
                try: episode = int(video.xpath('./td[@class="r-ep"]//text()')[0])
                except: episode = 0
                date = Datetime.ParseDate(video.xpath('./td[@class="r-date"]//text()')[0])
                # Skip full episodes for Android Clients
                if 'playlist.jhtml' in vid_url and Client.Platform in ('Android'):
                    continue
                oc.add(EpisodeObject(url = vid_url, index = episode, title = title, originally_available_at = date, thumb = R(ICON)))
        except:
            pass
  
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
####################################################################################################
# This produces videos for special pages. Right now only used for pop up videos
@route(PREFIX + '/videopage', season=int)
def VideoPage(url, title):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url)
    for item in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
        link = item.xpath('.//a/@href')[0]
        # The only way to get the title consistently is to get all text fields and combine them since each type of page arranges the title differently
        video_title_list = item.xpath('.//a//text()')
        video_title = ' '.join(video_title_list).replace('\n', '')
        if 'Pop Up Video' in title:
            try: video_title = video_title.split('videos ')[1].strip()
            except: video_title = video_title.split('Video: ')[1].strip()
        try: image = item.xpath('.//*[@itemprop="thumbnail" or @class="thumb"]/@src')[0].split('?')[0]
        except: image = R(ICON)
        try: date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
        except: date = ''
        desc = None
        if 'hrs ago' in date or 'today' in date or 'hr ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)
        if not image.startswith('http:'):
            image = BASE_URL + image
        if not link.startswith('http:'):
            link = BASE_URL + link

        oc.add(VideoClipObject(
            url=link,
            title=video_title,
            summary=desc,
            originally_available_at=date,
            thumb=Resource.ContentsOfURLWithFallback(url=image)
        ))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
#######################################################################################
# This function produces videos from a blog like best week ever
# SOMETIMES ONLY THE LATEST FULL EPISODE OFFERED ON THE BLOG WILL ACTUALLY PLAY
@route(PREFIX + '/blogplayer')
def BlogPlayer(title, url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    # To send shows directly to this function first, we need to check for videos
    for video in data.xpath('//article'):
        try: mgid = video.xpath('./section/div/@data-content-uri')[0]
        except: continue
        if '/cp~vid' in mgid:
            mgid = mgid.split('/cp~vid')[0]
        # need to build a url that will work with the url service
        if 'mgid:uma:videolist:' in mgid and Client.Platform in ('Android'):
            continue
        id_num = mgid.split('com:')[1]
        new_url = 'http://www.vh1.com/video/play.jhtml?id=' + id_num
        vid_title = video.xpath('./header/h3/a/@title')[0]
        date = video.xpath('.//span[@class="entry-date"]//text()')[0].split('|')[0]
        date = Datetime.ParseDate(date.strip())
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
############################################################################################################################
# This function creates an error message for entries that are not currrently available
@route(PREFIX + '/notavailable')
def NotAvailable(avail):
  return ObjectContainer(header="Not Available", message='This video is currently unavailable - %s.' %avail)

#####################################################################################
# For Producing Sections for Video page
@route(PREFIX + '/producecarousels')
def ProduceCarousels(title, url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url)
    for video in data.xpath('//div[contains(@class, "mdl-carousel")]'):
        show_type = video.xpath('.//@id')[0]
        if Client.Platform in ('Android') and show_type=='episodes-carousel':
            continue
        title = video.xpath('.//h2/span/a//text()')[0].strip()
        oc.add(DirectoryObject(key=Callback(MoreVideos, title=title, url=url, show_type=show_type), title = title))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
        return oc
#########################################################################################
# This will produce the items in the carousel sections for video page
@route(PREFIX + '/morevideos')
def MoreVideos(title, url, show_type):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url)
    for video in data.xpath('//div[@id="%s"]//li[@class="carouselItem "]' %show_type):
        vid_url = BASE_URL + video.xpath('.//a/@href')[0]
        title = video.xpath('.//div[@class="long"]//text()')[0]
        thumb = video.xpath('.//img//@src')[0].split('?')[0]
        if not thumb.startswith('http://'):
            thumb = BASE_URL + thumb
        try:
            date = video.xpath('.//i[@class="date"]//text()')[0].split()[1]  
            date = Datetime.ParseDate(date) 
        except:
            date = None
        # Most have a date but music videos have an artist field instead so add to title
            try:
                artist = video.xpath('.//i[@class="artist"]//text()')[0]
                title = '%s - %s' %(artist, title)
            except:
                pass
        if 'episodes' in show_type or 'shows' in show_type:
        # All appear to have an episode but some do not have a season but put both in a try/except to prevent any issues
            try: episode = int(RE_EPISODE.search(title).group(2))
            except: episode = 0
            try: season = int(RE_SEASON.search(title).group(2))
            except: season = 0
            oc.add(EpisodeObject(url = vid_url, title = title, index = episode, season = season, originally_available_at = date, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
        else:
            oc.add(VideoClipObject(url = vid_url, title = title, originally_available_at = date, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
