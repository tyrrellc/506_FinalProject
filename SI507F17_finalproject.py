print('\n\n   *** EXECUTION ***\n')

import datetime
import requests   # install
import json
import os
import glob
import re
from bs4 import BeautifulSoup   # install
import time
import psycopg2   # install
import psycopg2.extras
from config import *
import sys
import threading
from flask import Flask, render_template    # install
from flask_script import Manager


app = Flask(__name__)   #create instance of flask app

manager = Manager(app)


initPull = []
dateList = []
finalPull = []


# DATE AND TIME CLASS: Get and format date and time

class DateTime(object):

    def __init__(self):
        now = datetime.datetime.now()
        self.hr = now.hour
        self.mi = now.minute
        self.mo = now.month
        self.day = now.day
        if len(str(self.day)) == 1:
            self.day = '0'+str(self.day)
        self.yr = now.year

    def GetDate(self):
        tyr = str(self.yr)
        rryr = tyr[2]+tyr[3]
        aatoday = str(self.yr)+'-'+str(self.mo)+'-'+str(self.day)
        rrtoday = str(self.mo)+'/'+str(self.day)+'/'+rryr
        today = str(rryr)+str(self.mo)+str(self.day)
        return aatoday, rrtoday, today

    def GetTime(self):
        time = str(self.hr)+str(self.mi)
        return time

    def __contains__(self, test_time):
        return test_time in self.author

    def __repr__(self):
        return 'Month: {}\nDay: {}\nHour: {}\nMinutes: {}\n'.format(self.mo, self.day, self.hr, self.mi)


# EXTRACTION FUNCTIONS: Find text within large body of text

def find_between_rr( s, first, last ):
    """Extract section from rr email text and insert END"""

    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]+'END'
    except ValueError:
        return ""


def find_between( s, first, last ):
    """Extract section from large body of text"""

    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def find_specific(s, first, last ):
    """Extract specific data from text"""

    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


# RISK RANGE FUNCTIONS: access emails with subscription Risk Range data and extract

def find_rr():
    """Extract specific data from email file"""

    c = 0
    l = [['YIELD \n','\nSPX', '10YR'],['500 \n','\nRUT', 'S&P'],['RUSSELL2000 \n','\nCOMPQ', 'RUT'],['COMPOSITE \n','\nEND', 'COMPQ']]

    for item in initPull:
        s = initPull[c]
        #print(s)
        x = 0
        tempPull = []
        for stuff in l:
            d = l[x]
            first = d[0]
            last = d[1]
            specific = find_specific(s, first, last)
            temp = specific.split('\n')
            rr = [d[2],temp[0],temp[1]]
            tempPull.append(rr)
            x = x+1
        finalPull.append(tempPull)
        c = c+1
    return


def riskRangePull():
    """Access email files and control parsing functions"""

    path = './RR_Emails'
    for filename in glob.glob(os.path.join(path, '*')):
        rrfile = open(os.fsdecode(filename), encoding = 'latin-1')
        rrData = rrfile.read()
        date = re.findall('(\d+/\d+/\d+)',rrData)
        dateList.append(date[0])
        capture = find_between_rr(rrData,'UST10Y','XOP')
        initPull.append(capture)
        #print('\nDATA: ',rrData,'\n')
    return


def rrExecute():
    """Control extration functions and build risk range dictionary"""

    riskRangePull()
    find_rr()
    rr_dict = {}
    c = 0
    for item in dateList:
        rr_dict[dateList[c]] = finalPull[c]
        c = c+1
    return rr_dict


# API and SCRAPING FUNCTIONS: get data from two sources

def TimeSeriesDaily(stock):
    """Pull historic stock data from API"""

    aa_url = 'https://www.alphavantage.co/query?'
    apikey = 'Q1NS8MRIX8YWJNS'

    url = aa_url + 'function=TIME_SERIES_DAILY' + '&symbol=' + stock + '&outputsize=compact&apikey=' +apikey
    response = requests.get(url)

    if 'Error' in response:
        apikey = '1MVLSUZ696BBAND5'  #new one
        url = aa_url + 'function=TIME_SERIES_DAILY' + '&symbol=' + stock + '&outputsize=compact&apikey=' +apikey
        response = requests.get(url)
    #print(response.text)

    aa_h_dict = response.json()
    #print(aa_dict)
    return aa_h_dict


def scrape_control(vol):
    """Make scrape requests and control parsing functions"""

    base_url = 'https://finance.yahoo.com/quote/^'
    url = base_url + vol + '?p=^' + vol
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    section = soup.find_all('script')
    s = str(section)
    #for item in section:            #IF ISSUE
        #print(item.text, '\n\n\n')

    text = '"^' + vol + '":{'
    capture = find_between(s, text,'fiftyTwoWeekHighChange')
    change = find_specific(capture,'"regularMarketChange":{"raw":',',"fmt')
    opent = find_specific(capture,'"regularMarketOpen":{"raw":',',"fmt')
    #print('\nPRINT\n', capture, '\n\n', change, opent)   #IF ISSUE
    currentt = float(opent) + float(change)
    try:
        percentt = float(change)/float(opent)*100
    except:
        print('The market is not open. Execute program between 9:30 and 4:00 EST on normal trading days\n')
        return

    current = round(currentt, 2)
    percent = round(percentt, 2)
    return current, change, percent


