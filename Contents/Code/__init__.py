
TITLE = 'VH1'
PREFIX = '/video/vh1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.vh1.com'
VH1_ALLMENU = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'
SEARCH_URL = 'http://www.vh1.com/search/'
SERIES_VIDEOS = 'http://www.vh1.com/global/music/modules/video/shows/?seriesID='
PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id='
# The two variables below uses the base url and either %20Full%20Episodes  or %20Bonus%20Clips but %s will not work with '-' in url so have to split into two
POPULAR_AJAX_PART1 = '/global/music/modules/mostPopular/module.jhtml?category=Videos%20-%20TV%20Show%20Videos%20-%20'
POPULAR_AJAX_PART2 = '&contentType=videos&howManyChartItems=25&fluxSort=numberOfViews:today:desc&displayPostedDate=true'
MRSS_FEED = 'http://www.mtv.com/player/embed/AS3/rss/?uri=mgid:uma:videolist:vh1.com:%s'
PARTS_URL = 'http://www.vh1.com/video/play.jhtml?id=%s#parts=%s'

# THIS IS A LISTING FOR AWARDS SHOWS OR SPECIALS ON THE ALL SHOWS PAGE THAT WE WANT TO PRODUCE VIDEOS FOR BUT 
# BECAUSE THEY HAVE ENDED EVERY LINK WITH SERIES.JHTML INSTEAD OF CORRECT URL FOR A SPECIAL (/EVENT/) WE HAVE TO CHECK FOR THEM AND PULL THEM OUT
SPECIAL_LIST = ["Do Something Awards 2013", "VH1 Divas 2012", "Critics' Choice Television Awards (2011)", "The Best Super Bowl Concert Ever",
                "VH1 Super Bowl Blitz"]
# THIS IS A LIST OF ANY SHOWS OR SPECIALS IN THE ALL SHOWS PAGE THAT GIVE AN ERROR
BAD_ARCHIVE_LIST = ["VH1 Classic Main Format", "2008 Hip Hop Honors", "2009 Hip Hop Honors", "2010 Hip Hop Honors",
 "17th Annual Critics' Choice Movie Awards", "Best Day Ever", "Critics' Choice Movie Awards (2010)", "Critics' Choice Movie Awards (2011)",
 "DIVAS (2010)", "Do Something Awards 2010", "Do Something Awards 2011", "Do Something Awards 2012", "Ev & Ocho", "Front Row", "Posted", "You Oughta Know", 
 "VH1 Classic", "VH1 Divas (2009)", "VH1 Divas Celebrates Soul"]

RE_SERIES_ID = Regex("var seriesID = '(\d+)';")
RE_SEASON  = Regex('(Season|Seas.) ?(\d{1,2})')
RE_EPISODE  = Regex('(Episode|Ep.) ?(\d{1,3})')
RE_VIDID = Regex('(\d{7})')
RE_VIDID2 = Regex('(\d{6,7})')
RE_PARTS  = Regex('Top (\d{1,2}) Moments')

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
    oc.add(DirectoryObject(key=Callback(MostPopular, title='VH1 Videos'), title='VH1 Videos')) 
    #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.vh1", title=L("Search VH1 Videos"), prompt=L("Search for Videos")))
    return oc
