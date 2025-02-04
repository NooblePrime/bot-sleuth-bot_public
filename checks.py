from time import time, sleep
from pprint import pprint
from imageHandling import imageSearch, sortMedia
from vars import new_line
from praw.models import Redditor
from prawcore.exceptions import TooManyRequests
from praw.models.listing.mixins.redditor import SubListing
from vars import reddit
import re
week = 604800 #How long a week is in seconds.
month = 2592000 #Same but with month

#REDACTED SECTION

def checkCommentKarma(suspect: Redditor):
    if suspect.comment_karma < 0:
        return True
    return False

def checkIfDefaultUser(suspect: Redditor):
    user = suspect.name
    upper_count = len(re.findall(r'[A-Z]', user))
    digit_count = len(re.findall(r'\d', user))
    dash_count = len(re.findall(r'-', user))
    underscore_count = len(re.findall(r'_', user))
    
    line_check = ((underscore_count > 0) ^ (dash_count > 0)) and (underscore_count < 3 and dash_count < 3)
        
    if upper_count == 2 and digit_count == 4 and line_check:
        return True
    return False

#REDACTED SECTION

def notFrontPage(item, image):
    if re.findall(rf'https://www.reddit.com/r/{item.submission.subreddit}/((hot|top|new)|(comments/{item.submission.id}))/', image) == [] and image != f'https://www.reddit.com/r/{item.submission.subreddit}/':
        return True
    return False

def repostCheck(item, constraint = None):
    submission = item.submission
    comment_string = ""
    if hasattr(submission, 'post_hint'):
        if submission.post_hint == 'image' or (hasattr(submission, 'url') and submission.url.endswith('png')) or hasattr(submission, 'media_metadata'):
            if hasattr(submission, 'post_hint'):
                source = vars(submission)['preview']['images'][0]['source']['url']
            elif hasattr(submission, 'media_metadata'):
                image_list = vars(submission)["media_metadata"]
                if len(image_list) == 1:
                    for image in image_list:
                        source = image_list[image].url
                else:
                    comment_string = "This post contains multiple images. Cheking each one individually and displaying up to the first 5 matches for each image below." + new_line
                    media_ids = sortMedia(submission.gallery_data)
                    index = 1
                    for item in media_ids:
                        search = imageSearch(image_list[item].url)
                        matches = []
                        comment_string += f'Checking image {index} for matches...' + new_line
                        for image in search:
                            if item.submission.permalink not in image and image != f'https://www.reddit.com/r/{item.submission.subreddit}/' and notFrontPage(item, image):
                                duplicate = False
                                for match in matches:
                                    if match in image:
                                        duplicate = True
                                if not duplicate:
                                    matches.append(image)
                        match_count = len(matches)
                        high = False
                        if match_count > 0:
                            i = 0
                            for url in matches:
                                comment_string += f'[Match]({url})'
                                if i == len(matches) or i > 3:
                                    break
                                elif i < len(matches) - 1 or i < 4:
                                    comment_string += ', '
                                i += 1
                            comment_string = comment_string.removesuffix(", ")
                            if high == False and match_count >= 200:
                                high = True
                        else:
                            comment_string += "No matches found." + new_line
                    if high:
                        comment_string += new_line + "Please note that popular meme templates will yield extremely high amounts of matches, even if the text is different. The matches I have provided are the closest that reverse image searching could provide. If the text is different, this is probably OC and not a repost."
                    return comment_string
            else:
                source = submission.url

            search = imageSearch(str(source))
            matches = []

            comment_string = "Checking if image is a repost..." + new_line
            if constraint == 'subreddit':
                comment_string += 'Filtering out matches that are not in this subreddit...' + new_line
                for image in search:
                    if f'https://www.reddit.com/r/{item.submission.subreddit}/' in image and notFrontPage(item, image):
                        duplicate = False
                        for match in matches:
                            if match in image:
                                duplicate = True
                        if not duplicate:
                            matches.append(image)
            elif constraint == 'reddit':
                comment_string += 'Filtering out matches that are not from Reddit...' + new_line
                for image in search:
                    if 'https://www.reddit.com/' in image and notFrontPage(item, image):
                        duplicate = False
                        for match in matches:
                            if match in image:
                                duplicate = True
                        if not duplicate:
                            matches.append(image)
            else:
                for image in search:
                    if item.submission.permalink not in image and notFrontPage(item, image):
                        matches.append(image)
            match_count = len(matches)
            if match_count > 0:
                if match_count <= 5:
                    comment_string += f'{match_count} match'
                    if match_count != 1:
                        comment_string += 'es'
                    comment_string += ' found. Displaying below.' + new_line
                else:
                    comment_string += f'{match_count} matches found. Displaying first five below.' + new_line
                index = 0
                match_urls = [f'[Match]({url})' for url in matches[:5]]
                comment_string += ', '.join(match_urls)
                if match_count >= 200:
                    comment_string += new_line + "Please note that popular meme templates will yield extremely high amounts of matches, even if the text is different. The matches I have provided are the closest that reverse image searching could provide. If the text is different, this is probably OC and not a repost."
            else:
                comment_string += "I was unable to find any matches of this image through reverse image searching. It is likely OC."
        else:
            comment_string += "Unfortunately, this post type is not currently supported for repost checks. I apologize for the inconvenience."
    else:
        comment_string = "Reddit failed to provide necessary data. Unable to analyze."
        pprint(vars(submission))
    return comment_string
