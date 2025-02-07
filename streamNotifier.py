#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
from playsound import playsound
import requests
import sys
import os
import webbrowser
from concurrent.futures import ThreadPoolExecutor
import threading
from configparser import ConfigParser
from modules import twitchHtmlParser
from modules import youtubeHtmlParser

debug = False

# Initialize root window
root = tk.Tk()

# Setting up file paths
#workingFilePath = os.path.abspath(os.path.realpath(__file__))
#base_path = getattr(sys, '__MEIPASS', os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

def asset_path(relativePath):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, os.path.join(ASSET_DIR, relativePath))
    return os.path.join(ASSET_DIR, relativePath)

def setupChannelListFromConfig(configListString):
    newChannelList = configListString.strip('[').strip(']')
    newChannelList = newChannelList.replace("'", '')
    newChannelList = newChannelList.split(',')
    for item in newChannelList:
        if item == '':
            newChannelList.remove(item)
    return newChannelList

def callback(url):
    webbrowser.open(url)

# Initialize config and config functions
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# Deprecated images
live_light_image = tk.PhotoImage(file=asset_path("live_light.png"))
offline_light_image = tk.PhotoImage(file=asset_path("offline_light.png"))
error_light_image = tk.PhotoImage(file=asset_path("error_light.png"))
#
twitch_live_image = tk.PhotoImage(file=asset_path("twitch-live.png"))
twitch_offline_image = tk.PhotoImage(file=asset_path("twitch-offline.png"))
youtube_live_image = tk.PhotoImage(file=asset_path("youtube-live.png"))
youtube_offline_image = tk.PhotoImage(file=asset_path("youtube-offline.png"))
edit_button_image = tk.PhotoImage(file=asset_path("edit_button.png"))
remove_button_image = tk.PhotoImage(file=asset_path("remove_button.png"))

# Refresh Animation Image Set (tkinter limitation necessitates)
refreshing_one = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_1.png"))
refreshing_two = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_2.png"))
refreshing_three = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_3.png"))
refreshing_four = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_4.png"))
refreshing_five = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_5.png"))
refreshing_six = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_6.png"))
refreshing_seven = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_7.png"))
refreshing_eight = tk.PhotoImage(file=asset_path("refreshAnim\\refreshFrame_8.png"))
refreshing_frame_list = [refreshing_one, refreshing_two, refreshing_three, refreshing_four, refreshing_five, refreshing_six, refreshing_seven, refreshing_eight]

# Various settings that can be changed
####################################################################
# Setting that determines which stream title is displayed if user streaming on multiple sites
conflictingTitleVar = tk.StringVar()
conflictingTitleConfig = config.get('settings', 'primarysite')
conflictingTitleVar.set(conflictingTitleConfig)

# Setting that determines if noises play when things happen
streamGoneLiveSoundVar = tk.IntVar()
playSoundsConfig = config.getint('settings', 'playsound')
streamGoneLiveSoundVar.set(playSoundsConfig)

# Setting that determines if you want the window to be stickied on top of everything else
stickyWindowTopVar = tk.IntVar()
stickyWindowConfig = config.getint('settings', 'stickywindow')
stickyWindowTopVar.set(stickyWindowConfig)

# Setting up variables for use between functions
# Dictionary that contains live statuses per channel name
channelLiveStatusDict = {}

# Gets config file list of channels
channelList = setupChannelListFromConfig(config.get('info','channels'))
channelList = [channel.lower().strip(' ') for channel in channelList]

# Lists that will contain Labels to make dynamic on each boot up
channelNameLabels = []
channelLiveLabelsTwitch = []
channelLiveLabelsYoutube = []
streamTitleLabels = []
channelNameXButtons = []
channelNameEditButtons = []

# Fonts
twitch_font = ('Arial', 10, 'bold')
youtube_font = ('Roboto', 10, 'bold')
channel_name_font = ('Helvetica', 10, 'bold')

