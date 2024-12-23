import random as rnd
import numpy as np
import pandas as pd
from evo import Evo
from profiler import profile, Profiler

class Objectives:
    # Objectives
    def __init__(self, sections, tas):
        self.sections = sections
        self.tas = tas

    # Objective 1 - Minimize overallocation of TAs (overallocation)
    @profile
    def overallocate(self, assignments):
        """ Find the sum of overallocated tas """
        summed_array = np.sum(assignments, axis=1)
        tas_max = self.tas["max_assigned"].to_numpy()
        overallocated = (summed_array - tas_max)
        overallocated = sum(overallocated[overallocated > 0])
        return overallocated

    # Objective 2 - Minimize time conflicts (conflicts)
    @profile
    def conflicted_sections(self, assignments):
        """Counts the number of conflicting sections"""
        # Count hours per ta
        sections_per_ta = np.count_nonzero(assignments, axis=1)

        # Make array with daytime for section instead of 1
        section_times = self.sections['daytime'].to_numpy()
        section_times_array = np.where(assignments == 1, section_times, assignments)

        # counts unique sections
        unique_sections_per_ta = np.apply_along_axis(lambda row: len(np.unique(row[row != 0])),
                                                     axis=1, arr=section_times_array)

        # Sum more total sections than unique sections to find total conflicts
        conflicts = np.sum(sections_per_ta > unique_sections_per_ta)
        return conflicts


    # Objective 3 - Minimize Under-Support (undersupport)
    @profile
    def undersupport(self, assignments):
        """Finds the sum of allocated tas less than the designated minimum amount of tas
         for office hour sections with not enough support"""
        summed_array = np.sum(assignments, axis=0)
        tas_min = self.sections["min_ta"].to_numpy()
        undersupported = (tas_min - summed_array)
        undersupported = sum(undersupported[undersupported > 0])
        return undersupported


    # Objective 4 - Minimize the number of times you allocate a TA to a section they are unwilling to support
    # (unwilling)
    @profile
    def unwilling(self, assignments):
        """find number of tas assigned to sections marked unwilling"""
        lab_idxs = np.where(assignments == 1)
        lab_idxs = np.column_stack(lab_idxs)
        preferences = self.tas.drop(labels = ["ta_id", "name", "max_assigned"], axis = 1).to_numpy()
        pref_selected = preferences[lab_idxs[:, 0], lab_idxs[:, 1]]
        w_prefs = pref_selected[pref_selected == "U"]
        return w_prefs.size

    # Objective 5 - Minimize the number of times you allocate a TA to a section where they said “willing” but not
    # “preferred”. (unpreferred)
    @profile
    def unpreferred(self, assignments):
        """find number of tas assigned to sections marked unwilling"""
        lab_idxs = np.where(assignments == 1)
        lab_idxs = np.column_stack(lab_idxs)
        preferences = self.tas.drop(labels = ["ta_id", "name", "max_assigned"], axis = 1).to_numpy()
        pref_selected = preferences[lab_idxs[:, 0], lab_idxs[:, 1]]
        w_prefs = pref_selected[pref_selected == "W"]
        return w_prefs.size