def scrape():
    """Control yahoo scraping and build current data dictionary"""

    stocks = ['VXN','IXIC']
    values = {}
    try:
        for item in stocks:
            current, change, percent = scrape_control(item)
            values[item] = current
    except:
        print('\nThere was an issue scraping yahoo. Try again in a few minutes or wait until trading hours (9:30 - 4:00 EST).\n')
    time = today.GetTime()
    DAILYVALUES[time] = values

    return DAILYVALUES[time]


# CACHE FUNCTION: If market is current trading (930-4 EST), cache newest daily price data

def setCache():
    time = today.GetTime()
    if int(time) > 930 and int(time) < 1600:
        try:
            CACHE_DICT[TODAY] = DAILYVALUES
            with open('dailyData.json', 'w') as cache_file:
                cache_json = json.dumps(CACHE_DICT)
                cache_file.write(cache_json)
        except:
            print('\nThere was an issue scraping yahoo. Try again in a few minutes or wait until trading hours (9:30 - 4:00 EST).\n')
            return

    elif int(time) <= 930 or int(time) >= 1600:
        print('\nThe US markets are currently closed.\n')
    else:
        print('\nThere was an issue scraping yahoo. Try again in a few minutes.')

    return


# DATABASE ADMIN FUNCTIONS: Open DB connection and create if first run

def connect_to_db():
    try:
        conn = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
        print("Success connecting to database\n")
    except:
        print("Unable to connect to the database. Check server and credentials.")
        sys.exit(1) # Stop running program if there's no db connection.

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn, cur

conn, cur = connect_to_db()

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#cur.execute("DROP TABLE IF EXISTS ixicHistory")
#cur.execute("DROP TABLE IF EXISTS ixicExtra")

cur.execute("CREATE TABLE IF NOT EXISTS ixicHistory(Date CHAR(10), CommonDate CHAR(6), Open FLOAT, Close FLOAT, High FLOAT, Low Float, Volume BIGINT)")

cur.execute("CREATE TABLE IF NOT EXISTS ixicExtra(Date CHAR(8), CommonDate CHAR(6), rrHigh CHAR(7), rrLow CHAR(7), vxnHigh FLOAT, vxnLow Float)")


# DATABASE EXECUTION FUNCTIONS: prepare new data and write to DB

def convert(date, typeDate):
    """Prepare three seperate date formats for entry into db"""
    # aaformat, rrformat, today = 'yyyy-mm-dd', 'mm/dd/yy'  'yymmdd'
    if typeDate == 'aaTo':
        aax = ''.join( c for c in date if  c not in '-' )
        newDate = aax[2:8]  #format yymmdd
    elif typeDate == 'rrTo':
        #tD = ''.join( c for c in date if  c not in '/' )
        tD = date.split('/')
        newDate = tD[2]+tD[0]+tD[1]
    elif typeDate == 'toAA':
        newDate = '20' + str(date[0:1])+'-'+str(date[2:3])+'-'+str(date[4:5])
    elif typeDate == 'toRR':
        newDate = str(date[2:3])+'/'+str(date[4:5])+'/'+str(date[0:1])
    return newDate

def writeToDB(dict, type):
    """Formats data for two different tables and commits changes"""

    if type == 'aa':
        data = []
        for key, value in dict.items():
            common = convert(key, 'aaTo')
            tempDict = {
            'Date': key,
            'CommonDate': common,
            'Open': value['1. open'],
            'Close': value['4. close'],
            'High': value['2. high'],
            'Low': value['3. low'],
            'Volume': value['5. volume']
            }
            data.append(tempDict)

        cur.executemany("""INSERT INTO ixicHistory(Date, CommonDate, Open, Close, High, Low, Volume) VALUES (%(Date)s, %(CommonDate)s, %(Open)s, %(Close)s, %(High)s, %(Low)s, %(Volume)s)""",data)


    if type == 'rr':
        data = []
        for key, value in dict.items():
            common = convert(key, 'rrTo')
            tempDict = {
            'Date': key,
            'CommonDate': common,
            'rrHigh': value[3][2],
            'rrLow': value[3][1]
            }
            data.append(tempDict)

        cur.executemany("""INSERT INTO ixicExtra(Date, CommonDate, rrHigh, rrLow) VALUES (%(Date)s, %(CommonDate)s, %(rrHigh)s, %(rrLow)s)""",data)

    conn.commit() # Necessary to save changes in database
    return


# INITIAL EXEUTION STATEMENTS: run once to ensure db is up to date

# Get specific date format for each dataset and current time

today = DateTime()
AATODAY, RRTODAY, TODAY = today.GetDate()
print(repr(today))

