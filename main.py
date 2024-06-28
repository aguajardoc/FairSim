import requests
import datetime
from scipy.stats import pearsonr

# Dictionary with correlation coefficients per contest.
correlation = dict()

def getSelection(availableElements):
    chosenElement = len(availableElements) + 1
    # Skip if user has successfully picked an element from the list.
    while (not str(chosenElement).isnumeric() or int(chosenElement) - 1 >= len(availableElements)
           or int(chosenElement) - 1 < 0):
        print("Select an option from the list using the corresponding number:")
        
        # List all options and let user choose one.
        for index, unusedElement in enumerate(availableElements):
            print(f"{index + 1}. {unusedElement}")
        
        chosenElement = input("\n")
        
        # If user picked an element outside the range, let them retry.
        if (not str(chosenElement).isnumeric() or int(chosenElement) - 1 >= len(availableElements)
            or int(chosenElement) - 1 < 0):
            print("Please choose one of the listed options. Try again.")
    
    # Remove the element from the list of available elements and add it to the list of chosen elements.
    print(f"Filter {availableElements[int(chosenElement) - 1]} added successfully.")
    return availableElements.pop(int(chosenElement) - 1)


def processCategory(availableElements, chosenElements, category):
    newElement = True
    
    # Continue while the user keeps wanting to add more elements, and there are available elements.
    while newElement and availableElements:
        prompt = input(f"Do you wish to add a contest {category}? (Y/N): ")
        
        # Get user's selection if he wants to add a new element, break if not, re-prompt if wrong input.
        if prompt == 'Y':
            chosenElements.append(getSelection(availableElements))
        elif prompt == 'N':
            newElement = False
        else:
            print("Input must be 'Y' for yes or 'N' for no. Please try again.")
    
    # If user chose none, the default is all options.
    if len(chosenElements) == 0:
        for element in availableElements:
            chosenElements.append(element)
            

def fetchYear(year1, year2):
    currentYear = datetime.datetime.today().year
    
    # Allow user to add spaces before and after; we all make mistakes.
    year1 = year1.strip()
    year2 = year2.strip()
    
    # If the used inputted invalid date(s), (Pre-2000, Post-Current Season, or non-numeric), do all contests.
    if (not str(year1).isnumeric() or not str(year2).isnumeric() or int(year1) > int(year2)
        or int(year1) < 2000 or int(year2) > currentYear + 1):
        
        year1 = 2000
        year2 = currentYear
        
        print(f"Invalid range...using {year1}-{year2} as range.")
    # Else, take the range inputted by the user
    year1 = int(year1)
    year2 = int(year2)
    
    dateFilter = [year1, year2 + 1]
    
    # Make a dictionary of the items to search for in the API call. Why not a list? Because it allows for
    # O(1) search to validate the contest's year, speeding up execution time.
    ## For example, the range 2000-2002 results in the items "2000-2001" and "2001-2002" being added.
    contestDates = dict()
    
    for i in range(dateFilter[0], dateFilter[-1]):
        contestDates[i] = f"{i}-{i + 1}"
    
    print(contestDates)
    return contestDates
        

def addNew(id):
    # Call the API for a matching contest.
    candidateQuery = requests.get(f"https://codeforces.com/api/contest.standings?contestId={id}&showUnofficial=true")

    candidate = candidateQuery.json()
    
    # Check if the request was successful.
    candidateQuery.raise_for_status()
    
    # Find contest's number of problems, then make a dictionary to keep track of points per problem.
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
    
    # Get correlation coefficient for the contest's solved problems.
    numSolved = list()
    freq = list()
    for i in range(0, problemCount):
        if solved[i] > 0:
            numSolved.append(i)
            freq.append(solved[i])
            
    if len(numSolved) > 1:
        corr, _ = pearsonr(numSolved, freq)
        
        # Store coefficient in dictionary.
        correlation[id] = corr
        

# Ask user for type(s) and kind(s) of contests to consider.
types = ["ICPC", "IOI"]
userTypes = []

kinds = ["Official ICPC Contest", "Official School Contest", "Opencup Contest",
         "School/University/City/Region Championship", "Training Camp Contest",
         "Official International Personal Contest", "Training Contest"]
userKinds = []

processCategory(types, userTypes, "type")
processCategory(kinds, userKinds, "kind")

# Ask user for date range to consider.
print("Enter a date range for the contests.")
year1 = input("Beginning year: ")
year2 = input("Ending year: ")
contestDates = fetchYear(year1, year2)

# Show recap of their selection.
print('\n' * 50)
print("Applied Filters:")

for uType in userTypes:
    print(f"Type: {uType}")
    
for uKind in userKinds:
    print(f"Kind: {uKind}")
    
print(f"Date range for contests: {list(contestDates.keys())[0]}-{list(contestDates.keys())[-1]}\n")
print("Searching for valid contests...")
    
# Call the API for all gyms.
contestQuery = requests.get("https://codeforces.com/api/contest.list?gym=true")

contests = contestQuery.json()

# Variables to inform user on contest search progress.
contestTotal = len(contests["result"])
percentageChecked = 0
contestsChecked = 0

# Check every contest for the parameters inputted by the user.
contestCount = 0

for contest in contests["result"]:
    contestsChecked += 1
    
    # Check if the year is valid.
    contestDate = contest.get("season")
    if contestDate is None:
        continue
    
    # Check for filters, and add contest if it's a match.
    if (contest["type"] in userTypes and contest["phase"] == "FINISHED" and contest.get("kind") in userKinds
        and int(str(contestDate[:4])) in contestDates):
        
        addNew(contest["id"])
        contestCount += 1
        percentageChecked = (contestsChecked / contestTotal) * 100
        print(f"{contestCount} contest(s) found ({round(percentageChecked, 2)}% searched).")

# Print most linear contests, sorted by descending r value.
sortedCorrelations = sorted(correlation.items(), key=lambda x : x[1])
sortedDict = dict(sortedCorrelations)

print('\n' * 50)
print(f"The best contests, out of {contestCount} matches, are: \n")

topKeys = [key for key in sortedDict.keys()]
topCoefficients = [coefficient for coefficient in sortedDict.values()]

bestContests = [0] * 10 if len(correlation) >= 10 else [0] * len(correlation)

topSize = 10 if len(correlation) >= 10 else len(correlation)

for contest in contests["result"]:
    for i in range(0, topSize):
        if contest["id"] == topKeys[i]:
            bestContests[i] = contest["name"]

for i, contest in enumerate(bestContests):
    print(f"#{i+1}. {contest} (r = {topCoefficients[i]})")
