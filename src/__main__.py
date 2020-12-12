import os, pickle, time, re
from pathlib import Path
from youtubesearchpython import SearchVideos, SearchPlaylists
from termcolor import colored

# from IPython import embed; embed()

class MyYoutubePlayer:

    def __init__(self):
        self.history_dir = str(Path.home()) + '/.config/mini-youtube-player/history'
        self.video_playback = False
        self.history = None
        self.results = None
        self.search_string = ''
        self.player = 'mpv'
        self.player = 'ydl-vlc'
        self.player = 'cvlc'
        self.player = 'ydl-mpvh'
        self.player = 'ydl-mpv'

        # print('\n(Video-Playback is OFF)')
        # print('Enter: [H]elp, [q]uit, [v]ideo on/off, [number] to play audio/video, [text] to search videos on youtube')
        print(colored('''
   ---------------------
  | mini-youtube-player |
   ---------------------''', 'cyan'))
        
        self.main()


    def get_history_from_file(self):
        if Path(self.history_dir).is_file():
            self.history = []
            try:
                with open(self.history_dir, 'rb') as f:
                    self.history = pickle.load(f)
                #print('History loaded')
            except EOFError:
                pass


    def print_help(self):
        print(colored('''
    This is Mini-Youtube-Player.
    
    Main features:
    • It only works from the command line.
    • It does not use any Google or Youtube APIs, hence no struggle with their API-Keys and limitations.
    • You can use it to search youtube for videos or playlists, view audio or video, or download them.
    • It can store a local play history.
    • It uses colored output for videos that you have already played.
    
    Additional packages required: youtubesearchpython from https://github.com/alexmercerind/youtube-search-python -- thanks for the great work!!
    
    That's it. Miniyoutubeplayer is not intended to have many features.
    Instead it is intended to be simple and just work. (hopefully)
    
    Miniyoutubeplayer uses youtube-dl and mpv to playback youtube videos.
    One drawback is that the amount of time you can scroll forward a video is very limited.
    One advantage is that loading times are usually very quick - depending on your network speed.
    
    To overcome this drawback you can use 'v # mpv' or 'v # cvlc' to directly play the video in the player without using youtube-dl.
    
    The 'v # hd' command will try to find video in higher quality than standard. This will need ffmpeg in addition to youtube-dl and mpv.
        
    If you want me to save a history of played videos, create the empty file ~//.config/miniyoutubeplayer/history with read/write rights set to your user.
    Miniyoutubeplayer will automatically use this file once it exists.
    
    For playback we use the mpv media player and you can use its default shortkeys while playing video or audio,
    including: Space for play/pause, Arrow keys for seek forward/backward, f for fullscreen, q for quit etc.
    For a full list of commands, type 'man mpv' and read the INTERACTIVE CONTROL section.
    
    Some shortcuts for quicker use:
    #: Will immediately play the given number in the viewing-mode that is set (default is audio). You don't have to use 'a #' or 'v #'.
    v: Will toggle the viewing-mode to 'video' or 'audio'.
    text: This will search for videos containing 'text'.
    
    Have fun.
    Don't do stuff you are not allowed to do.
    
    ''', 'magenta'))


    def add_to_history(self, video):
        self.get_history_from_file()
        if self.history is not None:
            v = video.copy()
            if 'duration' not in v:
                v['duration'] = 'Playlist'
            v['index'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            self.history.append(v)
            with open( self.history_dir, 'wb' ) as f:
                pickle.dump( self.history, f, pickle.HIGHEST_PROTOCOL )
            #print('history saved')


    def is_yt_id_in_history(self, yt_id):
        self.get_history_from_file()
        for h in self.history:
            if h['id'] == yt_id:
                return True
        return False


    def print_results(self):
        print(f'\n Search for: {self.search_string}\n')
        
        print('    #  Title' + ' '*75 + 'Time   Views  Channel           Date')
        print('  ' + '-'*128)
        
        n = 0
        for r in self.results:
            n = n + 1
            index = str(r['index'] + 1) if type(r['index']) is int else str(r['index'])
            if 'duration' in r:
                text = '  ' + index.rjust(3) \
                     + '  ' + r['title'][:75] \
                     + (' ' * (76 - int(len(r['title'][:75])))) \
                     + r['duration'].rjust(9) + '  ' \
                     + str(human_readable_size(r['views'])).rjust(5) \
                     + '  ' + r['channel'][:14].ljust(15) \
                     + '  ' + ('-' if r.get('publishTime') is None else ' ' if len(r['publishTime'].split(" ", 1)[0]) == 1 else '' ) + r['publishTime']
            else:
                text = '  ' + index.rjust(3) + '  ' + r['title'][:110] # + r['count'].rjust(9)
            if self.is_yt_id_in_history(r['id']):
                text = colored(text, 'green')
            print(text)


    def play(self, numbers, mode=None, quality=None):
        try:
            for i in numbers:
                video = self.results[i]
                #yt_id = video['id']
                yt_link = video['link']
                
                self.add_to_history(video)
                
                if 'duration' in video:
                    print(colored('\n Playing: ' + video['title'] + ' (' +  video['duration'] + ')', 'magenta'))
                else:
                    print(colored('\n Playing: ' + video['title'] + ' (Playlist)\n', 'magenta'))
                
                print(' ' + yt_link + '\n')
                
                if self.video_playback or mode == 'v':
                    if quality == 'hd':
                        os.system(f'ffmpeg -loglevel quiet -i $(youtube-dl -g {yt_link} -f 303/bestvideo) -i $(youtube-dl -g {yt_link} -f bestaudio) -f matroska -c copy - | mpv -')
                    elif self.player == 'cvlc':
                        os.system(f'cvlc -q --play-and-exit {yt_link}')
                    elif self.player == 'ydl-mpv':
                        os.system(f'youtube-dl -i {yt_link} -o - | mpv -')
                    elif self.player == 'ydl-vlc':
                        os.system(f'youtube-dl -i {yt_link} -o - | vlc -')
                    else:
                        os.system(f'mpv {yt_link}')
                else:
                    os.system(f'mpv --no-video {yt_link}')
                    #os.system(f'youtube-dl -f bestaudio {ytid} -o - | mpv -')
        except:
            pass


    def main(self):
        while True:
            
            if self.results is not None: self.print_results()
            print('''
 s *: search for * in videos.             v #: play video.                   v # mpv: use mpv player.        dv #: download video.        h: show history.
 p *: search for * in playlists.          a #: play audio.                   v # vlc: use cvlc player.       da #: download audio.        H: show Help.
   a: play all search results.         v # hd: try playing video in HD.      v # cvlc: use vlc player.        y #: copy (yank) url.''')
            i = input('\n> ')
            
            # q is for Quit
            if i == 'q':
                break
            
            # <empty> does nothing
            elif i == '':
                continue
            
            # H is for Help
            elif i == 'H':
                self.print_help()
            
            # v is to toggle video_playback on/off
            elif i == 'v':
                self.video_playback = not self.video_playback
                print(' (Video-Playback is ', 'ON' if self.video_playback else 'OFF', ')', sep='')
            
            # show history
            elif i == 'h':
                self.results = []
                self.get_history_from_file()
                if self.history is None:
                    print('\n No history is saved on this computer.')
                    self.results = None
                    continue
                for num in range(1, min(len(self.history), 20)):
                    h = self.history[-num].copy()
                    h['index'] = str(num).rjust(3) + '  ' + h['index']
                    self.results.append(h)
            
            # play all videos
            elif i == 'a':
                self.play(list(range(0,20)))
            
            # play the video using default (video/audio) mode!
            elif i.isdigit():
                self.play([int(i)-1])
            
            # play the video using v mode
            elif re.match("^v \d$", i):
                self.play([int(i[2:])-1], mode='v')
            
            # play the video using v mode in HD!
            elif re.match("^v \d hd$", i):
                self.play([int(i[2:-3])-1], mode='v', quality='hd')
            
            # play the video using a mode
            elif re.match("^a \d$", i):
                self.play([int(i[2:])-1], mode='a')
            
            # Playlist search
            elif i[:2] == 'p ':
                self.results = SearchPlaylists(i[2:], offset=1, mode='dict', max_results=20, language="en-US", region="AT").result()['search_result']
                self.search_string = i
            
            # default video search
            elif i[:2] == 's ':
                self.results = SearchVideos(i[2:], offset=1, mode='dict', max_results=19, language="en-US", region="AT").result()['search_result']
                self.search_string = i
            
            # default video search
            else:
                # breakpoint()
                self.results = SearchVideos(i, offset=1, mode='dict', max_results=19, language="en-US", region="AT").result()['search_result']
                self.search_string = i


def human_readable_size(size, decimal_places=0):
    if size == 'LIVE': return size
    size = round(size, -(len(str(size))-2))
    for unit in [' ', 'K', 'M', 'B', 'T']:
        if size < 1000 or unit == 'T':
            break
        size /= 1000
    return f"{size:.{decimal_places}f}{unit}"

def main():
    pl = MyYoutubePlayer()

if __name__ == "__main__":
    main()
