## Make sure to backup the TrakEM2 project files! ##
## Make sure to backup this file before you modify it. ##

from ini.trakem2 import Project
import csv

foundNeurites = []

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()
neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    print("-----")
    print(neurite)
    print(neurite.getTitle())
    foundNeurites.append([neurite.getTitle()])

outfile = open('test.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeurites)
outfile.close()

#### Exercises:
# 0. Run the code and check what happened.
# 1. Read and explain to yourself the meaning of each line.
# 2. On line 9, Project.getProjects().get(0), what's the meaning of "."?
#    (It's about Java classes' methods, you can search the web, preferably Google.)
# 3. Comment out line 13, or line 14, or line 15, what happened?
#    (You can search what is a comment and how to use it in Python.)
# 4. On line 16, what is the meaning of "."? What will happen if you delete the "[]"?
#    (It's about Python class methods, again search for it.)
#    (After you omit the [], check the output test.csv file.)
# 5. On line 11, what will happen if you change the 2nd "neurite" (the one in double quotes)
#    to "synapse" (don't omit the double quotes)? What will happen if you change the first occurence?
# 6. On line 15, what will happen if you change neurite.getTitle() to neurite.getId() ?
#