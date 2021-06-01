# -*- coding: utf-8 -*-
"""
Created on Wed May 26 13:05:15 2021

@author: nm184423
"""
################################################################################################
## AUTHOR:  R. Abram Beyer
## DESCRIPTION:  Helpers file which contains bulk of functions used in
##               the CMS Star Rating HCAHPS download script.

##  This file gathers the Hospital General Information.csv file from the CMS
##  archive page.  Then gathers the HCAHPS - Hospital.csv files.
##  Then left joins both datasets together and returns the results as a csv file.


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

#Import necessary packages

#for controlling the browser.
#Using selenium for webscraping in order to generate javascript-generate webpage
#elements.
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
#for working with zipped files
import zipfile
#for putting data into easy dataframe format
import pandas as pd
#for requesting url data.  Get requests.
import requests
#for wrangling web data.
from bs4 import BeautifulSoup
#For working with urls
from urllib.parse import urljoin
#for working with operating systems, files, folders, etc.
import os
#for working with the zipped file from url
import io

# offers classes representing filesystem paths.  Used to help navigte project folder
# to locate the driver file.
import pathlib
#used to pause a bit after loading the webpage to ensure all javascript elements render
import time
#convert year string to datetime year
from datetime import datetime
################################################################################################


#Open Chrome browser.
#First set options, find path to the selenium chrome driver, initialize Chrome browser.
def create_browser_object():
    
    #open webpage with selenium in order to properly open javascript-generated page.
    #set selenium options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    current_path = pathlib.Path(__file__).parent.absolute()
    #driver_path = r'drivers\msedgedriver.exe'
    driver_path = r'drivers\chromedriver.exe'

    #initiate selenium Chrome browser
    browser_obj = webdriver.Chrome(options=options,executable_path = os.path.abspath(os.path.join(current_path,driver_path)))

    return(browser_obj)


#Wait for the page to load by checking for the H2 header element on the page.
#Once this is loaded, then we can be sure the javascript has finished generating
#the page elements.
def wait_for_archive_page_to_load(browser):
    
    my_root_element_xpath = '//*[@id="root"]/div/div/main/div[2]/div/div/div[2]/header/div[1]/div/h1'
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

    try:
        root_element = WebDriverWait(browser, 120,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, my_root_element_xpath)))
    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        print("Page loaded")
    time.sleep(2)   
    return(browser)


#Takes Chrome browser object and opens CMS' archive file page. 
#Then returns the browser object.
def open_cms_archive_path(browser):
    #set url variable to open with selenium  (url path to CMS archived zip files)
    url = r'https://data.cms.gov/provider-data/archived-data/hospitals'
    
    #open the url in Chrome
    browser.get(url)
    
    browser.maximize_window()
    
    return(browser)


#extract browser page source code, and parse with beautifulsoup into
#soup object for easy exploration.
def get_page_soup(browser):
    time.sleep(3)
    #download the page source (html)
    cms_page = browser.page_source
    
    #use bs4 (beautifulsoup) to parse the page source more easily
    soup_var = BeautifulSoup(cms_page, 'html.parser')
    
    return(soup_var)


#finds all zip file hrefs for all cms archive site
#that contain the phrase 'hos_revised' and end with .zip.
#returns just the hrefs (links)
def gather_cms_archive_hos_revised_flatfiles_zip(bs4_soup_obj):
    
    #gather all revised hospital files zipped folders
    #iterate over 'a' tags to get all hrefs ending in .zip and including the phrase 'hos_revised'
    revised_file_zips = [x['href'] for x in bs4_soup_obj.find_all('a', href=True) if x.text.endswith('.zip') and 'hos_revised' in x.text]
    
    return(revised_file_zips)


