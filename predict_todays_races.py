#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import sklearn
import requests
import json
import pandas as pd
import pickle
from api_tool import ApiTool

#FrontShoes RearShoes AmericanStyleCart Distance StartTrack StartType Month driverWpr coachWpr horseWpr
def fetchHorses(api_tool, raceId, start_type, race_number):
    runners = api_tool.getHorsesForRace(raceId)

    jsonRunners = json.loads(runners.text)['collection']
    rHorses = []

    for jsonHorse in jsonRunners:
        dbDict = {'Name': jsonHorse['horseName']}
        dbDict['FrontShoes'] = jsonHorse['frontShoes']
        dbDict['RearShoes'] = jsonHorse['rearShoes']
        dbDict['AmericanStyleCart'] = (jsonHorse['specialCart'] == 'YES')
        dbDict['CoachName'] = jsonHorse['coachName']
        dbDict['DriverName'] = jsonHorse['driverName']
        dbDict['Distance'] = jsonHorse['distance']
        dbDict['StartTrack'] = jsonHorse['startTrack']
        dbDict['StartType'] = start_type
        dbDict['Month'] = 10
        dbDict['raceNumber'] = race_number
            
        rHorses.append(dbDict)

    return rHorses

def fetchRaces(api_tool,cardId):
    races = api_tool.getRacesForCard(cardId)
    jsonRaces = json.loads(races.text)['collection']

    rRaces = []

    for jsonRace in jsonRaces:
        rRace = {}
        start_type = jsonRace['startType']
        rRace['summary'] = jsonRace['seriesSpecification']
        rRace['raceId'] = jsonRace['raceId']
        rRace['raceNumber'] = jsonRace['number']
        rRace['horses'] = fetchHorses(api_tool, jsonRace['raceId'], start_type, jsonRace['number'])
        rRaces.append(rRace)

    return rRaces



def add_win_percentages_to_df(df):
    coach_df = pd.read_csv('coaches.csv')
    coach_df.columns = ['name', 'count', 'wins', 'winsPerRace', 'meanOdds', 'oddsTotal']
    driver_df = pd.read_csv('drivers.csv')
    driver_df.columns = ['name', 'count', 'wins', 'winsPerRace', 'meanOdds', 'oddsTotal']
    horse_df = pd.read_csv('horses.csv')
    horse_df.columns = ['name', 'count', 'wins', 'winsPerRace', 'meanOdds', 'oddsTotal']

    coach_mean = coach_df["winsPerRace"].mean()
    driver_mean = driver_df["winsPerRace"].mean()
    horse_mean = horse_df["winsPerRace"].mean()


    coachWprList = []
    driverWprList = []
    horseWprList = []

    coaches = {}
    drivers = {}
    horses = {}

    for i, row in df.iterrows():
        coachName = row['CoachName']
        driverName = row['DriverName']
        horseName = row['Name']
    
        if driverName not in drivers:
            driverWpr = (driver_df.loc[driver_df['name'] == driverName]).winsPerRace
            drivers.update({driverName: driverWpr})
        else:
            driverWpr = drivers[driverName]
    
        if coachName not in coaches:
            coachWpr = (coach_df.loc[coach_df['name'] == coachName]).winsPerRace
            coaches.update({coachName: coachWpr})
        else:
            coachWpr = coaches[coachName] 
        
        if horseName not in horses:
            horseWpr = (horse_df.loc[horse_df['name'] == horseName]).winsPerRace
            horses.update({horseName: horseWpr})
        else:
            horseWpr = horses[horseName] 
        
        driverWprList.append(driverWpr)
        coachWprList.append(coachWpr)
        horseWprList.append(horseWpr)


    dlist = []
    for i in range(len(driverWprList)):
        if (len(driverWprList[i]) > 0):
            dlist.append(driverWprList[i].values[0])
        else:
            dlist.append(driver_mean)
        
    clist = []
    for i in range(len(coachWprList)):
        if (len(coachWprList[i]) > 0):
            clist.append(coachWprList[i].values[0])
        else:
            clist.append(coach_mean)  
        
    hlist = []
    for i in range(len(horseWprList)):
        if (len(horseWprList[i]) > 0):
            hlist.append(horseWprList[i].values[0])
        else:
            hlist.append(horse_mean)  


    df['driverWpr'] = dlist
    df['coachWpr'] = clist
    df['horseWpr'] = hlist


