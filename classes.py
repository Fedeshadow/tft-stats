import requests as rq
import sqlite3
from config import *
import time
from concurrent.futures import ThreadPoolExecutor, wait

class Utils:
    
    def request(self,url:str,use_case:str):
        req = rq.get(url)
        if req.status_code == 429:
            time.sleep(125)
            print(f"key limit exeeded in {use_case}, sleeping 130s")
            req = rq.get(url)
        if req.status_code == 403:
            print(f"key expired while {use_case}")
            quit()
        return req.json()
    
    def threading_region(self, func ,iterable:list, use_case:str):
        print(f"{use_case} started")
        t1 = time.time()
        with ThreadPoolExecutor() as executor:
            executor.map(func, iterable)
        t2 = time.time()
        print(f"{use_case} completed in {t2-t1} seconds")
    
    def convert_region(self,reg):
        if reg == "euw1":
            region = "europe"
        elif reg == "kr":
            region = "asia"
        elif reg == "na1":
            region = "americas"
        return region
        
class Api(Utils):
    def __init__(self):
        #self.lol_version = self.get_lol_version()
        self.key = key
        self.tier = ["PLATINUM","DIAMOND"]
        self.div = ["I","II","III","IV"]
        self.region = ["euw1","kr","na1"]
        self.languages = ["it_IT","en_US"]
    
    #def get_lol_version(self):
    #    return rq.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]

    def player_url(self, region, tier, div, page):
        return f"https://{region}.api.riotgames.com/tft/league/v1/entries/{tier}/{div}?page={page}&api_key={key}"

    def player_list(self, region='euw1',*args,**kwargs):
        for tier in self.tier:
            for div in self.div:
                for page in range(1,3):
                    url = self.player_url(region, tier, div, page)
                    player_list = self.request(url, f"player list region: {region}")

                    for p in player_list:
                        if not p['inactive']:
                            player = Player(p['summonerId'],region)
                            player.insert()
                    #TODO maybe aggregate player in batch and insert them per page
                    # delete insert method and create a sql representation for the obj
                    # then data = list comprehension
                    return #FIXME
                    
class Player(Utils):
    def __init__(self,summoner_id,region,account_id=None,puuid=None):
        self.region = region
        self.summoner_id = summoner_id
        if account_id is None:
            self.account_id, self.puuid = self.get_account_id()
        else:
            self.account_id, self.puuid = account_id, puuid
    
    def get_account_id(self):
        url = f'https://{self.region}.api.riotgames.com/tft/summoner/v1/summoners/{self.summoner_id}?api_key={key}'
        data = self.request(url, f"account id region: {self.region}")
        return data["accountId"], data["puuid"]
    
    def insert(self):
        
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        # valuta se creare la query nel db
        cursor.executescript(f"""INSERT INTO player(server,summonerId,accountId,puuid)
            VALUES ('{self.region}','{self.summoner_id}','{self.account_id}','{self.puuid}');""")
        connection.close()