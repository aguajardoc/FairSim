# FairSim
Codeforces API scraper for ICPC/IOI contests to maximize enjoyability while preparing for the ICPC and the IOI.

## Motivation
One way to practice one's Competitive Programming skills involves participating in "simulations": taking old, real problem sets used for in-person competitions and solving them as a team, simulating the contest environment as closely as possible. 

However, there's been a myriad of contests in the past 25 years; how does someone choose which one to practice from? Initially, taking random ICPC/IOI contests seems like a good idea, but sometimes, teams may feel defeated when they are only able to solve 1-2 problems in five hours (*cough* We've been there.); it takes out the fun out of this otherwise pleasurable hobby, **and does not motivate anyone to do better**.
## The Solution
To solve this, we could quantify a contest's perceived fairness. But, *what is fair*? Although this is subjective, it can be agreed that both, a low solve rate and a high solve rate, are uncompetitive. Thus, we can define an "ideal" contest as one in which there's a gradual skill curve; if 100 teams are able to solve at least 3 problems, seeing that only 6 teams are able to solve 4 problems implies a sudden skill-wall that blocks almost everyone. 

This is what we aim to prevent.

Now that we know what is fair, we can choose the tools to determine fairness. One of the simplest ways to figure this out is through the Pearson Correlation Coefficient, which measures the correlation between sets of data points. In this case, we measure the correlation between the number of problems a team has been able to solve against the number of teams that reached that point. This is cummulative, so, for example, if a team solves four problems, they contribute to the counts for 0, 1, 2, and 3 problems. 

Calculating this coefficient for all contests (from Codeforces's API) means we can sort the contests from highest to lowest correlation, and, as such, we can create a leaderboard of the fairest and unfairest contests by this metric.
## Limitations
- Some contests don't hold data on in-person contestants, so they have to be omitted as the calculations can't be made.

## WIP
This is still a Work In Progress, and new features are in development.
