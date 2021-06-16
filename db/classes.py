import re

class Game:
    def __init__(self, game):
        self.id = game['id']
        self.date = game['date']
        self.home_team = {
            'id': game['home_team'],
            'shots': []
        }
        self.away_team = {
            'id': game['away_team'],
            'shots': []
        }

    def get_time_elapsed(self, play):
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

    def get_shot(self, play):
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

    def insert_shots(self, plays):
        """
        Accepts list of play objects and inserts shot dictionary into home or away team shots
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
                if play['PLAYER1_TEAM_ID'] == self.home_team['id']:
                    home_shots += 1
                    shot_type, shot_range = self.get_shot(play)

                    shot = {
                        'shot_number': home_shots,
                        'player_id': play['PLAYER1_ID'],
                        'period': play['PERIOD'],
                        'play_clock': play['PCTIMESTRING'],
                        'time_elapsed': self.get_time_elapsed(play),
                        'shot_type': shot_type,
                        'shot_range': shot_range,
                        'is_make': is_make
                    }
                    self.home_team['shots'].append(shot)

                else:
                    away_shots += 1
                    shot_type, shot_range = self.get_shot(play)

                    shot = {
                        'shot_number': away_shots,
                        'player_id': play['PLAYER1_ID'],
                        'period': play['PERIOD'],
                        'play_clock': play['PCTIMESTRING'],
                        'time_elapsed': self.get_time_elapsed(play),
                        'shot_type': shot_type,
                        'shot_range': shot_range,
                        'is_make': is_make
                    }
                    self.away_team['shots'].append(shot)