# Column variables
extra_button_column = 0 # Uses 0-1 for extra buttons
channel_name_column = 2
twitch_live_status_column = 3
youtube_live_status_column = 4
title_column = 5

# Flags


def playStreamWentLiveSound():
    print(asset_path('assets\\liveNotification.mp3'))
    threading.Thread(target=playsound(asset_path('assets\\liveNotification.mp3')), daemon=True).start()

def setNewSettings(primarySite, playSounds, stickyWindow):
    settingsConfig = ConfigParser()
    settingsConfig.read(asset_path('config.ini'))
    settingsConfig.set('settings', 'primarysite', primarySite)
    global conflictingTitleConfig
    conflictingTitleConfig = primarySite
    settingsConfig.set('settings', 'playsound', str(playSounds))
    global playSoundsConfig
    playSoundsConfig = playSounds
    settingsConfig.set('settings', 'stickywindow', str(stickyWindow))
    global stickyWindowConfig 
    stickyWindowConfig = stickyWindow
    if os.name == 'nt' and stickyWindowConfig:
        root.call("wm", "attributes", ".", "-topmost", "true")
    elif os.name == 'nt' and not stickyWindowConfig:
        root.call("wm", "attributes", ".", "-topmost", "false")
    with open(asset_path('config.ini'), 'w') as f:
        settingsConfig.write(f)

#Building additional windows when requested
def buildSettingsWindow():
    settingsWindow = tk.Toplevel(root)
    settingsWindow.title("Settings")
    
    settingsFrame = ttk.Frame(settingsWindow)
    settingsFrame.grid(row=0, column=0, sticky="nsew")

    conflictingTitleLabel = tk.Label(settingsFrame, text='Title Priority')
    conflictingTitleDropdown = tk.OptionMenu(settingsFrame, conflictingTitleVar, 'Twitch', 'Youtube')

    streamGoneLiveSoundCheckbox = tk.Checkbutton(settingsFrame, text="Play Sounds", variable=streamGoneLiveSoundVar)

    stickyWindowCheckbox = tk.Checkbutton(settingsFrame, text="Always On Top", variable=stickyWindowTopVar)

    applyButton = tk.Button(settingsFrame, text='Apply Changes', command=lambda:setNewSettings(conflictingTitleVar.get(), streamGoneLiveSoundVar.get(), stickyWindowTopVar.get()))

    conflictingTitleLabel.grid(row=1, column=1, padx=5, pady=5)
    conflictingTitleDropdown.grid(row=1, column=2, pady=5)
    streamGoneLiveSoundCheckbox.grid(row=2, column=1, padx=5, pady=5)
    stickyWindowCheckbox.grid(row=3, column=1, padx=5, pady=5)
    applyButton.grid(row=4, column=1,padx=5, pady=5)

def buildHelpWindow():
    helpWindow = tk.Toplevel(root)
    helpWindow.title("Get Some Help")

    helpFrame = ttk.Frame(helpWindow)
    helpFrame.grid(row=0, column=0, sticky="nsew")

    redXImgLabel = tk.Label(helpFrame, image=remove_button_image)
    redXHelpLabel = tk.Label(helpFrame, text="Removes the channel on the same row.")
    redXImgLabel.grid(row=0, column=0)
    redXHelpLabel.grid(row=0, column=1)

    editImgLabel = tk.Label(helpFrame, image=edit_button_image)
    editHelpLabel = tk.Label(helpFrame, text="Opens GUI to edit channel name on the same row.")
    editImgLabel.grid(row=1, column=0)
    editHelpLabel.grid(row=1, column=1)

    #sarcasmLabel = tk.Label(helpFrame, text='You can probably figure the rest out, or open an issue on GitHub if you really want.')
    #sarcasmLabel.grid(row=2, column=2)

