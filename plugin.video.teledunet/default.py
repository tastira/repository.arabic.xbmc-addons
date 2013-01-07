from operator import itemgetter
import os
from xbmcswift2 import Plugin
from resources.lib.teledunet.api import TeledunetAPI
import xbmcplugin,xbmcgui,xbmcaddon

PLUGIN_NAME = 'Teledunet.com'
PLUGIN_ID = 'plugin.video.teledunet'
plugin = Plugin(PLUGIN_NAME, PLUGIN_ID, __file__)

CACHE_DURATION_MINUTES = 7
cache = plugin.get_storage('channels_cache.txt', TTL=CACHE_DURATION_MINUTES)
api = TeledunetAPI(cache)

@plugin.route('/')
def list_categories():

    items = [{
        'label': 'All',
        'path': plugin.url_for('list_all_channels')
    }, {
        'label': 'Browse by Category',
        'path': plugin.url_for('browse_by_category')
    }, {
        'label': 'Browse by Network',
        'path': plugin.url_for('browse_by_network')
    }]

    return items

@plugin.route('/list/all/')
def list_all_channels():
    channels = api.get_channels()

    for channel in channels:
        channel['path'] = plugin.url_for('play_video', url=channel['path'])
        channel['is_playable'] = True

    return channels

@plugin.route('/list/browse_by_category/')
def browse_by_category():
    categories = api.get_channels_grouped_by_category()

    for category in categories:
        category['path'] = plugin.url_for('list_channels_for_category', category_name=category['category_name'])
        del category['category_name']

    return sorted(categories, key=itemgetter('label'))

@plugin.route('/list/browse_by_network/')
def browse_by_network():
    networks = api.get_channels_grouped_by_network()

    for network in networks:
        network['path'] = plugin.url_for('list_channels_for_network', network_name=network['network_name'])
        del network['network_name']

    return sorted(networks, key=itemgetter('label'))

@plugin.route('/list/category/<category_name>')
def list_channels_for_category(category_name):
    channels = api.get_channels()
    category_channels = api.get_channels_for_category(channels, category_name)

    for channel in category_channels:
        channel['path'] = plugin.url_for('play_video', url=channel['path'])
        channel['is_playable'] = True

    return sorted(category_channels, key=itemgetter('label'))

@plugin.route('/list/network/<network_name>')
def list_channels_for_network(network_name):
    channels = api.get_channels()
    network_channels = api.get_channels_for_network(channels, network_name)

    for channel in network_channels:
        channel['path'] = plugin.url_for('play_video', url=channel['path'])
        channel['is_playable'] = True

    return sorted(network_channels, key=itemgetter('label'))

@plugin.route('/play/<url>/')
def play_video(url):
    print 'website url'
    print url
    rtmp_params = api.get_rtmp_params(url)

    def rtmpdump_output(rtmp_params):
        return (
            'rtmpdump.exe '
            '--rtmp "%(rtmp_url)s" '
            '--app "%(app)s" '
            '--swfUrl "%(swf_url)s" '
            '--playpath "%(playpath)s" '
            '-o test.flv'
        ) % rtmp_params

    def xbmc_output(rtmp_params):
        return (
            '%(rtmp_url)s '
            'app=%(app)s '
            'swfUrl=%(swf_url)s '
            'playpath=%(playpath)s '
            'live=%(live)s '
            'swfVfy=%(swfVfy)s '
        ) % rtmp_params

    playback_url = xbmc_output(rtmp_params)
    plugin.log.info('RTMP cmd: %s' % rtmpdump_output(rtmp_params))
    plugin.log.info('XBMC cmd: %s' % xbmc_output(rtmp_params))
    return plugin.set_resolved_url(playback_url)

def _art(file, *args):
    return os.path.join(plugin.addon.getAddonInfo('path'), file, *args)

if __name__ == '__main__':
    plugin.run()
