# NBA API imports
from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.endpoints import playbyplayv2

# Google Cloud imports
from google.cloud import storage

# Standard imports
import re
import os
import time

# External JSON imports
import ndjson


######################
# Cleaning Functions # 
######################
def transform_game_log(game_log):
    """
    Transform list of games (with duplicates) into list of distinct games:
    {'id': <id>, 'date': <date>, 'home_team': <team>, 'away_team': <team>}
    """

    games_dict = {}
    games_list = []

    for game in game_log:
        _id = game['GAME_ID']
        if _id not in games_dict.keys():
            games_dict[_id] = {
                'id': _id,
                'date': game['GAME_DATE'],
                'home_team': None,
                'away_team': None,
            }

        if '@' in game['MATCHUP']:
            games_dict[_id]['away_team'] = game['TEAM_ID']
        else:
            games_dict[_id]['home_team'] = game['TEAM_ID']

        if games_dict[_id]['home_team'] and games_dict[_id]['away_team']:
            games_list.append(games_dict[_id])

    return games_list

def create_game(game):
    """
    Function to create game dictionary
    """

    obj = {
        'id': game['id'],
        'date': game['date'],
        'home_team': {
            'id': game['home_team'],
            'shots': []
        },
        'away_team': {
            'id': game['away_team'],
            'shots': []
        }
    }

    return obj

def _get_shot(play):
    """
    Function to get shot type and range from 'EVENTMSGTYPE' in play dictionary
    """

    # Get play description
    if play['HOMEDESCRIPTION']:
        description = play['HOMEDESCRIPTION']
    if play['NEUTRALDESCRIPTION']:
        description = play['NEUTRALDESCRIPTION']
    if play['VISITORDESCRIPTION']:
        description = play['VISITORDESCRIPTION']

    # Extract range
    try:
        shot_range = int(re.search(r"[0-9]*(?=')", description)[0])
    except:
        shot_range = None

    # Extract shot type (2PT or 3PT)
    if re.search(r"3PT", description):
        shot_type = '3PT'
    else:
        shot_type = '2PT'

    return shot_type, shot_range

def _get_time_elapsed(play):
    """
    Function to convert play clock to time elapsed in game
    """
    
    base_time = 0
    for i in range(1, play['PERIOD']):
        if i <= 4:
            base_time += 12
        else:
            base_time += 5
    
    time_div = play['PCTIMESTRING'].split(':')
    if play['PERIOD'] <= 4:
        period_time = 12
    else:
        period_time = 5

    if time_div[1] == '00':
        minutes = period_time - int(time_div[0])
        seconds = 0
    else:
        minutes = period_time - 1 - int(time_div[0])
        seconds = 60 - int(time_div[1])

    minutes = str(minutes + base_time)
    if seconds == 0:
        seconds = '00'
    elif seconds < 10:
        seconds = '0' + str(seconds)
    else:
        seconds = str(seconds)

    return minutes + ':' + seconds

def insert_shots(plays, game):
    """
    Function accepts list of play objects and appends shot dictionaries into home or away team shots
    """

    home_shots = 0
    away_shots = 0

    for play in plays:
        # Determine if shot
        if (play['EVENTMSGTYPE'] == 1) or (play['EVENTMSGTYPE'] == 2):
            
            # Determine if shot was make or miss
            f = lambda x: True if x == 1 else False
            is_make = f(play['EVENTMSGTYPE'])

            # Determine home or away team
            if play['PLAYER1_TEAM_ID'] == game['home_team']['id']:
                home_shots += 1
                shot_type, shot_range = _get_shot(play)

                shot = {
                    'shot_number': home_shots,
                    'player_id': play['PLAYER1_ID'],
                    'period': play['PERIOD'],
                    'play_clock': play['PCTIMESTRING'],
                    'time_elapsed': _get_time_elapsed(play),
                    'shot_type': shot_type,
                    'shot_range': shot_range,
                    'is_make': is_make
                }
                game['home_team']['shots'].append(shot)

            else:
                away_shots += 1
                shot_type, shot_range = _get_shot(play)

                shot = {
                    'shot_number': away_shots,
                    'player_id': play['PLAYER1_ID'],
                    'period': play['PERIOD'],
                    'play_clock': play['PCTIMESTRING'],
                    'time_elapsed': _get_time_elapsed(play),
                    'shot_type': shot_type,
                    'shot_range': shot_range,
                    'is_make': is_make
                }
                game['away_team']['shots'].append(shot)

    return game


#####################
# Loading Functions #
#####################
def to_json(data, file):
    """
    Write data to newline delimited JSON file
    """

    with open(file, 'w') as f:
        ndjson.dump(data, f)

    print(f'{file} written')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to GCS".format(
            source_file_name, destination_blob_name
        )
    )


##############
# Run script #
##############
if __name__ == '__main__':
    BUCKET = os.environ.get('BUCKET')

    game_log = leaguegamelog.LeagueGameLog().get_normalized_dict()['LeagueGameLog']
    game_list = transform_game_log(game_log)
    season = game_log[0]['SEASON_ID']

    game_dicts = []
    i = 0
    for game in game_list:
        game_dict = create_game(game)
        plays = playbyplayv2.PlayByPlayV2(game_dict['id']).get_normalized_dict()['PlayByPlay']
        game_dict = insert_shots(plays, game_dict)
        game_dicts.append(game_dict)
        time.sleep(0.75)

        i += 1
        if i % 50 == 0:
            time.sleep(30)

    file = 'games' + '_' + season + '.json'
    to_json(game_dicts, file)
    upload_blob(BUCKET, file, file)