def preprocess_race(horseList):
    total_odds = 0
    
    for horse in horseList:
        total_odds += horse['Predicted odds']
    for horse in horseList:
        horse['Predicted odds'] = round((horse['Predicted odds'] / total_odds) * 100, 1)
    



def print_results(prediction_dict):
    print()
    for raceNumber, runners in prediction_dict.items():
        print('Race', raceNumber)
        preprocess_race(runners)
        total_odds = 0
    
        for horse in runners:
            print(horse['Name'], ':', horse['Predicted odds'])
            total_odds +=  horse['Predicted odds']
        
        print()

def process_results(predictions, raceNumbers, names):
    prediction_dict = {}
    for i in range(len(predictions)):
        if raceNumbers[i] in prediction_dict:
            prediction_dict[raceNumbers[i]].append({'Name': names[i], 'Predicted odds': round(predictions[i] * 100, 1)})
        else:
            prediction_dict[raceNumbers[i]] = [{'Name': names[i], 'Predicted odds': round(predictions[i] * 100, 1)}]
    
    print_results(prediction_dict)


def process_card(card, car_model, volt_model, at):
    races = fetchRaces(at, card['cardId'])
    
    all_horses = []

    for race in races:
        all_horses.extend(race['horses'])

    df = pd.DataFrame(all_horses)
    df.AmericanStyleCart = df.AmericanStyleCart.astype(int)
    df.FrontShoes = df.FrontShoes.replace(to_replace=['NO_SHOES', 'HAS_SHOES', 'UNKNOWN'], value=[0, 1, 1])
    df.RearShoes = df.RearShoes.replace(to_replace=['NO_SHOES', 'HAS_SHOES', 'UNKNOWN'], value=[0, 1, 1])
    df.StartType = df.StartType.replace(to_replace=['CAR_START', 'VOLT_START'], value=[0, 1])

    add_win_percentages_to_df(df)

    car_horses = df.loc[df['StartType'] == 0]
    volt_horses = df.loc[df['StartType'] == 1]

    car_names = car_horses.Name.values
    car_raceNumbers = car_horses.raceNumber.values

    volt_names = volt_horses.Name.values
    volt_raceNumbers = volt_horses.raceNumber.values

    

    cols_to_delete = ['Name', 'CoachName', 'DriverName', 'raceNumber', 'horseWpr', 'StartType']
    for col in cols_to_delete:
        del car_horses[col]
        del volt_horses[col]

    if not car_horses.empty:
        car_predictions = car_model.predict(car_horses)
        print('CAR STARTS')
        process_results(car_predictions, car_raceNumbers, car_names)
    if not volt_horses.empty:
        volt_predictions = volt_model.predict(volt_horses)
        print('VOLT STARTS')
        process_results(volt_predictions, volt_raceNumbers, volt_names)

    
    


def main():
    at = ApiTool()
    year = input('Year: ')
    month = input('Month: ')
    day = input('Day: ')
    car_model = pickle.load( open( "car_model.p", "rb" ) )
    volt_model = pickle.load( open( "volt_model.p", "rb" ) )
    cards = json.loads(at.getCardsForDate(day, month, year).text)['collection']

    for card in cards:
        if card['country']  != 'FI' and card['country']  != 'SE':
            continue
        print()
        print(card['trackName'])
        process_card(card, car_model, volt_model, at)
    

if __name__ == '__main__':
    main()