def gather_revised_zip_href_years_and_months(revised_file_zips):
    #Each year CMS has multiple revised files.  We only want the most recent revision for each year.
    #iterate over all the zip file names, create a list of all release months.  Take the max month for each year.
    #First, for each year, create a list of all months.
    #returns a dictionary.  Keys = years.  Values = list of revision months.
    year_dict = {}
    for i, item in enumerate(revised_file_zips):
        #item.split('_')[-1].split('.')[0], item.split('_')[-2])
        if item.split('_')[-1].split('.')[0] not in year_dict.keys():
            year_dict[item.split('_')[-1].split('.')[0]] = []
            year_dict[item.split('_')[-1].split('.')[0]].append(int(item.split('_')[-2]))
        else:
            year_dict[item.split('_')[-1].split('.')[0]].append(int(item.split('_')[-2]))

    return(year_dict)


def select_most_recent_revised_flatfile(href_list,revision_year_dictionary):
    #For each file release year, find and store the max month zip file url
    max_revised_file_zips = {}
    for i, item in enumerate(revision_year_dictionary.keys()):
        for j, item2 in enumerate(href_list):
            if item in item2 and str(max(revision_year_dictionary[item])) in item2:
                max_revised_file_zips[item] = item2
                
    return(max_revised_file_zips)




def find_min_max_revised_file_years(max_year_dictionary):
    
    #iterate over file years and find the min/max years.
    #exclude 2015 and 2014 because those years only have
    #incomplete files that include hospital lookup info. but not overall star rating.
    file_years = [datetime.strptime(x, '%Y').year for x in max_year_dictionary.keys() if datetime.strptime(x, '%Y').year not in [2015,2014]]
    
    max_year = max(file_years)
    min_year = min(file_years)
    
    return(min_year,max_year)




'''
def open_and_union_cms_revised_flatfiles(max_revised_file_zips):
    
    #iterate over all the zip file urls, open the Hospital General Information csv file.  
    #Add a new column to identify the data year.
    #Some years use slightly different columns names.  Rename columns so all file columns match.
    
    #initiate an empty list to hold all the final dataframes 
    #so we can easily union them together at the end.
    dataset_list = []
    #create base url variable
    cms_url = r'https://data.cms.gov'
    #loop over the year dictionary keys and open the zip file, then open the Hospital General Information csv file
    #within the zipped folder.
    for i, item in enumerate(max_revised_file_zips.keys()):
        #create the full url path to the zipped folder
        zipurl = urljoin(cms_url, max_revised_file_zips[item])
        r = requests.get(zipurl)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        #open the csv file.  Some older files use ISO 8859-1 encoding, newer ones use utf-8
        try:
            df = pd.read_csv(z.open('Hospital General Information.csv'), encoding='utf-8', dtype={ \
                0:'string'})
        except:
            df = pd.read_csv(z.open('Hospital General Information.csv'),encoding='ISO 8859-1', dtype={ \
                0:'string'})
            
        #create 'Year' column based on the year in the file name    
        df['Year'] = item
        
        #Renaming columns so all dataframe columns match.
        if 'Provider ID' in df.columns:
            
            df = df.rename(columns={'Provider ID': 'Facility ID'})
        
        if 'Hospital Name' in df.columns:
            
            df = df.rename(columns={'Hospital Name': 'Facility Name'})
        
        if 'Meets criteria for meaningful use of EHRs' in df.columns:
            
            df = df.rename(columns={'Meets criteria for meaningful use of EHRs': 'Meets criteria for promoting interoperability of EHRs'})
            
        
        #Year 2015 & 2014 only include hospital location/demographic data which is not useful.  Excluding those years.
        if item not in ['2015','2014']:
            dataset_list.append(df)
            
    #union all dataframes together
    final_df = pd.concat(dataset_list)
    
    return(final_df)

'''


#function reads either the Hospital General Information csv or 
#HCAHPS - Hospital csv given a zipfile zipped object containing
#csv files.

#This only works with CMS archived revised flatfile zipped folders.

