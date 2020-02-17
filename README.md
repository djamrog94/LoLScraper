# LoL Parser / Betting Model

This project attempts to profit off of mispricing of live bets made during LCS games.
------
This project can be broken into two pieces.
1. Historical data collection / analysis
2. Live game data collection / analysis

-----
# Historical Data Collection and Analysis

There are numerous elements to this piece:

The first step is to run the schedule function in schedule.py. 

Either run driver.py or multi_instance.py to begin parsing games
based on the game list created in schedule.
 
After all games or some games have been parsed, run the parser program

At any point can run the second function in schedule py; but recommend running repair program first
to fix broken games

After all games have been parsed; run query program

After all games have been successfully parsed and results have been saved; ready to train model

**MODEL TRAINING**

Currently two versions of model in ML program.

Create dataset function reads in game df saved in data/final and creates one df
that can be run through a model

History function takes in df from create dataset function and trains and saves a model


# Live Game Data Collection / Analysis

Live_game program is live version of parser. Code has to be slightly changed,
 but fundamentally is the same
 
At same time, main.py should be run
 
 
As game is parsed by live_game program, the main program reads in each new file,
and adds to live game df.

If file has a model trained for that time, convert that time frames list into format for model,
then run model and grab betting information. Compare implied probability from betting information to model's
probability of winning.

PROFIT!!