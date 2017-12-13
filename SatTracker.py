############################################################################### 
## For info on basemap module see:                                            #
## http://basemaptutorial.readthedocs.io/en/latest/                           #
## Author of this code: Peter Kongstad - kongstad25@gmail.com - November 2017 #
## Note it is build for python 2.7 and will not work correctly on python 3+   #
## Need to download and install google chrome webdriver for snapshot to work  #
###############################################################################

#%% Imported modules
import ephem
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import urllib2
from datetime import datetime
import math
#Selenium used for screenshot weather import - remember install ChromeDriver 
from selenium import webdriver
import time
import webbrowser
from PIL import Image


#%% Import the TLE from celesttrack website

#The following lines contain the category numbers for different satellites
#39430 This is for GomX1
#25544 This is for ISS
#41866 This is for GOES
#41765 This is for Tiangong 2

#Imports the raw html code with the TLE information from celestrak website
response = urllib2.urlopen('https://www.celestrak.com/cgi-bin/TLE.pl?CATNR=25544') # This is for ISS
data = response.read()

#Clean up its output, removing html code
sep = '</P'
data2 = str(data.split(sep, 1)[0])
sep = 'RE>'
cleaned = str(data2.split(sep, 1)[1])
print cleaned

#Crudely, but effectively select the TLE bits needed from the string
name=cleaned[1:15] #Scoops out the satellite name
line1=cleaned[26:95] #Strips the first line of the TLE
line2=cleaned[96:165] #Strips the second line of the TLE

#%% Using the ephem module to decipher the TLE information

#Using the TLE of the satellite to compute paramters
tle_rec = ephem.readtle(name, line1, line2)
tle_rec.compute()

#Calculate the altitude of the satellite in km's above Earth surface
altitude=tle_rec.elevation/1000

#Calculate it's velocity
velocity=math.sqrt((6.67*10**-11)*(5.98*10**24)/(6.38*10**6)+(altitude))

#Gets current time
times=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# This part prints the TLE data as longitude/latitude, altitucde, velocity and spatial resolution.
print "Current information for:", name;
print "Time:", times;
print "Longitude:", tle_rec.sublong;
print "Latitude:", tle_rec.sublat;
print "Altitude:" , tle_rec.elevation/1000, "[km]";
print "Velocity:",velocity/1000, "[km/s]";
print "Spatial Resolution of current altitude with the 35 mm lens:"
print  ((tle_rec.elevation/1000)/650)*60, "[pixels pr. m]";

#%% Prepare data for basemap mapping.

#Make the longitude and lattitude a string/variable for basemap operation
x_long=str(tle_rec.sublong)
x_lat=str(tle_rec.sublat)

#Remove the excess numbers past first colon due to basemap limitations of
#understanding latitude and longitude coordinates on both 3D and 2D map.
sep = ':'
ylattr = str(x_lat.split(sep, 1)[0])
ylongr = str(x_long.split(sep, 1)[0])

#%% Basemap operations
##############################################################################
# There was a lot of issues with getting both 3D and 2D map to work based on #
# the lat/long. Therefore I have different type of variables for it to work  #
##############################################################################

#The 3D Globe map
#Map perspective is set from the current lat/long of the satellite.
fig = plt.figure(1)
map = Basemap(projection='ortho',lon_0=ylongr,lat_0=ylattr,resolution='l')
map.bluemarble() #Sets the graphics for the globe, different options on basemap site
map.drawcoastlines(linewidth=0.25)
map.drawcountries(linewidth=0.25)
map.fillcontinents(color='green',lake_color='blue')
map.drawmapboundary(fill_color='aqua')
map.drawmeridians(np.arange(0,360,30))
map.drawparallels(np.arange(-90,90,30))

#This part plots the satellite as a red dot and with text, needs direct input of lonlat
sat_lon,sat_lat=map(ylongr,ylattr)
map.plot(sat_lon,sat_lat,marker='o',color='r')
plt.text(sat_lon,sat_lat, name,fontsize=12,fontweight='bold',ha='right',va='bottom',color='w')

#Paints a grid
nlats = 73; nlons = 145; delta = 2.*np.pi/(nlons-1)
lats = (0.5*np.pi-delta*np.indices((nlats,nlons))[0,:,:])
lons = (delta*np.indices((nlats,nlons))[1,:,:])
wave = 0.75*(np.sin(2.*lats)**8*np.cos(4.*lons))
mean = 0.5*np.cos(2.*lats)*((np.sin(2.*lats))**2 + 2.)
x, y = map(lons*180./np.pi, lats*180./np.pi)
date = datetime.utcnow()
CS=map.nightshade(date)
plt.title('Globe View') 
#plt.show()
plt.savefig('Globeview.png')



#%% Here comes the 2D world map

fig = plt.figure(2)
map = Basemap(projection='cyl')
map.drawcoastlines(linewidth=0.25)
map.drawcountries(linewidth=0.25)
map.fillcontinents(color='green',lake_color='aqua')
map.drawmapboundary(fill_color='aqua')
map.drawmeridians(np.arange(0,360,30))
map.drawparallels(np.arange(-90,90,30))

