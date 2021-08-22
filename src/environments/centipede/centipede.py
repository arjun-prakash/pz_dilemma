from gym import spaces
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers


MOVES = ['DEFECT', 'COOPERATE', 'NONE']
NUM_ITER = 100

def env(prob=False):
    env = raw_env(prob=prob)

    env = wrappers.CaptureStdoutWrapper(env)
    #env = wrappers.AssertOutOfBoundsWrapper(env)
    #env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """Two-player environment for classic centipede game .
    The observation is simply the last opponent action.

    https://www.semanticscholar.org/paper/The-Dynamic-of-Bicycle-Finals%3A-A-Theoretical-and-of-Dilger-Geyer/28ed6c168374bf1866fcdc0f01fa094448a1f009
    https://www.researchgate.net/publication/283119813_Strategic_Behavior_in_Road_Cycling_Competitions
    https://www.mdpi.com/2073-4336/11/3/35

    https://www.econstor.eu/bitstream/10419/167945/1/834230089.pdf
    """

    metadata = {'render.modes': ['human'], "name": "centipded_v0"}


    def __init__(self,n_agents=2, endowment=1, prob=False):

        self.prob = prob
        self.c = 0.1
        self.t = 200
        self.r = 0.5
        self.p = 0.7

        self.agents = ["player_" + str(r) for r in range(n_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: spaces.Discrete(2) for agent in self.agents}
        self.observation_spaces = {agent: spaces.Discrete(3) for agent in self.agents}
        print('Centipede!', NUM_ITER)
        print(self.observation_spaces)
        self.state = {agent: 2 for agent in self.agents}
        self.endowment = 1

        self.reinit()

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.observations = {agent: 2 for agent in self.agents} #placeholder
        self.state = {agent: 2 for agent in self.agents}

        self.endowment = 1
        self.num_moves = 0

    def render(self, mode="human"):
        try:
            #print('dones', self.dones)
            for i in self.agents:
                str_moves = ("Current moves of: {} , {}".format(i, MOVES[self.state[i]]))
                print(str_moves)
            print('rewards', self.rewards)
            print("")
            return self.dones
        except:
            'error'

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        #print('agent ', agent)
        #print('observation' , np.array(self.observations[agent]))
        return np.array(self.observations[agent])



    def close(self):
        pass

    def reset(self):
        self.reinit()

    def step(self, action):
        if self.dones[self.agent_selection]:
            r = self._was_done_step(action)
            return


        agent = self.agent_selection

        if self.prob:
            if action == 0:
                action = np.random.choice([0,1], p=[0.01,0.99])
                #if action == 1: print('flipped')

        self.state[agent] = action



        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            #print('iter', self.num_moves)

            if self.state[self.agents[0]] == 1 and self.state[self.agents[1]] == 1:
                self.rewards[self.agents[0]] = 0
                self.rewards[self.agents[1]] =  0

                self.num_moves += 1
                self.endowment += 2

                self.dones = {agent: self.num_moves >= NUM_ITER for agent in self.agents}

            elif self.state[self.agents[0]] == 0: #ORIGINAL IS 0
                self.rewards[self.agents[0]] = (self.endowment/2) + 1
                self.rewards[self.agents[1]] = (self.endowment/2) - 1

                self.dones = {agent: True for agent in self.agents}

            elif self.state[self.agents[1]] == 0: #original is 1
                self.rewards[self.agents[0]] = (self.endowment/2) - 1
                self.rewards[self.agents[1]] = (self.endowment/2) + 1

                self.dones = {agent: True for agent in self.agents}

            if self.num_moves >= NUM_ITER:
                print('game ended peacfully')
                self.rewards[self.agents[0]] = -1 #(self.endowment/2)
                self.rewards[self.agents[1]] = -1#  (self.endowment/2)
                self.dones = {agent: True for agent in self.agents}



            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]


        else:

            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = 2
            self._clear_rewards()


        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
