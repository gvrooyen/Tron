__author__ = 'gvrooyen'

import random

#noinspection PyStringFormat
class Judge(object):

    def __init__(self, state_file_red, state_file_blue, world_size = 30):

        try:
            with open(state_file_red) as f1, open(state_file_blue) as f2:
                pass
        except IOError:
            # If one or more of the state files don't yet exist, initialize with random player positions.
            red = (random.randint(0, world_size-1), random.randint(0, world_size-1))
            blue = red
            while blue == red:
                blue = (random.randint(0, world_size-1), random.randint(0, world_size-1))

            with open(state_file_red, 'w') as f1, open(state_file_blue, 'w') as f2:
                f1.write('%d %d %s\n' % (red + ('You',)))
                f1.write('%d %d %s\n' % (blue + ('Opponent',)))
                f2.write('%d %d %s\n' % (blue + ('You',)))
                f2.write('%d %d %s\n' % (red + ('Opponent',)))


