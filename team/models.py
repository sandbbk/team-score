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

    @property
    def stat(self):

        teamAGoals = self.goal_set.filter(scoringTeam=self.teamA).count()
        teamBGoals = self.goal_set.filter(scoringTeam=self.teamB).count()
        teamACardsYellow = self.card_set.filter(receivedTeam=self.teamA, color='yellow').count()
        teamBCardsYellow = self.card_set.filter(receivedTeam=self.teamB, color='yellow').count()
        teamACardsRed = self.card_set.filter(receivedTeam=self.teamA, color='red').count()
        teamBCardsRed = self.card_set.filter(receivedTeam=self.teamA, color='red').count()
        teamAsubstitutions = self.substitution_set.filter(inTeam=self.teamA).count()
        teamBsubstitutions = self.substitution_set.filter(inTeam=self.teamB).count()

        if self.status != 'is over':
            winner = None
            looser = None
            draw = False
        elif teamAGoals == teamBGoals:
            winner = None
            looser = None
            draw = True
        elif teamAGoals > teamBGoals:
            winner = self.teamA
            looser = self.teamB
            draw = False
        else:
            winner = self.teamB.id
            looser = self.teamA.id
            draw = False
        return {'winner': winner, 'looser': looser, 'draw': draw, 'teamA': {'id': self.teamA.id, 'goals': teamAGoals,
                'cardsYellow': teamACardsYellow, 'cardsRed': teamACardsRed, 'substitutions': teamAsubstitutions},
                'teamB': {'id': self.teamB.id, 'goals': teamBGoals, 'cardsYellow': teamBCardsYellow,
                'cardsRed': teamBCardsRed, 'substitutions': teamBsubstitutions}}


class Goal(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='goals')
    author = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='goals')
    assistant = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    scoringTeam = models.ForeignKey(Team, on_delete=models.CASCADE)
    time = models.TimeField()
    condition = models.CharField(choices=(('in game', 'in game'), ('free', 'free'), ('corner', 'corner'),
                                          ('penalty', 'penalty'), ('penalty 11m', 'penalty 11m')), max_length=11)

    class Meta:
        ordering = ('event',)


class Card(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='cards')
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    time = models.TimeField()
    color = models.CharField(choices=(('yellow', 'yellow'), ('red', 'red')), max_length=6)
    receivedTeam = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        ordering = ('event',)


class Substitution(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='substitutions')
    playerIn = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='substitutionsIn')
    playerOut = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='substitutionsOut')
    inTeam = models.ForeignKey(Team, on_delete=models.CASCADE)
    time = models.TimeField()

    class Meta:
        ordering = ('event',)
