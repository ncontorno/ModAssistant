import praw, time
from praw.handlers import MultiprocessHandler

usernm = "reddit_username" #all in lowercase
handler = MultiprocessHandler()
r = praw.Reddit(user_agent='Unique Agent by you v1.0')
#Use below for OAuth2 authentication
r.set_oauth_app_info('client_id','client_secret','redirect_uri')
r.refresh_access_information('refresh_token')
#Use below for password authentication - will be depreciated soon
passwd = "cAsEsEnSiTiVepassword"
r.login(username=usernm, password=passwd, disable_warning=True)

for passes in xrange(9):
	unread = r.get_unread(limit=None)
	subreddits = [subreddit.display_name.lower() for subreddit in r.get_my_moderation()]
	for message in unread:
		subreddit = message.subreddit
		try:
			banned_users_page_eoim = r.get_wiki_page('everyoneismod_banlist','banlist')
			banned_users_eoim = banned_users_page_eoim.content_md.strip().split()
			banned_users_page = r.get_wiki_page(message.subreddit,'banlist')
			banned_users = banned_users_page.content_md.strip().split()
		except praw.errors.NotFound:
			banned_users = (0,1)
			pass
		if message.subject.startswith('invitation to moderate'):
			message.mark_as_read()
			subreddit.accept_moderator_invite()
			continue
		if usernm not in message.body.lower():
			message.mark_as_read()
			continue
		if message.author is None:
			message.mark_as_read()
			continue
		if 'mod me' in message.body.lower():
			if message.subreddit.display_name.lower() not in subreddits:
				message.mark_as_read()
				message.reply("I am not a moderator in r/%s and cannot add you, u/%s." % (subreddit.display_name, message.author))
				continue
			if message.subreddit.display_name.lower() in subreddits:
				if message.author.name in (banned_users_eoim):
					if message.subreddit.display_name.lower() == ('every_one_is_mod'):
						message.mark_as_read()
						message.reply("You are on the r/%s blacklist, u/%s, and I cannot add you." % (subreddit.display_name, message.author))
						continue
				if message.author.name in (banned_users):
					message.mark_as_read()
					message.reply("You are on the r/%s blacklist, u/%s, and I cannot add you." % (subreddit.display_name, message.author))
					continue
				try:
					subreddit.add_moderator(message.author)
					message.mark_as_read()
					message.reply("I added you to r/%s as a moderator, u/%s." % (subreddit.display_name, message.author))
					continue
				except praw.errors.AlreadyModerator:
					message.mark_as_read()
					message.reply("u/%s, you are already a moderator in r/%s, [ya nerd.](http://i.imgur.com/UMDf17w.gif)" % (message.author, subreddit.display_name))
					continue
				except praw.errors.APIException:
					message.mark_as_read()
					message.reply("I had a problem adding you as a mod to r/%s. You may be banned. Contact the [moderators](https://www.reddit.com/message/compose?to=/r/%s) for assistance." % (subreddit.display_name, subreddit.display_name))
					continue
				except praw.errors.Forbidden:
					message.mark_as_read()
					message.reply("I do not have proper moderator permissions in r/%s. Contact the [moderators](https://www.reddit.com/message/compose?to=/r/%s) for assistance." % (subreddit.display_name, subreddit.display_name))
					continue
				except:
					message.mark_as_read()
					message.reply("I had a problem with your moderator request. Please check your syntax and try again or contact the [moderators](https://www.reddit.com/message/compose?to=/r/" + subreddit.display_name + ") for assistance.")
					continue
	time.sleep(60)