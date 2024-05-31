#Reading SQL data into python

#Installing the packages
%pip install psycopg2-binary 
%pip install pandas
%pip install matplotlib

#importing libraries and packages
import psycopg2
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

#define the connection parameters from PostgreSQL
db_params = { 
        "dbname" : "dp_world_assg",
        "user" : "postgres",
        "password" : "***********", #use your own password
        "host" : "localhost",
        "port" : "5432"
}

#SQL query to fetch the AIS and port datasets
query1 = "SELECT * FROM ais_2020_01"
query2 = "SELECT * FROM port"

#Connect to the PostgreSQL database and load data into a pandas dataframe
try:
    #Establish the connection
    connection = psycopg2.connect(**db_params)

    #Load the data into pandas df
    ais_df = pd.read_sql_query(query1,connection)
    port_df = pd.read_sql_query(query2, connection)

    #Print the df
    print(port_df)

except Exception as error:
    print(f"Error while connecting to PostgreSQL: {error}")

finally:
    if connection: connection.close()
    print("PostgreSQL connection is closed")


#Now that the data has been read, we move to Step 2 of the assignment, to create a bounding box.

#Create bounding Box
# For creating a bounding  box, we need to determine the center point, which is going to be our Port of Long Beach's coordinates

#Creating a function to extract port_coordinates
def port_coordinates(port_code):
    """
    This function searches the port dataframe and provides us with coordinates for port to be used in bounding box as center point.

    Parameter:
    port_code : It uses port_code as an input.

    Returns:
    It returns longitude and latitude of port.

    """

    port_data = port_df[port_df['port_code']==port_code]

    lat = port_data.iloc[0]['latitude']
    lon = port_data.iloc[0]['longitude']

    return(lat, lon)


def filter_ais_data(port_code, width, height):
    """
    This function filters ais data based on bounding box created to review sample of vessels in Long Beach Port data.

    Parameters:
    port_code : code of Long Beach port to get the coordinates for center point of Long Beach Port 
    width : width to be used in bounding box to filter out vessels beyond a given longitude.
    height : height to be used in bounding box to filter out vessels beyond a given latitude.

    Returns:
    cargo_df : This is the filtered AIS dataset that contains the cargo vessels in Long Beach Port on 1st and 2nd January, 2020.

    """
    
    #Get port coordinates
    lat, lon = port_coordinates(port_code)
    
    if lat is None or lon is None:
        raise ValueError(f"Port code {port_code} not found.")
    
    #Calculate Bounding box
    half_width = width/2
    half_height = height/2
    
    min_lat = lat - half_height
    max_lat = lat + half_height
    min_lon = lon - half_width
    max_lon = lon + half_width
    
    #Filter data based on vesseltype (cargo and tanker vessels have vesseltype code range between 70-89, since it is not mentioned whether to exclude tanker/container ships, I have considered the complete 70-89 range) and height and width of bounding box based on port coordinates.
    
    cargo_df = ais_df[
                (ais_df['vesseltype'] >= 70 ) & (ais_df['vesseltype'] <= 89 ) & (ais_df['lat'] >= min_lat) & (ais_df['lat'] <= max_lat) & (ais_df['lon'] >= min_lon) & (ais_df['lon'] <= max_lon)]
    
    return cargo_df



#Step 3 - Write a function that accepts port_code and outputs a table with two columns. A date-time column and the number of unique vessels within the port at a given block of time.

def num_of_vessels(port_code):
    """
    This function provides the unique count of cargo vessels at different hours of 1st and 2nd January 2020 at Long Beach Port. This function calls filter_ais_data function.

    Parameter:
    port_code : It uses port_code as an input.

    Returns:
    It returns a dataframe with list of date time and the count of unique vessels at each given time point at Long Beach Port.
    """
    
    filter_df = filter_ais_data(port_code, height, width)

    ais_df['basedatetime'] = pd.to_datetime(ais_df['basedatetime'])
    ais_df.dtypes

    ais_df['hourly_date'] = ais_df['basedatetime'].dt.floor('h')

    output_df = pd.DataFrame(ais_df.groupby('hourly_date')['imo'].nunique())

    output_df.reset_index(inplace=True)
    output_df = output_df.rename(columns={'hourly_date' : 'Date_Time', 'imo' : 'Count_of_vessels'})
    
    return output_df

#input parameters for functions
port_code='US LGB' #port_code
height = 0.1       #to determine width of bounding box
width = 0.1        #to determine height of bounding box

result_df = num_of_vessels(port_code)
display(result_df)


#Step 4: Illustrate the demand at various time points

#Plotting number of unique vessels by hour
plt.figure(figsize=(12,6))
plt.plot(result_df['Date_Time'],result_df['Count_of_vessels'],marker ='o', linestyle='-')
plt.xlabel('Datetime')
plt.ylabel('Number of Unique Vessels')
plt.title('Number of Unique Cargo Vessels in the Port of Long Beach')
plt.grid(True)
plt.show()


#Best temporal resolution - Hourly

#Compare demand on 2 days of January
result_df['Date'] = result_df['Date_Time'].dt.date
result_df['Hour'] = result_df['Date_Time'].dt.hour

#Group vessels by Date and Hour to get unique vessel counts
grouped_df = result_df.pivot_table(index='Hour',columns='Date',values='Count_of_vessels',aggfunc='sum')

#Plot the comparison between the 2 dates
grouped_df.plot(figsize=(12,6),marker='o', linestyle='-')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Unique Vessels')
plt.title('Comparison of Unique Cargo Vessels in the Port of Long Beach on 1st and 2nd January')
plt.grid(True)
plt.legend(title='Date')
plt.show()

#Check the variance in demand between January 1st and January 2nd
variance = grouped_df.var()
print("Variance in demand:")
print(variance)