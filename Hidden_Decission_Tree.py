#!python
# -*- coding: windows-1252 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Program Name: Hidden Decision Tree                                                                                   #
# Article: https://www.datasciencecentral.com/profiles/blogs/state-of-the-art-machine-learning-automation-with-hdt     #
# Article Author: Dr Vincent Granville                                                                               #
# Code Editor: Conrad Thiele (2019)                                                                                    #
# Email: conrad.thiele@outlook.com                                                                                     #
# Version: 1.0.0                                                                                                       #
# Python Version: 3.7.3                                                                                                #
# OS System designed on: Win10                                                                                         #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


import csv
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import time
from math import log
import re


pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
np.set_printoptions(edgeitems=3000)
np.core.arrayprint._line_width = 1000
start = time.time()


def predicted_page_view_24_bin(as_pandas):
    results_array = np.zeros(len(as_pandas))
    results_array.astype(np.float64)
    # 'Pred_Page_View_76bins'
    mean_log_pv_per_node_size = as_pandas.groupby('Node_Size', group_keys=True)['Log_Page_Views'].mean()
    for index, row in as_pandas.iterrows():
        if row['Node_Size'] > 10:
            results_array[index] = as_pandas['Pred_Page_View_76bins'][index]
        else:
            results_array[index] = mean_log_pv_per_node_size[row['Node_Size']]
    as_pandas['Pred_Page_View_24bins'] = pd.Series(results_array)
    return as_pandas


# Create an empty numpy array with zeros and then assign it type float64 which is standard double precision.
# 'mean_log_pv_per_node_size' contains a dataframe of each unique 'Node_Size' and the average values of the adjacent
# column  AVERAGEIF() in Excel 'Log_Page_Views' and is achieved using the pandas groupby() function.
# For loop iterates over all rows finds the contents of Node_Size and then uses the contents in the cell (float) as the
# Key in 'mean_log_pv_per_node_size' dataframe to return the value of the pair.
def predicted_page_view_76_bins(as_pandas):
    results_array = np.zeros(len(as_pandas))
    results_array.astype(np.float64)
    # Need to consider a different variable name??
    mean_log_pv_per_node_size = as_pandas.groupby('Node_Size', group_keys=True)['Log_Page_Views'].mean()
    for index, row in as_pandas.iterrows():
        results_array[index] = mean_log_pv_per_node_size[row['Node_Size']]
    as_pandas['Pred_Page_View_76bins'] = pd.Series(results_array)
    return as_pandas


# First create an empty numpy array with zeros and then assign it int8 as the values being stored are whole numbers.
# The node_count holds the key value pair for the count of unique Node keys and lists the total count as the value.
# Use for loop to got through each row of the dataframe when it hits column 'Node' the current scalar value is feed to
# the dataframe node_count as the Key to access the Value using basic indexing i.e. node_count['N-001-0000']
def count_node_name(as_pandas):
    results_array = np.zeros(len(as_pandas)) 
    results_array.astype(np.int8)
    node_count = as_pandas.groupby('Node')['Node'].count()
    for index, row in as_pandas.iterrows():
        results_array[index] = node_count[row['Node']]
    as_pandas['Node_Size'] = pd.Series(results_array)
    return as_pandas


# Create a node value from the count 0 or 1 in the below columns i.e. Forum, Blog, Python ...
# ix is just a counter, I could have put num, however, I liked the look of ix and has it's roots in panda functions
def node_name(as_pandas):
    temp_node_name = []
    for index, row in as_pandas.iterrows():
        temp_node_name.append('N-' + str(int(row['Forum'])) + str(int(row['Blog'])) + str(int(row['Python'])) + '-' +
                              str(int(row['R'])) + str(int(row['Machine_Learning'])) + str(int(row['Data_Science'])) +
                              str(int(row['Data'])) + str(int(row['Analytics'])))
    as_pandas['Node'] = pd.Series(temp_node_name)
    return as_pandas


def count_column_instances(as_pandas, searched_column, column_regex, output_column):
    results_array = np.zeros(len(as_pandas))
    results_array.astype(np.int8)
    for index, row in as_pandas.iterrows():
        find_name_instance = re.search(column_regex, row[searched_column], re.IGNORECASE)
        if find_name_instance:
            results_array[index] = 1
    as_pandas[output_column] = pd.Series(results_array)
    return as_pandas


# Count all article dates that are greater than 2014
def count_date(as_pandas):
    date_array = np.zeros(len(as_pandas['Date']))
    date_array.astype(np.int8)
    date_to_match = np.datetime64('2014-12-31 00:00:00')
    for index, row in as_pandas.iterrows():
        if row['Date'] > date_to_match:
            date_array[index] = 1
    as_pandas['Year > 2014'] = pd.Series(date_array)
    return as_pandas


