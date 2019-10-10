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

hitter_list= {"670623":"17","640492":"17","656537":"17"}
pitcher_list= {"621593":"17","656638":"17","660749":"17"}

#hot_variables
hot_avg = .000
hot_ops = .000
hot_pa = 0

hot_era = 999999990
hot_ip = 0

#reddit post variables
title = 'Weekly Tigers Fall League Update ' + end_date
hot_subreddit = 'Tigershotbot'

#runs through the dict of hitters and adds the 'hot' ones to a new dict
hitters={}
for player,sport in hitter_list.items():
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
            if (float(ops) > hot_ops or float(avg) > hot_avg) and (float(pa) > hot_pa):
                #print(hitter['fullName'],pa,hits,hr,rbi,avg,ops)
                name = "^" +  hitter['useName'] + " ^" + hitter['lastName'] 
                hitters.update({name :{"pa":pa,"hits":hits,"hr":hr,"rbi":rbi,"avg":avg,"ops":ops}}) 
        except:
            nostats = "This player doesn't have any stats for this period" 

pitchers={}
for player,sport in pitcher_list.items():
        pitching_stats = "https://statsapi.mlb.com/api/v1/people/" + str(player) + "?hydrate=stats(group=%5Bpitching%5D,type=%5BbyDateRange%5D,startDate=" + pitcher_start + ",endDate=" + end_date + ",sportId=" + sport +"),currentTeam"
        ps = requests.get(pitching_stats)
        pitching_data = json.loads(ps.content)
        
        for pitcher in pitching_data['people']:
            try: 
                era = pitcher['stats'][0]['splits'][1]['stat']['era']
                ip = pitcher['stats'][0]['splits'][1]['stat']['inningsPitched']
                whip =  pitcher['stats'][0]['splits'][1]['stat']['whip']
                k9 = pitcher['stats'][0]['splits'][1]['stat']['strikeoutsPer9Inn']
                if (float(era) < hot_era and float(ip) >= hot_ip):
                    #print(hitter['fullName'],pa,hits,hr,rbi,avg,ops)
                    name = "^" +  pitcher['useName'] + " ^" + pitcher['lastName'] 
                    pitchers.update({name :{"ip":ip,"era":era,"whip":whip,"k9":k9}}) 
            except:
                nostats = "This player doesn't have any stats for this period"    

selftext="" 
selftext = selftext + "###" + "Mesa Solar Sox"+ "\n\n"
selftext = selftext + "\n\n"
selftext = selftext + "^Name | ^PA | ^H | ^HR | ^RBI | ^AVG | ^OPS" + "\n"
selftext = selftext + "-----|-----|-----|-----|-----|-----|-----" + "\n" 

for h in hitters:
    selftext = selftext + h + "|^" + str(hitters[h]['pa']) + "|^" + str(hitters[h]['hits']) + "|^" + str(hitters[h]['hr']) + "|^" + str(hitters[h]['rbi']) + "|^" + str(hitters[h]['avg']) + "|^" + str(hitters[h]['ops']) + "\n"

selftext = selftext + "\n\n"

selftext = selftext + "Name | IP | ERA | WHIP | K/9" + "\n"
selftext = selftext + "-----|-----|-----|-----|-----" + "\n"

for p in pitchers:
        selftext = selftext + p +  "|^" + str(pitchers[p]['ip']) +  "|^" + str(pitchers[p]['era']) +  "|^" + str(pitchers[p]['whip']) +  "|^" + str(pitchers[p]['k9']) +  "\n"
        

#initialise PRAW Reddit instance and post the message

reddit = praw.Reddit('bot1')
selftext = selftext
reddit.subreddit(hot_subreddit).submit(title, selftext)