def read_cms_csv(zipped_obj,file_name = 'Hospital General Information.csv'):
    
    if file_name == 'Hospital General Information.csv':
        
        try:
            hgi_df = pd.read_csv(zipped_obj.open('Hospital General Information.csv'), encoding='utf-8', dtype={ \
                0:'string'})
            
            return(hgi_df)
        except:
            hgi_df = pd.read_csv(zipped_obj.open('Hospital General Information.csv'), encoding='ISO 8859-1', dtype={ \
                0:'string'})
            
            return(hgi_df)
            
    else:
        
        try:
            hcahps_df = pd.read_csv(zipped_obj.open('HCAHPS - Hospital.csv'), encoding='utf-8', dtype={ \
                0:'string', \
                12:'string', \
                14:'string', \
                17:'string', \
                19:'string'})
            
            return(hcahps_df)
        
        except:
        
            hcahps_df = pd.read_csv(zipped_obj.open('HCAHPS - Hospital.csv'), encoding='ISO 8859-1', dtype={ \
                0:'string', \
                12:'string', \
                14:'string', \
                17:'string', \
                19:'string'})
            
            return(hcahps_df)



#depending on the CMS archive file, rename some columns to make sure
#the union works across all years.

def rename_columns(df, file_name = 'Hospital General Information.csv'):
    
    if file_name == 'Hospital General Information.csv':
        
        hgi_df = df
        
        #Renaming columns so all dataframe columns match.
        if 'Provider ID' in hgi_df.columns:

            hgi_df = hgi_df.rename(columns={'Provider ID': 'Facility ID'})

        if 'Hospital Name' in hgi_df.columns:

            hgi_df = hgi_df.rename(columns={'Hospital Name': 'Facility Name'})

        if 'Meets criteria for meaningful use of EHRs' in hgi_df.columns:

            hgi_df = hgi_df.rename(columns={'Meets criteria for meaningful use of EHRs': 'Meets criteria for promoting interoperability of EHRs'})

        return(hgi_df)
        
    else:
        
        hcahps_df = df
        
        #Renaming columns so all dataframe columns match.
        if 'Provider ID' in hcahps_df.columns:

            hcahps_df = hcahps_df.rename(columns={'Provider ID': 'Facility ID'})

        if 'Hospital Name' in hcahps_df.columns:

            hcahps_df = hcahps_df.rename(columns={'Hospital Name': 'Facility Name'})

        if 'Measure Start Date' in hcahps_df.columns:

            hcahps_df = hcahps_df.rename(columns={'Measure Start Date': 'Start Date'})

        if 'Measure End Date' in hcahps_df.columns:

            hcahps_df = hcahps_df.rename(columns={'Measure End Date': 'End Date'})
        
        return(hcahps_df)




#create a function that handles either the hospital general information csv or the hcahps - hospital file


def open_and_union_cms_revised_flatfiles(max_revised_file_zips, file = 'Hospital General Information.csv'):
    
    #iterate over all the zip file urls, open the Hospital General Information csv file.  
    #Add a new column to identify the data year.
    #Some years use slightly different columns names.  Rename columns so all file columns match.

    #initiate an empty list to hold all the final dataframes 
    #so we can easily union them together at the end.
    dataset_list = []
    #create base url variable
    cms_url = r'https://data.cms.gov'
    #loop over the year dictionary keys and open the zip file, then open the Hospital General Information csv or the hcahps - hospital.csv
    # file depending on the parameter
    #within the zipped folder.
    for i, item in enumerate(max_revised_file_zips.keys()):
        #create the full url path to the zipped folder
        zipurl = urljoin(cms_url, max_revised_file_zips[item])
        r = requests.get(zipurl)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        #read the csv file from the zipped folder
        new_df = read_cms_csv(z,file)
        
        
        #create 'Year' column based on the year in the file name    
        new_df['Year'] = item
        new_df['Year'] = new_df['Year'].astype('str').str.strip()
        
        #name columns so they match across all years
        last_df = rename_columns(new_df,file)


        #print(df.columns)
        #Year 2015 & 2014 only include hospital location/demographic data which is not useful.  Excluding those years.
        if item not in ['2015','2014']:
            dataset_list.append(last_df)

    #union all dataframes together
    final_df = pd.concat(dataset_list)
    
    return(final_df)
    



