# ribomic
RIot BOard Message In Comment

What is this bot: The Riot Board Message In Comment (RIBOMIC) bot retrieves the contents written on Riot's official Board and post it as a comment on Reddit. It is somewhat similar to how /u/TweetsInCommentsBot works.

Purpose: The purpose of RIBOMIC is two folds. First of all, Riot's Board is very slow to load and does not innately support mobile platforms. Secondly, often leagueoflegends.com is blocked at work. Reposting the content as a comment on Reddit allows better viewing. RIBOMIC will attempt, within its best abilities, to preserve the formatting of the original post.

How to use: Post a link to from Riot's Board on /r/leagueoflegends Reddit. RIBOMIC does not load URLs from comments. If you wish to test the bot, try using /r/sandboxtest or other similar sandbox subreddits (the bot responds to links from any visible subreddits). If you have any questions or suggestions regarding the bot, PM /u/sufficiency. If you enjoy his work and would like the latest updates, consider following him on [Twitter](https://twitter.com/SufficientStats).

# Setup / Requirements
* Python 2
* PhantomJS

# Change Log

v0.9b: Code is completely refactored. The bot works lolesports.com articles as well.

v0.1.5.b: Quotations are improved. Embedded champion, item, and summoner flairs now work.

v0.1.4.b: In the case of large comment (more than 10,000 characters long), the bot will now attempt to break up the comment into pieces to bypass the Reddit comment limit.

v0.1.3b: Now works for all visible subreddits, not just /r/leagueoflegends

v0.1.2b: Links are handled better

v0.1.1b: Quotations work a little better - additional work is still needed

v0.1.0b: Initial version


# Disclaimer
RiotBoardMessageInCommentBot (RIBOMIC) powered by PRAW and PostgreSQL. RIBOMIC isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
