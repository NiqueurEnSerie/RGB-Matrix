import time
from datetime import datetime
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
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

# variables
brightness = 1
start = "07:30"
end = "22:00"
i = 0
clock = datetime.now().strftime("%I:%M")
ampm = datetime.now().strftime("%p")
date = datetime.today().strftime("%B %d")
realtime = datetime.now().strftime("%H:%M")
dayoftheweek = datetime.today().strftime("%A")

# colors & graphics
font_1 = graphics.Font()
font_2 = graphics.Font()
font_1.LoadFont("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/time.bdf")
font_2.LoadFont("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/text.bdf")
white = graphics.Color(255 * brightness, 255 * brightness, 255 * brightness)
green = graphics.Color(0 * brightness, 255 * brightness, 0 * brightness)
red = graphics.Color(255 * brightness, 0 * brightness, 0 * brightness)
purple = graphics.Color(128 * brightness, 0 * brightness, 128 * brightness)

# NHL Data
list_teams = {'1': 'Devils', '2': 'Islanders', '3': 'New_York_Rangers', '4': 'Flyers', '5': 'Penguins', '6': 'Bruins', '7': 'Sabres', '8': 'Canadiens', '9': 'Senators', '10': 'Leafs', '12': 'Canes', '13': 'Panthers', '14': 'Lightning', '15': 'Capitals', '16': 'Blackhawks', '17': 'Wings', '18': 'Predators', '19': 'Blues', '20': 'Flames', '21': 'Colorado_Avalanche', '22': 'Oilers', '23': 'Canucks', '24': 'Ducks', '25': 'Stars', '26': 'Kings', '28': 'Sharks', '29': 'Jackets', '30': 'Wild', '52': 'Jets', '53': 'Coyotes', '54': 'Knights', '55': 'Kraken'}

def NHLcontrol(teamid):
    try:
        gamelink = isPlaying(teamid)
        
        if gamelink != False:
            link = "https://statsapi.web.nhl.com" + gamelink
            gameinformation = requests.get(link).json()
            gamestatus = gameinformation['gameData']['status']['detailedState']
            hometeam = gameinformation['liveData']['linescore']['teams']['home']['team']['name']
            awayteam = gameinformation['liveData']['linescore']['teams']['away']['team']['name']

            if gamestatus == "Scheduled":
                startingTime = getGameTime(gameinformation['gameData']['datetime']['dateTime'])
                notStarted(hometeam, awayteam, startingTime)
            
            else:
                time_remaining = gameinformation['liveData']['linescore']['currentPeriodTimeRemaining']
                period = gameinformation['liveData']['linescore']['currentPeriod']
                homescore = gameinformation['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['goals']
                awayscore = gameinformation['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['goals']
                
                if time_remaining != 'Final':
                    currentlyPlaying(hometeam, awayteam, period, time_remaining, homescore, awayscore)
                else:
                    gameFinished(hometeam, awayteam, homescore, awayscore)
        else:
            nextgame = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamid) + "?expand=team.schedule.next").json()
            
            if 'nextGameSchedule' in nextgame['teams'][0]:
                fulltime = nextgame['teams'][0]['nextGameSchedule']['dates'][0]['date'].split('-')
                gametime = fulltime[1] + "-" +  fulltime[2]
                hometeam = nextgame['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['name']
                awayteam = nextgame['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['away']['team']['name']
                notPlaying(hometeam, awayteam, gametime)
            else:
                seasonOver(teamid)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)
        
def isPlaying(teamid):
    try:
        response = requests.get("https://statsapi.web.nhl.com/api/v1/schedule?date=").json()

        for game in range(0, response['totalGames']):
            if response['dates'][0]['games'][game]['teams']['home']['team']['id'] == teamid or response['dates'][0]['games'][game]['teams']['away']['team']['id'] == teamid:
                return response['dates'][0]['games'][game]['link']
        
        return False

    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)
        
def notPlaying(hometeam, awayteam, gametime):
    try:
        homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        homeimage = Image.open(getTeamImageLink(hometeam, homefile))
        awayimage = Image.open(getTeamImageLink(awayteam, awayfile))
        homeimage.thumbnail((25, 25), Image.ANTIALIAS)
        awayimage.thumbnail((25, 25), Image.ANTIALIAS)

        canvas.Clear()

        matrix.SetImage(homeimage.convert('RGB'), -7,0)
        matrix.SetImage(awayimage.convert('RGB'), 47,0)
        graphics.DrawText(canvas, font_2, 20, 12, white, "no game")
        graphics.DrawText(canvas, font_2, 23, 18, white, "today")
        graphics.DrawText(canvas, font_2, 4, 30, white, "Come back " + gametime)
        matrix.SwapOnVSync(canvas)

    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(e)

def notStarted(hometeam, awayteam, startime):
    try:
        homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
        awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"        
        homeimage = Image.open(getTeamImageLink(hometeam, homefile))
        awayimage = Image.open(getTeamImageLink(awayteam, awayfile))
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

