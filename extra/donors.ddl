create extension "uuid-ossp";

-- simple table of donations:
create table donors (
   id            uuid primary key default uuid_generate_v4(),
   donate_time   timestamp (6) with time zone default now(),
   donor_name    varchar,
   donation      numeric
);

-- function to blink the lights
create or replace function blink_a_light() returns trigger as $blink_it$
    begin
        if NEW.donation < 10.0 then
            -- blink one light once if we get a small donation
            update mylights set alert = 'select' where light_id = 1;
        else
            -- blink all the lights for 30 seconds if we get more then $10.
            update mylights set alert = 'lselect';
        end if;
        return null;
    end;
$blink_it$ LANGUAGE plpgsql;

-- blink whenever we receive a donation:
create trigger donation_received
AFTER insert on donors
    for each row execute procedure blink_a_light();

-------------------------------------------
-- try some donations:
insert into donors
(donor_name, donation)
values
('cheapskate1', 1.00)
;

insert into donors
(donor_name, donation)
values
('cheapskate2', 1.00)
;

insert into donors
(donor_name, donation)
values
('sugar daddy', 20.00)
;

