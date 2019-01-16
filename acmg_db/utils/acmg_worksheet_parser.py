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


def process_data(df, meta_dict):
    # Add sample ID and worksheet ID to meta data
    meta_dict['sample_id'] = df['#SampleId'].unique().tolist()[0]
    meta_dict['worksheet_id'] = df['WorklistId'].unique().tolist()[0]

    # Make empty variables for the loop
    # separate warnings and errors for django form validation - might not be needed
    error_list = []
    warning_list = []
    sorted_df = pd.DataFrame()
    fields = ['Variant', 'Genotype', 'Gene', 'Transcript', 'HGVSc', 'HGVSp', 'PreferredTranscript', 'CanonicalTranscript', 'Location']

    # make list of unique variants and loop through each one
    unique_variants = df['Variant'].unique()


    for var in unique_variants:
        # create a subset of the df containing only records for the variant
        subset = df.loc[df['Variant'] == var]

        # check if there is a record for perferred transcript
        if 'TRUE' not in subset['PreferredTranscript'].unique():

            # if there isnt a preferred transcript, check for a cononical transcript
            # if there isn't, throw an error and quit
            if 'TRUE' not in subset['CanonicalTranscript'].unique():
                error_list += ['ERROR: No preferred or canonical transcripts for {}, check the input data.'.format(var)]
                #raise ValueError("Couldn't load data")

            # if there is, throw a warning and continue
            else:
                warning_list += ['WARNING: No preferred transcript for {}, using canonical transcript.'.format(var)]
                # for each canonical transcript
                    #add to df - var, canon, transcript
                subset2 = subset.loc[subset['CanonicalTranscript'] == 'TRUE']
                temp_df = subset2.loc[:, fields]
                sorted_df = sorted_df.append(temp_df)
        
        # if there is a preferred transcript, add to the df
        else:
            # add each pt to df
            subset2 = subset.loc[subset['PreferredTranscript'] == 'TRUE']
            temp_df = subset2.loc[:, fields]
            sorted_df = sorted_df.append(temp_df)


    # sort the df and remove duplicates
    final_df = sorted_df.sort_values(['PreferredTranscript', 'CanonicalTranscript', 'HGVSc'], ascending=False).drop_duplicates('HGVSc').sort_index()
    final_df_json = final_df.to_json(orient='records')

    # add the data to the meta dictionary, convert to json
    meta_dict['variants'] = json.loads(final_df_json)
    meta_dict['warnings'] = warning_list
    meta_dict['errors'] = error_list
    meta_dict['test'] = []

    #return_json = json.dumps(meta_dict, indent=2, separators=(',', ':'))

    return meta_dict


def get_refseq_transcripts(transcript, hgvs_c):
    warn = []
    
    if hgvs_c == "":
        warn += ["HGVSc for {} is empty, cannot find the RefSeq transcript without it, add RefSeq transcript manually.".format(transcript)]
    
    query = "http://rest.ensembl.org/variant_recoder/human/{}:{}?".format(transcript, hgvs_c)
    
    r = requests.get(query, headers={ "Content-Type" : "application/json"})
 
    if not r.ok:
        warn += ['Could not connect to Ensembl database, add RefSeq transcript for {} manually.'.format(transcript)]
        
    else:
        decoded = r.json()

        nm_list = []
        for c in (decoded[0]['hgvsc']):

            # check that id is a refseq id
            if c.startswith('NM'):

                # check if the HGVSc matches
                split = c.split(':')
                if split[1] == hgvs_c:
                    nm_list += [split[0]]
                # sometimes there are differences between databases if there is a dup/del where the last base is dropped drop the name
                # e.g. c.*333dupA could also be called c.*333dup
                elif split[1] == hgvs_c[:-1]:
                    nm_list += [split[0]]

        if len(nm_list) == 0:
            warn += ['Could not find any RefSeq transcripts for {}, add transcripts manually.'.format(transcript)]

        # TODO hgvsp check??
        
    return nm_list, warn


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
