--
-- This handy table converts HTML color names to RGB, Hue-Sat-Bri, and XY.
-- It is based off the talbe here:  http://www.colorhexa.com/color-names
-- The XY values were computed based on the formulas described here:  
--     https://github.com/PhilipsHue/PhilipsHueSDK-iOS-OSX/blob/master/ApplicationDesignNotes/RGB%20to%20xy%20Color%20conversion.md
--

create table html_colors (

    color_name           varchar,
    color_hex            varchar,
    red                  smallint,
    green                smallint,
    blue                 smallint,
    hue_degree           numeric,
    saturation_percent   smallint,
    lightness_percent    smallint
    hue                  integer,
    saturation           smallint,
    brightness           smallint,
    hue_xy               numeric[],
    livingcolors_xy      numeric[]

);

comment on table html_colors is 
    "HTML Color Conversion Reference - Convenience table included with the Hue FDW code - https://github.com/rotten/hue-multicorn-postgresql-fdw"
;

copy html_colors from 'html_colors_data.csv' with CSV HEADER;

