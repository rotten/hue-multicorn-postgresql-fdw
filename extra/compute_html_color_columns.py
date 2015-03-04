#!/usr/bin/env python

## Read in the html_colors_source_data.csv file.
## Compute the additional columns we need for the HTML table.
## Output data a CSV ready for import into the table.

import sys
import csv
from colormath.color_objects import sRGBColor, XYZColor
from colormath.color_conversions import convert_color

outputFieldNames = [
    'color_name',
    'rgb',
    'red',
    'green',
    'blue',
    'hue_degree',
    'saturation_percent',
    'lightness_percent',
    'hue',
    'saturation',
    'brightness',
    'xy',
    'hue_xy',
    'livingcolors_xy'
]


sourceFileName = 'html_colors_source_data.csv'
outputFileName = 'html_colors_data.csv'

sourceFile = open(sourceFileName)
csvReader = csv.DictReader(sourceFile)

outputFile = open(outputFileName, 'w')
csvWriter = csv.DictWriter(outputFile, outputFieldNames)
csvWriter.writeheader()

for row in csvReader:

    # wrap the color_name in tics and double tic any ticks in the string
    row['color_name'] = "'%s'" % row['color_name'].replace("'", "''")

    # wrap the Hex value in tics:
    row['rgb'] = "'%s'" % row['rgb']

    ## the other columns from the sourceFile will be kept as is.

    ### Computed values:

    # convert "hue_degree" to "hue" - integer between 0 and 65535:
    row['hue'] = int((float(row['hue_degree']) / 360.0) * 65535)

    # convert "saturation_percent" to "saturation" -  integer between 0 and 254
    row['saturation'] = int((float(row['saturation_percent']) / 100.0) * 254)

    # convert "lightness_percent" to "brightness" - integer between 1 and 254
    row['brightness'] = int((float(row['lightness_percent']) / 100.0) * 253) + 1

    ###
    ## compute the XY values:

    rgbColor = sRGBColor(float(row['red']), float(row['green']), float(row['blue']), is_upscaled=True)
    xyzColor = convert_color(rgbColor, XYZColor)

    X = xyzColor.xyz_x
    Y = xyzColor.xyz_y
    Z = xyzColor.xyz_z

    if X + Y + Z:

        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)

    else:

       x = 0
       y = 0

    row['xy'] = "{%f,%f}" % (x, y)


    # Gamma Correction values found here:
    # https://github.com/PhilipsHue/PhilipsHueSDK-iOS-OSX/blob/master/ApplicationDesignNotes/RGB%20to%20xy%20Color%20conversion.md

    # Gamma Correction for Hue bulbs 

    # simple linear conversion: 
    gRed   = ((0.674 - 0.322) / 255) * float(row['red']) + 0.322
    gGreen = ((0.408 - 0.517) / 255) * float(row['green']) + 0.408
    gBlue  = ((0.168 - 0.041) / 255) * float(row['blue']) + 0.041

    rgbColor = sRGBColor(gRed, gGreen, gBlue)
    xyzColor = convert_color(rgbColor, XYZColor)

    X = xyzColor.xyz_x
    Y = xyzColor.xyz_y
    Z = xyzColor.xyz_z

    if (X + Y + Z):

        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)

    else:
 
        x = 0
        y = 0

    row['hue_xy'] = "{%f,%f}" % (x, y)

    # Gamma Correction for Living Color, Aura, and Iris bulbs:
    gRed   = ((0.703 - 0.296) / 255) * float(row['red']) + 0.296
    gGreen = ((0.709 - 0.214) / 255) * float(row['green']) + 0.214
    gBlue  = ((0.139 - 0.081) / 255) * float(row['blue']) + 0.081

    rgbColor = sRGBColor(gRed, gGreen, gBlue, is_upscaled=True)
    xyzColor = convert_color(rgbColor, XYZColor)

    X = xyzColor.xyz_x
    Y = xyzColor.xyz_y
    Z = xyzColor.xyz_z

    if (X + Y + Z):

        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)

    else:

        x = 0
        y = 0

    row['livingcolors_xy'] = "{%f,%f}" % (x, y)

    csvWriter.writerow(row)

sourceFile.close()
outputFile.close()

