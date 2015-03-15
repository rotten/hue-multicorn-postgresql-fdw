-- Example DDL for setting up the Sensors FDW
-----------------------------------------------------------------

create extension multicorn;

create server myhuesensors foreign data wrapper multicorn options 
    (wrapper 'hue_fdw.HueSensorsFDW.HueSensorsFDW', 
     bridge '192.168.200.118', 
     userName 'postgreshue')
;


-- config & state are different for different types of sensors:
-- http://www.developers.meethue.com/documentation/supported-sensors
--
-- So we leave them as json here instead of flattening them out into nice columns
-- They could be flattened into norma columns with a view for each sensor type (see below for an example).
create foreign table mysensors (
   sensor_id           smallint, 
   sensor_type         varchar,
   sensor_name         varchar,
   manufacturer        varchar,
   model_id            varchar,
   software_version    varchar,
   unique_id           varchar,
   config              json,
   state               json 
   
) server myhuesensors
;


create view my_daylight_sensors_view
as select

   sensor_id,
   sensor_name,
   manufacturer,
   model_id,
   software_version,
   config->'on'            as "is_on",
   config->'lat'           as  latitude,
   config->'long'          as  longitude,
   config->'sunriseoffset' as  sunrise_offset,
   config->'sunsetoffset'  as  sunset_offset,
   state->'daylight'       as  daylight,
   state->'lastupdated'    as  last_update

from
   mysensors 
where 
   sensor_type = 'Daylight'
;