class Agents:
    # AGENTS
    def __init__(self, sections, tas):
        self.sections = sections
        self.tas = tas

    @profile
    def delete_rand(self, assignments):
        """
        Change a random 1 to a 0.
        NOT USED
        """
        coords = np.where(assignments == 1)
        coords = np.column_stack(coords)
        if coords.size == 0:
            return assignments
        rand_coord = coords[np.random.choice(coords.shape[0])]
        assignments[rand_coord[0], rand_coord[1]] = 0
        return assignments

    @profile
    def add_rand(self, assignments):
        """
        Change a random 0 to a 1.
        NOT USED
        """
        coords = np.where(assignments == 0)
        coords = np.column_stack(coords)
        if coords.size == 0:
            return assignments
        rand_coord = coords[np.random.choice(coords.shape[0])]
        assignments[rand_coord[0], rand_coord[1]] = 1
        return assignments

    def change_rand_zero(self, assignments):
        """
        Picks a random coordinate and if it is a 0 change it to a 1.
        USED
        """
        rand_row = rnd.randint(0, 42)
        rand_col = rnd.randint(0, 16)
        if assignments[rand_row, rand_col] == 0:
            assignments[rand_row, rand_col] = 1
        return assignments

    def change_rand_one(self, assignments):
        """
        Picks a random coordinate and if it is a 1 change it to a 0.
        USED
        """
        rand_row = rnd.randint(0, 42)
        rand_col = rnd.randint(0, 16)
        if assignments[rand_row, rand_col] == 1:
            assignments[rand_row, rand_col] = 0
        return assignments

    @profile
    def delete_rand_overallocated(self, assignments):
        """
        For each TA that is overallocated, remove a random assignment of theirs.
        USED
        """
        # Find which tas are overallocated
        summed_array = np.sum(assignments, axis=1)
        tas_max = self.tas["max_assigned"].to_numpy()
        overallocated = summed_array > tas_max
        overallocated_rows = np.where(overallocated == True)[0]

        # Skip if there are no overallocated
        if len(overallocated_rows) == 0:
            return assignments

        # Get coords of 1s for rows with overallocation
        where = np.where(assignments == 1)
        idxs = np.column_stack(where)
        filtered_coords = idxs[np.isin(idxs[:, 0], overallocated_rows)]

        # Randomly choose a coord from filtered coords for each overallocated ta and change it to a 1
        selected_coords = np.array([filtered_coords[np.random.choice(np.where(filtered_coords[:, 0] == y)[0])]
                                    for y in overallocated_rows])
        assignments[selected_coords[:, 0], selected_coords[:, 1]] = 0
        return assignments

    @profile
    def delete_rand_unwilling(self, assignments):
        """
        Switch TAs assigned to sections marked unwilling out of the section.
        NOT USED
        """
        preferences = self.tas.drop(labels=["ta_id", "name", "max_assigned"], axis=1).to_numpy()
        # Modify the preferences array to only contain the preferences of sections that are assigned.
        overlay = np.where(assignments == 1, preferences, '0')
        # Find unpreferred sections.
        uw_idxs = np.where(overlay == 'U')
        uw_idxs = np.column_stack(uw_idxs)
        if len(uw_idxs) > 5:
            # Select 5 random indexes to replace
            rand_idxs = [rnd.randint(0, len(uw_idxs) - 1) for _ in range(5)]
            change_idxs = uw_idxs[rand_idxs]
            rows, cols = zip(*change_idxs)
            assignments[np.array(rows), np.array(cols)] = 0
            return assignments
        return assignments

    @profile
    def delete_rand_unpreferred(self, assignments):
        """
        Remove TAs from sections which they do not prefer.
        NOT USED
        """
        preferences = self.tas.drop(labels=["ta_id", "name", "max_assigned"], axis=1).to_numpy()
        overlay = np.where(assignments == 1, preferences, 0)
        uw_idxs = np.where(overlay == 'W')
        uw_idxs = np.column_stack(uw_idxs)
        if len(uw_idxs) > 1:
            rand_idxs = rnd.randint(0, len(uw_idxs) - 2)
            change_idxs = uw_idxs[rand_idxs]
            assignments[change_idxs] = 0
            return assignments
        return assignments

    @profile
    def add_rand_undersupported(self, assignments):
        """
        Switch TAs into certain sections that are undersupported
        USED
        """
        # Find undersupport columns
        summed_array = np.sum(assignments, axis=0)
        section_min = self.sections["min_ta"].to_numpy()
        undersupport = summed_array < section_min
        undersupport_cols = np.where(undersupport == True)[0]

        # Skip if no undersupport
        if len(undersupport_cols) == 0:
            return assignments

        # Get coords of 0s for rows with undersupport
        where = np.where(assignments == 0)
        idxs = np.column_stack(where)
        filtered_coords = idxs[np.isin(idxs[:, 1], undersupport_cols)]

        # Randomly choose a coord from filtered coords for each undersupport row and change it to a 1
        selected_coords = np.array([filtered_coords[np.random.choice(np.where(filtered_coords[:, 1] == y)[0])] for y in undersupport_cols])
        assignments[selected_coords[:, 0], selected_coords[:, 1]] = 1
        return assignments

def main():
    tas = pd.read_csv("tas.csv")
    sections = pd.read_csv("sections.csv")
    objectives = Objectives(sections, tas)
    agents = Agents(sections, tas)



    E = Evo()

    # Fitness criteria
    E.add_fitness_criteria("overallocated", objectives.overallocate)
    E.add_fitness_criteria("time_conflict", objectives.conflicted_sections)
    E.add_fitness_criteria("undersupport", objectives.undersupport)
    E.add_fitness_criteria("unwilling", objectives.unwilling)
    E.add_fitness_criteria("unpreferred", objectives.unpreferred)

    # Agents
    # Complex agents
    E.add_agent("Delete overallocated", agents.delete_rand_overallocated, k=1)
    E.add_agent("Add undersupported", agents.add_rand_undersupported, k=1)
    #E.add_agent("Delete random unwilling", agents.delete_rand_unwilling, k=1)
    #E.add_agent("Delete random unpreferred", agents.delete_rand_unpreferred, k=1)

    # Basic agents
    E.add_agent("Change random one", agents.change_rand_one, k=1)
    E.add_agent("Change random zero", agents.change_rand_zero, k=1)
    # E.add_agent("Delete random", agents.delete_rand, k=1)
    # E.add_agent("Add random", agents.add_rand, k=1)

    # Initial solution
    create_random_solution = np.ones((43, 17))
    E.add_solution(create_random_solution)

    E.evolve(n=10000000, dom=1, status=100000, time_limit=300)

    Profiler.report()



if __name__ == "__main__":
    main()