# Check DB to see if stock data is up to date
cur.execute('SELECT Date FROM ixicHistory')
aaDates = cur.fetchall()
aa_dict = TimeSeriesDaily('ixic')
if aaDates == []:   #if db is empty then write all data to db
    print('First Time Run on This Machine')
    print('Adding historic data to database\n')
    passDict = aa_dict['Time Series (Daily)']
    writeToDB(passDict, 'aa')
else:
    for sl in aaDates:
        sl = str(sl[0])
        if AATODAY == sl:
            print('Stock Data Up to Date   :)')
            break
        else:
            try:
                aatoday = aa_dict['Time Series (Daily)'][AATODAY]
                tempDict = {AATODAY:aatoday}
                writeToDB(tempDict, 'aa')
            except:
                print('There is no initial stock data for today   :(')
                AATODAYDATA = None
                break

# Check DB to see if Risk Range data is up to date
cur.execute('SELECT Date FROM ixicExtra')
rrDates = cur.fetchall()
rr_dict = rrExecute()
if rrDates == []:   #if db is empty then write all data to db
    writeToDB(rr_dict, 'rr')
else:
    for sl in sorted(rrDates, reverse=True):
        sl = str(sl[0])
        if RRTODAY == sl:
            print('Risk Range Data Up to Date   :)')
            break
        else:
            try:
                rrtoday = rr_dict[RRTODAY]
                tempDict = {RRTODAY:rrtoday}
                writeToDB(tempDict, 'rr')
            except:
                print('There is no Risk Range data for today   :(')
                RISKRANGE = None
                break

# Check cache to see if data up to date
try:
    with open('dailyData.json', 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICT = json.loads(cache_json)
        DAILYVALUES = CACHE_DICT[TODAY]
except:
    CACHE_DICT = {}
    DAILYVALUES = {}

if TODAY in CACHE_DICT.keys():
    print('\nContinuing to Flask.  Press ctrl+c to stop program.\n')
else:
    print('Setting Cache')
    scrape()
    setCache()


# FLASK OUTPUT

@app.route('/stocks')

def test():
    try:
        cur.execute("""SELECT * FROM ixicHistory JOIN ixicExtra ON (ixicHistory.CommonDate = ixicExtra.CommonDate)""")
        dbList = cur.fetchall()
        tdbList = sorted(dbList, reverse=True)
        selectList = tdbList[0:4]
        #data = selectList[0]
        #print(data)
        Date1 = selectList[1]
        Date2 = selectList[2]
        Date3 = selectList[3]

        rrTemp = rr_dict[RRTODAY]
        rrHigh = rrTemp[3][2]
        rrLow = rrTemp[3][1]
        #price = {'VXN': 12.28, 'IXIC': 6908.78}
        price = scrape()

        #return '<br><h1>Data for COMPQ for {}:</h1><br><h3>Risk Range: {} - {}</h3><h3>Current Price: {}</h3><br><h3>VXN: {}</h3><br><br><p>{}</p><br><table style="width:60%; border: 1px solid black; padding: 5px; background-color: #bfefff"><tr><th>Firstname</th><th>Lastname</th> <th>Age</th></tr><tr><td>Jill</td><td>Smith</td> <td>50</td></tr><tr><td>Eve</td><td>Jackson</td> <td>94</td></tr></table>'.format(RRTODAY, rrLow, rrHigh, price['IXIC'], price['VXN'], data)

        return '<br><h1>Data for COMPQ for {}:</h1><br><h3>Risk Range: {} - {}</h3><h3>Current Price: {}</h3><br><h3>VXN: {}</h3><br><br><br><br><table style="width:60%; border: 1px solid black; padding: 5px; background-color: #bfefff"><tr><th>Date</th><th>RR Low</th> <th>Mkt Low</th><th>RR High</th><th>Mkt High</th> <th>Open</th><th>Close</th> <th>Volume</th></tr><tr><td>{}</td><td>{}</td> <td>{}</td><td>{}</td><td>{}</td> <td>{}</td><td>{}</td><td>{}</td></tr><tr><td>{}</td><td>{}</td> <td>{}</td><td>{}</td><td>{}</td> <td>{}</td><td>{}</td><td>{}</td></tr><tr><td>{}</td><td>{}</td> <td>{}</td><td>{}</td><td>{}</td> <td>{}</td><td>{}</td><td>{}</td></tr></table>'.format(RRTODAY, rrLow, rrHigh, price['IXIC'], price['VXN'], Date1[0],Date1[10],Date1[5],Date1[9],Date1[4],Date1[2],Date1[3],Date1[6], Date2[0],Date2[10],Date2[5],Date2[9],Date2[4],Date2[2],Date2[3],Date2[6], Date3[0],Date3[10],Date3[5],Date3[9],Date3[4],Date3[2],Date3[3],Date3[6])


    except:
        return'<br><h2>There was an issue. Please ensure US markets are currently trading.</h2>'


if __name__ == '__main__':
    manager.run() # Runs the flask server in a special way that makes it nice to debug
