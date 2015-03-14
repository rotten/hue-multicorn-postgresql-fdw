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
    swversion          varchar,
    swupdate           json,
    api_version:       varchar,
    --
    linkbutton         boolean,
    zigbeechannel      integer,
    --
    UTC                timestamp,
    timezone:          varchar,
    localtime:         timestamp with timezone,
    --
    portalstate        json,
    portalconnection   varchar,
    portalservices     boolean,
    --
    dhcp               boolean,
    mac                macaddr,
    ipaddress          inet,
    netmask            varchar,
    gateway            inet,
    proxyaddress       varchar,
    proxyport          integer,
    --
    whitelist          json
    --
) server myhueconfig
;


-----------------------------------------------------------------
-- Scenes:


-----------------------------------------------------------------
-- Sensors:

