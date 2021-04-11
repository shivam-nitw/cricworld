from django.shortcuts import render
import json
import requests
from collections import defaultdict
from .models import Match
from django.db import models
# Create your views here.
def index(request):
    return render(request, "index.html", dict(link1='home'))


def overs(resS) :
    S = resS['data']['bowling'][0]['scores']
    Oone = 0
    Otwo = 0
    for i in S :
        Oone  = Oone + float(i['O'])
    if len(resS['data']['bowling']) > 1 :
        T = resS['data']['bowling'][1]['scores']
        for i in T:
            Otwo = Otwo + float(i['O'])

    over = { "Oone" : Oone , "Otwo" : Otwo}
    return  over

'''
    Approach for recent matches ->
        1. Make a hash map of names of teams in international matches and IPL ,Big Bash and all other Main T-20 leagues 
           of major countries
        2. If in 'matches' end point any of team name matches the above teams and the match is complete then stores the 
           date ,unique id, team names and anything else (if required) in Database.
        3. Fetch the last 15 match ID from data base in views.home and extract its data and store in a Dict obj and send to 
           home.html where it will be displayed in 'recent matches' in home.html
        4. send the chosen match id from 'recent matches' to scoreboard function and the data will be processed send to 
           scoreboard.html as it is in live matches case
    
    Approach for upcoming matches ->
        1.Get the Team names from the above created hash function and the matches which are yet to start today and the 
          matches whose date is after today.
        2. Only team names will be stated there .
        3. when user click of them we will show the expected squads        
'''

Teams={
        'India' : 1,'England' : 2, 'New Zealand' : 3 ,' Australia' : 4,                                    #mans International
        'South Africa' : 5 ,' Pakistan' : 6, 'Bangladesh' : 7 ,
        'Sri Lanka' : 8, ' West Indies' : 9,'Afghanistan' : 10, ' Ireland' : 11 ,
        'Netherlands' : 12, ' Zimbabwe' : 13 ,'  Oman' : 14, ' Scotland' : 15 ,' UAE' : 16,
        'Nepal' : 17, 'Namibia' : 18, 'United States' : 19 ,' Papua New Guinea' : 20,
        'Chennai Super Kings ' : 21 ,'Delhi Capitals' : 22, 'Kolkata Knight Riders' : 23 ,                 #IPL
        'Mumbai Indians' : 24, ' Punjab Kings' : 25,'Royal Challengers Bangalore' : 26,
        'Rajasthan Royals' : 27 ,'Sunrisers Hyderabad' : 28,
        'Sydney Sixers' : 29 ,'Perth Scorchers' : 30, '  Sydney Thunder' : 31,                             #Big Bash
        'Brisbane Heat' : 32, ' Adelaide Strikers' : 33 , ' Hobart Hurricaness' : 34 ,
        'Melbourne Stars' : 35, ' Melbourne Renegades' : 36,
        'India Women' : 37,'New Zealand Women' : 38 , ' South Africa Women' : 39 ,                         #Womens International
        'Pakistan Women' : 40,'Bangladesh Women' : 41 ,' Sri Lanka Women' : 42,
        'West Indies Women' : 43,' Ireland Women' : 44 ,' England Women' : 45 ,
        'Karachi Kings' : 46, 'Peshawar Zalmi' : 47 ,' Islamabad United' : 48,                             #PSL
        'Lahore Qalandars' : 49 ,'Multan Sultans' : 50, 'Quetta Gladiators' : 51 ,
        'Khulna Tigers' : 52, ' Rajshahi Royals' : 53,'Chattogram Challengers' : 54,                       #BPL
        'Dhaka Platoon' : 55 ,' Cumilla Warriors' : 56, 'Rangpur Rangers' : 57 ,' Sylhet Thunder' : 58,
        'Jamaica Tallawahs' :  59,' St Lucia Zouks' : 60, ' Guyana Amazon Warriors' : 61,                  #CPL
        'Barbados Tridents' : 62,'St Kitts & Nevis Patriots' : 63, 'Trinbago Knight Riders' : 64
        }

#Function for deciding the tournament name according to the team names
def tournament(team) :
    if Teams[team]>=1 and Teams[team]<=20 :
        return "Men's International"
    if Teams[team] >= 21 and Teams[team] <= 28:
        return "IPL"
    if Teams[team] >= 29 and Teams[team] <= 36:
        return "Big Bash"
    if Teams[team] >= 37 and Teams[team] <= 45:
        return "Women's International"
    if Teams[team] >= 46 and Teams[team] <= 51:
        return "PSL"
    if Teams[team] >= 52 and Teams[team] <= 58:
        return "BPL"
    if Teams[team] >= 59 and Teams[team] <= 64:
        return "CPL"

#Function to Add completed matches to database
def DB(res,desc,elec,s1,s2,man) :
    game = Match()
    game.unique_id = int(res['unique_id'])
    game.date = res['date']
    game.type=res["type"]
    game.sub_type=tournament(res['team-1'])
    game.teamone = res['team-1']
    game.teamtwo = res['team-2']
    game.scoreone = s1
    game.scoretwo = s2
    game.toss_winner_team = res['toss_winner_team']
    game.elected = elec
    game.winner_team = res['winner_team']
    game.man_of_the_match = man
    game.save()

#Function for adding Scores
def scores(i,resC,over) :
    l = len(resC['data'][i]['description'])
    for index in range(5, l):
        if (resC['data'][i]['description'][index] == 'v' and resC['data'][i]['description'][index - 1] == " " and
                resC['data'][i]['description'][index + 1] == " "):
            sone = resC['data'][i]['description'][0:index - 1]
            stwo = '(' + str(over['Oone']) + ')'
            sthree = resC['data'][i]['description'][index + 1:]
            sfour = '(' + str(over['Otwo']) + ')'
            if resC['data'][i]['batfirst'][0:5] == sone[0:5]:
                resC['data'][i]['score1'] = sone + stwo
                if over['Otwo'] == 0:
                    resC['data'][i]['score2'] = sthree
                else:
                    resC['data'][i]['score2'] = sthree + sfour
            else:
                resC['data'][i]['score1'] = sthree + stwo
                if over['Otwo'] == 0:
                    resC['data'][i]['score2'] = sone
                else:
                    resC['data'][i]['score2'] = sone + sfour
            break

#Function for toss decision
def toss(i,resC,a,b,team_1,team_2,toss_winner_team) :
    if (a[13:18] == b[0:5]):
        resC['data'][i]['elected'] = "bat"
        if (toss_winner_team == team_1):
            resC['data'][i]['batfirst'] = team_1
            resC['data'][i]['batsecond'] = team_2
        else:
            resC['data'][i]['batfirst'] = team_2
            resC['data'][i]['batsecond'] = team_1
    else:
        resC['data'][i]['elected'] = "bowl"
        if (toss_winner_team == team_1):
            resC['data'][i]['batfirst'] = team_2
            resC['data'][i]['batsecond'] = team_1
        else:
            resC['data'][i]['batfirst'] = team_1
            resC['data'][i]['batsecond'] = team_2


def home(request, endfor=None):
    keys = ["2CKFCOve0rdpvaKLOZQBxZzfOqn1",
            "SXCi9B1KSHOo5A9209U6x9nXmHm2",
            "WmUasHazyvYrXqyz9pYpmgeqOI72",
            "srZuPbXxGNQ4i0VxAHOudEx3jLv1",
            "dLuRPBeTWuRtZeKrIH9qDsUR6kS2"
            ]
    ID = ""
    res = defaultdict() # for cricket end point
    resR = defaultdict() # for Recent matches
    resS = defaultdict()  # for fantasy summery endpoint
    resU = defaultdict()    # for upcoming matches
    resU ={
        "data" : []
    }
    for i in keys :
        res = json.loads(requests.get(f'http://cricapi.com/api/cricket/?apikey={i}').text)
        if not 'error' in res.keys() :
            ID = i
            break

    # Cricapi Calls()
    resC = res
    k = 0   #  for ResU index
    resc = json.loads(requests.get(f'http://cricapi.com/api/matches/?apikey={ID}').text)
    for i in range(len(resC['data'])) :
        for j in range(len(resc['matches'])) :
            if not "team-1" in resc['matches'][j]:          #to avoid last entry fail, giving key error after the last entry
                continue
            if resc['matches'][j]['team-1'] in Teams :
                if(int(resC['data'][i]['unique_id']) == resc['matches'][j]['unique_id']) :
                    if 'toss_winner_team' in resc['matches'][j].keys()  :       #If toss has happened or not
                        resC['data'][i]['t_team_name'] = resc['matches'][j]['toss_winner_team']
                        resC['data'][i]['localteam'] = resc['matches'][j]['team-1']
                        resC['data'][i]['visitorteam'] = resc['matches'][j]['team-2']
                        I = resC['data'][i]['unique_id']
                        resS = json.loads(requests.get(f'http://cricapi.com/api/fantasySummary/?apikey={ID}&unique_id={I}').text)  #here f'' is included because we need to include variables there
                        if(len(resS['data']['fielding']) > 0) :     #To check if match started or not

                            resC['data'][i]['match_started'] = 'true'

                            # Adding Toss winner name and their decision
                            a = resS['data']['fielding'][0]['title']
                            b = resc['matches'][j]['toss_winner_team']
                            toss(i,resC,a,b,resc['matches'][j]['team-1'],resc['matches'][j]['team-2'],resc['matches'][j]['toss_winner_team'])

                            # Adding match date
                            resC['data'][i]['pubDate'] = resc['matches'][j]['date']

                            #Adding overs
                            over = overs(resS)
                            scores(i,resC, over)

                            #Processing man of the mtch and winner team
                            if resS['data']['man-of-the-match']!="" :
                                   resS['man_of_the_match'] = resS['data']['man-of-the-match']['name']
                            else :
                                resS['man_of_the_match'] = "null"

                            if not "winner_team" in resS['data'] :
                                resS["winner_team"] = "null"
                            else :
                                resS["winner_team"] = resS['data']['winner_team']

                            resC['data'][i]["winner_team"] = resS["winner_team"]
                            resC['data'][i]["man_of_the_match"] = resS["man_of_the_match"]

                            #Adding in DataBase

                            if resc['matches'][j]['team-1'] in Teams and 'winner_team' in resc['matches'][j] and not(Match.objects.filter(unique_id = resc['matches'][j]['unique_id'])):
                                DB(resc['matches'][j] , resC['data'][i]['description'], resC['data'][i]['elected'], resC['data'][i]['score1'], resC['data'][i]['score2'],resS['man_of_the_match'])

                        else :
                            resC['data'][i]['match_started'] = 'false'
                    else :
                        resC['data'][i]['match_started'] = 'false'
                if resc['matches'][j]['matchStarted'] == bool(0) :
                    resU['data'].append(resc['matches'][j])
                    a = "team-1"
                    b = "teamone"
                    if not "team-1" in resU['data'][k] :            #This is to avoid last entry fail
                        continue
                    resU['data'][k][b] = resU['data'][k].pop(a)
                    a = "team-2"
                    b = "teamtwo"
                    resU['data'][k][b] = resU['data'][k].pop(a)
                    k = k + 1
    resR['data'] = Match.objects.all().order_by('-date') # Change this later with last 15 records
    print("AA : ", resR['data'][0])
    return render(request, "home.html", {'resC' : resC['data'],'resR' : resR['data'],'resU' : resU['data']})

def scoreboard(request,id):
    id = int(id)
    keys = ["2CKFCOve0rdpvaKLOZQBxZzfOqn1",
            "SXCi9B1KSHOo5A9209U6x9nXmHm2",
            "WmUasHazyvYrXqyz9pYpmgeqOI72",
            "srZuPbXxGNQ4i0VxAHOudEx3jLv1",
            "dLuRPBeTWuRtZeKrIH9qDsUR6kS2"
            ]

    ID = ""

    res = defaultdict()
    resC = defaultdict()
    for i in keys:
        res = json.loads(requests.get(f'http://cricapi.com/api/cricket?apikey={i}').text)
        if not 'error' in res.keys():
            ID = i
            break


    I = 0
    for i in range(len(res['data'])):
        if int(res['data'][i]['unique_id']) == id :
            resC = res['data'][i]
            I = i
            break

    resS = json.loads(requests.get(f'https://cricapi.com/api/fantasySummary?apikey={ID}&unique_id={id}').text)
    #resc = json.loads(requests.get(f'http://cricapi.com/api/matches?apikey={i}').text)

    a = 0
    if len(resC) == 0 :
        resC['data'] = Match.objects.filter(unique_id = id)
        resS['summary'] = resC
        a = -1

    if a != -1 :
        # Adding team names according to batting order
        l = len(resS['data']['batting'][0]['title'])
        title = resS['data']['batting'][0]['title']
        title = title[::-1]  # reversing title
        title = title[27:l]
        title = title[::-1]
        resC['batfirst'] = title

        if  len(resS['data']['batting']) > 1  :
            l = len(resS['data']['batting'][1]['title'])
            title = resS['data']['batting'][1]['title']
            title = title[::-1]
            title = title[41:l]
            title = title[::-1]
            resC['batsecond'] = title
        else :
            resC['batsecond'] = "null"


        over = overs(resS)
        for index in range(5, l):
            if (resC['description'][index] == 'v' and resC['description'][index - 1] == " " and
                    resC['description'][index + 1] == " "):
                sone = resC['description'][0:index - 1]
                stwo = '(' + str(over['Oone']) + ')'
                sthree = resC['description'][index + 1:]
                sfour = '(' + str(over['Otwo']) + ')'
                if resC['batfirst'][0:5] == sone[0:5]:
                    resC['scoreonw'] = sone + stwo
                    if over['Otwo'] == 0:
                        resC['scoretwo'] = sthree
                    else:
                        resC['scoretwo'] = sthree + sfour
                else:
                    resC['score1'] = sthree + stwo
                    if over['Otwo'] == 0:
                        resC['scoretwo'] = sone
                    else:
                        resC['scoreone'] = sone + sfour
                break

        a = "dismissal-info"
        b = "dismissal_info"  # changing '-' to '_' as it is more convineant to parse '_' in DTL
        for i in range(len(resS['data']['batting'])):
            for j in resS['data']['batting'][i]['scores']:
                j[b] = j.pop(a)

        if resS['data']['man-of-the-match'] != "":
            a = 'man-of-the-match'
            b = 'man_of_the_match'
            resS['data'][b] = resS['data'].pop(a)
        else:
            resS['data']['man-of-the-match'] = 'null'
        resS['summary'] = resC

    #print("1 : ", resS['summary'][0]['teamone'])
    return render(request, "scoreboard.html", {'resC': resS, 'R' : resC})
