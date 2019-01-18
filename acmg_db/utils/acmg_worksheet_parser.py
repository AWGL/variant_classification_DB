import os
import csv
import json
import pandas as pd
import requests


def load_worksheet(input_file):
    # make empty lists to collect data
    headers = []
    data_values = []

    # make a csv reader object from the worksheet tsv file
    reader = csv.reader(input_file, delimiter='\t')
    
    # loop through lines, seperate out headers from data
    for line in reader:
        if line[0].startswith('#'):
            headers += [[field for field in line if field != '']]
        else:
            data_values += [line]
    
    # reverse data because variant database output is in reverse order
    data_values = list(reversed(data_values))
    data_headers = headers[-1]

    # pull out metadata
    report_info = []
    for i in headers[:-1]:
        report_info.append(i[0].strip('#'))

    # make a dataframe from data section
    df = pd.DataFrame(data=data_values, columns=data_headers)
    assert len(df['#SampleId'].unique()) == 1
    assert len(df['WorklistId'].unique()) == 1

    # make meta dictionary
    meta_dict = {'report_info': report_info}

    return df, meta_dict


# - MAIN --------------------------------------------------------------
def main():
    df, meta_dict = load_worksheet('test.tsv')
    variants_json, variants_dict = process_data(df, meta_dict)
    print(variants_json)

    if variants_dict["errors"]:
        print(variants_dict["errors"])
    if variants_dict["test"]:
        print('yes')


if __name__ == '__main__':
    main()
