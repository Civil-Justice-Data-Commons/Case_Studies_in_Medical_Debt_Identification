# This Python code for identifying medical debt is written for the Redivis
# context, a virtual computing platform used by the Georgetown Civil Justice 
# Data Commons for court data analysis. However, it can be easily ported to 
# other data environments. Throughout the code, sections which are Redivis 
# specific have been called out in comments.

# If you would like to use the Redivis platform and Georgetown CJDC's court 
# data, please visit redivis.com/cjdc to apply for access.


### Setup ###

# Import libraries
import numpy as np
import pandas as pd
import regex

# Redivis Specific
import redivis


### Functions ###

# ID the medical debt plaintiffs based on string identification alone, with
# excluded terms
def string_based_id(input_df, plaintiff_col_name, included_terms, excluded_terms):
	temp_df = input_df
	def string_id_tool(input_string, included_terms, excluded_terms):
		if type(input_string) != str:
			return False
		return (any(i_term in input_string for i_term in included_terms) and not any(e_term in input_string for e_term in excluded_terms))
	temp_df['med_debt_plaintiff'] = temp_df[plaintiff_col_name].apply(string_id_tool, included_terms=included_terms, excluded_terms=excluded_terms)
	return temp_df.loc[temp_df['med_debt_plaintiff'] == True]

# ID Based on Fuzzy Regex
# Base threshold: 0.95
def regex_based_id(input_df, plaintiff_col_name, included_terms, excluded_terms):
	temp_df = input_df
	def string_regex_tool(input_string, included_terms, excluded_terms):
		if type(input_string) != str:
			return False
		return (any(regex.search(f'(?e){i_term}{{e<={int(len(i_term) * 0.05) + 1}}}', input_string) is not None for i_term in included_terms) and not any(regex.search(f'(?e){e_term}{{e<={int(len(e_term) * 0.05) + 1}}}', input_string) is not None for e_term in excluded_terms) )
	temp_df['med_debt_plaintiff'] = temp_df[plaintiff_col_name].apply(string_regex_tool, included_terms=included_terms, excluded_terms=excluded_terms)
	return temp_df.loc[temp_df['med_debt_plaintiff'] == True]

# Method Runner
# Takes a list of lists, with each list being [method name, included terms, excluded terms], and a list of lists for cases [dataframe, name]
def method_runner(included_terms, excluded_terms, cases_dataframe, search_method):
	search_df = search_method(cases_dataframe, 'plaintiff', included_terms, excluded_terms)
	# Print out 10 random samples of 100 records each, to use in accuracy measuring
	# [print(f'Sample {i} \n{search_df.sample(n=100)["plaintiff"]}') for i in range(10)]
	search_list = list(set(search_df['case_num']))
	return search_list

# Print out the results, for analysis in other data environments. 
def printer(results):
	for result in results:
		print('-------------')
		print(f'{result} # of Cases: {len(set(results[result]))}')
		print('>')
		for r2 in results:
			print(f'>>> {result} & {r2} Overlap: {len(list(set(results[result]) & set(results[r2])))}')
		print('>')

# Add a column to the dataframe with flags for each method it was flagged by.
def add_cols(results, input_df):
	for result in results:
		input_df[result] = np.where(input_df['case_num'].isin(results[result]), True, False)
	return input_df


### Create Sub-String Lists ###

# Redivis Specific
# Get table data for all jurisdictions
ct_cases_df = redivis.table('ct_cases').to_pandas_dataframe()
ct_med_cases_df = redivis.table('ct_med_cases').to_pandas_dataframe()

# Redivis Specific
# Get table data for CMS data
cms_ct_df = redivis.table('cms_ct').to_pandas_dataframe()

