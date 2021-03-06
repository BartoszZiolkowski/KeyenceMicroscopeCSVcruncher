# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 15:26:11 2018

@author: Bartosz Ziółkowski

This code works on csv files generated by the keyence microscope.
It imports all *.CSV filed from the directory in which it is run, and generates a single csv file with statistical summary of the data (summary.csv),
provides the joined raw file (raw_data_joined.csv),
as well plots as a histogram (plot.jpg) and generates histogram raw data (histogram_raw_data.csv).

"""

import os, csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json



script_relative_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_relative_path)

config_file = "parameters.json"
cfg_string = open(config_file).read()
cfg_json = json.loads(cfg_string)

extension = cfg_json['extension']

bin_size = int(cfg_json['bin_size'])
xmin = int(cfg_json['xmin'])
xmax = int(cfg_json['xmax'])
ymin = int(cfg_json['ymin'])
ymax = int(cfg_json['ymax'])
title = cfg_json['title']
column_to_plot = cfg_json['column_to_plot']
color = cfg_json['color']


def getFilenames(directory):
    filenames = []
    for root, dirs_list, files_list in os.walk(os.getcwd()):
        for file_name in files_list:
            if os.path.splitext(file_name)[-1] == extension:
                filenames.append(file_name)
                print(file_name)

    return filenames

filenames = getFilenames(os.getcwd())


main_dataframe = pd.DataFrame()


plot_settings = {'column_to_plot': column_to_plot, 'title':title, 'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax, 'bin_size':bin_size, 'xlabel':'Size [um]', 'ylabel':'Count'}

for value in filenames:
    print(value)
    temp_dataframe = pd.read_csv(value, sep=',', encoding='windows-1252', skiprows=11)
    main_dataframe = main_dataframe.append(temp_dataframe, ignore_index=True)
    #print(temp_dataframe)

for i in range(0, len(list(main_dataframe))):
    for j in range(0, len(main_dataframe)):
        main_dataframe.iat[j,i] = pd.to_numeric(main_dataframe.iat[j,i], errors='ignore')


filtered_df = pd.DataFrame()
filtered_df = main_dataframe[pd.to_numeric(main_dataframe['No.'], errors='coerce').notnull()]

column_names = filtered_df.columns.values.tolist()
filtered_df2 = pd.DataFrame()

for i in column_names:
    try:
        filtered_df2[i] = filtered_df[i].astype('float')
    except ValueError:
            pass

summary = filtered_df2.describe(include=[np.number])


summary.to_csv(script_relative_path + '/summary.csv')
filtered_df2.to_csv(script_relative_path + '/summary.csv')


bins = [i for i in range(bin_size, xmax, bin_size)]
#y, binEdges, patches = plt.hist(filtered_df2[plot_settings['column_to_plot']], bins=np.arange(min(filtered_df2[plot_settings['column_to_plot']]), max(filtered_df2[plot_settings['column_to_plot']])  + plot_settings['bin_size'], plot_settings['bin_size']))
y, binEdges, patches = plt.hist(filtered_df2[plot_settings['column_to_plot']], bins=bins, color=color)
plt.axis([plot_settings['xmin'], plot_settings['xmax'], plot_settings['ymin'], plot_settings['ymax']])
plt.xlabel(plot_settings['xlabel'])
plt.ylabel(plot_settings['ylabel'])
plt.title(plot_settings['title'])

"""
plt.show()

bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
plt.plot(bincenters,y,'-')
"""

plt.savefig('plot.jpg', bbox_inches='tight', dpi=300 )



y_adjusted = np.append(y, 0)


hist_raw_data = {'bin':binEdges, 'count': y_adjusted}
hist_df = pd.DataFrame(hist_raw_data, columns=['bin', 'count'])
hist_df.to_csv(script_relative_path +'/histogram_raw_data.csv')

