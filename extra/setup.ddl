create extension multicorn;

create server myhuelights foreign data wrapper multicorn options 
    (wrapper 'hue_fdw.HueLightsFDW.HueLightsFDW', 
     bridge '192.168.200.118', 
     username 'postgreshue')
;

create foreign table mylights (
   light_id           smallint,
   software_version   varchar,
   unique_id          varchar,
   light_type         varchar,
   model_id           varchar,
   is_on              boolean,
   reachable          boolean,
   xy                 numeric[],
   hue                integer,
   brightness         integer,
   saturation         integer,
   color_temperature  integer,
   color_mode         varchar,
   effect             varchar,
   alert              varchar,
   pointsymbol        json
) server myhuelights
;


