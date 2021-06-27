from gym import spaces
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers


MOVES = ['DEFECT', 'COOPERATE', 'WAITING']

def env():
    env = raw_env()

    env = wrappers.CaptureStdoutWrapper(env)
    #env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """Two-player environment for classic prisoners dilemma.
    The observation is simply the last opponent action.

    http://www.ifaamas.org/Proceedings/aamas2021/pdfs/p898.pdf
    """

    metadata = {'render.modes': ['human'], "name": "CDN_v0"}


    def __init__(self,n_agents=6, endowment=100):

        self.pool = 0
        self.c = 0.1
        self.t = 200
        self.r = 0.5
        self.p = 0.7

        self.agents = ["player_" + str(r) for r in range(n_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: spaces.Discrete(2) for agent in self.agents}
        self.observation_spaces = {agent: spaces.Discrete(3) for agent in self.agents}
        print('Delimma!')
        print(self.observation_spaces)
        self.state = {agent: 2 for agent in self.agents}
        self.endowment = {agent: endowment for agent in self.agents}

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
        self.num_moves = 0

    def render(self, mode="human"):
        try:
            #print('dones', self.dones)
            for i in self.agents:
                str_moves = ("Current moves of: {} , {} with {}".format(i, MOVES[self.state[i]], self.endowment[i]))
                str_pool = ("Pool is: {} , Threshold is: {}".format(self.pool, self.t))
                print(str_moves)
            print('rewards', self.rewards)
            print(str_pool)
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
            return self._was_done_step(action)


        agent = self.agent_selection

        if action == 0: #DEFECT
            self.state[agent] = 0
        elif action == 1: #COOPERATE
            self.state[agent] = 1
            contribution = self.endowment[agent] * self.c
            self.endowment[agent] = self.endowment[agent] - contribution
            self.pool += contribution

        self.observations[agent] = action




        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():

            if self.pool > self.t:
                self.omega = 1
                is_disaster = 0
                self.dones = {agent: 1 for agent in self.agents}

            else:
                self.omega = 0
                is_disaster = np.random.choice(2,  p=[self.r, 1-self.r])

            for i in self.agents:
                if not is_disaster:
                    if self.observations[i] == 0:
                        self.rewards[i] = 0
                    elif self.observations[i] == 1:
                        self.rewards[i] = np.log(1 - self.c)

                if is_disaster:
                    if self.observations[i] == 0:
                        self.rewards[i] = np.log(1 - self.p)
                    elif self.observations[i] == 1:
                        self.rewards[i] = np.log(1 - self.c - self.p + (self.c*self.p))



            self.num_moves += 1
            self.dones = {agent: is_disaster for agent in self.agents}


        else:
            for i in self.agents:
                if self.agent_name_mapping[i] > self.agent_name_mapping[agent]:
                    self.state[i] = 2
                    #self.observations[self.agent_name_mapping[i]] = 2


            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
