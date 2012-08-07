__author__ = 'gvrooyen'

import argparse
import judge

if __name== '__main__':
    parser = argparse.ArgumentParser(description="Run a Tron Light Cycle combat session")
    parser.add_argument('player1', type=str, help="Path to Player 1's executable")
    parser.add_argument('player2', type=str, help="Path to Player 2's executable")
    args = parser.parse_args()

    j = judge.Judge('player1.state', 'player2.state')
