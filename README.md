# hue-multicorn-postgresql-fdw
## Multicorn based PostgreSQL Foreign Data Wrapper for Phillips Hue Lighting Systems

We've implemented 3 of the Philips Hue Endpoints to date:
*  Lights
*  Sensors
*  Config

This Foreign Data Wrapper was initially released as a companion to rotten's PG CONF US 2015 talk:  "**Implementing the Database Of Things with Foreign Data Wrappers**".  The slides and specific examples from this talk can be found in the */extras* folder in this repo.

###### How To Use This Software:

1.  You need to register the FDW with your Hue Bridge.  Functionality to do this is not built-in to this repo at this time.  Follow the instructions at http://www.developers.meethue.com/documentation/getting-started to set up a user.
  * The examples in this repo are based on having a user called *postgreshue* in the bridge.  You can use any user name you'd like - just remember to set the correct user when you run "create server"
  * When you set up your bridge make note of the IP Address (or hostname if you put it on DNS).  You will need this to be able to connect.  If you have trouble finding the IP address of your bridge, rotten has had luck using Miranda - https://code.google.com/p/miranda-upnp/ , and also just using *ping 255.255.255.255*
  * You may need to update the software on your bridge.  You can use the default Hue app to initialize this.  You can also PUT an update command.  There are examples of other PUT commands in the *api_experiments.py* script in the extra folder.  Documentation for triggering an update is here:  http://www.developers.meethue.com/documentation/software-update  -- it requires you to register to view the documentation though.
2.  Next you'll need Multicorn installed on your database server.  The easiest way to do this is to use pgxn.
  * `pgxn install multicorn`
3.  You'll need to download this repo:
  * `git clone https://github.com/rotten/hue-multicorn-postgresql-fdw.git`
4.  You may also need to install the python *requests* library:
  * `pip install requests`
5.  And install its code into your database server as well:
  1. `cd hue-multicorn-postgresql-fdw`
  2. `python ./setup.py install`
6.  Then, in your database create the multicorn extension:
  * `create extension multicorn;`
7.  You will need to create a **server** and a **foreign table**.  The command syntax to do so are in the *ddl* folder of this repo.
  * Unlike normal Foreign Tables, this code was developed very specifically for the table layout in the DDL file.  If you'd prefer other column names you can construct a view over the table.  There is an example of such a view in the *setup_sensors.ddl* file.
8.  If you'd like to try using color names instead of xy values, check out the *html_colors_table.ddl* file in the *colors* folder for an example of setting up and using a color reference table.  If you want to experiment with the *compute_html_color_columns.py* routine, you may need to install the python *colormath* library:
  * `pip install colormath`
  * Note that Browns and Greens are pretty disappointing with these bulbs.  You can see the color limitations on the Core concepts page - http://www.developers.meethue.com/documentation/core-concepts .  


That's it!  You should be able to use your lights as if they were data.  

---
### Troubleshooting tips

* Set `log_min_messages = debug1` in your *postgresql.conf* to see more verbose log messages (assuming you have `logging_collector=on` !).
  * You can send messages to your postgresql log files by adding `log_to_postgres("some message", DEBUG)` to the code.
* If you update the Python code, after you re-run `python setup.py ./install` you do not have to restart your database server.  You do have to log out of your database session and back in though to pick up the changes however.






