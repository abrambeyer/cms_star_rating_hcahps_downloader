# -*- coding: utf-8 -*-
"""
Created on Wed May 26 13:19:22 2021

@author: nm184423
"""
################################################################################################
## AUTHOR:  R. Abram Beyer
## DESCRIPTION:  Core python script which runs all functions necessary to 
##                download and union the most recent cms hospital general information/HCAHPS
##               files for each available year on CMS' archive site.


##What this project does:
    
##opens CMS archive data site
##collects all revised flatfile zipped folders
##selects the most recent zipped folder for each year on the page
##reads the Hospital General Information.csv file within each year's zipped folder into pandas dataframe.
##creates new year column for each file
##renames some columns so all files are aligned
##unions all file dataframes together

## Repeats the above steps for the HCAHPS - Hospital.csv files
## Left joins the resulting dataframes together on Facility ID and Year
## Returns a resulting csv file.
## The final output is one csv file for each year of data due to the large 
## data size.  Instead of just having hcahps or general information, the 
## resutl is a left-joined result set of hcahps and overall cms star and general info.



################################################################################################
## UPDATE LOG:


################################################################################################



import helpers


helpers.main_cms_revised_flatfile_downloader_hcahps()
