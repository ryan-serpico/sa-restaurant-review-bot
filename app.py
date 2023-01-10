import re
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
    # all_data.to_excel('playground/sample.xlsx', index=False)

    return all_data


def getInspectionDetails(inspections):
    # tenWorstInspections = inspections.head(10)
    worstInspection = inspections.head(1)
    # worstInspection = inspections.iloc[2]
    print(worstInspection)
    worstInspectionLink = worstInspection['Link'].values[0]
    
    response = requests.get(worstInspectionLink)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    inspection_date = soup.find_all('td')[3].get_text().strip()[5:]
    restaurant_name = soup.find_all('td')[13].get_text().strip()[19:].title()
    repeat_violations = soup.find_all('td')[15].find('strong').get_text().strip()[-1]
    score = soup.find_all('td')[16].get_text().strip()
    address = soup.find_all('td')[17].get_text().strip()[18:].replace('  ', ' ')

    # Find all the table elements on the page that have a class of "padL"
    # This will give us the table elements that contain the inspection details.
    table_elements = soup.find_all('table', class_='padL')

    # Loop through each table element and add the text from each td element to a list.
    # We will use this list to create a dataframe.
    data = []
    for table_element in table_elements:
        for td in table_element.find_all('td'):
            # If the td element text contains "AT INSPECTION:" add it to the list.
            if "AT INSPECTION:" in td.get_text():
                keyword = "AT INSPECTION:"
                before_keyword, OG_keyword, after_keyword = td.get_text().partition(keyword)
                # Remove any newlines and extra spaces from the text.
                after_keyword = after_keyword.replace('\n', '').strip()

                # Change to sentence case.
                after_keyword = after_keyword[0].upper() + after_keyword[1:].lower()
                data.append(after_keyword)
            elif "observed" in td.get_text().lower() and "conditions observed and noted below" not in td.get_text().lower():
                keyword = "observed"
                before_keyword, OG_keyword, after_keyword = td.get_text().partition(keyword)
                # Remove any newlines and extra spaces from the text.
                after_keyword = after_keyword.replace('\n', '').strip()

                # Change to sentence case.
                after_keyword = after_keyword[0].upper() + after_keyword[1:].lower()
                data.append(after_keyword)
            else:
                continue
        

    # Create a dataframe from the list of data.
    df = pd.DataFrame(data)
    print(df)
    df.to_csv('playground/at_inspection_sample.csv', index=False)


    
#     print(f"""Restaurant: {restaurant_name}
# Address: {address}
# Inspection Date: {inspection_date}
# Score: {score}
# Repeat Violations: {repeat_violations}
# """)

# TODO: Remove sampleData once you're done testing. Then replace the argument in getInspectionDetails with combineWeeklyCollections().
sampleData = pd.read_excel('playground/sample.xlsx')
getInspectionDetails(sampleData)