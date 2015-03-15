-- Example DDL for setting up the Lights FDW
--------------------------------------------

create extension multicorn;

create server myhuelights foreign data wrapper multicorn options 
    (wrapper 'hue_fdw.HueLightsFDW.HueLightsFDW', 
     bridge '192.168.200.118', 
     userName 'postgreshue',
     transitionTime '1')
;

create foreign table mylights (
   light_id           smallint,
   software_version   varchar,
   unique_id          varchar,
   light_type         varchar,
   model_id           varchar,
   reachable          boolean,
   -- mutable:
   is_on              boolean,
   xy                 numeric[],
   hue                integer,
   brightness         integer,
   saturation         integer,
   color_temperature  integer,
   color_mode         varchar,
   effect             varchar,
   alert              varchar,
   -- reserved for future api features:
   pointsymbol        json
   --
) server myhuelights
;

