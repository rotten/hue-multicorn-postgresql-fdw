-- Example DDL for setting up the Config FDW
-----------------------------------------------------------------

create extension multicorn;

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
    local_time         timestamp (6) with time zone,
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