def buildAboutWindow():
    aboutWindow = tk.Toplevel(root)
    aboutWindow.title("About")

    aboutFrame = ttk.Frame(aboutWindow)
    aboutFrame.grid(row=0, column=0, sticky="nsew")

    authorLabel = tk.Label(aboutFrame, text="This program was developed by Logan Vogt.\n Please don't yell at me if it sucks, I'm just a little guy.")
    authorLabel.grid(row=0, column=0)

def updateChannelListConfig():
    channelListConfig=ConfigParser()
    channelListConfig.read(asset_path('config.ini'))
    channelListConfig.set('info', 'channels', str(channelList))
    with open(asset_path('config.ini'), 'w') as f:
        channelListConfig.write(f)

def addNewChannel(newChannelName, addChannelWindow):
    newChannelName = newChannelName.lower().replace(' ', '')
    if not newChannelName:
        addChannelWindow.children['!frame'].children['!label'].configure(text='Text box is empty!')
    elif newChannelName in channelList:
        addChannelWindow.children['!frame'].children['!label'].configure(text='Channel already in list!')
    else:
        channelList.append(newChannelName)
        channelNameLabels.append(tk.Label(content_frame, text=newChannelName, font=channel_name_font))
        channelLiveLabelsTwitch.append(tk.Label(content_frame, image=error_light_image))
        channelLiveLabelsYoutube.append(tk.Label(content_frame, image=error_light_image))
        streamTitleLabels.append(tk.Label(content_frame))
        channelLiveStatusDict[newChannelName] = [False, False, '', '']
        channelNameLabels[len(channelNameLabels)-1].grid(row=len(channelList)+1, column=channel_name_column)
        channelLiveLabelsTwitch[len(channelLiveLabelsTwitch)-1].grid(row=len(channelList)+1, column=twitch_live_status_column)
        channelLiveLabelsYoutube[len(channelLiveLabelsYoutube)-1].grid(row=len(channelList)+1, column=youtube_live_status_column)
        streamTitleLabels[len(streamTitleLabels)-1].grid(sticky='W', row=len(channelList)+1, column=title_column)
        channelNameXButtons.append(tk.Button(content_frame, image=remove_button_image, command=lambda j=newChannelName:removeChannel(j)))
        channelNameXButtons[len(channelNameXButtons)-1].grid(row=len(channelList)+1, column=extra_button_column, pady=5)
        channelNameEditButtons.append(tk.Button(content_frame, image=edit_button_image, command=lambda j=newChannelName:(buildEditChannelNameWindow(j))))
        channelNameEditButtons[len(channelNameEditButtons)-1].grid(row=len(channelList)+1, column=extra_button_column+1)
        addButton.grid(row=len(channelList)+2, column=extra_button_column+2)
        refreshStreamerList(channelList, channelLiveLabelsTwitch, channelLiveLabelsYoutube, refreshButtonStatusLabel, streamTitleLabels, False)
        updateChannelListConfig()

def removeChannel(channelToRemove):
    if channelToRemove not in channelList:
        pass
    else:
        channelToRemoveIndex = channelList.index(channelToRemove)
        channelList.remove(channelToRemove)
        channelNameLabels.remove(channelNameLabels[channelToRemoveIndex])
        channelLiveLabelsTwitch.remove(channelLiveLabelsTwitch[channelToRemoveIndex])
        channelLiveLabelsYoutube.remove(channelLiveLabelsYoutube[channelToRemoveIndex])
        streamTitleLabels.remove(streamTitleLabels[channelToRemoveIndex])
        channelNameXButtons.remove(channelNameXButtons[channelToRemoveIndex])
        channelNameEditButtons.remove(channelNameEditButtons[channelToRemoveIndex])
        for element in content_frame.grid_slaves():
            if int(element.grid_info()['row'] == channelToRemoveIndex+2):
                element.grid_forget()
            elif int(element.grid_info()['row'] > channelToRemoveIndex+2):
                element.grid(row=element.grid_info()['row']-1, column=element.grid_info()['column'])
                if element['text'] == 'X':
                    element.configure(command=lambda i=element.grid_info()['row']:removeChannel(channelToRemove))
        updateChannelListConfig()

