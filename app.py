from io import BytesIO

import bs4
import openpyxl
import pandas as pd
import requests


# This fuction allows us to read an excel file from a url using openpyxl.
def load_workbook_from_url(url):
    """
    This helper function loads an excel file from a url using openpyxl. This way we don't need to download each file to our machine.
    """
    response = requests.get(url)
    wb = openpyxl.load_workbook(BytesIO(response.content))
    return wb

def getRestaurantReportCollectionLinks(year_id="#lt-229314405-2022"):
    """
    This function returns a list of URLs for weekly collections of restaurant reports. 

    Takes a year_id paramater, which you can find by inspecting the element of the year you want to scrape on the reataurant reports page. The example and default value is for 2022.
    """
    # First we get the html from the restaurant reports page.
    url = 'https://www.sanantonio.gov/Health/News/RestaurantReports'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Then we use the year_id to find the table of restaurant reports for that year.
    table = soup.select(f'{year_id}')

    # Then we get the links for each week of restaurant reports and add them to a list.
    linkList = []
    links = table[0].select('a')
    for link in links:
        absolute_url = 'https://www.sanantonio.gov' + link['href']
        linkList.append(absolute_url)

    return linkList

def combineWeeklyCollections():
    """
    This function combines all the weekly restaurant report collection data into one file, sorts it by total score in ascending order, and saves it as a .xlsx file.
    """
    # Start a counter to keep track of how many files we've processed.
    counter = 0

    # These are the column names we are going to rock with.
    columns = ['ESTABLISHMENT NAME', 'ESTABLISHMENT ADDRESS',
               'INSPECTION DATE',	'SECTOR',	'DISTRICT',	'TOTAL SCORE',	'LINK', 'Link']

    # Create an empty dataframe with the column names we want.
    all_data = pd.DataFrame(columns=columns)

    # Loop through each weekly collection of restaurant reports.
    for collection_link in getRestaurantReportCollectionLinks():
        
        # Add one to the counter and print it our to the terminal.
        counter += 1
        print(f"🐭 Processing file {counter}...")

        df = pd.read_excel(collection_link)

        wb = load_workbook_from_url(collection_link)
        ws = wb[wb.sheetnames[0]]

        # The following code grabs the hyperlinks from the excel file and adds them to a list.
        links = []
        for i in range(2, ws.max_row + 1):
            try:
                links.append(ws.cell(row=i, column=7).hyperlink.target)
            except:
                links.append('missing')
        
        # Now we add the list of hyperlinks to the dataframe.
        df['Link'] = links

        # Now we add the data from this week's collection to the all_data dataframe.
        all_data = pd.concat([all_data, df])
    
    # We drop the 'LINK' column because it's a duplicate of the 'Link' column.
    all_data.drop('LINK', axis=1, inplace=True)

    # We sort the data by total score in ascending order.
    all_data = all_data.sort_values(by=['TOTAL SCORE'])

    # We save the data as a .xlsx file.
    all_data.to_excel('playground/sample.xlsx', index=False)


combineWeeklyCollections()
