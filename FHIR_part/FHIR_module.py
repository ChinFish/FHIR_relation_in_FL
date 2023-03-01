# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
import requests
import pandas as pd
from time import time
import os


def find_all_lab_test(fhir_url):
    '''
    This function will create all of lab test mapping loinc code
    :param fhir_url: which fhir server we need
    :return: a csv file, which contain lab test mapping with loinc code
    '''
    rstype = 'Observation'
    select_url = fhir_url + '/' + rstype
    patient_data = requests.get(url=select_url).json()
    for i in range(len(patient_data['entry'])):
        # print(len((patient_data['entry'])))
        # print(patient_data['entry'][i]['resource']['code']['coding'][0]['display'])

        status = 'next'
        record_dict = {}
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                loinc_code = patient_data['entry'][j]['resource']['code']['coding'][0]['code']
                lab_test = patient_data['entry'][j]['resource']['code']['coding'][0]['display']
                record_dict[lab_test] = loinc_code
                # print(patient_data['entry'][j]['resource']['code']['coding'][0]['display'])
            # print(len(patient_data['entry']))

            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()
            # print('next Bundle!!')
            # print(next_link)
    # print(record_dict)
    keys = record_dict.keys()
    values = record_dict.values()
    df = pd.DataFrame({"Lab test": keys, "Loinc code": values})
    print(df)
    # df.to_csv("code_book.csv")


def check_mapping_resource_type(resouce_type_mapping_codebook, hospital_mapping_codebook):
    '''
    This function will check whether hospital mapping to the resource type or not.
    :param resouce_type_mapping_codebook: File location. Store resource type mapping each hospital LOINC code codebook
    :param hospital_mapping_codebook: File location. Store hospital lab test mapping LOINC code
    :return: hospital mapping resource type or not
    '''
    hospital_name = 'LOINC code test hospital'
    # print('resource type mapping codebook:{}'.format(resouce_type_mapping_codebook))
    # print('Hospital mapping codebook:{}'.format(hospital_mapping_codebook))

    # hospital_loinc_code = hospital_mapping_codebook['LOINC code'].values
    hospital_lab_test = hospital_mapping_codebook['Lab test'].values
    target_lab_test = resouce_type_mapping_codebook['Lab test'].values
    complete_flag = True
    # print(hospital_loinc_code)
    # print(hospital_lab_test)
    # print(len(hospital_mapping_codebook['LOINC code']))
    for i in range(len(hospital_lab_test)):
        if hospital_lab_test[i] not in target_lab_test:
            complete_flag = False
            print('Lab Test:{} is not mapping in Resource Type'.format(hospital_lab_test[i]))
            print('Please add mapping')
    if complete_flag:
        print('Mapping relation is already finish!')
    return complete_flag


