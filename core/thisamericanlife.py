import os, sys, datetime, titlecase, requests, codecs, feedparser, glob
from mutagen.id3 import APIC, TDRC, TALB, COMM, TRCK, TPE2, TPE1, TIT2, TCON, ID3
from bs4 import BeautifulSoup

_talPICURL = 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Thisamericanlife-wbez.png'
_talurl = 'http://feed.thisamericanlife.org/talpodcast'

def get_americanlife_info(epno, throwException = True, extraStuff = None, verify = True ):
    """
    Returns a tuple of title, year given the episode number for This American Life.
    """

    # first see if this episode of this american life exists...
    if extraStuff is None:
        resp = requests.get( 'http://www.thisamericanlife.org/radio-archives/episode/%d' % epno, verify = verify )
    else:
        resp = requests.get( 'http://www.thisamericanlife.org/radio-archives/episode/%d/%s' % ( epno, extraStuff ),
                             verify = verify )
    if resp.status_code != 200:
        raise ValueError("Error, could not find This American Life episode %d, because could not open webpage." % epno)
    
    enc = resp.headers['content-type'].split(';')[-1].split('=')[-1].strip().upper()
    if enc not in ( 'UTF-8', ):
        html = BeautifulSoup( unicode( resp.text, encoding=enc ), 'lxml' )
    else:
        html = BeautifulSoup( resp.text, 'lxml' )
    def get_date( date_s ):
        try:
            return datetime.datetime.strptime( date_s, '%B %d, %Y' ).date( )
        except:
            return datetime.datetime.strptime( date_s, '%b %d, %Y' ).date( )
    date_act = max(map(lambda elem: get_date( elem.text.strip( ).replace('.', '')),
                       html.find_all('span', { 'class' : 'date-display-single' })))
    year = date_act.year
    #
    title_elem_list = html.find_all('div', { 'class' : 'episode-title' } )
    if len(title_elem_list) != 1:
        if throwException:
            raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
        else: return None
    title = max(title_elem_list).text.strip()
    title = title.replace('Promo', '').strip( )
    return title, year

def get_american_life(epno, directory = '/mnt/media/thisamericanlife', extraStuff = None, verify = True ):
    """
    Downloads an episode of This American Life into a given directory.
    The description of which URL the episodes are downloaded from is given in
    http://www.dirtygreek.org/t/download-this-american-life-episodes.

    The URL is http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/epno.mp3
    
    Otherwise, the URL is http://www.podtrac.com/pts/redirect.mp3/podcast.thisamericanlife.org/podcast/epno.mp3
    """
    try:
        title, year = get_americanlife_info(epno, extraStuff = extraStuff, verify = verify)
    except ValueError as e:
        print(e)
        print('Cannot find date and title for This American Life episode #%d.' % epno)
        return

    if not os.path.isdir(directory):
        raise ValueError("Error, %s is not a directory." % directory)
    outfile = os.path.join(directory, 'PRI.ThisAmericanLife.%03d.mp3' % epno)    
    urlopn = 'http://www.podtrac.com/pts/redirect.mp3/podcast.thisamericanlife.org/podcast/%d.mp3' % epno

    resp = requests.get( urlopn, stream = True, verify = verify )
    if not resp.ok:
        urlopn = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' % epno
        resp = requests.get( urlopn, stream = True, verify = verify )
        if not resp.ok:
            print("Error, could not download This American Life episode #%d. Exiting..." % epno)
            return
    with open( outfile, 'wb') as openfile:
        for chunk in resp.iter_content(65536):
            openfile.write( chunk )
            
    mp3tags = ID3( )
    mp3tags['TDRC'] = TDRC(encoding = 0, text = [ u'%d' % year ])
    mp3tags['TALB'] = TALB(encoding = 0, text = [ u'This American Life' ])
    mp3tags['TRCK'] = TRCK(encoding = 0, text = [ u'%d' % epno ])
    mp3tags['TPE2'] = TPE2(encoding = 0, text = [ u'Ira Glass'])
    mp3tags['TPE1'] = TPE1(encoding = 0, text = [ u'Ira Glass'])
    try: mp3tags['TIT2'] = TIT2(encoding = 0, text = [ '#%03d: %s' % ( epno, title ) ] )
    except: mp3tags['TIT2'] = TIT2(encoding = 0, text = [ codecs.encode('#%03d: %s' % ( epno, title ), 'utf8') ])
    mp3tags['TCON'] = TCON(encoding = 0, text = [ u'Podcast'])
    mp3tags['APIC'] = APIC( encoding = 0, mime = 'image/png', data = requests.get( _talPICURL ).content )
    mp3tags.save( outfile )
    os.chmod( outfile, 0o644 )

def thisamericanlife_crontab( ):
    """
    This python module downloads a This American Life episode every weekend
    """

    def _get_track( filename ):
        assert( os.path.basename( filename ).endswith( '.mp3' ) ) 
        mp3tags = ID3( filename ) 
        if 'TRCK' not in mp3tags: return None 
        return int( mp3tags['TRCK'].text[0] )

    def _get_epno( entry ):
        if 'title' not in entry: return -1
        title = entry['title']
        epno = int( title.split(':')[0].strip( ) )
        return epno
    
    # get all track numbers, and find what's left
    episodes_here = set(filter(None, map(
        _get_track, glob.glob('/mnt/media/thisamericanlife/PRI.ThisAmericanLife.*mp3' ) ) ) )
    #episodes_left = set( range( 1, max( episodes_here ) + 1 ) ) - episodes_here

    #
    ## from RSS feed, find latest episode number
    d = feedparser.parse( 'http://feed.thisamericanlife.org/talpodcast' )
    epno = _get_epno( max(d['entries'], key = lambda ent: _get_epno( ent ) ) )
    if epno not in episodes_here:
        time0 = time.time( )
        logging.debug('downloading This American Life epsiode #%03d' % epno )
        try:
            thisamericanlife.get_american_life( epno )
            logging.debug("finished downloading This American Life episode #%03d in %0.3f seconds" % (
                epno, time.time( ) - time0 ) )
        except:
            print( "Could not download This American Life episode #%03d" % epno )
    else:
        print( "Already have This American Life episode #%03d" % epno )