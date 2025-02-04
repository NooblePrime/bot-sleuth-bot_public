from prawcore.exceptions import Forbidden, ServerError, NotFound, TooManyRequests
from praw.exceptions import RedditAPIException
import threading
from time import sleep, time
from cacheHandler import checkIfVisited, logVisit, cacheCleaner, logCooldown
from redditFunctions import attemptComment, markbot, unmarkbot, roundTimeDiff
from vars import reddit, bot_statement, trusted_users
import re
import json

def handleItem(item):
    retry = True
    try:
        while retry:
            info = vars(item)
            body = item.body.lower()
            if item.author is None:
                print("Author is None. Skipping...")
                item.mark_read()
                return
            author_name = item.author.name
            
            

            if author_name == item.parent().author.name:
                item.reply("This bot has limited bandwidth and is not a toy for your amusement. Please only use it for its intended purpose." + bot_statement)
                item.mark_read()
                return
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
                        attemptComment(item.parent().author, item, True, constraint='subreddit')
                    elif re.search(r"filter:[\s]{0,1}reddit", body) is not None:
                        attemptComment(item.parent().author, item, True, constraint='reddit')
                    else:
                        attemptComment(item.parent().author, item, True)
                    print('Replied to a post!')
                    item.mark_read()
                elif 'markbot' in body:
                    if 'unmarkbot' in body:
                        unmarkbot(item)
                    else:
                        markbot(item)
                    print('Replied to a post!')
                    item.mark_read()
                elif 'u/bot-sleuth-bot' in body and info['type'] == 'comment_reply':
                    if author_name not in trusted_users:
                        with open("cache.json", 'r') as file:
                            cache = json.load(file)
                            if author_name in cache.get("cooldowns", {}):
                                cooldown_time = cache["cooldowns"][author_name]["time"]
                                remaining_time = 180 - (time() - cooldown_time)
                                if remaining_time > 0:
                                    comment = f"You're doing that too much, please wait {roundTimeDiff(remaining_time)} before trying again."
                                    item.reply(comment)
                                    item.mark_read()
                                    return
                    try:
                        item.reply("Why are you trying to check if I'm a bot? I've made it pretty clear that I am." + bot_statement)
                        item.mark_read()
                        print("Replied to a post!")
                    except Forbidden:
                        print("Cannot comment on banned subreddit.")
                else:
                    attemptComment(item.parent().author, item, False)
                    print('Replied to a post!')
                    item.mark_read()
                logCooldown(author_name)
            retry = False
    except ServerError:
        print("Server error. Retrying...")
        sleep(60)
        retry = True
    except RedditAPIException as e:
        if 'RATELIMIT' in str(e) or 'Looks like you\'ve been doing that a lot.' in str(e):
            print("Rate limited. Retrying...")
            sleep(60)
            retry = True
        elif 'THREAD_LOCKED' in str(e) or 'DELETED_COMMENT' in str(e):
            print("Error:", str(e))
            item.mark_read()
            retry = False
    except TooManyRequests:
        print("Rate limited. Retrying...")
        sleep(60)
        retry = True
    except NotFound:
        print("Item not found. Skipping...")
        retry = False
    except Exception as e:
        print(f"Error handling item: {e}")
        retry = False

def mentionStream():
    for item in reddit.inbox.unread(limit=500):
        handleItem(item)
    print("Successfully checked old inbox items.")
    for item in reddit.inbox.stream():
        handleItem(item)

def submissionStream():
    for submission in reddit.subreddit("hazbin+memesopdidnotlike").stream.submissions():
        if not checkIfVisited(vars(submission)['id']):
            retry = True
            while retry:
                try:
                    attemptComment(submission.author, submission, False, constraint='sticky')
                    retry = False
                except TooManyRequests or RedditAPIException as e:
                    if ('RATELIMIT' or 'Looks like you\'ve been doing that a lot.' in str(e)) or TooManyRequests:
                        print("Rate limited. Retrying...")
                        sleep(60)
                        retry = True
            print('Replied to a post!')
            logVisit(vars(submission)['id'])

def bullshitStream():
    while True:
        print("Checking for dropped comments...")
        for comment in reddit.subreddit("all").search("u/bot-sleuth-bot", sort='comments', time_filter='hour'):
            try:
                if not comment.replies.list() == []:
                    checked = False
                    for item in comment.list():
                        if item.author == 'bot-sleuth-bot':
                            checked = True
                            break
                    if not checked:
                        handleItem(comment)
            except AttributeError:
                pass
        sleep(1800)

def cacheCleanerLoop():
    while True:
        cacheCleaner()
        sleep(3600)

if __name__ == "__main__":
    mentionThread = threading.Thread(target=mentionStream)
    mentionThread.start()

    submissionThread = threading.Thread(target=submissionStream)
    submissionThread.start()

    bullshitThread = threading.Thread(target=bullshitStream)
    bullshitThread.start()

    cacheCleanerThread = threading.Thread(target=cacheCleanerLoop)
    cacheCleanerThread.start()

    print("Startup successful.")