#####################################################################################
@route(PREFIX + '/showmain')
def ShowMain(title):
    oc = ObjectContainer(title2=title)
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
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=url), title=title))
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
# For Producing Popular Shows form main show page
@route(PREFIX + '/produceshows') 
def ProduceShows(title):
    oc = ObjectContainer(title2=title)
    local_url = url=BASE_URL+'/shows/'
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)

    for video in data.xpath('//div[@class="p2_show"]'):
        url = video.xpath('./a/@href')[0]
        if not url.startswith('http://'):
            url = BASE_URL + url
        title = video.xpath('.//a[@class="show_link"]//text()')[0].strip()
        thumb = BASE_URL + video.xpath('.//img/@src')[0]
        if '/season_' in url:
            oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url), title=title, thumb = thumb))
        elif '/celebrity/' in url:
            oc.add(DirectoryObject(key=Callback(BlogPlayer, title=title, url=url), title = title, thumb = thumb))
        elif url.endswith('series.jhtml'):
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=url, thumb = thumb), title=title, thumb = thumb))
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
            if '/best_week_ever/' in url or '/the_gossip_table/' in url:
                if '/celebrity/category/' not in url:
                    url_name = url.split('shows/')[1].split('/')[0]
                    url_name = url_name.replace('_', '-')
                    url = 'http://www.vh1.com/celebrity/category/%s/' %url_name
                oc.add(DirectoryObject(key=Callback(BlogPlayer, title=title, url=url), title = title))
            else:
                if '/season_' in url:
                    season = url.split('/season_')[1]
                    season = int(season.split('/')[0])
                else:
                    season=1
                oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=url, season=int(season)), title = title))
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
                #elif "Do Something Awards" in title and "2013" not in title:
                    #continue
                #Need to get the proper url for the videos for the rest since it puts series on the end and we need the video page
                else:
                    url = SpecialFix(url)
                oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title = title))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no shows to list right now.")
    else:
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
#######################################################################################
# This function produces seasons for each show based on the format 
@route(PREFIX + '/showseasons', season=int)
def ShowSeasons(title, url):
    oc = ObjectContainer(title2=title)
    local_url = url.replace('series', 'seasons')
    data = HTML.ElementFromURL(local_url)
    video_list = data.xpath('//div[1]/ol/li/div[contains(@class,"title")]/a')

    if video_list:
        for video in video_list:
            season_url = BASE_URL + video.xpath('.//@href')[0]
            # There is an error on the sites where some season 1 urls are not producing properly so we have to fix them
            try:
                season = int(season_url.split('season_')[1].split('/')[0])
            except:
                season = 1
                season_url = season_url.replace('series.jhtml', 'season_1/series.jhtml')
            title = String.DecodeHTMLEntities(video.xpath('./img//@alt')[0])
            thumb = video.xpath('./img//@src')[0]
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=season_url, season=season, thumb=thumb), title=title, thumb=thumb))
    # This handles any pages that get sent here but do not have seasons
    else:
        oc.add(DirectoryObject(key=Callback(ShowSections, title="All Seasons", url=url), title="All Seasons"))
        

    if len(oc) < 1:
        Log ('still no value for season objects')
        return ObjectContainer(header="Empty", message="There are no videos for this show.")
    else:
        return oc
#######################################################################################
# This function produces sections for shows and checks for videos
@route(PREFIX + '/showsection', season=int)
def ShowSections(title, url, thumb=None, season=0):
    oc = ObjectContainer(title2=title)
    show_name = title
    local_url = url.replace('series', 'video')
    content = HTTP.Request(local_url).content
    series_id = RE_SERIES_ID.search(content).group(1)
    data = HTML.ElementFromString(content)
    
    # check for videos first
    video_check = data.xpath('//li//a[text()="Watch Video"]')
    if video_check:
        # This gets the thumb for shows that do not have a thumb. Some old shows do not have an image so use a try/except
        if not thumb:
            try: thumb = data.xpath('//a[@href="series.jhtml"]/img/@src')[0]
            except: thumb = R(ICON)
        # This is for those shows that have sections listed below Watch Video
        sub_list = data.xpath('//li[contains(@class,"-subItem")]/div/a')
        if sub_list:
            for section in sub_list:
                section_filter = section.xpath('./@href')[0].split('filter=')[1]
                sec_url = '%s%s&filter=%s' %(SERIES_VIDEOS, series_id, section_filter)
                sec_title = section.xpath('.//text()')[2].strip()
                oc.add(DirectoryObject(key=Callback(VideoPage, title=sec_title, url=sec_url, season=season, show_name=show_name), title=sec_title, thumb=thumb))
        else:
            # Add a section that shows all videos
            all_url = '%s%s&filter=' %(SERIES_VIDEOS, series_id)
            oc.add(DirectoryObject(key=Callback(VideoPage, title='All Videos', url=all_url, season=season, show_name=show_name), title='All Videos', thumb = thumb))

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos for this show.")
    else:
        return oc
