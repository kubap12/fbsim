# Fbsim

Fbsim is a nondeterministic model of any football league written in Python utilising the Monte Carlo method and the elo system.

## About the project

The project was inspired by my love of football and programming. It works by simulating thousands of seasons of any football league and averaging it's results to give predictions.
It predicts the chance of a team ending up as champions, in the top 3, in the top 4 or being relegated from the team. These events can be adjusted to fit the needs.
To simulate a match it uses the elo system. The system gives every player(team) an elo ranking which defines its strength. For more details on the system check: http://clubelo.com/System

## Technologies used

Programming language: Python
Python libraries: numpy, matplotlib, os, timeit, pyodbc
Database: Microsoft Access, SQL

## Installation

All you need to install is the program. The only availible database is made by me, about the polish Ekstraklasa. I suggest you create your own, with different leagues. I recommend ClubElo: http://clubelo.com/

## Capabilities of the program

Calculating chances for 1st, top 3, top 4, relegation.
Drawing graphs of elo points and league points with respect to round.
Saving the end of season stats.
Utilising results of matches.
Using different model assumptions (e.g. homefield advantage, form in last 5 matches)
All of this can be controlled in the options tab. Unfortunately there is no manual, and won't be unless there will be outside motivation.

# Author

Jakub Podemski
