from django.db import models
from user_authenticate.models import User


class Competition(models.Model):

    name = models.CharField(max_length=128)
    startDate = models.DateField()
    endDate = models.DateField()


class Field(models.Model):

    name = models.CharField(max_length=32)
    city = models.CharField(max_length=20)
    district = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class UseField(models.Model):
    """
        This model used to set time of football field using.
    """
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='uses')
    start = models.DateTimeField()
    end = models.DateTimeField()


class Team(models.Model):

    teamName = models.CharField(max_length=32, unique=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    captain = models.ForeignKey('Player', on_delete=models.CASCADE)
    city = models.CharField(max_length=32)
    favoriteField = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, blank=True)
    players = models.ManyToManyField('Player', related_name='teams')

    def __str__(self):
        return self.teamName

    class Meta:
        ordering = ('teamName',)


class Player(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    role = models.CharField(max_length=10, choices=(('goal', 'goalkeeper'),
                                                    ('def', 'defender'), ('mid', 'midfielder'), ('fwd', 'forward')))
    healthStatus = models.BooleanField(default=True, db_index=True)
    number = models.SmallIntegerField(null=True, blank=True)
    city = models.CharField(max_length=32)
    district = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        full_name = None
        if self.user.first_name and self.user.last_name:
            full_name = f"{self.user.first_name}  {self.user.last_name}"
        return full_name if full_name is not None else self.user.email

    class Meta:
        ordering = ('user',)

    def events(self):
        events_all = Event.objects.all()
        return events_all.filter(teamA__players=self), events_all.filter(teamB__players=self)

    @property
    def stat(self, team_id=None, competition_id=None):
        # calculates statistics for the player belong to particular team.
        my_events_a, my_events_b = self.events()

        if team_id:
            my_events = my_events_a.filter(teamA__id=team_id) | my_events_b.filter(teamB__id=team_id)
        if competition_id:
            my_events = my_events.filter(competition__id=competition_id)
        else:
            my_events = my_events_a | my_events_b

        wins, looses, draws = 0, 0, 0

        # stat for events, where player in team A.
        for event in my_events_a:
            stat = event.stat['stat']
            if stat['winner'] == event.teamA.id:
                wins += 1
            elif stat['winner'] == event.teamB.id:
                looses += 1
            elif stat['draw']:
                draws += 1

        # stat for events, where player in team B.
        for event in my_events_b:
            stat = event.stat['stat']
            if stat['winner'] == event.teamB.id:
                wins += 1
            elif stat['winner'] == event.teamA.id:
                looses += 1
            elif stat['draw']:
                draws += 1
        my_goals = Goal.objects.filter(author=self)
        goals = my_goals.count()
        assists = Goal.objects.filter(assistant=self).count()
        goals_plus_assist = my_goals.filter(assistant=self).count()
        penalties = my_goals.filter(condition='penalty').count()

        return {'stat': {'wins': wins, 'loses': looses, 'draws': draws, 'goals': goals, 'assists': assists,
                         'goals_plus_assist': goals_plus_assist, 'penalties': penalties}}


class Event(models.Model):

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, blank=True, null=True)
    typeOfEvent = models.CharField(choices=(('match', 'match'), ('training', 'training')), max_length=8,
                                   default='training', verbose_name='Type of event')
    date = models.DateField(verbose_name='Date of event')
    startTime = models.TimeField(verbose_name='Time of start')
    status = models.CharField(choices=(('planned', 'planned'), ('cancelled', 'cancelled'), ('live', 'live'),
                                       ('postponed', 'postponed'), ('is over', 'is over')), max_length=9)
    teamA = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='events', verbose_name="Team A")
    teamB = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Team B")
    field = models.ForeignKey(Field, on_delete=models.CASCADE)

    class Meta:
        ordering = ('date',)
        unique_together = ('date', 'startTime', 'teamA', 'teamB')

    @property
    def stat(self):

        # This property returns statistics for an event

        team_a_goals = self.goals.filter(scoringTeam=self.teamA).count()
        team_b_goals = self.goals.filter(scoringTeam=self.teamB).count()

        team_a_cards_yellow = self.cards.filter(receivedTeam=self.teamA, color='yellow').count()
        team_b_cards_yellow = self.cards.filter(receivedTeam=self.teamB, color='yellow').count()

        team_a_cards_red = self.cards.filter(receivedTeam=self.teamA, color='red').count()
        team_b_cards_red = self.cards.filter(receivedTeam=self.teamA, color='red').count()

        team_a_substitutions = self.substitutions.filter(inTeam=self.teamA).count()
        team_b_substitutions = self.substitutions.filter(inTeam=self.teamB).count()

        if self.status != 'is over':
            winner = None
            looser = None
            draw = False
        elif team_a_goals == team_b_goals:
            winner = None
            looser = None
            draw = True
        elif team_a_goals > team_b_goals:
            winner = self.teamA.id
            looser = self.teamB.id
            draw = False
        else:
            winner = self.teamB.id
            looser = self.teamA.id
            draw = False
        return {'stat': {'winner': winner, 'looser': looser, 'draw': draw, 'teamA_': {'id': self.teamA.id, 'goals': team_a_goals,
                'cardsYellow': team_a_cards_yellow, 'cardsRed': team_a_cards_red, 'substitutions': team_a_substitutions},
                'teamB_': {'id': self.teamB.id, 'goals': team_b_goals, 'cardsYellow': team_b_cards_yellow,
                'cardsRed': team_b_cards_red, 'substitutions': team_b_substitutions}}}


class Goal(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='goals')
    author = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='my_goals')
    assistant = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    scoringTeam = models.ForeignKey(Team, on_delete=models.CASCADE)
    time = models.TimeField()
    condition = models.CharField(choices=(('in game', 'in game'), ('free', 'free'), ('corner', 'corner'),
                                          ('penalty', 'penalty')), max_length=11)

    class Meta:
        ordering = ('event',)
        unique_together = ('event', 'time')


class Card(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='cards')
    author = models.ForeignKey(Player, on_delete=models, related_name='my_cards')
    time = models.TimeField()
    color = models.CharField(choices=(('yellow', 'yellow'), ('red', 'red')), max_length=6)
    receivedTeam = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        ordering = ('event',)
        unique_together = ('event', 'author', 'time')


class Substitution(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='substitutions')
    playerIn = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='substitutionsIn')
    playerOut = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='substitutionsOut')
    inTeam = models.ForeignKey(Team, on_delete=models.CASCADE)
    time = models.TimeField()

    class Meta:
        ordering = ('event',)
        unique_together = ('event', 'playerIn', 'playerOut')
