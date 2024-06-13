# DFLogViewer

Hi, it's Ryu here, on my newly-created GitHub account called glumprong, which is also my Twitch username incidentally, although I haven't streamed any DF yet ha ha.

I created this viewer so that log files can be viewed via OBS Browser Source with transparent overlay. You can also use it as a general announcement viewer in the browser. 
It is inspired by the work done on AnnouncementWindow, AnnouncementWindow+, and the updates to filters.txt for the Steam version of Dwarf Fortress. You can find those 
various things at these addresses:

- https://github.com/NuAoA/AnnouncementWindow
- https://github.com/BrachystochroneSD/AnnouncementWindow
- https://www.reddit.com/r/dwarffortress/comments/10qbm07/using_announcementwindow_for_game_logs_with_df/

## Installation

I am not releasing a "release", binary, deb, etc, for this repo. You'll need Python 3. You'll need to install flask and watchdog via pip or alternative
tool. It's recommended to create a virtual environment using venv or similar. You can use the system Python if you like. 

Then you need to tell app.py where your stuff is. That should be pretty straightforward, you'll need to get your game log file path, and the other 2 things are local to
this install, so that should be simple enough too. Then you just need to run app.py in a terminal.

The server runs on localhost:4444. There is a settings page at localhost:4444/settings where you can select the font size, weight, style, and colour, for all the 
different message categories. You can also filter out categories that you don't want to see (e.g. job cancellation spam). After you save it, you'll need to reload your page at localhost:4444. 

## Info

I am not a programmer! Well I am, but I'm actually a data engineer, by trade. So, I make no excuse for the likely shitty code in here! Feel free to change it :) Perhaps
in the future I'll make a legends viewer including a map or something. But that'll be a much larger effort. :) 

Here's a screenshot. 

![Screenshot 2024-06-13 16-12-06](https://github.com/glumprong/DFLogViewer/assets/172610858/8f59fc72-a561-4870-a1f6-1539daefda3f)