#Need to convert the string with lat/long to an integer for flat map to work
ylongri=int(ylongr);
ylattri=int(ylattr);
sat_lon,sat_lat=map(ylongri,ylattri)
map.plot(sat_lon,sat_lat,marker='o',color='r')
plt.text(sat_lon,sat_lat,name,fontsize=12,fontweight='bold',ha='right',va='bottom',color='w')
date = datetime.utcnow()
CS=map.nightshade(date)
plt.title('2D Map View')
#plt.show()
plt.savefig('MercatorView.png')

#%% Adding weather client from openweathermap.org
#Chromedriver must be installed on system in a path that python can recognize - https://sites.google.com/a/chromium.org/chromedriver/home

#Convert to string for URL usage
sat_latstr=str(sat_lat)
sat_lonstr=str(sat_lon)

#Uses google chrome client to screenshot the current weather data at the location - Ignore the window that opens.
browser = webdriver.Chrome()
url=('http://openweathermap.org/weathermap?basemap=satellite&cities=false&layer=precipitation&lat='+sat_latstr+'=&lon='+sat_lonstr+'&zoom=7')
browser.get(url)
time.sleep(8)             #Give it some time to load the images
browser.save_screenshot('currentweather.png')
browser.quit()

#%% Crops image
img = Image.open('currentweather.png') # uses PIL library to open image in memory
half_the_width = img.size[0] / 2
half_the_height = img.size[1] / 2
img4 = img.crop(
    (
        half_the_width - 929/2,
        half_the_height - 620/2,
        half_the_width + 890/2,
        half_the_height + 884/2
    )
)
img4.save("currentweathercropped.png")

#%% Adding google maps satellite view of area and screenshotting it.
browser2 = webdriver.Chrome()
zoomlevel=str(8)
url2=('http://www.google.com/maps/@'+sat_latstr+','+sat_lonstr+','+zoomlevel+'z/data=!3m1!1e3') 

browser2.get(url2)
time.sleep(5)             #Give it some time to load the images
browser2.save_screenshot('GECurrent.png')
browser2.quit()

#%% Crops image
img = Image.open('GECurrent.png') # uses PIL library to open image in memory
half_the_width = img.size[0] / 2
half_the_height = img.size[1] / 2
img4 = img.crop(
    (
        half_the_width - 929/2,
        half_the_height - 700/2,
        half_the_width + 929/2,
        half_the_height + 888/2
    )
)
img4.save("GECurrentcropped.png")

#%% Displays the two imported images
#webbrowser.open("currentweathercropped.png")
#webbrowser.open("GECurrentcropped.png")

#%% Resize images smaller
basewidth = 300
img = Image.open('currentweathercropped.png')
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), Image.ANTIALIAS)
img.save('currentweathercroppedsmall.png') 

basewidth = 300
img = Image.open('GECurrentcropped.png')
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), Image.ANTIALIAS)
img.save('GECurrentcroppedsmall.png') 

#%% GUI Interface

import Tkinter as tk
from tkFont import Font
from PIL import ImageTk, Image
from Tkinter import END

#Converting information from floats to strings
alt=str(altitude)
vel=str(velocity/1000)
spat=str(((tle_rec.elevation/1000)/650)*60)
spacer='  '; #Unelegant method for spacing the lines

#This creates the main window of an application
window = tk.Tk()
window.title("Sat Track")
window.geometry("1200x800")
window.configure(background='#f0f0f0')
    
                 
#Imports the pictures.
pic1 = "Globeview.png"
pic2 = "MercatorView.png"
pic3 = "currentweathercroppedsmall.png"
pic4 = "GECurrentcroppedsmall.png"

#Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
img1 = ImageTk.PhotoImage(Image.open(pic1))
img2 = ImageTk.PhotoImage(Image.open(pic2))
img3 = ImageTk.PhotoImage(Image.open(pic3))
img4 = ImageTk.PhotoImage(Image.open(pic4))

header = tk.Label(window, text="Aarhus University Satellite Control Center", font=Font(size=40))
header.pack()

toprow = tk.Frame(window)
infobox = tk.Text(toprow, width=50, height=7, font=("Calibri",12))
infobox.pack(side = "left") 
infobox.insert(END,"Current information for:"+spacer+name +'\n'+
               "Time:" +space+times+ '\n'+
               "Longitude:"+space +x_long+ '\n'+
               "Latitude:" +space+x_lat+ '\n'+     
               "Altitude:" +space+alt+space+ "[km]"+'\n'+
               "Velocity:" +space+vel+space+ "[km/s]" + '\n'+
               "Spatial Resolution: "+space +spat+space+ "[Pixels pr. m]"
               )
toprow.pack()

midrow = tk.Frame(window)
globeview = tk.Label(midrow, image = img1)
globeview.pack(side = "left") # the side argument sets this to pack in a row rather than a column
mercatorview = tk.Label(midrow, image = img2)
mercatorview.pack(side = "left")
midrow.pack() # pack the toprow frame into the window 

bottomrow = tk.Frame(window)
currentweather= tk.Label(bottomrow, image = img3)
currentweather.pack(side = "left")
gearth = tk.Label(bottomrow, image = img4)
gearth.pack(side = "left")
bottomrow.pack()

#Start the GUI
window.mainloop()