from api_tool import ApiTool;
from datetime import date, timedelta
import pandas as pd
import os

import json


class DataBuilder():

    def __init__(self, *args, **kwargs):
        self.api_tool = ApiTool()
        self.updatedDF: pd.DataFrame = pd.read_csv('updated.csv')
        self.performances = []
    
    def getLastUpdated(self):    
        last_row = self.updatedDF.tail(1)
        return [self.updatedDF["day"].iloc[-1], self.updatedDF["month"].iloc[-1], self.updatedDF["year"].iloc[-1]]
    
    def updateLastUpdated(self):
        today = date.today()
        temp_df = pd.DataFrame({'day':[today.day],'month': [today.month],'year': [today.year]})
        temp_df.to_csv('updated.csv', mode='a',header=False, index=False)   

    def buildDatabaseFromDate(self, day, month, year):
        
        today = date.today()
        
        if (year > today.year):
            print("Invalid date")
            return
        elif (year == today.year and month > today.month):
            print("Invalid date")
            return
        elif (year == today.year and month == today.month and day > today.day):
            print("Invalid date")
            return

        delta = timedelta(days=1)
        race_date = date(year, month, day)
        print(race_date)

        while race_date < today:
            self._handleDate(race_date)
            race_date += delta
        
        self.dataFrame = pd.DataFrame(self.performances)

        if not os.path.isfile('data.csv'):
            self.dataFrame.to_csv('data.csv', header='column_names', index=False)
        else:
            self.dataFrame.to_csv('data.csv',  mode='a', header=False, index=False)
            

    def _handleDate(self, date):
        cards = self.api_tool.getCardsForDate(date.day, date.month, date.year)
        jsonCards = json.loads(cards.text)['collection']

        for jsonCard in jsonCards:
            if (jsonCard['country'] == "FI" or jsonCard['country'] == "SE"):
                self._handleRaces(jsonCard['cardId'], date)


    def _handleRaces(self, cardId, date):
        races = self.api_tool.getRacesForCard(cardId)
        jsonRaces = json.loads(races.text)['collection']

        for jsonRace in jsonRaces:
            try:
                winner = int(str(jsonRace['toteResultString']).split('-')[0])
                time = jsonRace['startTime']
                start_type = jsonRace['startType']
                self._handleHorses(jsonRace['raceId'], winner, date, time, start_type)
            except:
                continue
            


    def _handleHorses(self, raceId, winner, date, time, start_type):

        

        pools = self.api_tool.getPoolsForRace(raceId)
        runners = self.api_tool.getHorsesForRace(raceId)

        jsonRunners = json.loads(runners.text)['collection']

        winnerPool = json.loads(pools.text)['collection'][0]

        if (winnerPool is None or winnerPool['poolType'] != "VOI"):
            return
        
        odds = self.api_tool.getOddsForPool(winnerPool['poolId'])
        jsonOdds = json.loads(odds.text)['odds']
        oddDict = {}

        for jsonOdd in jsonOdds:
            number = jsonOdd['runnerNumber']
            if ('probable' in jsonOdd):
                oddDict[number] =  float(jsonOdd['probable']) / 100

        for jsonHorse in jsonRunners:

            if (jsonHorse['startNumber'] not in oddDict):
                continue

            dbDict = {'Name': jsonHorse['horseName']}
            dbDict['FrontShoes'] = jsonHorse['frontShoes']
            dbDict['RearShoes'] = jsonHorse['rearShoes']
            dbDict['AmericanStyleCart'] = (jsonHorse['specialCart'] == 'YES')
            dbDict['CoachName'] = jsonHorse['coachName']
            dbDict['DriverName'] = jsonHorse['driverName']
            dbDict['Distance'] = jsonHorse['distance']
            dbDict['StartTrack'] = jsonHorse['startTrack']
            dbDict['Sire'] = jsonHorse['sire']
            dbDict['StartTime'] = time
            dbDict['StartType'] = start_type
            dbDict['Day'] = date.day
            dbDict['Month'] = date.month
            dbDict['Year'] = date.year

            if (winner == jsonHorse['startNumber']):
                dbDict['Winner'] = True
            else: 
                dbDict['Winner'] = False
            
            
            dbDict['Odds'] = oddDict[jsonHorse['startNumber']]

            self.performances.append(dbDict)
                










