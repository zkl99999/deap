#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

"""This example contains the adaptation test from *Potter, M. and De Jong, K.,
2001, Cooperative Coevolution: An Architecture for Evolving Co-adapted
Subcomponents.* section 4.2.3. A species is added each 100 generations.
"""

import random
try:
    import pylab
except ImportError:
    pylab = False

from deap import algorithms
from deap import tools

import coev_coop_base

IND_SIZE = coev_coop_base.IND_SIZE
SPECIES_SIZE = coev_coop_base.SPECIES_SIZE
TARGET_SIZE = 30
NUM_SPECIES = 1

noise =      "*##*###*###*****##*##****#*##*###*#****##******##*#**#*#**######"
schematas = ("1##1###1###11111##1##1111#1##1###1#1111##111111##1#11#1#11######",
             "1##1###1###11111##1##1000#0##0###0#0000##000000##0#00#0#00######",
             "0##0###0###00000##0##0000#0##0###0#0000##001111##1#11#1#11######")

toolbox = coev_coop_base.toolbox
if pylab:
    toolbox.register("evaluate_nonoise", coev_coop_base.matchSetStrengthNoNoise)

def main(extended=True, verbose=True):
    target_set = []
    
    stats = tools.Statistics(lambda ind: ind.fitness.values, n=NUM_SPECIES)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std)
    stats.register("Min", min)
    stats.register("Max", max)
    
    if verbose:
        column_names = ["gen", "evals"] + stats.functions.keys()
        logger = tools.EvolutionLogger(column_names)
        logger.logHeader()
    
    ngen = 300
    adapt_length = 100
    g = 0
    add_next = [adapt_length]
    
    for i in range(len(schematas)):
        target_set.extend(toolbox.target_set(schematas[i], TARGET_SIZE/len(schematas)))
    
    species = [toolbox.species() for _ in range(NUM_SPECIES)]
    
    # Init with random a representative for each species
    representatives = [random.choice(s) for s in species]
    
    if pylab and extended:
        # We must save the match strength to plot them
        t1, t2, t3 = list(), list(), list()
    
    while g < ngen:
        # Initialize a container for the next generation representatives
        next_repr = [None] * len(species)
        for i, s in enumerate(species):
            # Variate the species individuals
            s = algorithms.varAnd(s, toolbox, 0.6, 1.0)
            
            r = representatives[:i] + representatives[i+1:]
            for ind in s:
                ind.fitness.values = toolbox.evaluate([ind] + r, target_set)
                
            stats.update(s, index=i, add=True)
            
            if verbose: 
                logger.logGeneration(gen="%d.%d" % (g, i), evals=len(s), stats=stats, index=i)
            
            # Select the individuals
            species[i] = toolbox.select(s, len(s))  # Tournament selection
            next_repr[i] = toolbox.get_best(s)[0]   # Best selection
            
            g += 1
        
            if pylab and extended:
                # Compute the match strength without noise for the
                # representatives on the three schematas
                t1.append(toolbox.evaluate_nonoise(representatives,
                    toolbox.target_set(schematas[0], 1), noise)[0])
                t2.append(toolbox.evaluate_nonoise(representatives,
                    toolbox.target_set(schematas[1], 1), noise)[0])
                t3.append(toolbox.evaluate_nonoise(representatives,
                    toolbox.target_set(schematas[2], 1), noise)[0])
        
        representatives = next_repr
        
        # Add a species at every *adapt_length* generation
        if add_next[-1] <= g < ngen:
            species.append(toolbox.species())
            representatives.append(random.choice(species[-1]))
            add_next.append(add_next[-1] + adapt_length)
    
    if extended:
        for r in representatives:
            # print individuals without noise
            print "".join(str(x) for x, y in zip(r, noise) if y == "*")
    
    if pylab and extended:
        # Do the final plotting
        pylab.plot(t1, '-', color="k", label="Target 1")
        pylab.plot(t2, '--', color="k", label="Target 2")
        pylab.plot(t3, ':', color="k", label="Target 3")
        max_t = max(max(t1), max(t2), max(t3))
        for n in add_next:
            pylab.plot([n, n], [0, max_t + 1], "--", color="k")
        pylab.legend(loc="lower right")
        pylab.axis([0, ngen, 0, max_t + 1])
        pylab.xlabel("Generations")
        pylab.ylabel("Number of matched bits")
        pylab.show()
    
if __name__ == "__main__":
    main()