pz_dilemma
==============================

Game Theory extension for [petting zoo](pettingzoo.ml)

[Blog post on the centipede game](https://medium.com/@arjunprakash_18193/cycling-centipedes-and-multi-agent-reinforcement-learning-5cf3c5d9ebd7)

# Prisoners Dilemma Example

Import
```
from src.environments import dilemma_v0
import supersuit as ss
from stable_baselines3 import A2C
from pettingzoo.utils.conversions import to_parallel
```

Set up environment
```
env = dilemma_v0.env('pd')
env = to_parallel(env)
env = ss.pettingzoo_env_to_vec_env_v0(env)
env = ss.concat_vec_envs_v0(env, 4, base_class='stable_baselines3')
```


Train Model
```
model = A2C('MlpPolicy',
            env,
            verbose=3,
            tensorboard_log='tmp/')
model.learn(total_timesteps=2000000)
model.save("policy")
```

Run model
```
env = dilemma_v0.env('pd')
env.reset()
for agent in env.agent_iter():
    obs, reward, done, info = env.last()
    act = model.predict(obs)[0] if not done else None
    env.step(act)
    env.render()
```

Test environment
```
from pettingzoo.test import parallel_api_test
from src.environments import simple_pd_v0

env = simple_pd_v0.env()
env = to_parallel(env)

parallel_api_test(env, num_cycles=10)
```
