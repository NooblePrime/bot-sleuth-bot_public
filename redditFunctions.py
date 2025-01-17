import checks
from praw.exceptions import RedditAPIException
from prawcore.exceptions import Forbidden
from pprint import pprint
from vars import new_line, bot_statement, trusted_users

def constructComment(suspect):
    try:
        name = suspect.name
    except AttributeError:
        return "Account or post was deleted, so user info could not be fetched. Unable to analyze"
    except Exception as e:
        if str(e) == 'received 404 HTTP response':
            return "Unable to access user information. It is likely the account has been suspended or deleted."
        return "Fatal error! Displaying details..." + new_line + str(e)
    if name == "pixel-counter-bot":
        return "That is a bot made by the same person who made me."
    if name == "syko-san":
        return "That is the person who made me! He's a bit of an NPC sometimes, but not a bot."
    if name == "bot-sleuth-bot":
        return "Why are you trying to check if I'm a bot? I've made it pretty clear that I am."
    if name.lower() in trusted_users:
        return "This account has been verified as a trustworthy user by the developer of this bot, or someone trusted by him. Further checking is unnecessary."
    if name.lower() in open('marked_bots.txt').read():
        return f'Trustworthy sources have manually verified that u/{name} is a bot. Further checking is unnecessary. If this is a mistake, please contact the user who flagged you or [u/syko-san](https://www.reddit.com/user/syko-san/) to have it corrected.'
    
    #A LOT OF REDACTED CODE

    suspicion_quotient = suspicion/maximum_suspicion
    comment += f'Suspicion Quotient: {suspicion_quotient:.2f}' + new_line

    if suspicion_quotient <= 0:
        comment += f'This account is not exhibiting any of the traits found in a **typical** karma farming bot. It is extremely likely that u/{name} is a human.'
    elif suspicion_quotient >= 0.8:
        comment += f'This account exhibits multiple major traits commonly found in karma farming bots. It is extremely likely that u/{name} is a bot made to farm karma.'
    elif suspicion_quotient >= 0.7:
        comment += f'This account exhibits major traits commonly found in karma farming bots. It is highly likely that u/{name} is a bot made to farm karma.'
    elif suspicion_quotient >= 0.5:
        comment += f'This account exhibits traits commonly found in karma farming bots. It\'s likely that u/{name} is a bot.'
    elif suspicion_quotient >= 0.3:
        comment += f'This account exhibits a few minor traits commonly found in karma farming bots. u/{name} is either a human account that recently got turned into a bot account, or a human who suffers from severe NPC syndrome.'
    elif suspicion_quotient >= 0:
        comment += f'This account exhibits one or two minor traits commonly found in karma farming bots. While it\'s possible that u/{name} is a bot, it\'s very unlikely.'

    return comment

def attemptSticky(comment):
    try:
        comment.mod.distinguish(sticky = True)
    except Forbidden:
        pass

def attemptComment(suspect, item, repost, constraint = None):
    if item.author.name == 'AutoModerator':
        item.reply("Message from developer: I've noticed a few subreddits have started using AutoModerator to call this bot. This method isn't quite ideal for me, so if you'd like to automate the bot's usage on your subreddit, please reach out to [u/syko-san](https://www.reddit.com/user/syko-san/) to discuss it.")
        return
    sub_contributors = []
    try:
        for contributor in item.subreddit.contributor():
            sub_contributors.append(contributor)
    except Forbidden:
        pass
    if suspect in sub_contributors:
        try:
            reply = item.reply(f'u/{suspect.name} has been approved by the moderators of this subreddit. Skipping check to save bandwidth.' + bot_statement)
        except RedditAPIException:
            print("Comment was deleted.")
        if constraint == 'sticky':
            attemptSticky(reply)
        return
    elif repost:
        comment_string = checks.repostCheck(item, constraint)
    else:
        comment_string = constructComment(suspect)

    try:
        reply = item.reply(comment_string + bot_statement)
        attemptSticky(reply)
        print("Replied to a post!")
    except Forbidden:
        print("Cannot comment on banned subreddit, private messaging user.")
        try:
            item.author.message(subject="I was banned.", message=f'Hello. It appears that I have been banned from r/{item.submission.subreddit.display_name} and am unable to reply to [this comment]({item.context}), so I have privately messaged you to display the results instead. The constructed reply is as follows:\n\n' + comment_string + bot_statement)
        except RedditAPIException or Forbidden:
            pass
    except Exception as e:
        print("Unexpected error!")
        pprint(e)
