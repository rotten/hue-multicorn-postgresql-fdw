update mylights
  set 
  is_on = true,
  brightness = 255,
  xy = (select xy from html_colors where color_name = 'rich carmine')
;

select pg_sleep(3);

update mylights
  set
  xy = (select xy from html_colors where color_name = 'screamin green')
where
   light_id = 1;

update mylights
  set
  xy = (select xy from html_colors where color_name = 'indigo')
where
   light_id = 2;

update mylights
  set
  xy = (select xy from html_colors where color_name = 'orange red')
where
  light_id = 3;

select pg_sleep(3);

update mylights
  set
  alert='lselect'
where
   light_id = 1;

select pg_sleep(2);

update mylights
  set
  alert='lselect'
where
   light_id = 2;

select pg_sleep(2);

update mylights
  set
  alert='lselect'
where
   light_id = 3;

select pg_sleep(3);

update mylights
  set
  effect='colorloop',
  alert='lselect'
;

select pg_sleep(30);

update mylights
  set
  is_on = false
;


