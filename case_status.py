'''
Automatic USCIS case status checker by Ohad Michel.
This script collects the current status of all your pending applications,
the current waiting times and number of days remaining for inquiry.
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import datetime
import time
import os

def Get_text(elem):
    '''
    Extracts text from HTML elements
    Input: elem - HTML element
    Output: A string of the content
    '''
    return BeautifulSoup(elem, features='html5lib').text

def format_date(date):
    '''
    Converts dates to datetime lib input format
    Input: date - a date in the form "January 1, 2018"
    Output: a tuple (year,month,day) "(2018,1,1)"
    '''
    month_dict = {'January':1, 'February':2, 'March':3, 'April':4,
                  'May':5, 'June':6, 'July':7, 'August':8, 'September':9,
                  'October':10, 'November':11, 'December':12}

    date_list = date.split()
    year = int(date_list[2])
    day = int(date_list[1].replace(',', ''))
    month = month_dict[date_list[0]]
    return (year, month, day)

def Get_app_status(first_receipt_num, num_receipts = 4):
    '''
    Gets the current status of the application
    Inputs: 
    first_receipy_num - full number of the first receipt in the format XXX0123456789
    num_receipts - number of forms filed    
    Output:
    status - a list containing all the information given by USCIS for each form
    '''
    status = [] # initialize status list
    Letters = first_receipt_num[0:3] # keep first 3 letters
    first_num = int(first_receipt_num[3:]) # convert number to int
    # Find status for all the receipts
    for i in range(num_receipts):

        driver.get('https://egov.uscis.gov/casestatus/landing.do') # navigate to USCIS

        search_text = driver.find_element_by_name('appReceiptNum') # find search text box
        search_text.clear() # clear text box
        search_text.send_keys( Letters + str(first_num + i) ) # enter receipt number

        search_button = driver.find_element_by_name('initCaseSearch') # find search button
        search_button.click() # click search button
        # append element containing all the relevant information
        status.append(driver.find_element_by_class_name('text-center').get_attribute('outerHTML'))
    
    return status

def Get_times(form_name, office_name, RD):
    '''
    Gets processing times
    inputs: form_name - name as appears on USCIS website
            office - the office where processing is done as appears on USCIS website
            RD - Received date on the form in the format (yyyy, mm, dd)
    outputs: est - estimate of time for processing
            days_for_inquiry - number of days of wait for inquiry 
    '''
    driver.get('https://egov.uscis.gov/processing-times/') # navigate to USCIS
    time.sleep(0.5)
    selectForm = Select(driver.find_element_by_id('selectForm')) # find first drop down
    selectForm.select_by_visible_text(form_name) # select form name
    time.sleep(0.5)
    selectOffice = Select(driver.find_element_by_id('officeOrCenter')) # find second drop down
    selectOffice.select_by_visible_text(office_name) # select office name
    get_button = driver.find_element_by_id('getProcTimes') # find submit button
    get_button.click() # click submit button
    time.sleep(1)

    r = 1 if form_name[2]=='4' else 0 # choose relevant raw in the table
    # get waiting time estimate from table
    est = Get_text(driver.find_elements_by_id('est')[r].get_attribute('outerHTML'))
    # get inquiry date from table
    date = Get_text(driver.find_elements_by_id('date')[r].get_attribute('outerHTML'))
    # compute number of days to inquiry
    days_for_inquiry = datetime.date(*RD) - datetime.date(*format_date(date))
    est = ' '.join(est.split()) # clean estimate string

    return est, days_for_inquiry.days

'''Run and print results'''

FF = os.environ['FF'] # first form receipt number
RD = format_date(os.environ['RD']) # form received dated

driver = webdriver.Chrome() # launch a chrome webdriver
status = Get_app_status(FF)
I485_str = 'I-485 | Application to Register Permanent Residence or Adjust Status'
I765_str = 'I-765 | Application for Employment Authorization'
est_485, days_485 = Get_times(I485_str, 'Los Angeles CA', RD)
est_765, days_765 = Get_times(I765_str, 'California Service Center', RD)
driver.close()

form_name = ['I-485', 'I-130', 'I-131', 'I-765']
print('Status:')
print('-------')
for i in range(4):
    print(form_name[i] + ': ' + BeautifulSoup(status[i], features="html5lib").find('h1').text)

print('--------------------------------------------------------------------------')
print('I-765 estimate waiting time: ' + est_765 + ', inquiry in ' + str(days_765) + ' days')
print('I-485 estimate waiting time: ' + est_485 + ', inquiry in ' + str(days_485) + ' days')