from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from gym import spaces
import numpy as np
import warnings
from scipy import stats

from pettingzoo.utils import wrappers

#from .board import Board

NONE = [0,0,0,0,0]
NUM_ITERS = 100

def env():
    env = raw_env()
    env = wrappers.CaptureStdoutWrapper(env)
    #env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    #env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    metadata = {'render.modes': ['human'], "name": "blotto_v0"}

    def __init__(self, size=5, num_resources=100):
        super().__init__()
        self.size = size
        self.board = self.squares = [0] * size
        self.num_resources = num_resources


        self.agents = ["player_1", "player_2"]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))


        #self.action_spaces = {i:  spaces.Box(low= np.zeros((self.size,)), high= np.ones((self.size,))*self.num_resources, shape=(self.size,), dtype=np.int8) for i in self.agents}
        #self.observation_spaces = {i:  spaces.Box(low= np.zeros((self.size,)), high= np.ones((self.size,))*self.num_resources, shape=(self.size,), dtype=np.int8) for i in self.agents}

        self.action_spaces = {i:  spaces.MultiDiscrete([self.num_resources for x in range(self.size)]) for i in self.agents}
        self.observation_spaces = {i:  spaces.MultiDiscrete([self.num_resources for x in range(self.size)]) for i in self.agents}


        self.rewards = {i: 0 for i in self.agents}
        self.dones = {i: False for i in self.agents}
        #self.infos = {i: {'legal_moves': list(range(0, 9))} for i in self.agents}

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

        self.reinit()


    # Key
    # ----
    # blank space = 0
    # agent 0 = 1
    # agent 1 = 2
    # An observation is list of lists, where each list represents a row
    #
    # [[0,0,2]
    #  [1,2,1]
    #  [2,1,0]]


    def reinit(self):
        print('lk')
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: NONE for agent in self.agents}
        self.observations = {agent: NONE for agent in self.agents}
        self.num_moves = 0

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])


        return {'observation': observation}

    def _legal_moves(self):
        return [i for i in range(len(self.board.squares)) if self.board.squares[i] == 0]

    # action in this case is a value from 0 to 8 indicating position to move on tictactoe board
    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection

        self.state[self.agent_selection] = action
        #print("agent1",self.state[self.agents[0]])
        #print("agent2",self.state[self.agents[1]])
        #print("sum",sum(self.state[self.agents[0]] - self.state[self.agents[1]]))


        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            win_counter = []
            for i in range(self.size):
                if self.state[self.agents[0]][i] > self.state[self.agents[1]][i]:
                    win_counter.append(0)
                else:
                    win_counter.append(1)

            m, _ = stats.mode(win_counter)
            winner = m[0]

            if winner == 0:
                self.rewards[self.agents[0]] = 1
                self.rewards[self.agents[1]] = -1

            else:
                self.rewards[self.agents[0]] = -1
                self.rewards[self.agents[1]] = 1

            #illegal states
            if sum(self.state[self.agents[0]]) > self.num_resources: self.rewards[self.agents[0]] = -10
            if sum(self.state[self.agents[1]]) > self.num_resources: self.rewards[self.agents[1]] = -10



            self.num_moves += 1
            self.dones = {agent: self.num_moves >= NUM_ITERS for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = NONE
            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

    def reset(self):
        # reset environment
        self.board =[0] * self.size

        self.agents = self.possible_agents[:]
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {i: 0 for i in self.agents}
        self.dones = {i: False for i in self.agents}
        self.infos = {i: {} for i in self.agents}
        # selects the first agent
        self._agent_selector.reinit(self.agents)
        self._agent_selector.reset()
        self.agent_selection = self._agent_selector.reset()

    def render(self, mode="human"):
        #if len(self.state[self.agents[1]]) and len(self.state[self.agents[0]]):
        try:
            game_state_string = ("Current state: Agent1: {} , Agent2: {}".format(np.array(self.state[self.agents[0]]).flatten(), np.array(self.state[self.agents[1]]).flatten()))
            print(game_state_string)
            print('winner is: ', np.argmax([self.rewards[self.agents[0]], self.rewards[self.agents[1]]]))
            #print('wins ', stats.mode(self.win_counter))

            return
        except:
            'error'


         #game_state_string


    def close(self):
        pass
