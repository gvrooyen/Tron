__author__ = 'gvrooyen'

import argparse
import judge
import logging
from constants import *
import subprocess

def file_exists(filename):
    """Returns True if the file with the specified filename exists."""
    try:
        with open(filename):
            return True
    except IOError:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a Tron Light Cycle combat session")
    parser.add_argument('player1', type=str, help="Path to Player 1's executable")
    parser.add_argument('player2', type=str, help="Path to Player 2's executable")
    parser.add_argument('-F1', '--statefile1', type=str, default='player1.state',
        help="Player 1's state file")
    parser.add_argument('-F2', '--statefile2', type=str, default='player2.state',
        help="Player 1's state file")
    parser.add_argument('-D', '--debug', action='store_true', default=False,
        help="Switch on debugging output")

    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    sf1_exists = file_exists(args.statefile1)
    sf2_exists = file_exists(args.statefile2)

    if (not args.force) and (sf1_exists or sf2_exists):
        if sf1_exists and sf2_exists:
            logger.error("The state files %s and %s already exist." % (args.statefile1, args.statefile2))
        else:
            filename = args.statefile1 if sf1_exists else args.statefile2
            logger.error("The state file %s already exists." % filename)
        logger.error("Use the --force flag to overwrite existing state files.")
        exit(1)

    # Create the empty state files
    j = judge.Judge()
    winner = None

    while not winner:
        try:
            j.world.save(args.statefile1, player=BLUE)
            subprocess.check_call([args.player1, args.statefile1])
            winner = j.adjudicate(args.statefile1)
            j.world.save(args.statefile2, player=RED)
            subprocess.check_call([args.player2. args.statefile2])
            winner = j.adjudicate(args.statefile2)
        except:
            logger.error("Error while adjudicating the state files.")
            exit(1)

    logger.info("The winner is Player %d!" % winner)

