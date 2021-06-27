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

        self.action_spaces = {agent: spaces.MultiDiscrete([2,n_agents]) for agent in self.agents}
        self.observation_spaces = {agent: spaces.Box(low=-1, high=1, shape=(1,n_agents), dtype=np.int8) for agent in self.agents}
        print('Delimma v2')
        print(self.observation_spaces)
        self.reinit()

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: [0,0] for agent in self.agents}
        self.observations = {agent: np.zeros(len(self.agents)) for agent in self.agents}
        self.num_moves = 0

    def render(self, mode="human"):
        try:
            #print('dones', self.dones)
            for i in self.agents:
                #string_partners = ("Current partners of: {} , {}".format(i, self.agents[self.state[self.agents[self.agent_name_mapping[i]]][1]]))
                string_moves = ("Current moves: {} : {}, {}, {}".format(i, self.game.moves[self.state[self.agents[self.agent_name_mapping[i]]][0]], self.agents[self.state[self.agents[self.agent_name_mapping[i]]][1]],self.game.moves[self.state[self.agents[self.state[self.agents[self.agent_name_mapping[i]]][1]]][0]]))
                print(string_moves)
                #print(string_partners)

            print('rewards', self.rewards)
            print("")
            return self.dones
        except:
            'error'

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        #print('agent ', agent)
        #print('observation' , np.array(self.observations[agent]))
        print('observations', self.observations)
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
        dilemma_action = self.state[self.agent_selection][0]
        selector_action = self.state[self.agent_selection][1]
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
                if self.state[self.agents[agent_index]][0] == 0:
                    self.observations[i][agent_index] = 1
                if self.state[self.agents[agent_index]][0] == 1:
                    self.observations[i][agent_index]= -1

                if self.state[self.agents[selector_action]][0] == 0:
                        self.observations[i][selector_action] = 1
                if self.state[self.agents[selector_action]][0] == 1:
                        self.observations[i][selector_action] = -1

                #self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
                #self.observations[i]['dilemma'] = 1
            #    self.observations[i]['dilemma'] = [0,0,0,1]

            self.rewards[self.agents[agent_index]] = self.game.get_payoff()[(self.state[self.agents[agent_index]][0],self.state[self.agents[selector_action]][0])][0]
            print('current state', self.state)

            #self.state[self.agents[1 - self.agent_name_mapping[agent]]] = self.game.NONE


            #self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
