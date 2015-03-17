--
-- This handy table converts HTML color names to RGB, Hue-Sat-Bri, and XY.
-- It is based off the table here:  http://www.colorhexa.com/color-names
-- 
-- The XY values were computed using python's colormath module after being gamma corrected for the bulb type.
-- The script that was used can be found in this directory:  compute_html_color_columns.py
--
-- Your milage may vary.  With the bulbs we were initially using for testing, the non-gamma corrected colors looked the best.
-- Browns and greens didn't work as well as reds and blues.
-- 

create table html_colors (

    color_name           varchar primary key,
    rgb                  varchar,
    red                  smallint,
    green                smallint,
    blue                 smallint,
    hue_degree           numeric,
    saturation_percent   numeric,
    lightness_percent    numeric,
    hue                  integer,
    saturation           smallint,
    brightness           smallint,
    xy                   numeric[], -- not gamma corrected
    hue_xy               numeric[], -- rgb gamma corrected for Hue bulbs
    livingcolors_xy      numeric[]  -- rgb gamma corrected for Living Color, Aurua, and Iris

);

comment on table html_colors is 
    'HTML Color Conversion Reference - Convenience table included with the Hue FDW code - https://github.com/rotten/hue-multicorn-postgresql-fdw'
;

-- you'll need the full path to the csv so your postgres server can find it:
copy html_colors from '/some/path/to/html_colors_data.csv' with CSV HEADER;

--------------------------------------------------------------------------------------------------
-- You can set your lights to these colors by doing:
update mylights
  set
  xy = (select xy from html_colors where color_name = 'crimson red')
where  
   light_id = 1;

-- or

update mylights
  set
  hue = c.hue,
  saturation = c.saturation,
  brightness = c.brightness
from
   (select hue, saturation, brightness from html_colors where color_name = 'crimson') c   
where  
   light_id = 1;

