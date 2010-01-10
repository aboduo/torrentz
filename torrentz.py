#!/usr/bin/python env
#
# Automagic torrent url download
# powered by www.torrentz.com and some urllib/feedparser magic
# FIXME: nice getopts instead of this crap
# FIXME: regexp for string matching
#
# -- (c) 2010 mathieu.geli@gmail.com
#

import urllib,feedparser,sys,os


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    RED  = '\033[31m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1;1m'

    def disable(self):
        self.HEADER = ''
        self.BLUE = ''
        self.GREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
	slef.BOLD = ''

def trackerfindurl(tracker, page):
	if DEBUG: print "trackerfindurl(%s, page)" % tracker
	begin = page.find(tracker)
	if DEBUG: print "begin:", begin
	ofs = page[begin:].find(">")
	if DEBUG: print "ofs:", ofs
	if begin == -1 or ofs == -1:
		print "Sorry, no tracker link found :-("
		return ''
	else:
		return page[begin:begin+ofs].split()[0]


def trackerextracturl(match_begin, match_end, page):
	if DEBUG: print "trackerextracturl(%s, %s, page)" % (match_begin, match_end)
	begin = page.find(match_begin)
	if DEBUG: print "begin:", begin
	ofs  = page[begin:].find(match_end)
	if DEBUG: print "ofs:", ofs
	if begin == -1 or ofs == -1:
		return ''
	else:
		return page[begin:begin+ofs]


if sys.argv.__len__() != 4:
	print "usage: %s search_query team tracker" % sys.argv[0]
	print " * search_query: double-quoted strings separated with spaces, e.g \"Dollhouse s02e10\""
	print " * team: torrent team or none for all, e.g: eztv"
	print " * tracker: torrent site, e.g: bt-chat, thepiratebay, ..."
	print ""
	print "Example:"
	print "$ python torrentz.py \"linux iso\" none tpb"
	print "0:	Linux Mint 8 Helena iso                            		 (688 Mb) S: 637  P: 50"
	print "1:	Ubuntu v9 04 desktop amd64 CD iso FINAL            		 (696 Mb) S: 216  P: 4"
	print "2:	ubuntu 8 10 desktop i386 iso                       		 (698 Mb) S: 132  P: 2"
	print "3:	Linux Mint 8 Universal \\\Helena\\\ iso            		 (1070 Mb) S: 105  P: 16"
	print "4:	CrunchBang Linux 9 04 01 32bit crunchbang 9 04 01  		 (620 Mb) S: 60  P: 18"
	print "5:	kubuntu 8 10 desktop amd64 iso                     		 (695 Mb) S: 7  P: 1"
	print "Which torrent to retrieve ? : _"
	print ""
	print "Downloaded torrent file goes into a place defined by the pytnon var destdir."
	print "Ususally it will be rtorrent auto-download directory..."
	sys.exit(-1)

# feed_verifiedP means give us RSS with only verified torrents and sorted by descending peers numbers
# any other filter can be constructed via this simple syntax (i.e: verifiedS, gives only verified in HTML sorted by size)

site = "http://www.torrentz.com/feed_verifiedP"
string_max = 50
search = sys.argv[1]
team = sys.argv[2].lower()
webtracker = sys.argv[3].lower()
destdir="/home/mathieu/ftp/dl/torrents"
DEBUG=0

params = urllib.urlencode({'q' : search})
f = urllib.urlopen(site + "?%s" % params)
feed = feedparser.parse(f.read())
item_num = feed["items"].__len__()
if item_num == 0: print "Sorry, no torrents found."; sys.exit(0)

for i in range(item_num):
	item = feed["items"][i]
	title = item['title'][:string_max]
	# on veut des titres de longueurs egaux et strippes a une longueure max, donc on padde la fin avec ' '
	if item['title'].__len__() < string_max:
		title+=(string_max-item['title'].__len__())*' '
	v = item['summary_detail']['value']
	# pattern matching de size, seeds & peers a la va-vite
	size = v['Size: '.__len__(): v.find("Seed")].strip()
	seeds = v[v.find("Seeds")+'Seeds: '.__len__(): v.find("Peer")]
	peers = v[v.find("Peers")+'Peers: '.__len__(): v.find("Hash")]
	if title.lower().find(team) >= 0 or team == "none":
		printstr = "%d:\t%s \t\t (%s) S: "+bcolors.BOLD+bcolors.RED + "%s" + bcolors.ENDC + " P: "+bcolors.BOLD+bcolors.GREEN+"%s"+bcolors.ENDC
		print printstr % (i, title, size, seeds, peers)

os.write(sys.stdout.fileno(), "Which torrent to retrieve ? (or q for quit) : ")
torrent = sys.stdin.readline()
if torrent.strip() == "q": print "Bye."; sys.exit(0)
trackerindex = feed['items'][int(torrent)]['link']
title = feed['items'][int(torrent)]['title'].replace(' ', '_')

if DEBUG: print "GET %s" % trackerindex
trackers = urllib.urlopen(trackerindex)

# on doit choisir sur quel referenceur de tracker on veut aller
# bt-chat ? thepiratebay ? ...

page = trackers.read()

if webtracker == "bt-chat":
	url = trackerfindurl("http://www.bt-chat.com", page)
	url = url.replace('"', '')
	if DEBUG: print "GET %s" % url
	if url:
		page = urllib.urlopen(url)
		torrent = trackerextracturl("download.php", ">", page.read())
		if torrent == '':
			print "Sorry no url extraction worked :-("
		else:
			torrent = torrent.replace('"', '')
			torrent = "http://www.bt-chat.com/"+torrent
			if DEBUG:
				print torrent
			else:
				t = urllib.urlopen(torrent)
				FILE = open(destdir+"/"+title+".torrent", "w")
				FILE.write(t.read())
				FILE.close()
	else:
		print "Sorry no tracker found in torrentz index :-("

if webtracker == "tpb":
	url = trackerfindurl("http://thepiratebay.org", page)
	if DEBUG: print "GET %s" % url
	if url:
		page = urllib.urlopen(url)
		torrent = trackerextracturl("http://torrents.thepiratebay.org", ".torrent", page.read())
		if torrent == '':
			print "Sorry no url extraction worked :-("
		else:
			torrent = torrent.replace('"', '')
			if DEBUG: print torrent
			else:
				t = urllib.urlopen(torrent)
				FILE = open(destdir+"/"+title+".torrent", "w")
				FILE.write(t.read())
				FILE.close()
	else:
		print "Sorry no tracker found in torrentz index :-("
	
#trackerfindurl("http://btjunkie.org", page)
#trackerfindurl("http://www.vertor.com", page)
