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