def set_new_columns(as_pandas):
    titles = ['Year > 2014', 'Forum', 'Blog', 'Python', 'R', 'Machine_Learning', 'Data_Science',
              'Data', 'Analytics', 'Node', 'Node_Size', 'Pred_Page_View_76bins', 'Pred_Page_View_24bins',
              'Z_JackKnife']
    for index, word in enumerate(titles):
        if word == 'Node':
            as_pandas.insert(len(as_pandas.columns), titles[index], '0000000000')
        else:
            as_pandas.insert(len(as_pandas.columns), titles[index], 0)
    return as_pandas


# Insert new column header then count the number of letters in 'Title'
def title_length(as_pandas):
    as_pandas.insert(len(as_pandas.columns), 'Title_Length', 0)
    as_pandas['Title_Length'] = as_pandas['Title'].map(str).apply(len)
    return as_pandas


# Insert new column header. Log, can be thought of as percentage of change in 'Page Views' as it is equal to the linear
# comparison of logX1 - logX2. The map function allows for function to be performed on all rows in column 'Page_Views'.
def log_page_view(as_pandas):
    as_pandas.insert(len(as_pandas.columns), 'Log_Page_Views', 0)
    as_pandas['Log_Page_Views'] = as_pandas['Page_Views'].map(lambda x: log(1 + float(x)))
    return as_pandas


def change_to_numeric(as_pandas):
    # Check for missing values then convert the column to numeric.
    # Not sure why the first line below produces NaN's for all rows in column
    # as_pandas['Page_Views'] = as_pandas.replace(r'^\s*$', np.nan, regex=True)
    as_pandas['Page_Views'] = pd.to_numeric(as_pandas['Page_Views'], errors='coerce')
    return as_pandas


def change_column_names(as_pandas):
    as_pandas.rename(columns={'Unique Pageviews': 'Page_Views'}, inplace=True)
    return as_pandas


def change_date(as_pandas):
    as_pandas['Date'] = pd.to_datetime(as_pandas['Date'])
    return as_pandas


def open_as_dataframe(file_name_in):
    reader = pd.read_csv(file_name_in, encoding='windows-1251')
    return reader


# Get each column of data including the heading and separate each element i.e. Title, URL, Date, Page Views
# and save to string_of_rows with comma separator for storage as a csv file.
def get_columns_of_data(*args):
    # Function that accept variable length arguments
    string_of_rows = str()
    num_cols = len(args)
    try:
        if num_cols > 0:
            for index, element in enumerate(args):
                if index == (num_cols - 1):
                    string_of_rows = string_of_rows + element + '\n'
                else:
                    string_of_rows = string_of_rows + element + ','
    except UnboundLocalError:
        print('Empty file \'or\' No arguments received, cannot be zero')
    return string_of_rows


def open_file(file_name):
    try:
        with open(file_name) as csv_file_in, open('HDT_data5.txt', 'w') as csv_file_out:
            csv_read = csv.reader(csv_file_in,   delimiter='\t')
            for row in csv_read:
                try:
                    row[0] = row[0].replace(',', '')
                    csv_file_out.write(get_columns_of_data(*row))
                except TypeError:
                    continue
        print("The file name '{}' was successfully opened and read".format(file_name))
    except IOError:
        print('File not found \'OR\' Not in current directory\n')


def main():
    # The regex_dict defines the column to search in and the values to be used in the search
    regex_url_dict = {'URL': ['.*forum*.', '.*blog*.'],
                      'URL_Col_Name': ['Forum', 'Blog']
                      }
    regex_title_dict = {'Title': ['.*python*.', ',* r *.', '.*machine learn*.',
                                  '.*data science*.', '.*data*.', '.*analy*.'],
                        'Title_Col_Name': ['Python', 'R', 'Machine_Learning',
                                           'Data_Science', 'Data', 'Analytics']
                        }

    open_file('HDTdata3.txt')
    multi_sets = open_as_dataframe('HDT_data5.txt')
    multi_sets = change_date(multi_sets)
    multi_sets = change_column_names(multi_sets)
    multi_sets = change_to_numeric(multi_sets)
    multi_sets = log_page_view(multi_sets)
    multi_sets = title_length(multi_sets)
    multi_sets = set_new_columns(multi_sets)
    # Count the number of occurrences of words in either the Title or URL via dictionary key value pairs.
    multi_sets = count_date(multi_sets)
    for num_url in range(len(regex_url_dict)):
        count_column_instances(multi_sets, next(iter(regex_url_dict)), regex_url_dict['URL'][num_url],
                               regex_url_dict['URL_Col_Name'][num_url])

    for num_title in range(len(regex_title_dict)):
        count_column_instances(multi_sets, next(iter(regex_title_dict)), regex_title_dict['Title'][num_title],
                               regex_title_dict['Title_Col_Name'][num_title])
    multi_sets = node_name(multi_sets)
    multi_sets = count_node_name(multi_sets)
    multi_sets = predicted_page_view_76_bins(multi_sets)
    predicted_page_view_24_bin(multi_sets)
    # print(multi_sets)


main()


