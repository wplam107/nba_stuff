# Imports from https://github.com/swar/nba_api
from nba_api.stats.static import teams as tm
from nba_api.stats.endpoints import teamgamelog as tgl
from nba_api.stats.endpoints import playbyplayv2 as pbp

# Configs for ETL
from configparser import ConfigParser

# Timeout avoidance
from time import sleep

# Custom imports
from models import Game, Team
from etl_functions import to_json, upload_blob


# Get and set configs
config = ConfigParser()
config.read('./private/config.ini')
BUCKET = config.get('gcp', 'BUCKET')
SEASON = '20-21-reg'

# Retrieve and clean NBA team data
teams = tm.get_teams()
teams[0]['state'] = 'Georgia'
teams[7]['city'] = 'San Francisco'
teams[13]['city'] = 'Minneapolis'
teams[17]['city'] = 'Indianapolis'
teams[25]['city'] = 'Salt Lake City'

if __name__ == '__main__':
    team_objs = []
    for team in teams:
        team = Team(team)
        games = tgl.TeamGameLog(team.id).get_normalized_dict()['TeamGameLog']

        for game in games:
            game = Game(game)
            plays = pbp.PlayByPlayV2(game.game_id).get_normalized_dict()['PlayByPlay']
            game.insert_shots(plays)
            team.insert_game(dict(game))
            sleep(0.5)
        
        team_objs.append(dict(team))
        print(f'{team.full_name} ready')
        sleep(30)


    file = SEASON + '.json'
    to_json(team_objs, file)
    upload_blob(BUCKET, file, file)