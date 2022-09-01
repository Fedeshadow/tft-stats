# tft-stats
## About the project
 ![Logo](images/logo.png)

This project handles the data analysis side of the Alexa Skill [Team Fight Tactics Comps ](https://it.wikipedia.org/wiki/Lingua_italiana "Lingua italiana").\
It makes use of the Riot Api and sqlite as a local database.

Altough it is already designed to collect sufficient data to make aviable more complex analysis, at the moment it only recomends best items for each champion.\
More functions, such as best augments for each comps and winrate, can be easily performed with a litte more SQL and Alexa Skill implementation.

Please note that you will need a Riot API development key in order to access the Riot Api, in order to collect players' and matches' id.


[Altra immagine]
###  Installation
1. Get a riot development API Key at [Riot development portal](https://developer.riotgames.com)
2. Clone the repo
	```sh 
	git clone https://github.com/Fedeshadow/tft-stats.git
	```
3. install pandas package (sqlite3 should be already installed)
	```sh 
	pip install pandas
	```
4. Enter your API and mongo credentials in  `config.py`
	```python
	key = "your_lol_API_key_goes_here"
	db = "database.db"
	```
5. run the script (on linux)
	```sh 
	nohup python3 -u main.py &>> activity.log&
	```