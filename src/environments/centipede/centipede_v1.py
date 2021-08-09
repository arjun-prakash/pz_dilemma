from gym import spaces
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
import supersuit as ss


MOVES = ['DEFECT', 'COOPERATE', 'NONE']
NUM_ITER = 100

def env():
    env = raw_env()

    env = wrappers.CaptureStdoutWrapper(env)
    #env = ss.flatten_v0(env)
    #env = ss.dtype_v0(env, np.int8)
    #env = wrappers.AssertOutOfBoundsWrapper(env)
    #env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """Two-player environment for classic prisoners dilemma.
    The observation is simply the last opponent action.

    http://www.ifaamas.org/Proceedings/aamas2021/pdfs/p898.pdf
    """

    metadata = {'render.modes': ['human'], "name": "centipded_v0"}


    def __init__(self,n_agents=2, endowment=1):

        self.pool = 0
        self.c = 0.1
        self.t = 200
        self.r = 0.5
        self.p = 0.7

        self.agents = ["player_" + str(r) for r in range(n_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: spaces.Discrete(3) for agent in self.agents}
        self.observation_spaces = {agent: spaces.Discrete(NUM_ITER) for agent in self.agents}

        #self.observation_spaces = {agent: spaces.Dict({'op_action':spaces.Discrete(2), 'num_moves':spaces.Box(low=0, high=NUM_ITER, shape=(1,1), dtype=np.int8)}) for agent in self.agents}
        #self.observation_spaces = {agent: spaces.Box(low=0, high=NUM_ITER, shape=(2,), dtype=np.int8) for agent in self.agents}
        #self.observation_spaces = {i:  spaces.MultiDiscrete([3,NUM_ITER]) for i in self.agents}


        print('Centipede!')
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
        self.observation_spaces = {i:  spaces.MultiDiscrete([3,NUM_ITER]) for i in self.agents}
        self.state = {agent: 2 for agent in self.agents}
        self.observations = {agent: np.zeros(100) for agent in self.agents}

        self.endowment = 10
        self.num_moves = 0

    def render(self, mode="human"):
        try:
            #print('dones', self.dones)
            for i in self.agents:
                str_moves = ("Current moves of: {} , {}".format(i, MOVES[self.state[i]]))
                print(str_moves)
            print('rewards', self.rewards)
            print("")
            print(self.observations)
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

        self.state[agent] = action


        #self.state[agent]['num_moves'] = self.num_moves





        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():

            if self.state[self.agents[0]] == 1 and self.state[self.agents[1]] == 1:
                self.rewards[self.agents[0]] = 1
                self.rewards[self.agents[1]] =  1

                self.num_moves += 1
                self.endowment +=1

                self.dones = {agent: self.num_moves >= NUM_ITER for agent in self.agents}

            elif self.state[self.agents[0]] == 0:
                self.rewards[self.agents[0]] = self.endowment + 10
                self.rewards[self.agents[1]] = self.endowment - 10

                self.dones = {agent: True for agent in self.agents}

            elif self.state[self.agents[1]] == 0:
                self.rewards[self.agents[0]] = self.endowment - 10
                self.rewards[self.agents[1]] = self.endowment + 10

                self.dones = {agent: True for agent in self.agents}


            # observe the current state
            for i in self.agents:
                #self.observations[i] = [self.state[self.agents[1 - self.agent_name_mapping[i]]], self.num_moves]
                #self.observations[i][1] = self.num_moves

                # self.observations[i][0] = np.eye(NUM_ITER)[self.state[self.agents[1 - self.agent_name_mapping[i]]]]
                # self.observations[i][1] = one_hot_targets = np.eye(NUM_ITER)[self.num_moves]





                tmp = np.zeros(NUM_ITER)
                tmp = np.insert(tmp, [self.state[self.agents[1 - self.agent_name_mapping[i]]]], self.num_moves)
                self.observations[i] = tmp
                print('obs', self.observations[i])





        else:

            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = np.zeros(100)
            self._clear_rewards()


        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