# Set up the lists of strings to be used in string-based identification
georgetown_med_terms = (
	'MEDICAL', 'MEDICINE', 'HOSPITAL',
	'CLINIC', 'REHAB', 'EMERGEN',
	'URGENT', 'DIAGNOSTIC', 'DIALYSIS',
	'HOSPICE', 'TELEHEALTH', 'SURGERY',
	'SURGIC', ' MD ', 'D.O.', 'FOOT AND ANKLE',
	'ANESTHESIOLOG', 'OBSTETRIC', 'GYNECOLOG',
	'UROLOG', 'NEPHROLOG', 'PLASTIC SURGERY',
	'SURGEON', 'INTERNAL MEDICINE',
	'FAMILY MEDICINE', 'NURSING HOME',
	'ALLERGY', 'ALLERGIST', 'DIABETES',
	'KIDNEY', 'CARDIOVASC', 'CARDIO',
	'BRAIN AND SPINE', 'NEUROSURGERY',
	'NEUROLOG', 'ORTHOPED', 'ANESTHESIO',
	'ANESTHESIA', 'NEUROSPINE', 'RESPIRATORY',
	'IMMUNOLOG', 'ENDOCRINOLOG', 'CHIROPRACT',
	'OPTOMETR', 'GASTROENTEROLOG', 'ENDOSCOPY',
	'sMRI', 'sEYE', 'OPTHALMOLOG', 'sFERTILITY',
	'THERAPHY', 'PSYCHIATR', 'BEHAVIOR',
	'ENDODONTIC', 'ORTHODON', 'DENTIST',
	'ORTHOTIC', 'RESEARCH', 'ONCOLOG',
	'CANCER', 'AMBULANCE', 'LABORATORY',
	'sLABS', ' LABS'
	)
georgetown_exclude_terms = (
	'BANK', 'LAWN', 'BOND',
	'CREDIT', 'ANIMAL', 'MOTORS',
	'CAR', 'VETERINARY', 'FCU'
	)
combinded_guelph_med_terms = (
	'CLINIC', 'HEALTH', 'HOSPITAL',
	'MEDICAL CENTER', 'AMBULANCE',
	'DOCTOR', 'HEALTHCARE', 'HEART',
	'HOSPICE', 'HOSPITALIZED',
	'MEDICINE', 'NURSE', 'NURSING',
	'OUTPATIENT', 'PEDIATRIC',
	'PHYSICIAN', 'PREVENTION',
	'PSYCHIATRIC', 'SPECIALIST',
	'WELFARE', 'DENTAL', 'DISPENSARY',
	'GYNECOLOGIST', 'IMMUNIZATION',
	'INFIRMARY', 'ORTHOPEDIC',
	'PATIENT', 'PHARMACY', 'REPRODUCTIVE',
	'SURGICAL', 'WELLBEING'
	)
combinded_guelph_exclude_terms = (
	'AID', 'CAMP', 'CARE', 'CENTER',
	'EDUCATION', 'ENVIRONMENTAL',
	'HYGIENE', 'NEARBY', 'NUTRITION',
	'POOR', 'PUBLIC', 'STUDY',
	'VETERINARY'
	)

# Set up the manually-identified med debt plaintiffs, based on manual review of 
# the top 100 and 1000 plaintiffs.
# The top plaintiffs lists for our jurisdictions are excluded here for privacy 
# protection.
ct_manual_top_100 = ()
ct_manual_top_1000 = ()


### Running the Methods ###

# Doing the work
# Setup a dictionary to hold the case ID results of our work for comparison.
ct_med_results = {}
ct_all_results = {}

# Set Options to allow for the max display of rows with Pandas to allow for accuracy sampling
pd.set_option('display.max_rows', None)

# Verified Med Debt Cases
ct_med_results['Georgetown CT Med Simple String Match'] = method_runner(georgetown_med_terms, georgetown_exclude_terms, ct_med_cases_df, string_based_id)
ct_med_results['Georgetown CT Med Regex Exclude Match'] = method_runner(georgetown_med_terms, georgetown_exclude_terms, ct_med_cases_df, regex_based_id)
ct_med_results['Georgetown CT Med Regex No Exclude Match'] = method_runner(georgetown_med_terms, [], ct_med_cases_df, regex_based_id)