####################################################################################################
# This produces videos for most popular as well for specials
# PAGING FOR VIDEOS SENT HERE COULD VARY WIDELY MAY WANT TO INCREASE RESULTS FOR MOST POPULAR TO 50 INSTEAD
@route(PREFIX + '/videopage', season=int)
def VideoPage(url, title, season=0, show_name=''):
    oc = ObjectContainer(title2=title)
    # THIS IS A UNIQUE DATA PULL
    id_num_list = []
    data = HTML.ElementFromURL(url)
    for item in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
        try: image = item.xpath('.//img[@itemprop="thumbnail"]//@src')[0].split('?')[0]
        # When there isn't an image, they provide a default image
        except: image = item.xpath('.//img//@src')[0].split('?')[0]
        if not image.startswith('http:'):
            image = BASE_URL + image
        try: date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
        except: date = ''
        if 'hrs ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)

        # This pulls other data for show videos in table format
        try:
            link = item.xpath('.//@mainurl')[0]
            video_title = item.xpath('.//@maintitle')[0]
            desc = item.xpath('.//@maincontent')[0]
            show = show_name
        # This pulls other data for all other types of videos
        except:
            link = item.xpath('.//a[@itemprop="url"]/@href')[0]
            # The only way to get the title consistently is to get all text fields and combine them since each type of page arranges the title differently
            video_title_list = item.xpath('.//a//text()')
            video_title = ' '.join(video_title_list).replace('\n', '')
            try:
                # The VH1 most popular pulls have the show and/or the episode title in two different locations
                # and sometimes have new lines in the middle of them so need to strip that away here
                show = video_title
                title1 = item.xpath('./p[@class="deck"]//text()')[0].strip()
                video_title = title1.replace('\n', ' ')
            except:
                show = None
            desc = None

        # Here we are building a url either with a part number or with building a playlist
        if not link.startswith('http:'):
            link = BASE_URL + link
        # Pop up video(format is http://www.vh1.com/video/play.jhtml?id=) lists the parts in the metadata so we do not need to the extra call for them
        if 'Pop Up Video' in title:
            # clean up the title a little
            try: video_title = video_title.split(': ')[1].strip()
            except: pass
            try:
                parts = item.xpath('.//div[@class="vidCount"]//text()')[0].strip().split()[0]
                # take the number of parts out of the title
                video_title = video_title.split('videos')[1].strip()
                new_url = '%s#parts=%s' %(link, parts)
            except:
                new_url = link
        # This handles specials
        elif '#id=' in link and PLAYLIST not in url:
            # We first check to see if the id_num has been processed so we do not have to do any uneccessary calls
            id_num = RE_VIDID.search(link).group(1)
            if id_num not in id_num_list:
                id_num_list.append(id_num)
                (new_url, video_title) = BuildUrl(link)
            else:
                continue
        # This handles full episodes
        elif 'playlist.jhtml' in link:
            # Just define parts for a few smaller shows
            if show_name in ['That Metal Show', 'Behind the Music Remastered']:
                new_url =  link + '#parts=5'
            new_url = link
        # This handles video clips
        elif '/video/play.jhtml?id=' in link:
            # First check for parts in title via top moments
            try:
                vid_parts = RE_PARTS.search(link).group(1)
                new_url = link + '#parts=' + vidparts
            except:
                try:
                    # This checks for 7 digit mgid number
                    id_num = RE_VIDID.search(link).group(1)
                    new_url = PLAYLIST + id_num
                # this is just in case any of the videos have a 6 digit number instead of 7
                except:
                    new_url = link
        else:
            new_url = link
            
        # Skip full episodes and videos with parts for Android Clients
        if Client.Platform in ('Android') and ('playlist.jhtml' in new_url or '#parts=' in new_url):
            continue

        if PLAYLIST in new_url:
            oc.add(DirectoryObject(key=Callback(VideoPage, title=video_title, url=new_url), title=video_title, thumb=image, summary=desc))
        else:
            if show:
                # check for episode
                try: episode = item.xpath('.//li[@class="list-ep"]//text()')[0]
                except: episode = None
                if episode and episode.isdigit()==True:
                    season = int(episode[0])
                    episode = int(episode)
                # check for episode and season in title
                else:
                    try:  episode = int(RE_EPISODE.search(video_title).group(2))
                    except: episode = 0
                    if season==0:
                        try: season = int(RE_SEASON.search(video_title).group(2))
                        except: pass
                oc.add(EpisodeObject(url=new_url, title=video_title, season=season, show=show, index=episode, summary=desc, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))
            else:
                oc.add(VideoClipObject(url=new_url, title=video_title, summary=desc, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc) < 1:
        Log ('no value for objects')
        # Found some old VH1 shows that use an old table setup so added an addtional pull for those old formats here
        try:
            for video in data.xpath('//table[@class="video-list"]/tr'):
                try: vid_url = video.xpath('./td[@class="r-title"]/a//@href')[0]
                except: continue
                # Skip full episodes for Android Clients
                if 'playlist.jhtml' in vid_url and Client.Platform in ('Android'):
                    continue
                if not vid_url.startswith('http://'):
                    vid_url = BASE_URL + vid_url
                title = video.xpath('./td[@class="r-title"]/a//text()')[0]
                #For these old shows, it would be impossible to determine the number of parts so using default and sending clips to Video page as playlist
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
#######################################################################################
# This function produces videos from a blog like best week ever
# SOMETIMES ONLY THE LATEST FULL EPISODE OFFERED ON THE BLOG WILL ACTUALLY PLAY
# NEED TO ADD ANDROID CHECK HERE 
@route(PREFIX + '/blogplayer')
def BlogPlayer(title, url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    # To send shows directly to this function first, we need to check for videos
    for video in data.xpath('//article'):
        try: mgid = video.xpath('./section/div/@data-content-uri')[0]
        except: continue
        # need to build a url that will work with the url service and check for blank videos since many older full episodes are empty
        # if the mgid has videolist in it we send it to get the number of parts otherwise we just get the id number and make it a video clip
        if 'mgid:uma:videolist:' in mgid:
            if Client.Platform in ('Android'):
                continue
            else:
                (new_url, alt_title) = BuildUrl(mgid)
        else:
            id_num = mgid.split('com:')[1]
            new_url = 'http://www.vh1.com/video/play.jhtml?id=' + id_num
        if not new_url:
            continue
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
# This function finds the mgid number(id_num) and pulls the mrss feed to see how many parts it has 
@route(PREFIX + '/partscheck', parts=int)
def PartsCheck(url):
    try:
        id_num = RE_VIDID.search(url).group(1)
        data = XML.ElementFromURL(MRSS_FEED %id_num, cacheTime = CACHE_1DAY)
        item_list = data.xpath('//item')
        # YOU COULD ALSO PICK UP THE ALTERNATE TITLE HERE
        try: alt_title = data.xpath('//title')[0].text
        except: alt_title = None
        parts = len(item_list)
    except:
        id_num = RE_VIDID2.search(url).group(1)
        parts=1
        alt_title = ''

    str_parts = str(parts)
    #Log('the value of parts is %s and the value of id_num is %s' %(str_parts, id_num))
    #Log('the value of alt_title is %s' %alt_title)
    return (parts, id_num, alt_title)
#####################################################################################
# This function builds a new url to work with the parts variable in the URL service
# If there is more than one part, it will creates a URL with a parts extension that can be used by the MediaObject in the URL service
@route(PREFIX + '/buildurl', parts=int)
def BuildUrl(url):
    (parts, id_num, alt_title) = PartsCheck(url)
    if parts > 1:
        new_url = PARTS_URL %(id_num, parts)
    elif parts == 1:
        new_url = 'http://www.vh1.com/video/play.jhtml?id=' + id_num
    else:
        new_url = None

    return (new_url, alt_title)
