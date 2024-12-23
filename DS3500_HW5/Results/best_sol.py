import numpy as np
import pandas as pd
from assignta import Objectives

best_sol = np.array()


print(best_sol.shape)
tas = pd.read_csv("tas.csv")
sections = pd.read_csv("sections.csv")


O = Objectives(sections, tas)

print(O.overallocate(best_sol))
O.conflicted_sections(best_sol)
O.undersupport(best_sol)
O.unwilling(best_sol)
O.unpreferred(best_sol)
