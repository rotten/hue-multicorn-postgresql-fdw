create extension multicorn;

-----------------------------------------------------------------
-- Lights:

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

-----------------------------------------------------------------
-- Config:


create server myhueconfig foreign data wrapper multicorn options
    (wrapper 'hue_fdw.HueConfigFDW.HueConfigFDW',
     bridge '192.168.200.118',
     username 'postgreshue')
;

create foreign table myconfig (
    name               varchar,
    software_version   varchar,
    software_update    json,
    api_version        varchar,
    --
    link_button        boolean,
    zigbee_channel     integer,
    --
    UTC                timestamp,
    timezone           varchar,
    local_time         timestamp (6) with timezone,
    --
    portal_state       json,
    portal_connection  varchar,
    portal_services    boolean,
    --
    dhcp               boolean,
    mac                macaddr,
    ip_address         inet,
    netmask            varchar,
    gateway            inet,
    proxy_address      varchar,
    proxy_port         integer,
    --
    whitelist          json
    --
) server myhueconfig
;


-----------------------------------------------------------------
-- Scenes:


-----------------------------------------------------------------
-- Sensors:

