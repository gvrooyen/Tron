__author__ = 'gvrooyen'

from collections import deque

MLS_TAPS_10 = [
    [10, 7],
    [10, 9, 8, 5],
    [10, 9, 7, 6],
    [10, 9, 7, 3],
    [10, 9, 6, 1],
    [10, 9, 5, 2],
    [10, 9, 4, 2],
    [10, 8, 7, 5],
    [10, 8, 7, 2],
    [10, 8, 5, 4],
    [10, 8, 4, 3],
    [10, 9, 8, 7, 5, 4],
    [10, 9, 8, 7, 4, 1],
    [10, 9, 8, 7, 3, 2],
    [10, 9, 8, 6, 5, 1],
    [10, 9, 8, 6, 4, 3],
    [10, 9, 8, 6, 4, 2],
    [10, 9, 8, 6, 3, 2],
    [10, 9, 8, 6, 2, 1],
    [10, 9, 8, 5, 4, 3],
    [10, 9, 8, 4, 3, 2],
    [10, 9, 7, 6, 4, 1],
    [10, 9, 7, 5, 4, 2],
    [10, 9, 6, 5, 4, 3],
    [10, 8, 7, 6, 5, 2],
    [10, 9, 8, 7, 6, 5, 4, 3],
    [10, 9, 8, 7, 6, 5, 4, 1],
    [10, 9, 8, 7, 6, 4, 3, 1],
    [10, 9, 8, 6, 5, 4, 3, 2],
    [10, 9, 7, 6, 5, 4, 3, 2]
]


def lfsr(taps, seed = None):
    """
    Generator for a maximum-length sequence.
    Note that this is not intended to be a computationally efficient implementation -- it uses character list
    operations rather than bit-level computations.

    Source: Mattia Gobbi, http://stackoverflow.com/questions/3735217/linear-feedback-shift-register
    """

    if seed == None:
        seed = [1]*taps[0]

    result = []

    sr, xor = seed, 0
    while True:
        for t in taps:
            xor += sr[t-1]
        if xor % 2 == 0:
            xor = 0
        else:
            xor = 1
        result.append(xor)
        sr, xor = [xor] + sr[:-1], 0
        # print sr
        if sr == seed:
            break

    return result

def xor(L1,L2):
    return [L1[i]^L2[i] for i in xrange(0,min(len(L1),len(L2)))]

def gold10(N = 1023, tapsets = (0,1)):
    S1 = lfsr(MLS_TAPS_10[tapsets[0]])
    S2x = lfsr(MLS_TAPS_10[tapsets[1]])
    S2 = S2x + S2x
    result = []
    for i in xrange(0,N):
        result.append(xor(S1[0:N],S2[i:N+i]))
    return result

def list2bin(E):
    return sum([a*2**e for (e,a) in enumerate(E[::-1])])

def save_gold10(bits = 64, filename = 'zobrist.h', N = 1023, tapsets = (0,1), style = 'c'):
    G = gold10(N,tapsets)
    nums = [list2bin(g[0:bits]) for g in G]
    F = open(filename, 'w')
    if style == 'c':
        guard = filename.upper().replace('.', '_')
        F.write("#ifndef %s\n" % guard)
        F.write("#define %s\n\n" % guard)
        F.write("using namespace std;\n\n")
        F.write("long long int zobrist[1023] = {\n")
    elif style == 'python':
        F.write("zobrist = [\n")
    for n in nums[:-1]:
        F.write('    ' + str(n) + ',\n')
    F.write('    ' + str(n) + '\n')
    if style == 'c':
        F.write("};\n\n")
        F.write("#endif\n")
    elif style == 'python':
        F.write("]\n")
    F.close()




