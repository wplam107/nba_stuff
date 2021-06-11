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

class Game:
    def __init__(self, game):
        self.id = game['id']
        self.date = game['date']
        self.is_home = game['is_home']
        self.opponent = game['opponent']
        self.shots = []

    def insert_shot(self, shot):
        assert type(shot) == dict
        self.shots.append(shot)

    def __iter__(self):
        yield 'game_id', self.id
        yield 'date', self.date
        yield 'is_home', self.is_home
        yield 'opponent', self.opponent
        yield 'shots', self.shots

class Shot:
    def __init__(self, shot):
        self.id = shot['EVENTNUM']
        self.player_id = shot['PLAYER1_ID']
        self.period = shot['PERIOD']
        self.play_clock = shot['PCTIMESTRING']
        self.time_elapsed = None
        self.shot_type = None
        self.range = None

        f = lambda x: True if x == 1 else False
        self.is_make = f(shot['EVENTMSGNUM'])

        if shot['HOMEDESCRIPTION']:
            self.description = shot['HOMEDESCRIPTION']
        if shot['NEUTRALDESCRIPTION']:
            self.description = shot['NEUTRALDESCRIPTION']
        if shot['VISITORDESCRIPTION']:
            self.description = shot['VISITORDESCRIPTION']

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

    def get_shot_type(self):
        """
        Method to get shot type from 'EVENTMSGTYPE' in play dictionary
        """

        