def editChannelName(channelToRename, newChannelName, renameWindow):
    newChannelName = newChannelName.lower().replace(' ', '')
    if channelToRename not in channelList:
        renameWindow.children['!frame'].children['!label'].configure(text='This shouldn\'t ever be seen')
    elif not newChannelName: 
        renameWindow.children['!frame'].children['!label'].configure(text='Textbox is empty!')
    elif newChannelName in channelList:
        renameWindow.children['!frame'].children['!label'].configure(text='Channel already in list!')
    else:
        channelToRenameIndex = channelList.index(channelToRename)
        channelList[channelToRenameIndex] = newChannelName
        channelNameLabels[channelToRenameIndex].configure(text=newChannelName.lower())
        channelLiveStatusDict[newChannelName] = channelLiveStatusDict.pop(channelToRename)
        channelNameXButtons[channelToRenameIndex].configure(command=lambda j=newChannelName: removeChannel(j))
        channelNameEditButtons[channelToRenameIndex].configure(command=lambda j=newChannelName: buildEditChannelNameWindow(j))
        renameWindow.destroy()
        updateChannelListConfig()
        refreshStreamerList(channelList, channelLiveLabelsTwitch, channelLiveLabelsYoutube, refreshButtonStatusLabel, streamTitleLabels, False)

def buildEditChannelNameWindow(channelToRename):
    editChannelWindow = tk.Toplevel(root)
    #editChannelWindow.geometry("160x100")
    editChannelWindow.title("Edit")

    editChannelFrame = ttk.Frame(editChannelWindow)
    editChannelFrame.grid(row=0, column=0)

    editChannelPromptString = 'Renaming \"' + channelToRename + "\""
    editChannelPrompt = tk.Label(editChannelFrame, text=editChannelPromptString)
    editChannelPrompt.grid(row=1, column=1, padx=10)

    editChannelTextEntry = tk.Entry(editChannelFrame)
    editChannelTextEntry.grid(row=2, column=1, padx=10, pady=5)
    editChannelTextEntry.focus()

    editChannelButton = tk.Button(editChannelFrame, text='Change', command=lambda:editChannelName(channelToRename, editChannelTextEntry.get(), editChannelWindow))
    editChannelButton.bind('<Return>', lambda:editChannelName(channelToRename, editChannelTextEntry.get(), editChannelWindow))
    editChannelButton.grid(row=3, column=1, padx=10)

def buildAddChannelWindow():
    addChannelWindow = tk.Toplevel(root)
    addChannelWindow.geometry("200x100")
    addChannelWindow.title("Add")

    addChannelFrame = ttk.Frame(addChannelWindow)
    addChannelFrame.grid(row=0, column=0)

    newChannelPrompt = tk.Label(addChannelFrame, text='Channel name to add')
    newChannelPrompt.grid(row=1, column=1, padx=40)

    newChannelTextEntry = tk.Entry(addChannelFrame)
    newChannelTextEntry.grid(row=2, column=1, padx=40)
    newChannelTextEntry.focus()

    newChannelAddButton = tk.Button(addChannelFrame, text='Add channel', command=lambda:addNewChannel(newChannelTextEntry.get(), addChannelWindow))
    newChannelAddButton.bind('<Return>', lambda:addNewChannel(newChannelTextEntry.get(), addChannelWindow))
    newChannelAddButton.grid(row=3, column=1, padx=40)

# Setting up details of main window
####################################################################
root.geometry("400x400")
if os.name == 'nt' and stickyWindowConfig:
    root.wm_attributes("-topmost", 1)

defaultBgColor = root.cget('bg')

menuBar = tk.Menu(root)
settingsMenu = tk.Menu(menuBar, tearoff=0)
settingsMenu.add_command(label="Settings", command=lambda:buildSettingsWindow())
menuBar.add_cascade(label="Options", menu=settingsMenu)

