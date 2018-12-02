import gym
import universe  # register the universe environments
import sys
import math
import numpy as np
import random 

from agent import ApproximateQAgent
from utils.env import create_slither_env
from universe.wrappers import Unvectorize


center_x = 270  
center_y = 235


# The snake moves to the directing of the mouse
# but to output the direction to a neural network we need to break the output to more discrete values

# the radius is the distance from the head of the snake to the mouse pointer(in pixel)
radius = 30
# This is the number of points we want around the head of the snake
# Ex: With 8 points where the mouse can be positioned around the head of the snake
# Note the distance from the point to the head is the same for all
#       *
#     *   *
#   *   s   *
#     *   *
#       *
# You can add more resolution to this if you want but it may increase learning time
resolution_points = 8
degree_per_slice = 360//resolution_points

# Available actions in the game
action_sheet = []
action_sheet_init = []

# We put all mouse positions in the action_sheet
for point in range(resolution_points):
    degree = point*degree_per_slice
    y_value_offset = radius * math.sin(math.radians(degree))
    x_value_offset = radius * math.cos(math.radians(degree))
    coord = universe.spaces.PointerEvent(center_x + x_value_offset, center_y + y_value_offset, 0)
    action_sheet.append((center_x + x_value_offset, center_y + y_value_offset))


    action_sheet_init.append(coord)


def get_best(loc):

    min_dis = 1000
    best_act = None
    print("this min food is ", loc)

    for i in action_sheet:
      dis = abs(loc[0] - i[0]) + abs(loc[1] -i[1])

      if (dis < min_dis):
        best_act = universe.spaces.PointerEvent(i[0], i[1], 0)
        min_dis = dis
    print("the best action is", best_act)
    return best_act


if __name__ == '__main__':
 
  # Create customized and processed slither env
  #universe.configure_logging(False)

  ### init the q learning agent
  features_index = ["me_perc","snake_perc", "food_perc", "min_snake", "min_food"]

  learning_agent = ApproximateQAgent()
  test_features = [2.29333333e-03, 1.00000000e+00 ,1.22200000e-02 ,1.00000000e+00, 9.40000000e-01]
  new_features = dict()
  action = random.choice(action_sheet)

  for i in range(len(features_index)):
    new_features[features_index[i]] = test_features[i]

  print("new is ",features_index)
  learning_agent.update(action ,1, new_features)

  action = learning_agent.getAction(new_features)

  env = create_slither_env('features')
  env = Unvectorize(env)
  env.configure(fps=5.0, remotes=1, start_timeout=15 * 60, vnc_driver='go', vnc_kwargs={'encoding': 'tight', 'compress_level': 0, 'fine_quality_level': 50})

  observation_n = env.reset()


  while True:
    action = get_best((observation_n[5,0,0],observation_n[6,0,0]))
    ### design action that would decrease min_food 
    action = universe.spaces.PointerEvent(observation_n[5,0,0],observation_n[6,0,0],0)

    observation_n, reward_n, done_n, info = env.step([action])

    #me_perc , snake_perc, food_perc, min_snake, min_food,

    features = observation_n.flatten()
    print(features)
    new_features = dict()

    for i in range(len(features_index)):

      new_features[features_index[i]] = features[i]

    learning_agent.update(action ,reward_n, features)

    action = learning_agent.getAction(new_features)

    env.render()

