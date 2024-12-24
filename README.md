# Evolution Model to Assign TAs
Uses an evolution model to assign TAs to the best possible section times. Data includes minimum tas a section needs, maximum sections a TA can have, time conflicts in sections, and TA preferences for section times. The model uses multiple agents to work with the evolution to minimize the number of issues in each solution, only keeping equal or better solutions. A mix of semi-random agents and agents to target specific issues in the solution allows the model to gradually improve its solution until the best possible solution is found.


Files:
assignta - contains objectives to measure the number of issues in a solution, agents to apply to the solution to improve it, and the code to initialize the evolution. 

evo - applies agents to solutions, runs objectives on solutions to see if improvements were made, keeps improved solutions to gradually improve the model

test_assignta - pytest file to test objectives accuracy

profiler - time the evolution (assignment was to see how strong of a solution was possible in 5 minutes), counts iterations of each agent, and total agents applied, time for each agent


Data Files:
tas - individual ta information - preferred, unpreffered, and unwilling sections, max sections possible, ta id, and ta name

sections - information about each section, min tas needed, section time (some sections times are the same, crucial not to have one ta in two sections that are at the same time)


Results Files:
results - all objective scores of the 6 best possible solutions (2 was the lowest issues possible)

best_result - determined that the best result had a score of 2 unpreffered sections (this seemed like the best of the issues to have)

profiler_report - data from profiler

pytest_results - results from pytest 