helpMenu = tk.Menu(menuBar, tearoff=0)
helpMenu.add_command(label="Help", command=lambda:buildHelpWindow())
helpMenu.add_command(label="About", command=lambda:buildAboutWindow())
menuBar.add_cascade(label="Help", menu=helpMenu)

root.config(menu=menuBar)

refreshTimer = 60000*5

frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")

canvas = tk.Canvas(frame)
Vscrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
Hscrollbar = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)

canvas.configure(yscrollcommand=Vscrollbar.set)
canvas.configure(xscrollcommand=Hscrollbar.set)

content_frame = ttk.Frame(canvas)
content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

refreshButtonStatusLabel = tk.Label(content_frame, text = '')
addButton = tk.Button(content_frame, text='Add Channel', command=lambda:buildAddChannelWindow())

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

canvas.create_window((0, 0), window=content_frame, anchor='nw')
canvas.grid(row=0, column=0, sticky='nsew')
Vscrollbar.grid(row=0, column=4, sticky='ns')
Hscrollbar.grid(row=1000, column=0, sticky='we')
####################################################################

#Doesn't really do anything to great effect right now, but might be useful in future for CAPTCHA issues.
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

def get_response(channelName):
    liveStatusList = [channelName, 'Offline', 'Offline', '', '', '']
    twitchUrlParser = twitchHtmlParser.twitchHtmlParser()
    youtubeUserUrlParser = youtubeHtmlParser.youtubeHtmlParser('user')
    if not channelName == 'debugchanneltw' or not channelName == 'debugchannelyt' or not channelName == 'debugchannelboth':
        twitchUrlResponse = requests.get('https://www.twitch.tv/' + channelName, headers=headers).content.decode('utf-8')
        youtubeUserUrlResponse = requests.get('https://www.youtube.com/@' + channelName, headers=headers).content.decode('utf-8')
        #Temporarily made Google mad at me. Hopefully it goes away next time I open this. CAPTCHA issues from accidentally spamming requests.
        #Maybe find a way to get around that in future.
        #youtubeUrlResponse = ''

        if 'isLiveBroadcast' in twitchUrlResponse:
            liveStatusList[1] = 'Live'
            twitchUrlParser.feed(twitchUrlResponse)
            liveStatusList[3] = twitchUrlParser.data
        if 'Tap to watch live' in youtubeUserUrlResponse:
            liveStatusList[2] = 'Live'
            youtubeUserUrlParser.feed(youtubeUserUrlResponse)
            livestreamVideoID = youtubeUserUrlParser.data
            youtubeVideoUrlParser = youtubeHtmlParser.youtubeHtmlParser('video')
            youtubeVideoUrlResponse = requests.get('https://www.youtube.com/watch?v=' + str(livestreamVideoID)).content.decode('utf-8')
            youtubeVideoUrlParser.feed(youtubeVideoUrlResponse)
            liveStatusList[4] = youtubeVideoUrlParser.data
            liveStatusList[5] = livestreamVideoID

    return liveStatusList

