import requests as rq
import sqlite3
from config import *
import time
from concurrent.futures import ThreadPoolExecutor, wait
import pandas as pd
import json
import os

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
        self.lol_version = self.get_lol_version()
        self.key = key
        self.tier = ["PLATINUM","DIAMOND"]
        self.div = ["I","II","III","IV"]
        self.region = ["euw1","kr","na1"]
        self.languages = ["it_IT","en_US"]
    
    def get_lol_version(self):
        return rq.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]

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
    
    def match_list(self,reg="euw1",*args,**kwargs):
        """
        populate db with matchIds
        """
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM players WHERE server='{reg}'")
        players = cursor.fetchall()
        cursor.close()
        
        try:
            for p in players:
                player = Player(region=p[0],summoner_id=p[1],account_id=p[2],puuid=p[3])
                player.insert_match_list()
                
                return #FIXME
        except Exception as e:
            print(e)
    
    def matches_fetch(self,reg="euw1",*args,**kwargs):
        region = self.convert_region(reg)
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.execute(f"""SELECT * FROM matches 
                            WHERE server='{reg}' AND notFetched=true""")            

        matches = [m[1] for m in cursor.fetchall()]
        cursor.close()
        for m in matches:
            try:
                match = Match(m,region)
                if not match.check_version(self.lol_version):
                    connection = sqlite3.connect(db)
                    cursor = connection.cursor()
                    cursor.execute(f"""UPDATE matches
                                       SET notFetched = false, discarded=true
                                       WHERE id='{m}'""")
                    connection.commit()
                    connection.close()
                    continue
                match.match_analysis()
            except Exception as e:
                print(e)
    
    def champ_name_converter(self, items):
        url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions.json"
        data = self.request(url, "champ names")
        names = []
        for _id in items["champID"]:
            for c in data:
                if _id == c["character_id"]:
                    names.append(c["display_name"])
                    break
        return pd.DataFrame(names,columns =['names'])

    def items_name_converter(self, items:dict, lang):
        if lang == "it_IT":
            url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/it_it/v1/tftitems.json"
        else:
            url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftitems.json"
        data = self.request(url, "item conversion")
        final_dict = {}
        for champ in items.keys():
            new_items = []
            for item in items[champ]:
                for i in data:
                    if i["nameId"] == item:
                        new_items.append(i["name"])
                        break
            final_dict[champ] = new_items
        if not os.path.isdir("./results/"):
            os.makedirs("./results/")
        with open(f"results/item_dict_{lang}.json","w") as f:
            json.dump(final_dict, f, indent=2)
                


    def champion_items_maker(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        with open('queries/champ_items_view.sql') as f:
            query = f.read()
        cursor.execute(query)
        cursor.close()

        with open('queries/champ_items_select.sql') as f:
            query1 = f.read()
        connection = sqlite3.connect(db)
        items = pd.read_sql_query(query1, connection)
        names = self.champ_name_converter(items)
        final = pd.concat([names,items], axis=1)

        build={}
        for champ in final["names"]:
            row = final[final["names"]==champ]
            build[champ] = [row.iat[0,2],row.iat[0,3],row.iat[0,4]]
        
        for lang in self.languages:
            self.items_name_converter(build, lang)

        
                    
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
        cursor.executescript(f"""INSERT INTO players(server,summonerId,accountId,puuid)
            VALUES ('{self.region}','{self.summoner_id}','{self.account_id}','{self.puuid}');""")
        connection.close()
    
    def insert_match_list(self):      # 10 games per player
        region = self.convert_region(self.region)
        url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{self.puuid}/ids?start=0&count=10&api_key={key}"
        match_ids = self.request(url, f"match list from player in region {region}")  
        
        data = [(self.region, id, False, True, False) for id in match_ids]
        
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        with open('queries/insert_match_id.sql') as f:
            query = f.read()
        cursor.executemany(query,data)
        connection.commit()
        cursor.close()

class Match(Utils):
    def __init__(self,match_id,server="europe"):
        self.id = match_id
        self.url = f"https://{server}.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key={key}"
        self.data = self.request(self.url, "match data")
        self.region = server
    
    def check_version(self,version):
        v = "".join([i for i in version.split(".")[:2]])   # exctract current patch
        m_v = "".join([i for i in self.data['info']['game_version'].lstrip('Version ').split(".")[:2]])
        if v != m_v:
            return False
        return True

    def list_complete(self, l:list, lenght:int):
        """Sort the list and add zeros to reach the max lenght"""
        l.sort()
        while len(l)<lenght:
            l.append(0)
        return l[:lenght]

    def match_analysis(self):
        comp_params, champ_params = [],[]
        for comp in self.data['info']['participants']:
            augments = comp['augments']
            traits = [c['name'] for c in comp['traits'] if c['tier_current'] > 0 ]
            place = comp['placement']
            champions = []
            for champ in comp['units']:
                name = champ['character_id']
                items = champ['itemNames']
                champions.append(name)

                sql_row = tuple([self.id,place,name] + self.list_complete(items,3))
                champ_params.append(sql_row)
            
            sql_row = tuple([self.id,place] + self.list_complete(traits, 8) + self.list_complete(champions, 10) + self.list_complete(augments, 3))
            comp_params.append(sql_row)
        
        with open('queries/comp_insert.sql') as f:
            query1 = f.read()
        with open('queries/champ_insert.sql') as f:
            query2 = f.read()
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.executemany(query1, comp_params)
        connection.commit()
        cursor.close()
        
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.executemany(query2, champ_params)
        connection.commit()
        cursor.close()

        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.execute(f"""UPDATE matches
                            SET notFetched= false, fetched=true
                            WHERE id='{self.id}'""")
        connection.commit()
        connection.close()


        
        