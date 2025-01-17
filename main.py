from prawcore.exceptions import Forbidden, ServerError, TooManyRequests
from praw.exceptions import RedditAPIException
import threading
from time import sleep
from pprint import pprint
from checks import checkIfVisited, logVisit
from redditFunctions import attemptComment, markbot, unmarkbot
from vars import reddit, bot_statement
import re

def mentionStream():
    retry = True
    while retry:
        try:
            for item in reddit.inbox.unread(limit=500):
                info = vars(item)
                body = item.body.lower()
                if 'invitation to moderate' in item.subject:
                    try:
                        item.subreddit.mod.accept_invite()
                        print(f'Accepted invite to moderate r/{item.subreddit.display_name}')
                    except Exception as e:
                        print(f'No invite from r/{item.subreddit.display_name}')
                    item.mark_read()
                if item.new and ((info['type'] == 'username_mention') or (info['type'] == 'comment_reply' and 'u/bot-sleuth-bot' in body)):
                    if 'repost' in body:
                        if re.search(r"filter:[\s]{0,1}subreddit", body) is not None:
                            attemptComment(item.parent().author, item, True, constraint = 'subreddit')
                        elif re.search(r"filter:[\s]{0,1}reddit", body) is not None:
                            attemptComment(item.parent().author, item, True, constraint = 'reddit')
                        else:
                            attemptComment(item.parent().author, item, True)
                        print('Replied to a post!')
                        item.mark_read()
                    elif 'u/bot-sleuth-bot' in body and info['type'] == 'comment_reply':
                        try:
                            item.reply("Why are you trying to check if I'm a bot? I've made it pretty clear that I am." + bot_statement)
                            item.mark_read()
                            print("Replied to a post!")
                        except Forbidden:
                            print("Cannot comment on banned subreddit.")
                        except RedditAPIException as e:
                            if 'THREAD_LOCKED' in str(e):
                                print("Thread was locked.")
                            elif 'DELETED_COMMENT' in str(e):
                                print("Comment was deleted.")
                            item.mark_read()
                        except Exception as e:
                            print("Unexpected error!")
                            pprint(e)
                    elif 'markbot' in body:
                        if 'unmarkbot' in body:
                            unmarkbot(item)
                        else:
                            markbot(item)
                        print('Replied to a post!')
                        item.mark_read()
                    else:
                        attemptComment(item.parent().author, item, False)
                        print('Replied to a post!')
                        item.mark_read()
            retry = False
        except ServerError or TooManyRequests:
            print("Server error. Retrying...")
            sleep(5)
            retry = True
    
    print("Successfully checked old inbox items.")

    retry = True
    while retry:
        try:
            for item in reddit.inbox.stream():
                info = vars(item)
                body = item.body.lower()
                if 'invitation to moderate' in item.subject:
                    try:
                        item.subreddit.mod.accept_invite()
                        print(f'Accepted invite to moderate r/{item.subreddit.display_name}')
                    except Exception as e:
                        print(f'No invite from r/{item.subreddit.display_name}')
                    item.mark_read()
                elif item.new and ((info['type'] == 'username_mention') or (info['type'] == 'comment_reply' and 'u/bot-sleuth-bot' in body)):
                    if 'repost' in body:
                        if re.search(r"filter:[\s]{0,1}subreddit", body) is not None:
                            attemptComment(item.parent().author, item, True, constraint = 'subreddit')
                        elif re.search(r"filter:[\s]{0,1}reddit", body) is not None:
                            attemptComment(item.parent().author, item, True, constraint = 'reddit')
                        else:
                            attemptComment(item.parent().author, item, True)
                        print('Replied to a post!')
                        item.mark_read()
                    elif 'u/bot-sleuth-bot' in body and info['type'] == 'comment_reply':
                        try:
                            item.reply("Why are you trying to check if I'm a bot? I've made it pretty clear that I am." + bot_statement)
                            item.mark_read()
                            print("Replied to a post!")
                        except Forbidden:
                            print("Cannot comment on banned subreddit.")
                        except RedditAPIException as e:
                            if 'THREAD_LOCKED' in str(e):
                                print("Thread was locked.")
                            elif 'DELETED_COMMENT' in str(e):
                                print("Comment was deleted.")
                            item.mark_read()
                        except Exception as e:
                            print("Unexpected error!")
                            pprint(e)
                    elif 'markbot' in body:
                        if 'unmarkbot' in body:
                            unmarkbot(item)
                        else:
                            markbot(item)
                        print('Replied to a post!')
                        item.mark_read()
                    else:
                        attemptComment(item.parent().author, item, False)
                        print('Replied to a post!')
                        item.mark_read()
            retry = False
        except ServerError or TooManyRequests:
            print("Server error. Retrying...")
            sleep(5)
            retry = True

def submissionStream():
    retry = True
    while retry:
        try:
            for submission in reddit.subreddit("hazbin+memesopdidnotlike").stream.submissions():
                if not checkIfVisited(vars(submission)['id']):
                    attemptComment(submission.author, submission, False, constraint = 'sticky')
                    print('Replied to a post!')
                    logVisit(vars(submission)['id'])
            retry = False
        except ServerError or TooManyRequests:
            print("Server error. Retrying...")
            sleep(5)
            retry = True

mentionThread = threading.Thread(target = mentionStream)
mentionThread.start()
submissionThread = threading.Thread(target=submissionStream)
submissionThread.start()

print("Startup successful.")