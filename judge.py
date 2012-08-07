__author__ = 'gvrooyen'

import random

#noinspection PyStringFormat
class Judge(object):

    def __init__(self, state_file_blue, state_file_red, world_size = 30):

        try:
            with open(state_file_blue), open(state_file_red):
                pass
        except IOError:
            # If one or more of the state files don't yet exist, initialize with random player positions.
            blue = (random.randint(0, world_size-1), random.randint(0, world_size-1))
            red = blue
            while red == blue:
                red = (random.randint(0, world_size-1), random.randint(0, world_size-1))

            with open(state_file_blue, 'w') as f1, open(state_file_red, 'w') as f2:
                f1.write('%d %d %s\n' % (blue + ('You',)))
                f1.write('%d %d %s\n' % (red + ('Opponent',)))
                f2.write('%d %d %s\n' % (red + ('You',)))
                f2.write('%d %d %s\n' % (blue + ('Opponent',)))

        # Firstly, we initialise the world with Red's file. We'll later check that Blue's file is consistent.

