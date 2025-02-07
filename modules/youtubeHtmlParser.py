from html.parser import HTMLParser
import json

class youtubeHtmlParser(HTMLParser):
    
    def __init__(self, pageType='user'):
        super(youtubeHtmlParser, self).__init__()
        self.pageType = pageType

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        decoder = json.JSONDecoder()
        dictionary = {}
        if 'var ytInitialData' in data:
            # Parsed result has extra data that needs to be truncated for successful JSON reading.
            data = data[20:len(data)-1]
            dictionary = json.loads(data)
            self.data = youtubeHtmlParser.handle_data_struct(dictionary, self.pageType)
    
    # pageType determines what tag a page needs to find for the program to work.
    # pageType 'user' sets up to scrape and find out the URL of a currently live streamer (only works if the streamer's live status has already been checked)
    # pageType 'video' scrapes for a videos title on a given Youtube page response that is passed in
    def handle_data_struct(data_struct, pageType):
        data_struct_type = type(data_struct)
        liveID = ''
        if data_struct_type == dict:
            for key in data_struct.keys():
                liveID = youtubeHtmlParser.handle_data_struct(key, pageType)
                if not liveID:
                    liveID = youtubeHtmlParser.handle_data_struct(data_struct[key], pageType)
                if liveID == 'videoIdsFound':
                    liveID = data_struct[key][0]
                    break
                elif liveID == 'titleFound':
                    liveID = data_struct[key]['runs'][0]['text']
                    break
                elif liveID:
                    break
        elif data_struct_type == list:
            for item in data_struct:
                liveID = youtubeHtmlParser.handle_data_struct(item, pageType)
                if liveID:
                    break
        else:
            if pageType == 'user':
                if 'videoIds' in str(data_struct):
                    liveID = 'videoIdsFound'
            elif pageType == 'video':
                if 'title' in str(data_struct):
                    liveID = 'titleFound'
        return liveID  