import numpy as np


class Game():

    def __init__(self, num_iters=1000):
        self.moves = []
        self.num_iters = num_iters


    def get_payoff(self):
        pass

    def get_num_iters(self):
        return self.num_iters


class Prisoners_Dilemma(Game):

    def __init__(self):

        super().__init__()

        self.COOPERATE = 0
        self.DEFECT = 1
        self.NONE = 2
        self.moves = ["COOPERATE", "DEFECT", "None"]

        self.r = 3 #reward
        self.p = 1 #punishment
        self.t = 5 #temptation
        self.s = 0 #suckers payoff

        self.payoff = {
            (self.COOPERATE, self.COOPERATE): (self.r, self.r),
            (self.COOPERATE, self.DEFECT): (self.s, self.t),
            (self.DEFECT, self.COOPERATE): (self.t, self.s),
            (self.DEFECT, self.DEFECT): (self.p, self.p)
        }

    def get_payoff(self):

        return self.payoff


class Samaritans_Dilemma(Game):

    def __init__(self):

        super().__init__()


        self.SOCIAL = 0
        self.ANTI_SOCIAL = 1
        self.NONE = 2
        self.moves = ["SOCIAL", "ANTI_SOCIAL", "None"]



        self.payoff = {
            (self.ANTI_SOCIAL, self.SOCIAL): (2, 2), #no help, work
            (self.ANTI_SOCIAL, self.ANTI_SOCIAL): (1, 1), #no help, no work
            (self.SOCIAL, self.SOCIAL): (4,3), #help, work
            (self.SOCIAL, self.ANTI_SOCIAL): (3, 4) #help, no work
        }

    def get_payoff(self):

        return self.payoff

class Stag_Hunt(Game):

    def __init__(self):

        super().__init__()


        self.STAG = 0
        self.HARE = 1
        self.NONE = 2
        self.moves = ["STAG", "HARE", "None"]



        self.payoff = {
            (self.STAG, self.STAG): (4, 4),
            (self.STAG, self.HARE): (1, 3),
            (self.HARE, self.STAG): (3,1),
            (self.HARE, self.HARE): (2, 2)
        }

    def get_payoff(self):

        return self.payoff


class Chicken(Game):

    def __init__(self):

        super().__init__()


        self.SWERVE = 0
        self.STRAIGHT = 1
        self.NONE = 2
        self.moves = ["SWERVE", "STRAIGHT", "None"]



        self.payoff = {
            (self.SWERVE, self.SWERVE): (0, 0),
            (self.STRAIGHT, self.SWERVE): (1, -1),
            (self.SWERVE, self.STRAIGHT): (-1,1),
            (self.STRAIGHT, self.STRAIGHT): (-1000, -1000)
        }

    def get_payoff(self):

        return self.payoff
