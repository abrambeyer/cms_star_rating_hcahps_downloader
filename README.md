# cms_star_rating_hcahps_downloader
This project collects and wrangles all archived HCAHPS - Hospital.csv and Hospital General Information.csv files from cms.gov (Centers for Medicare and Medicaid Services). *[archive page](https://data.cms.gov/provider-data/archived-data/hospitals)*  The resulting datasets will be a left join of the general information and hcahps data so we can have a comparison of overall cms star rating and hcahps survey results.  The file creates one csv file for each year on the archive site excluding 2014 and 2015.

The purpose of this dataset is to help analysts explore the relationship between overall cms star rating and hcahps (patient satisfaction).  *[HCAHPS Overview](https://www.cms.gov/Medicare/Quality-Initiatives-Patient-Assessment-Instruments/HospitalQualityInits/HospitalHCAHPS).*    

The data is made available by *[CMS.gov](https://www.cms.gov/Medicare/Quality-Initiatives-Patient-Assessment-Instruments/HospitalQualityInits/HospitalCompare)*

Hospital Compare provides data on over 4,000 Medicare-certified hospitals, including acute care hospitals, critical access hospitals (CAHs), children’s hospitals, Veterans Health Administration (VHA) Medical Centers, and hospital outpatient departments.

* NOTE: *  The final output is writtent to csv file.  However, the hospital's facility ID should be read in as a string due to some facilities having a leading zero in their facility ID.


# Python Project Folder: cms_star_rating_hcahps_gather

## What this project does:
    
1. Opens CMS archive data site
2. Collects all revised flatfile zipped folders
3. Selects the most recent zipped folder for each year on the page
4. Reads the Hospital General Information.csv file within each year's zipped folder into pandas dataframe.
5. Creates new year column for each file
6. Renames some columns so all files are aligned
7. Unions all file dataframes together
8. Repeats the above steps for the HCAHPS - Hospital.csv files.
9. Cleans up columns names and data types.
10. Left joins the Hospital General Information, Overall CMS Star to the HCAHPS scores 
11. Writes final dataframe for each year to csv file.


* Includes 2 main python scripts:
  * cms_star_rating_hcahps_downloader.py  (runs the main function)
  * helpers.py   (holds all necessary functions and imports necessary packages)

* Final Output:
  Should output csv file for each data release year to the data folder which includes all revised flatfile "Hospital General Informationc.csv" file data for every year on 
  the *[archive page](https://data.cms.gov/provider-data/archived-data/hospitals)* excluding data for years 2015 and 2014.  2015 and 2014 are excluded because their
  Hospital General Information files only include hospital contact information rather than CMS Star Rating.


* Attribution:

  All Hospital Compare websites are publically accessible. As works of the U.S. government, Hospital Compare data are in the public domain and permission is not required to  reuse them. An attribution to the agency as the source is appreciated. Your materials, however, should not give the false impression of government endorsement of your commercial products or services.
