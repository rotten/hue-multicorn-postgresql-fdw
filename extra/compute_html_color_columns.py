#!/usr/bin/env python

## Read in the html_colors_source_data.csv file.
## Compute the additional columns we need for the HTML table.
## Output data a CSV ready for import into the table.

import sys
import csv

outputFieldNames = [
    'color_name',
    'color_hex',
    'red',
    'green',
    'blue',
    'hue_degree',
    'saturation_percent',
    'lightness_percent',
    'hue',
    'saturation',
    'brightness',
    'hue_xy',
    'livingcolors_xy'
]


sourceFileName = 'html_colors_source_data.csv'
outputFileName = 'html_colors_data.csv'

sourceFile = open(sourceFileName)
csvReader = csv.DictReader(csvFile)

outputFile = open(outputFileName, 'w')
csvWriter = csv.DictWriter(csvFile, outputFieldNames)

for row in csvReader:

    # convert "hue_degree" to "hue" - integer between 0 and 360:
    row['hue'] = int((row['hue_degree'] / 360.0) * 65535)

    # convert "saturation_percent" to "saturation" -  integer between 0 and 254
    row['saturation'] = int((row['saturation_percent'] / 100.0) * 254)

    # convert "lightness_percent" to "brightness" - integer between 1 and 254
    row['brightness'] = int((row['lightness_percent'] / 100.0) * 253) + 1

    ## compute the XY values:

    #gamma correct the Red
    if (row['red'] > 0.04045):
        gRed = pow((red   + 0.055) / (1.0 + 0.055), 2.4) 
    else:
        gRed = (red   / 12.92)

    float g = (green > 0.04045f) ? pow((green + 0.055f) / (1.0f + 0.055f), 2.4f) : (green / 12.92f);
    float b = (blue  > 0.04045f) ? pow((blue  + 0.055f) / (1.0f + 0.055f), 2.4f) : (blue  / 12.92f);
