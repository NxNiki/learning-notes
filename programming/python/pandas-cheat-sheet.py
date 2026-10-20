# check if dir exists:

import os
from os import path
#trying to make directory if it does not already exist:
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
    
# pandas:
spm_vbm_aal = pd.read_csv(data_dir+"/GMV_AAL_AvgExtract.csv", delimiter = ",", index_col = [0])

spm_vbm_aal.iloc[:,0].replace(to_replace=\
                              r'.nii.gz',
                              value='', regex=True, inplace = True)
                              
# set column name:
aal_label = pd.read_csv(atlas_dir+"/AAL_116_Label.csv", delimiter = ',')
spm_vbm_aal.columns = ['names'] + aal_label['ROIname'].to_list()

# drop column:
label_fa = label_fa.drop(['Unnamed: 0.1'], axis = 1)


# add 'label' to column names to avoid duplication with tract features:
label_fa.columns = [str(col) + '(label)' for col in label_fa.columns]

multimodal_features = pd.concat([vbm, label_fa*-1, tract_fa*-1], axis = 1,)


# change data type in dataframe:
behav_data = behav_data.astype({'SUBJID': 'int64'})
behav_data["Med_Rating"] = behav_data["Med_Rating"].apply(pd.to_numeric, errors='coerce')

# select rows based on value in column:
behav_data = behav_data.loc[behav_data["Med_Rating"]<2,:]

# select rows based on multiple conditions:
# need parenthese for each condition: (condition1) & (condition2)
value = complete_df.loc[(complete_df['site']==tms) & (~complete_df[var].isna()), var]

# multilevel index:
row_index = pd.MultiIndex.from_tuples([(i , j) for i in test_variables for j in ['t value', 'p value', "Cohen's d",]])

# merge data frame:
behav_feature = behav_data_hc.merge(multimodal_features, how = "inner", right_on = "names", left_on = "SUBJID")


# stats by group:
print(subject_split_info[["Train_index", "Sex"]].groupby(["Train_index", "Sex"]).size())
print(subject_split_info[["Train_index", "age_at_cnb"]].groupby(["Train_index"]).mean())
subject_split_info[["Train_index", "age_at_cnb"]].groupby(["Train_index"]).std()

# get column values:
features_keys = features_keys.columns.get_level_values(0)


# format report of p values:
report2 = report.copy()
report2.iloc[:, 1:] = report2.iloc[:, 1:].astype(float).round(3)
# report.iloc[:,1:]=report.iloc[:,1:].mask(report.iloc[:,1:].le(0.05), report.astype(str).apply(lambda x : x.str[:5]).add('*'))

report2[report2.iloc[:,1:].le(2)] = report2[
    report2.iloc[:,1:].le(2)].astype(str).apply(lambda x : x.str[:5]).apply(lambda x : x.str.ljust(5, fillchar='0'))

report2[report_corrected.iloc[:,1:].le(0.05)] = report2[
    report_corrected.iloc[:,1:].le(0.05)].astype(str).apply(lambda x : x.str[:5]).add('*')

report2[report_corrected.iloc[:,1:].le(0.01)] = report2[
    report_corrected.iloc[:,1:].le(0.01)].astype(str).apply(lambda x : x.str[:5]).add('**')


# or:
report2[report.gt(0)] = report2[report.gt(0)] .astype(str).apply(lambda x : x.str[:5])
report2[report.lt(0)] = report2[report.lt(0)] .astype(str).apply(lambda x : x.str[:6])


# data exploration:

print('How many different companies are represented in the data set?')
print(len(data['Company Name'].unique()))

print('What is the total number of jobs created for businesses in Queens?')
print(data.loc[data['Borough'] == 'QUEENS', 'Job created'].sum())

print('How many different unique email domains names are there in the data set?')
print(data['company email'].str.extract(r".*@(.*)").nunique(axis=0))

print('Considering only NTAs with at least 5 listed businesses, what is the average total savings and the total jobs \n'
      'created for each NTA?')
print(data[
          ['Company Name', 'Job created', 'Total Savings', 'Neighborhood Tabulation Area (NTA) (2020)']
      ].groupby('Neighborhood Tabulation Area (NTA) (2020)', as_index=True).agg(
    {'Company Name': 'count', 'Job created': 'mean', 'Total Savings': 'mean'}
).rename(columns={'Company Name': 'Number of companies'}).query("`Number of companies` >= 5"))
