# dp_world_assignment

To run this project, the SQL code needs to be executed first, followed by Python code.
The password is private, so please use your own password for running the code. 

The SQL code creates a database to store AIS data and Port coordinates.

The Python code helps in the filtering and analysis of the datasets.

For accessing the data from SQL database, the psycopg2 package needs to be installed and a connection to the SQL database needs to be established in the python environment. This is a part of the code shared.

The illustrations and insights are available in the repo wiki.


An important assumption made in the project is regarding the cargo vessel -

  Since it is not specified that cargo vessels do not include container ships/ tanker ships, all vessels with vesseltype between 70-89 have been considered as tankers and container ships are also cargo vessels, carrying oil and other chemicals.