def _on_mousewheel(event):
   canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def main():

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    root.title('Streamer Statuses')

    # Aesthetics
    invisibleLabelLeft = tk.Label(content_frame, text='', padx=20)
    invisibleLabelLeft.grid(row=0, column=0)

    # Label widgets
    label = tk.Label(content_frame, text='Channels')
    twitchLabel = tk.Label(content_frame, text='Twitch')
    youtubeLabel = tk.Label(content_frame, text='Youtube')
    label.grid(row=1, column=channel_name_column)
    twitchLabel.grid(row=1, column=twitch_live_status_column)
    youtubeLabel.grid(row=1, column=youtube_live_status_column, padx=12)

    # Don't fully understand how the value of max_workers affects efficiency. Investigate?
    with ThreadPoolExecutor() as p:
        responses = p.map(get_response, channelList)
        for response in responses:
            channelLiveStatusDict[response[0]] = response[1:]

    for i in range(0, len(channelList)):

        currentChannel = channelList[i]

        # Setting up the labels for the channel index
        streamTitleLabels.append(tk.Label(content_frame))
        streamTitleLabels[i].grid(sticky='W', row=i+2, column=title_column)

        channelNameLabels.append(tk.Label(content_frame, text=channelList[i], font=channel_name_font))
        channelNameLabels[i].grid(row=i+2, column=channel_name_column)

        channelLiveLabelsTwitch.append(tk.Label(content_frame, padx=5))
        channelLiveLabelsTwitch[i].grid(row=i+2, column=twitch_live_status_column)
        ##############################################
        
        channelInfo = channelLiveStatusDict[channelList[i]]

        if 'Live' == channelInfo[0]:
            channelLiveLabelsTwitch[i].configure(image=twitch_live_image)
            tempUrlTw = 'http://www.twitch.tv/' + str(channelList[i])
            channelLiveLabelsTwitch[i].bind("<Button-1>", lambda event, j=tempUrlTw: callback(j))
            channelLiveLabelsTwitch[i].configure(cursor='hand2')
            if channelInfo[2]:
                if ('Offline' == channelInfo[1]) or ('Twitch' == conflictingTitleConfig):
                    streamTitleLabels[i].configure(text=channelInfo[2], bg='purple', fg='white', font=twitch_font, justify='left')
        else:
            channelLiveLabelsTwitch[i].configure(image=twitch_offline_image)

        channelLiveLabelsYoutube.append(tk.Label(content_frame, padx=5))
        channelLiveLabelsYoutube[i].grid(row=i+2, column=youtube_live_status_column, padx=8)

        if 'Live' == channelInfo[1]:
            channelLiveLabelsYoutube[i].configure(image=youtube_live_image)
            tempUrlYt = 'http://www.youtube.com/watch?v=' + channelInfo[4]
            channelLiveLabelsYoutube[i].bind("<Button-1>", lambda event, j=tempUrlYt: callback(j))
            channelLiveLabelsYoutube[i].configure(cursor='hand2')
            if channelInfo[3]:
                if ('Offline' == channelInfo[0]) or ('Youtube' == conflictingTitleConfig):
                    streamTitleLabels[i].configure(text=channelLiveStatusDict[channelList[i]][3], bg='red', fg='white', font=youtube_font, justify='left')
        else:
            channelLiveLabelsYoutube[i].configure(image=youtube_offline_image)

        channelNameXButtons.append(tk.Button(content_frame, image=remove_button_image, command=lambda channelName=currentChannel:removeChannel(channelName)))
        channelNameXButtons[i].grid(row=i+2, column=extra_button_column)

        channelNameEditButtons.append(tk.Button(content_frame, image=edit_button_image, command=lambda channelName=currentChannel:(buildEditChannelNameWindow(channelName))))
        channelNameEditButtons[i].grid(row=i+2, column=extra_button_column+1)


    # Button widget
    refreshButton = tk.Button(content_frame, text="Refresh", command=lambda:refreshStreamerList(channelList, channelLiveLabelsTwitch, channelLiveLabelsYoutube, refreshButtonStatusLabel, streamTitleLabels, True))
    refreshButton.grid(row=0, column=extra_button_column+2, pady=10)
    refreshButtonStatusLabel.grid(row=0, column=extra_button_column+3, pady=10)

    addButton.grid(row=len(channelList)+2, column=extra_button_column+2, pady=10)

    # Setting up refresh to check once each minute
    root.after(refreshTimer, refreshStreamerList, channelList, channelLiveLabelsTwitch, channelLiveLabelsYoutube, refreshButtonStatusLabel, streamTitleLabels, False)

    # Start GUI loop
    root.mainloop()