def currentlyPlaying(hometeam, awayteam, period, time, hscore, ascore):
    period_text = ''

    if period == 1:
        period_text = "1st period"
    elif period == 2:
        period_text = "2nd period"
    else:
        period_text = "3rd period"
    
    homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
    awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
    homeimage = Image.open(getTeamImageLink(hometeam, homefile))
    awayimage = Image.open(getTeamImageLink(awayteam, awayfile))

    homeimage.thumbnail((25, 25), Image.ANTIALIAS)
    awayimage.thumbnail((25, 25), Image.ANTIALIAS)

    canvas.Clear()

    matrix.SetImage(homeimage.convert('RGB'), -7,0)
    matrix.SetImage(awayimage.convert('RGB'), 47,0)
    graphics.DrawText(canvas, font_1, 19, 20, white, str(hscore))
    graphics.DrawText(canvas, font_1, 35, 20, white, str(ascore))
    graphics.DrawText(canvas, font_2, 31, 15, white, "-")

    if time == "END":
        graphics.DrawText(canvas, font_2, 4, 30, white, period_text + " - " + str(time))
    else:
        graphics.DrawText(canvas, font_2, 1, 30, white, period_text + " - " + str(time))

    matrix.SwapOnVSync(canvas)

def gameFinished(hometeam, awayteam, hscore, ascore):
    homefile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
    awayfile = "/home/pi/rpi-rgb-led-matrix/img/NHLlogos/"
    homeimage = Image.open(getTeamImageLink(hometeam, homefile))
    awayimage = Image.open(getTeamImageLink(awayteam, awayfile))
    homeimage.thumbnail((25, 25), Image.ANTIALIAS)
    awayimage.thumbnail((25, 25), Image.ANTIALIAS)
    canvas.Clear()
    matrix.SetImage(homeimage.convert('RGB'), -7,0)
    matrix.SetImage(awayimage.convert('RGB'), 47,0)
    graphics.DrawText(canvas, font_1, 19, 20, white, str(hscore))
    graphics.DrawText(canvas, font_1, 35, 20, white, str(ascore))
    graphics.DrawText(canvas, font_2, 31, 15, white, "-")
    graphics.DrawText(canvas, font_2, 2, 30, white, "Gameover")
    graphics.DrawText(canvas, font_2, 38, 30, white, str(clock))
    graphics.DrawText(canvas, font_2, 56, 30, white, str(ampm))
    graphics.DrawText(canvas, font_2, 34, 30, white, "-")
    matrix.SwapOnVSync(canvas)

def seasonOver(teamid):
    canvas.Clear()
    logo = Image.open("/home/pi/rpi-rgb-led-matrix/img/NHLlogos/" + list_teams[str(teamid)] + '.jpg')
    logo.thumbnail((25, 25), Image.ANTIALIAS)
    matrix.SetImage(logo.convert('RGB'), 5,3)
    graphics.DrawText(canvas, font_2, 35, 12, white, "Season")
    graphics.DrawText(canvas, font_2, 35, 19, white, "over")
    matrix.SwapOnVSync(canvas)

def getTeamImageLink(team, filename):
    teamsplit = team.split()
    file = filename

    for i in range(len(teamsplit)):
        if i == len(teamsplit)-1:
            file += teamsplit[i] + ".jpg"
        else:
            file += teamsplit[i] + "_"

    return file

def getGameTime(time):
    split_time = time.split('T')[1].split('Z')[0].split(':')
    hours = split_time[0]
    minutes = split_time[1]

    if int(hours) < 4:
        hours = 12 - (4-int(hours))
        ampm = "pm"
    else:
        hours = int(hours)-4
        ampm = 'am'

    if hours > 12:
        hours = hours-12
        ampm = "pm"

    startime = str(hours) + ":" + minutes + " " + ampm
    return startime

def reset_colors():
    white = graphics.Color(255 * brightness, 255 * brightness, 255 * brightness)
    green = graphics.Color(0 * brightness, 255 * brightness, 0 * brightness)
    red = graphics.Color(255 * brightness, 0 * brightness, 0 * brightness)
    purple = graphics.Color(128 * brightness, 0 * brightness, 128 * brightness)

def pixelength(text):
    pixelength = len(text)*3 + (len(text)-1)
    return pixelength 

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

def time_display():
    brightness = 1
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
        matrix.SwapOnVSync(canvas)

    except KeyboardInterrupt:
        sys.exit()

    except Exception as e:
        print(e)

def night_display(day, month, year):    
    brightness = 0.2
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

while True:
    clock = datetime.now().strftime("%I:%M")
    ampm = datetime.now().strftime("%p")
    date = datetime.today().strftime("%B %d")
    realtime = datetime.now().strftime("%H:%M")
    dayoftheweek = datetime.today().strftime("%A")

    if (realtime >= start) & (realtime <= end):
        if i == 0:
            time_display()
            i = 1
            time.sleep(5)
        else:
            NHLcontrol(3)
            i = 0
            time.sleep(5)
    else:
        todaysdate = str(datetime.today()).split('-')
        night_display(int(todaysdate[2].split(' ')[0]), int(todaysdate[1]), int(todaysdate[0]))

