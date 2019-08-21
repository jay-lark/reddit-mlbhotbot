#!/usr/bin/env python3

import statsapi
import json
import requests
from pprint import pprint
import praw
import datetime

now = datetime.datetime.now()
end_date = now.strftime("%m/%d/%Y")
hitter_start = datetime.datetime.now()- datetime.timedelta(days=7)
hitter_start = hitter_start.strftime("%m/%d/%Y")
pitcher_start = datetime.datetime.now()- datetime.timedelta(days=11)
pitcher_start = pitcher_start.strftime("%m/%d/%Y")


#Detroit = 116
#Toldeo = 512
#Erie = 106

reddit = praw.Reddit('bot1')

teams={"116":"1","512":"11","106":"12","582": "14","5071": "16","473":"16"}
start_date="08/13/2019"
#end_date="08/20/2019"


def get_team(teamID):
    team = "https://statsapi.mlb.com/api/v1/teams/"+teamID
    r = requests.get(team)
    data = json.loads(r.content)
    team_name = data['teams'][0]['name']
    return team_name


def get_hitters(teamId):
    team_roster = "https://statsapi.mlb.com/api/v1/teams/"+teamId+"/roster"
    r = requests.get(team_roster)
    data = json.loads(r.content)
    hitters={}
    for x in data['roster']:
        if (x['position']['name'] != "Pitcher"):
          hitters.update({x['person']['id']:x['person']['fullName']})
    return(hitters)

def get_pitchers(teamId):
    team_roster = "https://statsapi.mlb.com/api/v1/teams/"+teamId+"/roster"
    r = requests.get(team_roster)
    data = json.loads(r.content)
    pitchers={}
    for x in data['roster']:
        if (x['position']['name'] == "Pitcher"):
          pitchers.update({x['person']['id']:x['person']['fullName']})
    return(pitchers)

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
                    hot_hitters.update({hitter['fullName'] :{"pa":pa,"hits":hits,"hr":hr,"rbi":rbi,"avg":avg,"ops":ops}}) 
            except:
                nostats = "This player doesn't have any stats for this period"     
    return(hot_hitters)

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
                    hot_pitchers.update({pitcher['fullName'] :{"ip":ip,"era":era,"whip":whip,"k9":k9}}) 
            except:
                nostats = "This player doesn't have any stats for this period"     
    return(hot_pitchers)



message="#HOT \n"  
    


for t,s in teams.items():
    current_team = get_team(t)
    message = message + "###" + current_team + "\n\n"
    message = message + "\n\n"
    message = message + "Name | PA | H | HR | RBI | AVG | OPS" + "\n"
    message = message + "-----|-----|-----|-----|-----|-----|-----" + "\n"
   
    hitters = get_hitters(t)

    pitchers=get_pitchers(t)

    hot_hit= get_hot_hit(hitters,s)
    hot_pit= get_hot_pitch(pitchers,s)
    #pprint(hot_hit)

    for h in hot_hit:
        message = message + h + "|" + str(hot_hit[h]['pa']) + "|" + str(hot_hit[h]['hits']) + "|" + str(hot_hit[h]['hr']) + "|" + str(hot_hit[h]['rbi']) + "|" + str(hot_hit[h]['avg']) + "|" + str(hot_hit[h]['ops']) + "\n"
    message = message + "\n\n"
    message = message + "Name | IP | ERA | WHIP | K/9" + "\n"
    message = message + "-----|-----|-----|-----|-----" + "\n"

    for p in hot_pit:
        message = message + p +  "|" + str(hot_pit[p]['ip']) +  "|" + str(hot_pit[p]['era']) +  "|" + str(hot_pit[p]['whip']) +  "|" + str(hot_pit[p]['k9']) +  "\n"
        
        


    
    #print(hot_pit)


print(message)
    #pprint(hot_pit)
title = 'Weekly Tigers Hot or Not'
selftext = message
reddit.subreddit('Tigershotbot').submit(title, selftext)
#print(hitter_start)