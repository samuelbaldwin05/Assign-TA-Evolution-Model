import random as rnd
import copy
from functools import reduce
import numpy as np
from profiler import Profiler, profile
import time

class Evo:

    def __init__(self):
        self.pop = {}     # evaluation --> solution
        self.fitness = {} # name --> objective function
        self.agents = {} # name --> (operator function, num_solutions_input)

    def add_fitness_criteria(self, name, f):
        """ Register an objective with the environment """
        self.fitness[name] = f

    def add_agent(self, name, op, k=1):
        """ Register an agent with the environment """
        self.agents[name] = (op, k)

    def add_solution(self, sol):
        """ Add a solution to the population   """
        eval = tuple([(name, f(sol)) for name, f in self.fitness.items()])
        self.pop[eval] = sol   # ((name1, objval1), (name2, objval2)....)  ===> solution


    def get_random_solutions(self, k=1):
        """ Pick k random solutions from the population """
        if len(self.pop) == 0: # no solutions in the population (This should never happen!)
            return []
        else:
            solutions = tuple(self.pop.values())
            # Doing a deep copy of a randomly chosen solution (k times)
            return [copy.deepcopy(rnd.choice(solutions)) for _ in range(k)]


    def run_agent(self, name):
        """ Invoke a named agent on the population """
        op, k = self.agents[name]
        picks = self.get_random_solutions(k)
        for i in range(k):
            new_solution = op(picks[i])
            self.add_solution(new_solution)


    def dominates(self, p, q):
        """
        p = evaluation of one solution: ((obj1, score1), (obj2, score2), ... )
        q = evaluation of another solution: ((obj1, score1), (obj2, score2), ... )
        """
        pscores = np.array([score for name, score in p])
        qscores = np.array([score for name, score in q])
        score_diffs = qscores - pscores
        return min(score_diffs) >= 0 and max(score_diffs) > 0.0



    def reduce_nds(self, S, p):
        return S - {q for q in S if self.dominates(p, q)}

    def remove_dominated(self):
        nds = reduce(self.reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k: self.pop[k] for k in nds}

    @profile
    def evolve(self, n=10000000, dom=100, status=1000, time_limit=300):
        """ Run random agents n times
        n:  Number of agent invocations
        status: How frequently to output the current population
        """
        agent_names = list(self.agents.keys())
        start_time = time.time()

        for i in range(n):
            # Check if time limit has been exceeded
            if (time.time() - start_time) >= time_limit:
                print("Time")
                print("Ended on iteration: ", i, "\n")
                # Write final results to csv file
                with open("results.csv", "w") as outfile:
                    outfile.write("groupname,overallocation,conflicts,undersupport,unwilling,unpreferred\n")
                    for idx, (eval, sol) in enumerate(self.pop.items()):
                        # print("Solution #: ", (idx + 1), "\nEvaluation: ", eval, "\nSolution  :\n", sol, "\n")
                        metrics = ""
                        for j in range(len(eval)):
                            metrics += "," + str(eval[j][1])
                        outfile.write(f"jms" + metrics + "\n")
                # Save the final set of solutions and their scores to a text file
                # with open("best_result.txt", "w") as outfile:
                #     outfile.write("Best final solution log\n")
                # with open("best_result.txt", "a") as outfile:
                #     for idx, (eval, sol) in enumerate(self.pop.items()):
                #         for row in sol:
                #             for col in row:
                #                 outfile.write(f"{col:<5}")
                #             outfile.write("\n")
                #         outfile.write("\n")
                #         outfile.write(str(eval))
                #         outfile.write("\n")
                break

            pick = rnd.choice(agent_names)
            self.run_agent(pick)

            if i % dom == 0:
                self.remove_dominated()

            if i % status == 0:
                self.remove_dominated()
                print("Iteration: ", i)
                print("Size     : ", len(self.pop))
                print(self)

        self.remove_dominated()

    def __str__(self):
        """ Output the solutions in the population """
        #rslt = ""
        evals = []
        scores = []
        rslt = ""
        for eval, sol in self.pop.items():
            #rslt += str(eval) + ":\t" + str(sol) + "\n"
            total = sum(value for _, value in eval)
            evals.append(eval)
            scores.append(total)
        avg = sum(scores) / len(scores)
        avg = f"{avg:.2f}"
        min_index = scores.index(min(scores))
        rslt += "Min score: " + str(min(scores)) + "\nAverage score: " + avg + "\n" + (str(evals[min_index])) + "\n"
        return rslt



