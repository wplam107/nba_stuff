import re
import dateutil.parser as dparser

class Shot:
    def __init__(self, shot, shot_num):
        self.shot_num = shot_num
        self.player_id = shot['PLAYER1_ID']
        self.period = shot['PERIOD']
        self.play_clock = shot['PCTIMESTRING']

        # Determine if shot was make or miss
        f = lambda x: True if x == 1 else False
        self.is_make = f(shot['EVENTMSGTYPE'])

        # Get play description used for data extraction
        if shot['HOMEDESCRIPTION']:
            self.description = shot['HOMEDESCRIPTION']
        if shot['NEUTRALDESCRIPTION']:
            self.description = shot['NEUTRALDESCRIPTION']
        if shot['VISITORDESCRIPTION']:
            self.description = shot['VISITORDESCRIPTION']

        self.time_elapsed = None
        self.shot_type = None
        self.range = None

    def get_time_elapsed(self):
        """
        Method to convert play clock to time elapsed in game
        """
        
        base_time = 0
        for i in range(1, self.period):
            if i <= 4:
                base_time += 12
            else:
                base_time += 5
        
        time_div = self.play_clock.split(':')
        if self.period <= 4:
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

        self.time_elapsed = minutes + ':' + seconds

    def get_shot(self):
        """
        Method to get shot type and range from 'EVENTMSGTYPE' in play dictionary
        """

        # Extract range
        try:
            self.range = int(re.search(r"[0-9]*(?=')", self.description)[0])
        except:
            self.range = None

        # Extract shot type (2PT or 3PT)
        if re.search(r"3PT", self.description):
            self.shot_type = '3PT'
        else:
            self.shot_type = '2PT'

    def __iter__(self):
        yield 'shot_number', self.shot_num
        yield 'player_id', self.player_id
        yield 'period', self.period
        yield 'play_clock', self.play_clock
        yield 'time_elapsed', self.time_elapsed
        yield 'shot_type', self.shot_type
        yield 'range', self.range
        yield 'is_make', self.is_make


class Game:
    def __init__(self, game):
        self.game_id = game['Game_ID']
        self.date = dparser.parse(game['GAME_DATE']).date()

        if re.search(r'@', game['MATCHUP']):
            self.is_home = False
        else:
            self.is_home = True

        self.opponent = game['MATCHUP'].split()[2]
        self.shots = []

    def insert_shots(self, plays):
        """
        Method to insert a list of plays
        """

        i = 1
        for play in plays:
            # Determine if play is shot, only inserting shots
            if (play['EVENTMSGTYPE'] == 1) or (play['EVENTMSGTYPE'] == 2):
                if play['PLAYER1_TEAM_ABBREVIATION'] != self.opponent:
                    shot = Shot(play, i)
                    shot.get_time_elapsed()
                    shot.get_shot()
                    self.shots.append(dict(shot))
                    i += 1
                else:
                    pass
            else:
                pass

    def __iter__(self):
        yield 'game_id', self.game_id
        yield 'date', self.date
        yield 'is_home', self.is_home
        yield 'opponent', self.opponent
        yield 'shots', self.shots


class Team:
    def __init__(self, team):
        self.id = team['id']
        self.full_name = team['full_name']
        self.abbreviation = team['abbreviation']
        self.nickname = team['nickname']
        self.city = team['city']
        self.state = team['state']
        self.games = []

    def insert_game(self, game):
        assert type(game) == dict
        self.games.append(game)

    def __iter__(self):
        yield 'id', self.id
        yield 'full_name', self.full_name
        yield 'abbreviation', self.abbreviation
        yield 'nickname', self.nickname
        yield 'city', self.city
        yield 'state', self.state
        yield 'games', self.games