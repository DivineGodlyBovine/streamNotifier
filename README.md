# Streaming Notifier
I tried to make this nice, but let's face it, the minute anyone else uses this it's going to fall apart at the seams, isn't it?

## How to Run
Requires an internet connection.
Currently, there is no nice way to do it. You need to clone it locally and run
```
python ./streamNotifier.py
```
Working on compiling this into a nice exe, or otherwise streamlining the process.
A good idea for Windows would be to run a batch file with that command so you can just run it that way.

## Basic Use
Click the "Add Channel" button to add another channel you want to be notified about.  Even if someone only streams on one site, this program checks both sites with the same username.
The Red X buttons remove the channel from being watched that it shares a row with.
The pencil buttons (yes, it's a pencil) opens a dialog box to let you edit the name of the row.
There's a handful of settings as well:
	Primary Site:
		Twitch or Youtube. Only matters if someone is streaming on both sites, just which stream title to display.
	Always On Top:
		Whether the GUI sticks above other programs. Be careful, this often means it will also stick on top of dialog boxes it opens.
	Enable sounds:
		Enable or disable whether you want a sound played when a stream becomes live. Plays once per channel per site on update.

## Known Bugs
- Very occasionally, a refresh will cause a Twitch channel that is online to appear offline. Another refresh fixes this, but will cause duplicate noises if the noise is enabled.
- Rarely, certain YouTube channels don't seem to work with it at all. Seems sporadic and hard to recreate.
If you have insight as to why these may be happening, please let me know via a GitHub issue. I guess you could message me but... why?

## Customization
The nice thing about the current set up is that, if you change any of the files, you can customize this locally to your liking. Do whatever you want, man. Just don't claim you made the base stuff or sell it.