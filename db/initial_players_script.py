# Static data from https://github.com/swar/nba_api
from nba_api.stats.static import players as p

# File handling
import os

# Custom imports
from etl_functions import to_json, upload_blob, set_configs
from models import Player

if __name__ == '__main__':
    # Set configs
    BUCKET = set_configs()
    SEASON = '20-21'

    # Retrieve all active players and transform
    players = p.get_active_players()
    players = [ dict(Player(player)) for player in players ]

    # Load data then delete local file
    file = 'players-' + SEASON + '.json'
    to_json(players, file)
    upload_blob(BUCKET, file, file)
    os.remove(file)
    print(f'Local {file} removed.')