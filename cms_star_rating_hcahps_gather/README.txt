
Python Scripts:

cms_star_rating_hcahps_downloader.py:

Opens a Chrome browser,
collects the most recent revised flatfile from each archive year available on the page,
opens the 'Hospital General Information.csv' csv file into a pandas dataframe,
and unions all years together while creating a 'Year' column to indicate which year
the data came from.

Does the same thing for each HCAHPS - Hospital.csv file.

Cleans column names and data types, left joins the HCAHPS data to the hospital general information.

outputs a csv file for each data release year.  Data is broken up by each due to large file size.

helpers.py:  Stores all functions necessary for the script.


Output Description:

Final unioned csv file is output to the data folder by default.  One csv file for each data release year.

Output is a csv file.  HOWEVER, Hospital facility IDs (Medicare IDs) can have
a leading zero.  A csv file may accidently truncate the leading zero.  Be sure to read
the csv file facility id column as a string.


What the cms_star_rating_hcahps_downloader.py script does:

opens CMS archive data site
collects all revised flatfile zipped folders
selects the most recent zipped folder for each year on the page
reads the Hospital General Information.csv file within each year's zipped folder into pandas dataframe.
creates new year column for each file
renames some columns so all files are aligned
unions all file dataframes together

 Repeats the above steps for the HCAHPS - Hospital.csv files
 Left joins the resulting dataframes together on Facility ID and Year
 Returns a resulting csv file.
 The final output is one csv file for each year of data due to the large 
 data size.  Instead of just having hcahps or general information, the 
 resutl is a left-joined result set of hcahps and overall cms star and general info.