def create_big_table(fhir_url):
    '''
    This function will according to resource type mapping table,
    then get all patient ID from each LOINC code(lab test)
    :param fhir_url: which fhir server we need
    :return: a big table
    '''

    mapping_data = pd.read_excel('resource type mapping codebook.xlsx')
    mapping_data = mapping_data.set_index('Lab test')
    # mapping_data = pd.read_csv('code_book.csv')
    loinc_code = pd.read_excel('Hospital mapping codebook(example).xlsx')
    loinc_code = loinc_code.set_index('Lab test')
    mapping_data = pd.concat((mapping_data, loinc_code), axis=1, copy=False)
    print(mapping_data.reset_index())
    mapping_data = mapping_data.reset_index()
    df_big_table = pd.DataFrame()
    component = set()
    # Deal with no component part
    for i in range(len(mapping_data.axes[0])):
        patient_id = []
        lab_test_value = []
        big_table = {}
        lab_test = mapping_data.iloc[i]['Lab test']
        rstype = mapping_data.iloc[i]['Resource Type']
        loinc_code = mapping_data.iloc[i]['LOINC code']
        # loinc_code = mapping_data.iloc[i]['LOINC code']
        # print('lab test:{},Resource type:{},loinc_code:{}'.format(lab_test, rstype, loinc_code))
        select_url = fhir_url + '/' + rstype
        params = {'code': loinc_code}
        patient_data = requests.get(url=select_url, params=params).json()

        # search all the data in Bundle
        status = 'next'
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                # print(patient_data['entry'][j]['resource']['code']['coding'][0]['display'])
                # print(patient_data['entry'][j]['resource']['code']['coding'][0]['code'])

                if 'component' not in patient_data['entry'][j]['resource']:
                    patient_id.append(patient_data['entry'][j]['resource']['subject']['reference'][8:])
                    lab_test_value.append(patient_data['entry'][j]['resource']['valueQuantity']['value'])
                else:
                    component.add(loinc_code)
                    if 'valueQuantity' in patient_data['entry'][j]['resource']:
                        patient_id.append(patient_data['entry'][j]['resource']['subject']['reference'][8:])
                        lab_test_value.append(patient_data['entry'][j]['resource']['valueQuantity']['value'])
            # print(len(patient_data['entry']))
            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()

        big_table['Patient_ID'] = patient_id
        big_table[lab_test] = lab_test_value
        df_temp = pd.DataFrame(big_table)
        df_temp = df_temp.set_index('Patient_ID')

        df_big_table = pd.concat((df_big_table, df_temp), axis=1, copy=False)
        # print(df_big_table)
        # print('Big table test{}'.format(i+1))
    # print(df_big_table)
    # component = {'35094-2', '9269-2'}
    # print(component)

    # Deal with component part
    for code in component:
        lab_test_and_value = {}
        big_table = {}
        # print('code', code)
        rstype = 'Observation'
        select_url = fhir_url + '/' + rstype
        params = {'code': code}
        patient_data = requests.get(url=select_url, params=params).json()
        # print(patient_data)
        status = 'next'
        patient_id = []
        # lab_test_and_value[code] = []
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                patient_id.append(patient_data['entry'][j]['resource']['subject']['reference'][8:])
                for k in range(len(patient_data['entry'][j]['resource']['component'])):
                    lab_test = patient_data['entry'][j]['resource']['component'][k]['code']['coding'][0]['display']
                    lab_test_value = patient_data['entry'][j]['resource']['component'][k]['valueQuantity']['value']
                    if lab_test not in lab_test_and_value:
                        lab_test_and_value[lab_test] = []
                    lab_test_and_value[lab_test].append(lab_test_value)

                    # patient_id.append(patient_data['entry'][j]['resource']['subject']['reference'][8:])
                    # lab_test_value.append(patient_data['entry'][j]['resource']['valueQuantity']['value'])
            # print(len(patient_data['entry']))
            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()

        big_table['Patient_ID'] = patient_id
        for lab_test in lab_test_and_value.keys():
            big_table[lab_test] = lab_test_and_value[lab_test]
        # print(big_table)
        df_temp = pd.DataFrame(big_table)
        df_temp = df_temp.set_index('Patient_ID')

        df_big_table = pd.concat((df_big_table, df_temp), axis=1, copy=False)
    # print(df_big_table)

    print('Big table create successfully!!')
    # output big table become csv format
    # df_big_table.to_csv('./data/Big_Table.csv')
    df_big_table.to_csv('Test_Fhir_server_data.csv')


if __name__ == '__main__':
    fhir_server_url = 'http://120.126.47.119:8002/fhir'

    # create_big_table(fhir_server_url)

    # find_all_lab_test(fhir_server_url)

    rstype_map_codebook = pd.read_excel('resource type mapping codebook.xlsx')
    hospital_map_codebook = pd.read_excel('Hospital mapping codebook(example).xlsx')
    time_check_map_start = time()
    check = check_mapping_resource_type(resouce_type_mapping_codebook=rstype_map_codebook,
                                        hospital_mapping_codebook=hospital_map_codebook)
    time_check_map_end = time()

    '''test data exist function'''
    # print(os.path.exists('data/Big_Table.csv') is False)
    # # Already mapping and check big table is exist or not
    # if os.path.exists('data/Big_Table.csv') is False and check:
    #     print('======Design big table======')
    #     if os.path.exists('data') is False:
    #         os.mkdir('data')

    start_time_create_big_table = time()
    create_big_table(fhir_url=fhir_server_url)
    end_time_create_big_table = time()
    print('execute check map time:{}', format(time_check_map_end - time_check_map_start))
    print('execute big table time:{}', format(end_time_create_big_table - start_time_create_big_table))
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