def write_cms_cvs_files_by_year(output_merged_df,list_of_data_years):
    
    #iterate over each dataset year, subset the data then output to csv file with unique dataset name.
    
    for i, year in enumerate(list_of_data_years):
        
        one_year_output_merged_df = output_merged_df[output_merged_df['Year'] == year]
        print("final df shape(",str(year),"):",one_year_output_merged_df.shape)
        one_year_output_merged_df.to_csv("data/cms_hospital_patient_satisfaction_and_overall_star" + str(year) + '.csv',index=False)



def main_cms_revised_flatfile_downloader_hcahps():
    
    #initialize Chrome
    browser_var = create_browser_object()
    
    #open CMS archive page
    browser_var2 = open_cms_archive_path(browser_var)
    
    
    browser_var2 = wait_for_archive_page_to_load(browser_var2)
    
    #extract browser page source code, and parse with beautifulsoup into
    #soup object for easy exploration.
    bs4_soup_var = get_page_soup(browser_var2)
    
    
    #finds all zip file hrefs for all cms archive site
    #that contain the phrase 'hos_revised' and end with .zip.
    #returns just the hrefs (links)
    revised_zip_href_list = gather_cms_archive_hos_revised_flatfiles_zip(bs4_soup_var)
    
    #print(revised_zip_href_list)
    
    year_dict = gather_revised_zip_href_years_and_months(revised_zip_href_list)
    
    
    #loops over revised flatfile hrefs and finds the most recent one.
    max_year_revision_dict = select_most_recent_revised_flatfile(revised_zip_href_list,year_dict)
    
    #figure out what the min and max years are for the archive webpage.
    min_file_year, max_file_year = find_min_max_revised_file_years(max_year_revision_dict)
    
    #read the hospital general information csv file into pandas dataframe
    #union all dataframes together except 2015 and 2014 because those years do not include
    #an overall cms star rating.
    
    
    csv_df_list = []
    for i, csv_file_name in enumerate(['Hospital General Information.csv','HCAHPS - Hospital.csv']):
        
        final_csv_file_df = open_and_union_cms_revised_flatfiles(max_year_revision_dict,csv_file_name)
        
        print(csv_file_name,':', final_csv_file_df.shape)
        csv_df_list.append(final_csv_file_df)
    
    
    final_df_hgi = csv_df_list[0]
    final_df_hcahps = csv_df_list[1]
    
    #make sure each dataset's facility id is a string.
    final_df_hgi['Facility ID'] = final_df_hgi['Facility ID'].astype(str).str.strip().str.upper()
    final_df_hcahps['Facility ID'] = final_df_hcahps['Facility ID'].astype(str).str.strip().str.upper()
    
    #remove hospital general information contact info other than facility id 
    #because that exists in the hcahps dataset
    final_df_hgi_slim = final_df_hgi[['Facility ID', 'Hospital Type', 'Hospital Ownership',
           'Emergency Services',
           'Meets criteria for promoting interoperability of EHRs',
           'Hospital overall rating', 'Hospital overall rating footnote',
           'Mortality national comparison',
           'Mortality national comparison footnote',
           'Safety of care national comparison',
           'Safety of care national comparison footnote',
           'Readmission national comparison',
           'Readmission national comparison footnote',
           'Patient experience national comparison',
           'Patient experience national comparison footnote',
           'Effectiveness of care national comparison',
           'Effectiveness of care national comparison footnote',
           'Timeliness of care national comparison',
           'Timeliness of care national comparison footnote',
           'Efficient use of medical imaging national comparison',
           'Efficient use of medical imaging national comparison footnote',
           'Year']]
    
    #join the datasets.  Use hcahps dataset as left dataframe in order to only keep facilities with hcahps results.
    result_df = pd.merge(final_df_hcahps, final_df_hgi_slim, on=["Facility ID", "Year"])
    
    print('All Years Combined:',result_df.shape)
    
    #write unioned dataframe with all years to excel file in the data folder.
    #takes a dataframe with a column name 'Year' and writes a 
    #csv file for each data year row as a csv to the data folder.
    write_cms_cvs_files_by_year(result_df,result_df['Year'].unique())


    #close the browser
    browser_var2.close()
    
    
    
    