#!/usr/bin/env python3

#import statsapi 
import json
import requests
import praw
import datetime

#Get the date, we'll track hitters for the last 7 days and pitchers for the last 11
now = datetime.datetime.now()
end_date = now.strftime("%m/%d/%Y")
hitter_start = datetime.datetime.now()- datetime.timedelta(days=7)
hitter_start = hitter_start.strftime("%m/%d/%Y")
pitcher_start = datetime.datetime.now()- datetime.timedelta(days=11)
pitcher_start = pitcher_start.strftime("%m/%d/%Y")


# Teams we want to track are in the dictionary below.  First number is the teamID and the second is the sport ID.
# You can find the IDs for all the teams here:  https://statsapi.mlb.com/api/v1/teams/  

teams={"116":"1","512":"11","106":"12","582": "14","5071": "16","473":"16"}

#Gets the team name fromthe ID

def get_team(teamID):
    team = "https://statsapi.mlb.com/api/v1/teams/"+teamID
    r = requests.get(team)
    data = json.loads(r.content)
    team_name = data['teams'][0]['name']
    return team_name

#gets a list of all the hitters and their playerID on a team

def get_hitters(teamId):
    team_roster = "https://statsapi.mlb.com/api/v1/teams/"+teamId+"/roster"
    r = requests.get(team_roster)
    data = json.loads(r.content)
    hitters={}
    for x in data['roster']:
        if (x['position']['name'] != "Pitcher"):
          hitters.update({x['person']['id']:x['person']['fullName']})
    return(hitters)

#gets a list of all the pitchers and their playerID on a team

def get_pitchers(teamId):
    team_roster = "https://statsapi.mlb.com/api/v1/teams/"+teamId+"/roster"
    r = requests.get(team_roster)
    data = json.loads(r.content)
    pitchers={}
    for x in data['roster']:
        if (x['position']['name'] == "Pitcher"):
          pitchers.update({x['person']['id']:x['person']['fullName']})
    return(pitchers)

#runs through the dict of hitters and adds the 'hot' ones to a new dict

def get_hot_hit(players,sport):
    hot_hitters={}
    for player in players:
        hitting_stats = "https://statsapi.mlb.com/api/v1/people/" + str(player) + "?hydrate=stats(group=%5Bhitting%5D,type=%5BbyDateRange%5D,startDate=" + hitter_start + ",endDate=" + end_date + ",sportId=" + sport + "),currentTeam"
        hs = requests.get(hitting_stats)
        hitting_data = json.loads(hs.content)
        
        for hitter in hitting_data['people']:
            try: 
                avg = hitter['stats'][0]['splits'][1]['stat']['avg']
                ops = hitter['stats'][0]['splits'][1]['stat']['ops']
                pa =  hitter['stats'][0]['splits'][1]['stat']['plateAppearances']
                hits = hitter['stats'][0]['splits'][1]['stat']['hits']
                hr = hitter['stats'][0]['splits'][1]['stat']['homeRuns']
                rbi = hitter['stats'][0]['splits'][1]['stat']['rbi']
                if (float(ops) > .850 or float(avg) > .320) and (float(pa) > 14):
                    #print(hitter['fullName'],pa,hits,hr,rbi,avg,ops)
                    name = "^" +  hitter['useName'] + " ^" + hitter['lastName'] 
                    hot_hitters.update({name :{"pa":pa,"hits":hits,"hr":hr,"rbi":rbi,"avg":avg,"ops":ops}}) 
            except:
                nostats = "This player doesn't have any stats for this period"     
    return(hot_hitters)

#runs through the dict of pitchers and adds the 'hot' ones to a new dict

def get_hot_pitch(players,sport):
    hot_pitchers={}
    for player in players:
        pitching_stats = "https://statsapi.mlb.com/api/v1/people/" + str(player) + "?hydrate=stats(group=%5Bpitching%5D,type=%5BbyDateRange%5D,startDate=" + pitcher_start + ",endDate=" + end_date + ",sportId=" + sport +"),currentTeam"
        ps = requests.get(pitching_stats)
        pitching_data = json.loads(ps.content)
        
        for pitcher in pitching_data['people']:
            try: 
                era = pitcher['stats'][0]['splits'][1]['stat']['era']
                ip = pitcher['stats'][0]['splits'][1]['stat']['inningsPitched']
                whip =  pitcher['stats'][0]['splits'][1]['stat']['whip']
                k9 = pitcher['stats'][0]['splits'][1]['stat']['strikeoutsPer9Inn']
                if float(era) < 3 and float(ip) >= 5:
                    #print(hitter['fullName'],pa,hits,hr,rbi,avg,ops)
                    name = "^" +  pitcher['useName'] + " ^" + pitcher['lastName'] 
                    hot_pitchers.update({name :{"ip":ip,"era":era,"whip":whip,"k9":k9}}) 
            except:
                nostats = "This player doesn't have any stats for this period"    
    return(hot_pitchers)


# Loop through the teams list, find all their players, and then find the hot ones

selftext=""  
    
for t,s in teams.items():
    current_team = get_team(t)
    hitters = get_hitters(t)
    pitchers=get_pitchers(t)
    hot_hit= get_hot_hit(hitters,s)
    hot_pit= get_hot_pitch(pitchers,s)
    selftext = selftext + "###" + current_team + "\n\n"
    selftext = selftext + "\n\n"
    if len(hot_hit) > 0:
      selftext = selftext + "^Name | ^PA | ^H | ^HR | ^RBI | ^AVG | ^OPS" + "\n"
      selftext = selftext + "-----|-----|-----|-----|-----|-----|-----" + "\n"
   



  
    for h in hot_hit:
        selftext = selftext + h + "|^" + str(hot_hit[h]['pa']) + "|^" + str(hot_hit[h]['hits']) + "|^" + str(hot_hit[h]['hr']) + "|^" + str(hot_hit[h]['rbi']) + "|^" + str(hot_hit[h]['avg']) + "|^" + str(hot_hit[h]['ops']) + "\n"

    selftext = selftext + "\n\n"
    if len(hot_pit) > 0:
        selftext = selftext + "Name | IP | ERA | WHIP | K/9" + "\n"
        selftext = selftext + "-----|-----|-----|-----|-----" + "\n"

    for p in hot_pit:
        selftext = selftext + p +  "|^" + str(hot_pit[p]['ip']) +  "|^" + str(hot_pit[p]['era']) +  "|^" + str(hot_pit[p]['whip']) +  "|^" + str(hot_pit[p]['k9']) +  "\n"
        

#initialise PRAW Reddit instance and post the message

reddit = praw.Reddit('bot1')
title = 'Weekly Hot Tigers Thread  ' + end_date
selftext = selftext
reddit.subreddit('motorcitykitties').submit(title, selftext)
