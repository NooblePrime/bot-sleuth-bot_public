import praw
reddit = praw.Reddit(
    #REDACTED CODE
)
new_line = "\n\n"
bot_statement = "\n\n^(I am a bot. This action was performed automatically. Check my profile for more information.)"
trusted_users = #REDACTED
def banStatement(subreddit_name: str, comment_link: str, comment_string: str):
    return f"Hello. It appears that I have been banned from r/{subreddit_name.replace('_', '\\_')} and am unable to reply to [this comment]({comment_link}), so I have privately messaged you to display the results instead. The constructed reply is as follows:\n\n" + comment_string + bot_statement
