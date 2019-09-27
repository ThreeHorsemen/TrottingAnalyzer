import requests

class ApiTool:


    def __init__(self):
        self.headers = {
	        'Content-type':'application/json',
	        'Accept':'application/json',
	        'X-ESA-API-Key':'ROBOT'
            }
        self.session = requests.Session()
    

    def getCardsForDate( self, day, month, year ):
        uri = "https://www.veikkaus.fi/api/toto-info/v1/cards/date/"  + str(year) +  "-" + str(month) + "-" + str(day)
        response = self.session.get(uri, headers=self.headers)
        return response

    def getRacesForCard(self, cardId):
        uri = "https://www.veikkaus.fi/api/toto-info/v1/card/" + str(cardId) + "/races"
        response = self.session.get(uri, headers=self.headers)
        return response
    
    def getHorsesForRace( self, raceId ):
        uri = "https://www.veikkaus.fi/api/toto-info/v1/race/" + str(raceId) + "/runners"
        response = self.session.get(uri, headers=self.headers)
        return response

    def getPoolsForRace( self, raceId ):
        uri = "https://www.veikkaus.fi/api/toto-info/v1/race/" + str(raceId) + "/pools"
        response = self.session.get(uri, headers=self.headers)
        return response
    
    def getOddsForPool(self, poolId):
        uri = "https://www.veikkaus.fi/api/toto-info/v1/pool/" + str(poolId) + "/odds" 
        response = self.session.get(uri, headers=self.headers)
        return response



    

        
    