def refreshStreamerList(channels:list, twLabels, ytLabels, statusLabel, titleLabels, buttonClicked):

    # I want this to be an animation but am too stupid to make it happen rn
    statusLabel.configure(image=refreshing_frame_list[0])
    statusLabel.update_idletasks()

    # Dictionary that contains live statuses per channel name
    refreshLiveStatusDict = {}

    with ThreadPoolExecutor() as p:
        responses = p.map(get_response, channels)
        for response in responses:
            refreshLiveStatusDict[response[0]] = response[1:]

    for i in range(0, len(channels)):

        currentChannelName = channels[i]

        channelRefreshInfo = refreshLiveStatusDict[currentChannelName]
        channelExistingInfo = channelLiveStatusDict[currentChannelName]

        if 'Live' == channelRefreshInfo[0]:
            if 'Offline' == channelExistingInfo[0]:
                twLabels[i].configure(image=twitch_live_image)
                tempUrlTw = 'http://www.twitch.tv/' + str(channelList[i])
                twLabels[i].bind("<Button-1>", lambda event, j=tempUrlTw: callback(j))
                twLabels[i].configure(cursor='hand2')
                twLabels[i].update_idletasks()
                if playSoundsConfig:
                    playStreamWentLiveSound()
                channelExistingInfo[0] = True
            if 'Live' == channelRefreshInfo[1]:
                if conflictingTitleConfig == 'Youtube':
                    titleLabels[i].configure(text=channelRefreshInfo[3], bg='red', fg='white', font=youtube_font, justify='left')
                else:
                    titleLabels[i].configure(text=channelRefreshInfo[2], bg='purple', fg='white', font=twitch_font, justify='left')
            else:
                if conflictingTitleConfig == 'Twitch':
                    titleLabels[i].configure(text=channelRefreshInfo[2], bg='purple', fg='white', font=twitch_font, justify='left')

        else:
            twLabels[i].configure(image=twitch_offline_image)
            if 'Live' == channelExistingInfo[0]:
                channelExistingInfo[0] = 'Offline'
                twLabels[i].configure(cursor='arrow')
                twLabels[i].unbind('<Button-1>')
            if 'Offline' == channelRefreshInfo[1]:
                titleLabels[i].configure(text='', bg=defaultBgColor)

        if 'Live' == channelRefreshInfo[1]:
            if 'Offline' == channelExistingInfo[1]:
                ytLabels[i].configure(image=youtube_live_image)
                tempUrlYt = 'http://www.youtube.com/watch?v=' + channelRefreshInfo[4]
                ytLabels[i].bind("<Button-1>", lambda event, j=tempUrlYt: callback(j))
                ytLabels[i].configure(cursor='hand2')
                ytLabels[i].update_idletasks()
                if playSoundsConfig:
                    playStreamWentLiveSound()
                channelExistingInfo[1] = True
            if 'Live' == channelRefreshInfo[0]:
                if conflictingTitleConfig == 'Twitch':
                    titleLabels[i].configure(text=channelRefreshInfo[2], bg='purple', fg='white', font=twitch_font, justify='left')
                else:
                    titleLabels[i].configure(text=channelRefreshInfo[3], bg='red', fg='white', font=youtube_font, justify='left')
            else:
                titleLabels[i].configure(text=channelRefreshInfo[3], bg='red', fg='white', font=youtube_font, justify='left')

        else:
            ytLabels[i].configure(image=youtube_offline_image)
            if 'Live' == channelExistingInfo[1]:
                channelExistingInfo[1] = 'Offline'
                ytLabels[i].configure(cursor='arrow')
                ytLabels[i].unbind('<Button-1>')
            if 'Offline' == channelRefreshInfo[0]:
                titleLabels[i].configure(text='', bg=defaultBgColor)

    statusLabel.configure(image='')

    isRefreshing = False

    # We only want to refresh after refreshTimer length from the initial check, not every time we push the refresh button
    # That would lead to many overlapping checks and probably spam websites with requests
    if not buttonClicked:
        root.after(refreshTimer, refreshStreamerList, channels, twLabels, ytLabels, statusLabel, titleLabels, False)

if __name__ == "__main__":
    main()