ct_med_results['Guelph CT Med Simple String Match'] = method_runner(combinded_guelph_med_terms, combinded_guelph_exclude_terms, ct_med_cases_df, string_based_id)
ct_med_results['Guelph CT Med Regex Exclude Match'] = method_runner(combinded_guelph_med_terms, combinded_guelph_exclude_terms, ct_med_cases_df, regex_based_id)
ct_med_results['Guelph CT Med Regex No Exclude Match'] = method_runner(combinded_guelph_med_terms, [], ct_med_cases_df, regex_based_id)

ct_med_results['Top 100 CT Med Simple String Match'] = method_runner(ct_manual_top_100, [], ct_med_cases_df, string_based_id)
ct_med_results['Top 100 CT Med Regex Match'] = method_runner(ct_manual_top_100, [], ct_med_cases_df, regex_based_id)

ct_med_results['Top 1000 CT Med Simple String Match'] = method_runner(ct_manual_top_1000, [], ct_med_cases_df, string_based_id)
ct_med_results['Top 1000 CT Med Regex Match'] = method_runner(ct_manual_top_1000, [], ct_med_cases_df, regex_based_id)

ct_med_results['CMS Hospital Names CT Med Simple String Match'] = method_runner(cms_ct_terms, [], ct_med_cases_df, string_based_id)
ct_med_results['CMS Hospital Names CT Med Regex Match'] = method_runner(cms_ct_terms, [], ct_med_cases_df, regex_based_id)

ct_med_results['CT Med Debt Verified Cases'] = ct_med_cases_df['case_num']

# All CT Cases
ct_all_results['Georgetown CT All Simple String Match'] = method_runner(georgetown_med_terms, georgetown_exclude_terms, ct_cases_df, string_based_id)
ct_all_results['Georgetown CT All Regex Exclude Match'] = method_runner(georgetown_med_terms, georgetown_exclude_terms, ct_cases_df, regex_based_id)
ct_all_results['Georgetown CT All Regex No Exclude Match'] = method_runner(georgetown_med_terms, [], ct_cases_df, regex_based_id)

ct_all_results['Guelph CT All Simple String Match'] = method_runner(combinded_guelph_med_terms, combinded_guelph_exclude_terms, ct_cases_df, string_based_id)
ct_all_results['Guelph CT All Regex Exclude Match'] = method_runner(combinded_guelph_med_terms, combinded_guelph_exclude_terms, ct_cases_df, regex_based_id)
ct_all_results['Guelph CT All Regex No Exclude Match'] = method_runner(combinded_guelph_med_terms, [], ct_cases_df, regex_based_id)

ct_all_results['Top 100 CT All Simple String Match'] = method_runner(ct_manual_top_100, [], ct_cases_df, string_based_id)
ct_all_results['Top 100 CT All Regex Match'] = method_runner(ct_manual_top_100, [], ct_cases_df, regex_based_id)

ct_all_results['Top 1000 CT All Simple String Match'] = method_runner(ct_manual_top_1000, [], ct_cases_df, string_based_id)
ct_all_results['Top 1000 CT All Regex Match'] = method_runner(ct_manual_top_1000, [], ct_cases_df, regex_based_id)

ct_all_results['CMS Hospital Names CT All Simple String Match'] = method_runner(cms_ct_terms, [], ct_cases_df, string_based_id)
ct_all_results['CMS Hospital Names CT All Regex Match'] = method_runner(cms_ct_terms, [], ct_cases_df, regex_based_id)

ct_all_results['CT All Debt Verified Cases'] = ct_med_cases_df['case_num']

# Redivis Specific
# Output a table from the DF of results for further analysis in Redivis
redivis.current_notebook().create_output_table(add_cols(ct_med_results, ct_med_cases_df))