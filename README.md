# SI 507  - Final Project

### Colin Tyrrell - tyrrellc


## Overview

This app collects and displays data pertaining to the NASDAQ Index (^INIX) to assist with trading. It pulls from an API to obtain historical stock data. It then scrapes Yahoo Finance to get the latest NASDAQ and volatility price. Next it pulls data from a subfolder of emails from a trading subscription service. It uses a cache for prices scraped throughout the day and a database for all historical data. Flask is used to display the current subscription data and prices and a few days worth of historical data, which allows for better decisions when trading. The file 'Execution.MOV' shows the app in operation from start to finish.

* stackoverflow was used countless times for assistance and code


## Instructions

1. Set up a virtual environment. (mine was named 'venv_final')
2. create a database named 'stockData1' and change the username in config.py
3. Install the requirements.txt items  (non-standard: requests, bs4, psycopg2, flask)
4. Wait for US trading hours and run the Main Code file with Python3. [the program will still work if not between **9:30-4:00 EST M-F**; however, this time period is when all actions will occur and full data will be displayed]
5. In command prompt, type 'python3 SI507F17_finalproject.py runserver'
6. Open http://localhost:5000/stocks to see the display

Note: All API keys are included with the main code file and no action is required from tester.


## Files and Folders

* This README
* Main Code: `SI507F17_finalproject.py`
* Tests: 'FinalProject_tests.py'
* Installation Requirements: 'requirements.txt'
* DB Config: config.py
* Folder: RR_Emails (contains emails from subscription service)


## What Should Happen

1. Upon running, the app will first set up two databases if they do not exist, both for historical stock data.
2. The app will then call the DateTime class to get the date and time formats used by other functions. (The console will print a representation)
3. The app will SELECT dates from the stock data db table ('ixicHistory') and call the API for data. If the db is empty, the app checks if the current date is in the table, and if it is not, the API data will be entered into the db. (Note: this code, the function writeToDB I think is interesting)
4. The app will SELECT dates from the extra data db table ('ixicExtra') and run functions to check a subfolder for emails from a subscription service which contain trading data. I wrote a script that takes the emails and creates a text version in this subfolder. (**For this project I included fake emails going out a week from turn-in to simulate how they work**) If the db is empty, the app checks if the current date is in the table, and if it is not, the scrape data will be entered into the db.
5. If problems are encountered anywhere above, print statements should make you aware of the problem.
6. If it is not trading hours, you will be told so. If it is trading hours, the app will scrape yahoo finance for current prices (Note: Yahoo Finance uses React, which made scraping very difficult. My parsing functions are interesting)
7. The app will then check if there is a cache file, and if there is, check if it has today's date. If there is no cache file or if today's date is not within it, it will save the updated cache.
8. The final section will then SELECT data from the database and display it in a Flask app along with some of the other data pulled/created at 'http://localhost:5000/stocks'.  (watch the movie Execution.MOV to see the above actions)


## Major Challenges Encountered

1. Writing a program this large was a challenge. Around the 250 line mark and thereafter, when I had to write the cache and DB functions, countless major and minor issues were encountered. Also, simply finding code or where errors occurred was a challenge.

2. Since my app uses stock data, and the markets are only open 9:30-4 EST, I obtained very different results when running it at different times of the day. I also had to wait until trading time to run full tests.

3. Date formats from the different data sources was a continuous thorn in my side. If I started over I would convert all dates immediately after pulling.



This was fun!
