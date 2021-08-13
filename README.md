# reddit-mlbhotbot
Script that will poll the MLB API for players on a hot/cold streak and then post the results to reddit.


## Requirements
- Python 3
- PRAW
- Reddit API Access

## Reddit-Bot 
To use the Reddit API you need to register your application to get your appi ID and secret token.  https://www.reddit.com/prefs/apps/

## PRAW
Install and configure PRAW, a Python wrapper for the Reddit API. https://praw.readthedocs.io/en/latest/getting_started/configuration.html

## Configuration
Modify the following variables at the top of the file to adjust the play evaluation criteria:


**hitter_start** By default the script will look at the last 7 days for hitters.  Adjust the time frame in this variable

**pitcher_start** By default the script will look at the last 11 days for pitchers.  Adjust the time frame in this variable

**teams**  This is a dictionary of the teams to look at.  The key is the teamID while the value is the sportID.  Team and sport IDs can be found by searching the MLB API output at this URL:  https://statsapi.mlb.com/api/v1/teams/

If a batter hits over the following values, they will be considered 'hot':  
**hot_avg** 
**hot_ops** 
**hot_pa** 

If a pitcher has an era under **hot_era** and has pitched at least the number of innings in **hot_ip** they will be considered 'hot.'

**title**  The title of the Reddit post.

**hot_subreddit**  The subreddit to post to.

## ToDo
Add requirements.txt
