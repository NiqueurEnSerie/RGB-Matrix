import time
from datetime import datetime
import json
import colorsys
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
from PIL import Image, ImageFont, ImageDraw, ImageSequence
import sys
import requests

#Configuration of the display
options = RGBMatrixOptions()
options.gpio_slowdown = 4
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.row_address_type = 0
options.multiplexing = 0
options.pwm_bits = 11
options.brightness = 100
options.pwm_lsb_nanoseconds = 130
options.led_rgb_sequence = "RBG"
options.pixel_mapper_config = ""
matrix = RGBMatrix(options = options)
canvas = matrix.CreateFrameCanvas()

# Graphics stuff
font_1 = graphics.Font()
font_1.LoadFont("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/time.bdf")
font_2 = graphics.Font()
font_2.LoadFont("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/text.bdf")

brightness = 1

# colors
white = graphics.Color(255 * brightness, 255 * brightness, 255 * brightness)
green = graphics.Color(0 * brightness, 255 * brightness, 0 * brightness)
red = graphics.Color(255 * brightness, 0 * brightness, 0 * brightness)
purple = graphics.Color(128 * brightness, 0 * brightness, 128 * brightness)

def nhlscore(team, teamid): #main function
    try:
        gamelink = isPlaying(teamid) #check if playing 
        
        if gamelink != False:
            playing = True

            while playing: #team is playing
                fullgamelink = "https://statsapi.web.nhl.com" + gamelink
                currentgame = requests.get(fullgamelink).json()
                linescore = currentgame['liveData']['linescore']
                currentperiod = linescore['currentPeriod']
                hometeam = linescore['teams']['home']['team']['name']
                awayteam = linescore['teams']['away']['team']['name']

                if currentperiod == 0: #game hasnt started
                    time = currentgame['gameData']['datetime']['dateTime']
                    split1 = time.split('T')
                    split2 = split1[1].split('Z')
                    split3 = split2[0].split(':')
                    minutes =  split3[1]

                    if int(split3[0]) < 4:
                        hour = 12 - (4-int(split3[0]))
                        ampm = "pm"
                    else:
                        hour = int(split3[0])-4
                        ampm = 'am'

                    if hour > 12:
                        hour = hour-12
                        ampm = "pm"

                    startime = str(hour) + ":" + minutes + " " + ampm
                    notstarted(hometeam, awayteam, startime)
                    break

                else: #game is currently being played or ended
                    if linescore['currentPeriodTimeRemaining'] != "Final": #game is in progress
                            currentlyPlaying(hometeam, awayteam, fullgamelink)
                            break
                    else:
                        gameFinished(hometeam, awayteam, fullgamelink) #game is over
                        break
        else:
            notPlaying(3)

    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)

def isPlaying(teamid): #check if a team is playing
    try:
        response = requests.get("https://statsapi.web.nhl.com/api/v1/schedule?date=").json()
        totalgames = response['totalGames']
    
        for i in range(0, totalgames):
            hometeam = response['dates'][0]['games'][i]["teams"]['home']['team']['name']
            awayteam = response['dates'][0]['games'][i]["teams"]['away']['team']['name']

            if (hometeam == list_teams[teamid]) or (awayteam == list_teams[teamid]):
                gamelink = response['dates'][0]['games'][i]['link']
                return gamelink 
            else:
                continue
        return False
    
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)

def notstarted(hometeam, awayteam, startime): #game not started 
    try:
        homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"

        hsplit = hometeam.split()
        asplit = awayteam.split()

        for i in range(len(hsplit)):
            if i == len(hsplit)-1:
                homefile += hsplit[i] + ".jpg"
            else:
                homefile += hsplit[i] + "_"

        for i in range(len(asplit)):
            if i == len(asplit)-1:
                awayfile += asplit[i] + ".jpg"
            else:
                awayfile += asplit[i] + "_"
        
        homeimage = Image.open(homefile)
        awayimage = Image.open(awayfile)
        homeimage.thumbnail((25, 25), Image.ANTIALIAS)
        awayimage.thumbnail((25, 25), Image.ANTIALIAS)

        canvas.Clear()
        matrix.SetImage(homeimage.convert('RGB'), -7,0)
        matrix.SetImage(awayimage.convert('RGB'), 47,0)
        graphics.DrawText(canvas, font_1, 19, 20, white, str("0"))
        graphics.DrawText(canvas, font_1, 35, 20, white, str('0'))
        graphics.DrawText(canvas, font_2, 31, 15, white, "-")

        graphics.DrawText(canvas, font_2, 2, 30, white, "Game Time: " + startime)
        matrix.SwapOnVSync(canvas)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)

