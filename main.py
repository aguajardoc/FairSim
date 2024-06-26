import requests
from scipy.stats import pearsonr

# Dictionary with correlation coefficients per contest
correlation = dict()
        
def addNew(id):
    # Call the API for an ICPC contest
    candidateQuery = requests.get(f"https://codeforces.com/api/contest.standings?contestId={id}&showUnofficial=true")

    candidate = candidateQuery.json()
    
    # Check if the request was successful
    candidateQuery.raise_for_status()
    
    # Find contest's number of problems, then make a dictionary to keep track of points per problem
    problemCount = 1
    solved = {0 : 0}
    
    for problem in candidate["result"]["problems"]:
        solved[problemCount] = 0
        problemCount += 1
        
    
    # Filter per candidate type, and grab number of points that original participants acquired
    # Solved holds the number of teams who solved AT LEAST i problems.
    for team in candidate["result"]["rows"]:
        if team["party"]["participantType"] == "VIRTUAL" and team["party"]["ghost"] == True:
            for i in range(int(team["points"]), -1, -1):
                solved[i] += 1
    
    # Get correlation coefficient for the contest's solved problems
    numSolved = list()
    freq = list()
    for i in range(0, problemCount):
        if solved[i] > 0:
            numSolved.append(i)
            freq.append(solved[i])
            
    if len(numSolved) > 1:
        corr, _ = pearsonr(numSolved, freq)
        
        # Store coefficient in dictionary
        correlation[id] = corr



# Call the API for all gyms
contestQuery = requests.get("https://codeforces.com/api/contest.list?gym=true")

contests = contestQuery.json()

# Check every contest, if they are of the ICPC type and they have occurred, process the ID.
for contest in contests["result"]:
    if contest["type"] == "ICPC" and contest["phase"] == "FINISHED" and contest.get("kind") == "Official ICPC Contest":
        addNew(contest["id"])

# Print most linear contests, sorted by descending r value
sortedCorrelations = sorted(correlation.items(), key=lambda x : x[1])
sortedDict = dict(sortedCorrelations)

print("The best contests are: \n")

topKeys = [key for key in sortedDict.keys()]
topCoefficients = [coefficient for coefficient in sortedDict.values()]

bestContests = [0] * 10

for contest in contests["result"]:
    for i in range(0, 10):
        if contest["id"] == topKeys[i]:
            bestContests[i] = contest["name"]

for i, contest in enumerate(bestContests):
    print(f"#{i+1}. {contest} (r = {topCoefficients[i]})")
    
