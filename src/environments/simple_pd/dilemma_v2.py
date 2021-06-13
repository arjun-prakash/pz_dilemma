from gym import spaces
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


    def __init__(self, game='pd',n_agents=4):

        GAMES = {'pd':Prisoners_Dilemma(), 'sd':Samaritans_Dilemma(),'stag': Stag_Hunt(), 'chicken': Chicken()}

        self.game = GAMES[game]

        self.agents = ["player_" + str(r) for r in range(n_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: spaces.Dict({'dilemma':spaces.Discrete(2),'selector':spaces.Discrete(n_agents)}) for agent in self.agents}
        self.observation_spaces = {agent: spaces.Dict({'dilemma':spaces.Discrete(3),'selector':spaces.Discrete(n_agents)}) for agent in self.agents}
        print('Delimma v2')
        self.reinit()

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: {'dilemma':self.game.DEFECT} for agent in self.agents}
        self.observations = {agent: {'dilemma':self.game.DEFECT} for agent in self.agents}
        self.num_moves = 0

    def render(self, mode="human"):
        try:
            #print('dones', self.dones)
            for i in self.agents:
                string_moves = ("Current moves: {} : {}".format(i, self.game.moves[self.state[self.agents[self.agent_name_mapping[i]]]['dilemma']]))
                string_partners = ("Current partners of: {} , {}".format(i, self.agents[self.state[self.agents[self.agent_name_mapping[i]]]['selector']]))

                print(string_moves)
                print(string_partners)

            print(self.rewards)
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
        self.state[self.agent_selection] = action
        dilemma_action = self.state[self.agent_selection]['dilemma']
        selector_action = self.state[self.agent_selection]['selector']
        # collect reward if it is the last agent to act

        agent_index = self._agent_selector._current_agent
        #t > r > p > s
        #2r > t + s
        #print(self.state[self.agents[0])
        #print('ok')

        if self._agent_selector.is_last():

            self.num_moves += 1
            self.dones = {agent: self.num_moves >= self.game.get_num_iters() for agent in self.agents}


        else:
            #need to do both?

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
                print('obs',self.observations[i])


            self.rewards[self.agents[agent_index]], self.rewards[self.agents[selector_action]] = self.game.get_payoff()[(self.state[self.agents[agent_index]]['dilemma'],self.state[self.agents[selector_action]]['dilemma'])]
            #self.state[self.agents[1 - self.agent_name_mapping[agent]]] = self.game.NONE


            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