def notPlaying(teamid): #no game today
    try:
        nextgame = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamid) + "?expand=team.schedule.next").json()
        hometeam = nextgame['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['name']
        awayteam = nextgame['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['away']['team']['name']
        fullstartime = nextgame['teams'][0]['nextGameSchedule']['dates'][0]['date']
        time.split1 = fullstartime.split('-')
        startime = time.split1[1] + "-" + time.split1[2]

        homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"

        hsplit = hometeam.split()
        asplit = awayteam.split()

        for i in range(len(hsplit)):
            if i == len(hsplit)-1:
                homefile += hsplit[i] + ".jpg"
            else:
                homefile += hsplit[i] + "_"

        for i in range(len(asplit)):
            if i == len(asplit)-1:
                awayfile += asplit[i] + ".jpg"
            else:
                awayfile += asplit[i] + "_"
        
        homeimage = Image.open(homefile)
        awayimage = Image.open(awayfile)
        homeimage.thumbnail((25, 25), Image.ANTIALIAS)
        awayimage.thumbnail((25, 25), Image.ANTIALIAS)

        canvas.Clear()
        matrix.SetImage(homeimage.convert('RGB'), -7,0)
        matrix.SetImage(awayimage.convert('RGB'), 47,0)
        graphics.DrawText(canvas, font_2, 20, 12, white, "no game")
        graphics.DrawText(canvas, font_2, 23, 18, white, "today")
        graphics.DrawText(canvas, font_2, 4, 30, white, "Come back " + startime)
        matrix.SwapOnVSync(canvas)

    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)

def currentlyPlaying(hometeam, awayteam, gamelink): #game is in progress
    try:
        currentgame = requests.get(gamelink).json()
        currentperiod = currentgame['liveData']['linescore']['currentPeriod']
        timeremaining = currentgame['liveData']['linescore']['currentPeriodTimeRemaining']
        homescore = currentgame['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['goals']
        awayscore = currentgame['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['goals']

        homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"

        hsplit = hometeam.split()
        asplit = awayteam.split()

        for i in range(len(hsplit)):
            if i == len(hsplit)-1:
                homefile += hsplit[i] + ".jpg"
            else:
                homefile += hsplit[i] + "_"

        for i in range(len(asplit)):
            if i == len(asplit)-1:
                awayfile += asplit[i] + ".jpg"
            else:
                awayfile += asplit[i] + "_"

        period = ""
        
        if currentperiod == 1:
            period = "1st period"
        elif currentperiod == 2:
            period = "2nd period"
        else:
            period = "3rd period"
        
        homeimage = Image.open(homefile)
        awayimage = Image.open(awayfile)
        homeimage.thumbnail((25, 25), Image.ANTIALIAS)
        awayimage.thumbnail((25, 25), Image.ANTIALIAS)

        canvas.Clear()
        
        matrix.SetImage(homeimage.convert('RGB'), -7,0)
        matrix.SetImage(awayimage.convert('RGB'), 47,0)
        graphics.DrawText(canvas, font_1, 19, 20, white, str(homescore))
        graphics.DrawText(canvas, font_1, 35, 20, white, str(awayscore))
        graphics.DrawText(canvas, font_2, 31, 15, white, "-")
        
        if timeremaining == "END":
            graphics.DrawText(canvas, font_2, 4, 30, white, period + " - " + str(timeremaining))
        else:
            graphics.DrawText(canvas, font_2, 1, 30, white, period + " - " + str(timeremaining))

        matrix.SwapOnVSync(canvas)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)

def gameFinished(hometeam, awayteam, gamelink): #game is over
    try:
        currentgame = requests.get(gamelink).json()
        currentperiod = currentgame['liveData']['linescore']['currentPeriod']
        timeremaining = currentgame['liveData']['linescore']['currentPeriodTimeRemaining']
        homescore = currentgame['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['goals']
        awayscore = currentgame['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['goals']

        homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"

        hsplit = hometeam.split()
        asplit = awayteam.split()

        for i in range(len(hsplit)):
            if i == len(hsplit)-1:
                homefile += hsplit[i] + ".jpg"
            else:
                homefile += hsplit[i] + "_"

        for i in range(len(asplit)):
            if i == len(asplit)-1:
                awayfile += asplit[i] + ".jpg"
            else:
                awayfile += asplit[i] + "_"
        
        homeimage = Image.open(homefile)
        awayimage = Image.open(awayfile)
        homeimage.thumbnail((25, 25), Image.ANTIALIAS)
        awayimage.thumbnail((25, 25), Image.ANTIALIAS)
        canvas.Clear()
        matrix.SetImage(homeimage.convert('RGB'), -7,0)
        matrix.SetImage(awayimage.convert('RGB'), 47,0)
        graphics.DrawText(canvas, font_1, 19, 20, white, str(homescore))
        graphics.DrawText(canvas, font_1, 35, 20, white, str(awayscore))
        graphics.DrawText(canvas, font_2, 31, 15, white, "-")
        graphics.DrawText(canvas, font_2, 2, 30, white, "Gameover")
        graphics.DrawText(canvas, font_2, 38, 30, white, str(clock))
        graphics.DrawText(canvas, font_2, 56, 30, white, str(ampm))
        graphics.DrawText(canvas, font_2, 34, 30, white, "-")
        matrix.SwapOnVSync(canvas)    
    
    except KeyboardInterrupt:
        sys.exit()

    except Exception as e:
        print(e)

def getSmallTextOffset(small_text): #text formatting
    small_text_length = 0
    for i in range(len(small_text)):
        if (list(small_text)[i] == " "):
            small_text_length += 1
        elif (list(small_text)[i] == u"\N{DEGREE SIGN}" or list(small_text)[i].lower() == "i"):
            small_text_length += 2
        elif (list(small_text)[i] == ","):
            small_text_length += 3
        else:
            small_text_length += 4
    return (64 - small_text_length)/2 + 1   

def pixelength(text):
    pixelength = len(text)*3 + (len(text)-1)
    return pixelength 

def timedisplay():
    
    brightness = 1

    # colors
    white = graphics.Color(255 * brightness, 255 * brightness, 255 * brightness)
    purple = graphics.Color(128 * brightness, 0 * brightness, 128 * brightness)

    try:
        ampm_location = 57-(clock.count("1")*3)
        

        canvas.Clear()
        graphics.DrawText(canvas, font_2, 5, 8, white, date)
        graphics.DrawText(canvas, font_1, 4, 24, purple, clock)
        graphics.DrawText(canvas, font_2, ampm_location, 14, purple, list(ampm)[0])
        graphics.DrawText(canvas, font_2, ampm_location, 20, purple, list(ampm)[1])
        graphics.DrawText(canvas,font_2, (ampm_location-pixelength(dayoftheweek)+3), 30, white, dayoftheweek)

        # graphics.DrawText(canvas, font_2, getSmallTextOffset(outside), 30, white, outside)
        matrix.SwapOnVSync(canvas)

    except KeyboardInterrupt:
        sys.exit()

    except Exception as e:
        print(e)

def nightime():
        
    brightness = 0.2

    # colors
    white = graphics.Color(255 * brightness, 255 * brightness, 255 * brightness)
    purple = graphics.Color(128 * brightness, 0 * brightness, 128 * brightness)

    imagefile = "/home/pi/rpi-rgb-led-matrix/img/moon/" + moon_phase(month,day,year) + ".jpg"
    image = Image.open(imagefile)
    image.thumbnail((25, 25), Image.ANTIALIAS)
    dateform = (str(day) + "/" + str(month) + "/" + str(year))

    if clock[0] == "0":
        goodtime = clock[1] + ":" + clock[3] + clock[4]
    else:
        goodtime =  clock[0]+ clock[1] + clock[3] + clock[4]
        

    canvas.Clear()
    matrix.SetImage(image.convert('RGB'), -2,5)
    graphics.DrawText(canvas, font_1, 20, 18, white, goodtime)
    graphics.DrawText(canvas, font_2, 26, 27, purple, dateform)
    matrix.SwapOnVSync(canvas)   

def moon_phase(month, day, year):
    ages = [18, 0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26, 7]
    offsets = [-1, 1, 0, 1, 2, 3, 4, 5, 7, 7, 9, 9]
    description = ["new","waxc","fq","waxb","full","wanb","lq","wanc"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    if day == 31:
        day = 1

    days_into_phase = ((ages[(year + 1) % 19] + ((day + offsets[month-1]) % 30) + (year < 1900)) % 30)
    index = int((days_into_phase + 2) * 16/59.0)

    if index > 7:
        index = 7
    
    status = description[index]
    
    return status


#variables
start = "08:00"
end = "23:00"
weekend = False
i = 0
clock = datetime.now().strftime("%I:%M")
ampm = datetime.now().strftime("%p")
date = datetime.today().strftime("%B %d")
realtime = datetime.now().strftime("%H:%M")
dayoftheweek = datetime.today().strftime("%A")


while True:
    clock = datetime.now().strftime("%I:%M")
    ampm = datetime.now().strftime("%p")
    date = datetime.today().strftime("%B %d")
    realtime = datetime.now().strftime("%H:%M")
    dayoftheweek = datetime.today().strftime("%A")

    if (realtime >= start) & (realtime <= end):
        if i == 0:
            timedisplay()
            i = 1
            time.sleep(5)
        elif i == 1:
            nhlscore("New York Rangers", "3")
            i = 0
            time.sleep(5)
    else:
        todaysdate = datetime.today()
        fulldate = str(todaysdate).split("-")
        year = int(fulldate[0])
        month = int(fulldate[1])
        day = int(fulldate[2].split(" ")[0])
        nightime()
        

        




