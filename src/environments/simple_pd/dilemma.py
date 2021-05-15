from gym.spaces import Discrete
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from .game import Prisoners_Dilemma, Samaritans_Dilemma, Stag_Hunt, Chicken




def env(game='pd'):
    env = raw_env(game)
    env = wrappers.CaptureStdoutWrapper(env)
    #env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """Two-player environment for classic prisoners dilemma.
    The observation is simply the last opponent action."""

    metadata = {'render.modes': ['human'], "name": "simple_pd_v0"}


    def __init__(self, game='pd'):

        GAMES = {'pd':Prisoners_Dilemma(), 'sd':Samaritans_Dilemma(),'stag': Stag_Hunt(), 'chicken': Chicken()}

        self.game = GAMES[game]

        self.agents = ["player_" + str(r) for r in range(2)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: Discrete(2) for agent in self.agents}
        self.observation_spaces = {agent: Discrete(3) for agent in self.agents}

        self.reinit()

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: self.game.NONE for agent in self.agents}
        self.observations = {agent: self.game.NONE for agent in self.agents}
        self.num_moves = 0

    def render(self, mode="human"):
        try:
            #print('dones', self.dones)
            string = ("Current state: Agent1: {} , Agent2: {}".format(self.game.moves[self.state[self.agents[0]]], self.game.moves[self.state[self.agents[1]]]))
            print(string)
            print(self.rewards)
            print("")
            return self.dones
        except:
            'error'

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])

    def close(self):
        pass

    def reset(self):
        self.reinit()

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection

        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act


        #t > r > p > s
        #2r > t + s

        if self._agent_selector.is_last():
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = self.game.get_payoff()[(self.state[self.agents[0]], self.state[self.agents[1]])]

            self.num_moves += 1
            self.dones = {agent: self.num_moves >= self.game.get_num_iters() for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = self.game.NONE
            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
