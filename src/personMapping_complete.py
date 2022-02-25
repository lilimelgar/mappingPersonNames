#!/usr/bin/env python
# coding: utf-8

# All the steps to map person names from two lists (ListA and ListB). It gives as output a list of candidates for the mapping with scores.

## Import libraries
import matplotlib
import pandas as pd
import numpy as np
import re
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
# import jellyfish

# from IPython.display import display
from IPython.display import clear_output

import csv

# from IPython.display import display, HTML
# # display(HTML("<style>.container { width:95% !important; }</style>"))
# # pd.options.display.max_columns = 10
# pd.options.display.max_rows = 1000
# # pd.options.display.width = 1000

# to add timestamp to file names
import time

# for progress bar (https://datascientyst.com/progress-bars-pandas-python-tqdm/)
from tqdm import tqdm
from time import sleep


pathFolder = f'/Users/Melga001/stack/training/reproducibleCodeUU/testrepo/data/'

# Step1. Import and prepare files for mapping

# Import ListA

# here I need to import ListA, which will be an external list of names (Nodegoat, CERL, etc.) to map to
dfA_t00 = pd.read_csv(f"{pathFolder}raw/listA.csv", sep = ",", index_col=False, encoding= 'unicode_escape', engine='python')


# Import list to map to (LIST B)
dfB_t00 = pd.read_csv(f"{pathFolder}raw/listB.csv", sep = ",", index_col=False, encoding= 'unicode_escape', engine='python')


# Prepare ListA and ListB

# Prepare ListA

# # drop unnecessary columns for mapping
# dfA_t01 = dfA_t00.drop(['Unnamed: 0'], axis=1).copy()

# If no dropping, make a copy:
dfA_t01 = dfA_t00.copy()


# Depending on the structure of ListA and ListB, assign the column names

# dfA--> basic info
dfA_t01.columns = ['personIdA',
               'personStrIdA', 
               'nameStringA', 
               'dateBirthA', 
               'dateDeathA', 
               'dateFlA',
               ]


dfA = dfA_t01.reset_index(drop=True)


# convert datatypes and fill in empty values
dfA_columns = dfA.columns

for column in dfA_columns:
    dataType = dfA.dtypes[column]
    if dataType == np.float64:
        dfA[column] = dfA[column].fillna(0.0)
        dfA[column] = dfA[column].astype(int)
    if dataType == object:
        dfA[column] = dfA[column].fillna('null')
        dfA[column] = dfA[column].astype(str)
        

#Prepare ListB

# # drop extra column that is created when exporting to Csv from previous notebook
# # drop also other columns that won't be used in the mappings

# # dfB_t01 = dfB_t00.drop(['Unnamed: 0', 'isUncertain_dateBirth', 'isUncertain_dateDeath', 'SKpersonId'], axis=1).copy()
# dfB_t01 = dfB_t00.drop(['Unnamed: 0'], axis=1).copy()

# If no dropping, make a copy:
dfB_t01 = dfB_t00.copy()


# Depending on the structure of ListA and ListB, assign the column names


# dfB--> basic info
dfB_t01.columns = [
                   'personIdB',
                   'personStrIdB', 
                   'nameStringB', 
                   'dateBirthB', 
                   'dateDeathB', 
                   'dateFlB',
    #                'ndgPersonIdB'
#                    'placeB'
                   ]


dfB = dfB_t01.reset_index(drop=True).copy()


# convert datatypes and fill in empty values
dfB_columns = dfB.columns

for column in dfB_columns:
    dataType = dfB.dtypes[column]
    if dataType == np.float64:
        dfB[column] = dfB[column].fillna(0.0)
        dfB[column] = dfB[column].astype(int)
    if dataType == object:
        dfB[column] = dfB[column].fillna('null')
        dfB[column] = dfB[column].astype(str)
        

# ## Store listA and listB for future reference
# # add date, version
# # (would be cool to find a way to insert this automatically, adding these details at the beginning of this notebook)

# timestr = time.strftime("%Y%m%d-%H%M%S")
# fileListA = (f"{pathFolder}ListA_{timestr}.csv")
# dfA.to_csv(fileListA)

# fileListB = (f"{pathFolder}ListB_{timestr}.csv")
# dfB.to_csv(fileListB)


# ## Create a dataframe to store the mappings
dfC = pd.DataFrame()


# # Run mapping script
# v42
# used for testing this script in cy15, last use: Friday 18 February, 17.15
## NOTE: before running this script, run the script with validations for dates of birth/date and fl. It includes:
# dates have 4 digits
# the absolute difference between the date of flourish and the date of death cannot be higher than 100
# From here onwards, I use score types with letters, see Excel sheet for explanation (https://timelessfuture.stackstorage.com/s/g0BOzE05D8ykMxBx)

############################## SET BUFFER VALUES #######################################
## set buffer1 for difference between dates of birth or death:
buf1 = 5
## set buffer2 for difference between date of birth of personA and Fl date of personB (example, if personA was born in 1600 and lived the max. average human life of the time (80 years) this personA died in 1680. In the most extreme case, that person send/received a letter with personB who at the youngest age could be 15 or 20, thus, personB born in 1640, and personB died in 1720. Thus, the difference between dFlB and dbirthA is 120 years). If I want to be more precise, or if both persons were born in the same year, change it to 100 (which is the max. life expectancy)
buf2 = 120
## set buffer3 for the biggest difference between dates of flourish between personA and personB (example, if dBirthA is 1600 and dDeathA is 1680, and dBirthB is 1640 and dDeathB is 1720, the extreme dates of flourish in the later side are dFlA = 1680 and dFlB = 1720. The extreme dates of flourished on the earlier side can be dflA = 1620 and dflB = 1660. If we rest from the biggest dfl possible (1720) the earliest dfl possible (1620) we have 100). If one wants to be more precise, it could be changed to some value between 60 to 80, but if I want the minimum difference use buf6.
buf3 = 100
## set buffer4 for the minimum age in which a person can send or receive a letter. This could be as early as 7 years...
buf4 = 7
## set value of max. life expectancy
buf5 = 80
## set value of the smallest difference allowed between Flourished dates (e.g., to group persons that got fl. date from letter date)
buf6 = 15

############################## CAPTURE VARIABLES FROM DFs #######################################
# for indexB, rowB in dfB.iterrows():
for indexB, rowB in tqdm(dfB.iterrows(), total=dfB.shape[0]):
	# Capture basic standard columns for the mapping dataset B (to be mapped) as variables 
	personIdB = dfB.loc[indexB,'personIdB']
	personStrIdB = dfB.loc[indexB,'personStrIdB']
	nameStringB = dfB.loc[indexB,'nameStringB']
	dateBirthB = dfB.loc[indexB,'dateBirthB']
	dateDeathB = dfB.loc[indexB,'dateDeathB']
	dateFlB = dfB.loc[indexB,'dateFlB']
	# # Optional columns, activate if the dataset has these columns and write lines to add them to DFC
	# placeB = dfB.iloc[indexB,'placeB']
	# caseB = dfB.loc[indexB,'caseB']
	# scoreTypeB = dfB.loc[indexB,'scoreTypeB']
	sleep(0.01)
	for indexA, rowA in dfA.iterrows():
		# Capture basic standard columns for the mapping dataset A (to be mapped to) as variables
		personIdA = dfA.loc[indexA,'personIdA']
		personStrIdA = dfA.loc[indexA,'personStrIdA']
		nameStringA = dfA.loc[indexA,'nameStringA']
		dateBirthA = dfA.loc[indexA,'dateBirthA']
		dateDeathA = dfA.loc[indexA,'dateDeathA']
		dateFlA = dfA.loc[indexA,'dateFlA']
		# # Optional columns, activate if the dataset has these columns and write lines to add them to DFC
		# rolesA = dfA.loc[indexA,'rolesA']
		# bioA = dfA.loc[indexA,'bioA']
		# correspondentsA = dfA.loc[indexA,'correspondentsA']
		# altNamesA = dfA.loc[indexA,'altNamesA']
		# cenPersonIDsA = dfA.loc[indexA,'cenPersonIdsA']
		# placeA = dfA.loc[indexA,'placeA']
		# languageA = dfA.loc[indexA,'languageA']
		# caseA = dfA.loc[indexA,'caseA']
		# scoreTypeA = dfA.loc[indexA,'scoreTypeA']

############################## SET STRING MATCHING SETTINGS #######################################

		# Algorithm to be used
		matchScore1 = fuzz.token_sort_ratio(nameStringA, nameStringB)
		matchScore2 = fuzz.token_set_ratio(nameStringA, nameStringB)
		matchScore3 = fuzz.partial_ratio(nameStringA, nameStringB) #compares parts of strings, low score is useful to avoid matches like this (('Carlieri Jacopo', 'Jacopo Battieri'))

		# String score ranges
		rangeScoreVeryLow = 50
		rangeScoreLow = 60
		rangeScoreMid = 80
		rangeScoreHigh = 100

		# ############################## CLASSIFICATION OF CASES #######################################
		# classification of the cases depending on how precise the mapping should be
		## casesPrecise: is for the cases in which dates exist or are more complete, thus, the string score can be lower
		## caseLoose is the opposite
		caseName = ''
		caseVeryPrecise = {'A'}
		casesPrecise = {'B1', 'B2', 'C1', 'C2', 'D', 'E', 'F', 'H', 'I', 'J', 'K', 'M'}
		casesLoose = {'A-', 'A--', 'A---', 'B1-', 'B2-', 'C1-', 'C2-', 'D-', 'D--', 'D---', 'E-', 'E--', 'F-', 'G1', 'G1-', 'G1--', 'G2', 'G2-', 'H-', 'K-', 'K--', 'K---', 'L', 'L-','M-', 'M--', 'X', 'Z'}
		casesNoisy = {'Y'}


############################## CAPTURE SCORE TYPES #######################################
		############# SCORES TYPE A
		# definition Score typeA: persons in both datasets (A and B) have complete dates of birth and death (rules = dates of birth and death are the same)
		if ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
			# A -> exactly the same dates of birth/date
			if (dateBirthA == dateBirthB) and (dateDeathA == dateDeathB):
				caseName = 'A'
			# A- -> with buffer: one of the two dates is the same, and the other one has difference defined in buffer
			elif (dateBirthA == dateBirthB and (0 < abs (dateDeathB - dateDeathA) <= buf1)) or (dateDeathA == dateDeathB and (0 < abs (dateBirthB - dateBirthA) <= buf1)):
				caseName = 'A-'
			# A-- -> with buffer in both: both dates have difference defined in buffer, when they have Fl. dates
			elif (dateFlA != 0 and dateFlB != 0) and ((0 < abs (dateBirthB - dateBirthA) <= buf1) and (0 < abs (dateDeathB - dateDeathA) <= buf1)) and (dateFlA <= dateDeathB) and (dateFlB <= dateDeathA):
				caseName = 'A--'
			# A--- -> with buffer in both: both dates have difference defined in buffer, no Fl. dates
			elif (0 < abs (dateDeathB - dateDeathA) <= buf1) and (0 < abs (dateBirthB - dateBirthA) <= buf1):
				caseName = 'A---'

		############# SCORES TYPE B
		# definition ScoreB: persons in either dataset A or B have complete dates of birth and death, and the mapping dataset has either of the two plus Flourished date (uses rules: either dates of birth or death are the same or with buffer, and date of Flourished is between dates of birth and/or death)
		#### B1
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
			# B1 -> dates of birth complete (applying rule for dateFl in relation to date of death of the other set)
			if (dateDeathB == 0):
				if ((dateBirthA == dateBirthB) and (dateFlB <= dateDeathA)):
					caseName = 'B1'
				# B1- -> with buffer in db
				elif ((0 < abs(dateBirthB - dateBirthA) <= buf1) and (dateFlB <= dateDeathA)):
					caseName = 'B1-'
			elif (dateDeathA == 0):
				if ((dateBirthA == dateBirthB) and (dateFlA <= dateDeathB)):
					caseName = 'B1'
				# B1- -> with buffer in db
				elif ((0 < abs(dateBirthB - dateBirthA) <= buf1) and (dateFlA <= dateDeathB)):
					caseName = 'B1-'
		#### B2 -> dates of death complete (applying rule for dateFl in relation to date of death of the other set)
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)):
			# B2 -> dates of death complete (applying rule for dateFl in relation to date of death of the other set)
			if (dateBirthB == 0):
				if ((dateDeathA == dateDeathB) and (dateFlB <= dateDeathA)):
					caseName = 'B2'
				# B1- -> with buffer in db
				elif ((0 < abs(dateDeathB - dateDeathA) <= buf1) and (dateFlB <= dateDeathA)):
					caseName = 'B2-'
			elif (dateBirthA == 0):
				if ((dateDeathA == dateDeathB) and (dateFlA <= dateDeathB)):
					caseName = 'B2'
				# B1- -> with buffer in db
				elif ((0 < abs(dateDeathB - dateDeathA) <= buf1) and (dateFlA <= dateDeathB)):
					caseName = 'B2-'


		############# SCORES TYPE C
		# definition ScoreC: persons in either dataset A or B have complete dates of birth and death, and the mapping dataset has either of the two but flourished date is not be present in the set with incomplete dates (rules: either dates of birth or death are the same, and Florished date is not used)
		#### C1
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
			# C1 -> dates of birth complete (applying rule for dateFl in relation to date of death of the other set)
			if dateDeathB == 0 or dateDeathA == 0:
				if (dateBirthA == dateBirthB):
					caseName = 'C1'
				# C1- -> with buffer in db
				elif (0 < abs(dateBirthB - dateBirthA) <= buf1):
					caseName = 'C1-'
		#### C2 -> dates of death complete (applying rule for dateFl in relation to date of death of the other set)
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
			# C2 -> dates of death complete (applying rule for dateFl in relation to date of death of the other set)
			if dateBirthB == 0 or dateBirthA == 0:
				if (dateDeathA == dateDeathB):
					caseName = 'C2'
				# C1- -> with buffer in db
				elif (0 < abs(dateDeathB - dateDeathA) <= buf1):
					caseName = 'C2-'


		############# SCORES TYPE D
		# definition ScoreD: persons in either dataset A or dataset B have either dates (of birth and/ordeath) and also both datasets have the Flourished date (uses rules: either dates of birth or death are the same (or have buffer), and date of Flourished is between dates of birth and/or death following some rules)
		# D with date of birth
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)):
			# D -> case with same db and same date of flourished
			if ((dateBirthA != 0 and dateBirthB != 0) and (dateBirthA == dateBirthB) and (dateFlA == dateFlB)):
				caseName = 'D'
			# D- -> case when dates of birth are the same but not the flourished dates (applies rules)
			elif ((dateBirthA == dateBirthB) and (0 < abs(dateFlA - dateFlB) <= buf3)) or ((dateBirthA == dateBirthB) and (0 < abs(dateFlA - dateFlB) <= buf3)):
				caseName = 'D-'
			# D-- ->case with db with buffer and same date of flourished
			elif ((0 < abs(dateBirthB - dateBirthA) <= buf1) and (dateFlA == dateFlB)):
				caseName = 'D--'
			# D--- ->case when dates of birth have buffer and dates of Fl are not the same
			elif ((0 < abs(dateBirthB - dateBirthA) <= buf1) and ((0 < abs(dateFlA - dateFlB) <= buf3) and (0 < abs(dateFlA - dateFlB) <= buf3))):
				caseName = 'D---'
		# D with date of death
		elif ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
			# D -> case with same dd and same date of flourished
			if ((dateDeathA !=0 and dateDeathB !=0) and (dateDeathA == dateDeathB) and (dateFlA == dateFlB)):
				caseName = 'D'
			# D- -> case when dates of birth or death are the same but not the flourished dates (applies rules)
			elif ((dateDeathA == dateDeathB) and ((dateDeathA >= dateFlB) and (dateDeathB >= dateFlA)) and (0 < abs(dateFlA - dateFlB) <= buf3)):
				caseName = 'D-'
			# D-- ->case with dates with buffer and same date of flourished
			elif ((0 < abs(dateDeathB - dateDeathA) <= buf1) and (dateFlA == dateFlB)):
				caseName = 'D--'
			# D--- ->case when dates of birth or death have buffer and dates of Fl are not the same
			elif ((0 < abs(dateDeathB - dateDeathA) <= buf1) and ((dateDeathA >= dateFlB) and (dateDeathB >= dateFlA)) and (0 < abs(dateFlA - dateFlB) < buf3)):
				caseName = 'D---'


		############# SCORES TYPE E
		# definition ScoreE: none of the persons in either datasets A or B have complete dates of birth and death, one set has Flourished date the other don't (rules = either dates of birth are the same, or dates of death are the same)
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
			# E -> same db
			if (dateBirthA != 0 and dateBirthB != 0) and (dateBirthA == dateBirthB):
				caseName = 'E'
			# E- -> same dd
			elif (dateDeathA != 0 and dateDeathB != 0) and (dateDeathA == dateDeathB):
				caseName = 'E-'
			# E-- -> case with date buffer, (add it only with high percentage string match)
			elif (0 < abs(dateBirthB - dateBirthA) <= buf1) or (0 < abs (dateDeathB - dateDeathA) <= buf1):
				caseName = 'E--'


		############# SCORES TYPE F
		# definition ScoreF: none of the persons in datasets A or B have complete dates of birth and death, they don't have Flourished date either (rules = either dates of birth are the same, or dates of death are the same, or with buffer)
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)):
			# F -> exact match between dates of birth
			if (dateBirthA != 0 and dateBirthB != 0) and (dateBirthA == dateBirthB):
				caseName = 'F'
			# F -> exact match between dates of death
			if (dateDeathA != 0 and dateDeathB != 0) and (dateDeathA == dateDeathB):
				caseName = 'F'
			# F- -> case with date buffer for dates of birth (add it only with high percentage string match)
			if (dateBirthA != 0 and dateBirthB != 0) and (0 < abs(dateBirthB - dateBirthA) <= buf1):
				caseName = 'F-'
			# F- -> case with date buffer for dates death (add it only with high percentage string match)
			if (dateDeathA != 0 and dateDeathB != 0) and (0 < abs (dateDeathB - dateDeathA) <= buf1):
				caseName = 'F-'


		############# SCORES TYPE G
		# definition ScoreG: persons in one of the datasets have complete dates of birth and death (Flourished date is optional) and persons to map have only Flourished date (rules: one of the persons has complete dates of birth and death, the other person has only Flourished date, which is between dates of birth and/or death following some rules)
		# both datasets have dfl
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA !=0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA !=0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)):
		    caseName = 'GTest'
		    # G -> both datasets have Fl. date and there is an exact match
		    if (dateFlA != 0 and dateFlB !=0) and (dateFlB == dateFlA):
		        caseName = 'G1'
		    # G- -> both have Fl. date and the difference between the two is minimal
		    elif (dateFlA != 0 and dateFlB !=0) and (0 < abs(dateFlA - dateFlB) <= buf6):
		        caseName = 'G1-'
		    # G-- -> both have Fl. date and the difference between the two is maximal
		    elif (dateFlA != 0 and dateFlB !=0) and (0 < abs(dateFlA - dateFlB) <= buf3):
		        caseName = 'G1--'
		# one of the datasets doesn't have dfl
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA ==0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)):
		    # dflB has to be between db and dd of A but taking into account the min age at which someone writes (buf4)
		    if (dateBirthA + buf4 <= dateFlB <= dateDeathA):
		        caseName = 'G2'
		    # if the date of Fl is between db and dd but there is a small difference with db
		    elif (dateBirthA <= dateFlB <= dateDeathA):
		        caseName = 'G2-'
		elif ((dateBirthA == 0 and dateDeathA == 0 and dateFlA !=0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
		    # dflA has to be between db and dd of B but taking into account the min age at which someone writes (buf4)
		    if (dateBirthB + buf4 <= dateFlA <= dateDeathB):
		        caseName = 'G2'
		    # if the date of Fl is between db and dd but there is a small difference with db
		    elif (dateBirthB <= dateFlA <= dateDeathB):
		        caseName = 'G2-'


		############# SCORES TYPE H
		# definition ScoreH: persons in both datasets have incomplete dates of birth and death (either of the two in contrary way), but Flourished date is there
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)):	
			# H-> Fl. dates match exactly
			if dateFlA == dateFlB:
				caseName = 'H'
			# H- -> Fl. dates don't match (applies rules with the available dates) - with dbA available
			elif (dateBirthA != 0 and dateBirthB == 0) and ((abs(dateDeathB - dateBirthA) <= buf5)) and ((abs(dateFlA - dateFlB) <= buf3)):
				caseName = 'H-'
			# H- -> Fl. dates don't match (applies rules with the available dates) - with dbB available
			elif (dateBirthA == 0 and dateBirthB != 0) and ((abs(dateDeathA - dateBirthB) <= buf5)) and ((abs(dateFlA - dateFlB) <= buf3)):
				caseName = 'H-'


		############# SCORES TYPE I 
		# definition Score I: persons in both datasets have incomplete dates of birth and death (either of the two in contrary way), and Flourished date is only in one of the sets
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
			# I -> only logics for dates of birth or death
			if ((dateBirthA != 0 and dateDeathB != 0) and (abs(dateDeathB - dateBirthA) <= buf5)) or ((dateBirthB != 0 and dateDeathA != 0) and (abs(dateDeathA - dateBirthB) <= buf5)):
				caseName = 'I'
			# I- -> logics for Fl. date when db is present
			elif dateBirthA !=0 or dateBirthB != 0:
				if (dateBirthA + buf4) <= dateFlB <= (dateBirthA + buf5):
					caseName = 'I-'
			# I- -> logics for Fl. date when dd is present
			elif dateDeathA !=0 or dateDeathB != 0:
				if (dateDeathA - buf4) <= dateFlB <= ((dateDeathA - buf4) + buf5):
					caseName = 'I-'


		############# SCORES TYPE J
		# definition ScoreJ: persons in both datasets have incomplete dates of birth and death (either of the two) in the opposite way, and none has Flourished date
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)):
			# only logics for dates of birth or death
			if ((dateDeathB != 0 and dateBirthA != 0) and (abs(dateDeathB - dateBirthA) <= buf5)) or ((dateDeathA != 0 and dateBirthB !=0) and (abs(dateDeathA - dateBirthB) <= buf5)):
				caseName = 'J'


		############# SCORES TYPE K
		#definition ScoreK: persons in one dataset have incomplete dates of birth and death (either of the two) plus Flourished date, and persons in the other dataset have none of the two, only Flourished date
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
			# K -> Fl. dates match exactly    
			if dateFlA == dateFlB:
				caseName = 'K'
			# K- -> Fl. dates don't match, applies rules when dd is present
			elif dateDeathA !=0 or dateDeathB != 0:
				if (dateDeathA - buf5) <= dateFlB <= dateDeathA:
					caseName = 'K-'
				elif (dateDeathB - buf5) <= dateFlA <= dateDeathB:
					caseName = 'K-'
			# K-- -> Fl. dates don't match, applies rules when db available
			elif dateBirthA !=0 or dateBirthB != 0:
				if (dateBirthA + buf4) <= dateFlB <= (dateBirthA + buf5):
					caseName = 'K--'
				elif (dateBirthB + buf4) <= dateFlA <= (dateBirthB + buf5):
					caseName = 'K--'				
			# K--- -> Fl. dates don't match (applies rules with the available dates)
			elif (abs(dateFlA - dateFlB) <= buf3):
				caseName = 'K---'


		############# SCORES TYPE L
		# definition ScoreL: persons in one dataset have incomplete dates of birth and death (either of the two) and no Flourished date, persons in the other dataset have no date of birth nor death, but do have Flourished date
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)):	
			# L -> when db is present
			if dateBirthA !=0:
				if (dateBirthA + buf4) <= dateFlB <= (dateBirthA + buf5):
					caseName = 'L'
			elif dateBirthB != 0:
				if (dateBirthB + buf4) <= dateFlA <= (dateBirthB + buf5):
					caseName = 'L'
			# L -> when dd is present
			elif dateDeathA !=0:
				# smallest difference between the two
				if (dateDeathA - dateFlB) <= buf1:
					caseName = 'L'
				# biggest difference between the two
				elif (dateDeathA - dateFlB) <= (buf5 - buf4):
					caseName = 'L-'
			elif dateDeathB != 0:
				# smallest difference between the two
				if (dateDeathB - dateFlA) <= buf1:
					caseName = 'L'
				# biggest difference between the two
				elif (dateDeathB - dateFlA) <= (buf5 - buf4):
					caseName = 'L-'


		# ############# SCORES TYPE M
		# definition ScoreM: persons in both datasets have only date of Flourished
		elif (dateBirthA == 0 and dateBirthA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0):
			# M -> same Fl. dates
			if dateFlA == dateFlB:
				caseName = 'M'
			# M- -> small difference between dates of Fl.
			elif 1 <= abs(dateFlB - dateFlA) <= buf6:
				caseName = 'M-'
			# M-- -> biggest difference between dates of Fl.                
			elif 1 <= abs(dateFlB - dateFlA) <= buf3:
				caseName = 'M--'
					

		# SCORES TYPE X
		# definition ScoreX: persons in one dataset have both dates, and in the other dataset no dates at all
		elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
			caseName = 'X'
									

		############# SCORES TYPE Y
		# definition ScoreY: persons in one dataset have either date, and in the other dataset no dates at all
		elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)):
			caseName = 'Y'

		############# SCORES TYPE Z
		# definition ScoreZ: this group includes persons with no dates at all in both datasets, scores rely on string matching only (no other rules)
		elif (dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0):
			caseName = 'Z'



# ############################## RUN STRING MATCHING #######################################
		# this rule only applies to cases of type A when the dates are exactly the same (e.g., to match 'Olivarius Vredius' with 'Olivier de Wree')
		if caseName in caseVeryPrecise:
			if rangeScoreVeryLow <= matchScore1 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore1
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)
			elif rangeScoreVeryLow <= matchScore2 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore2
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore2'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)

		elif caseName in casesPrecise:
			if rangeScoreLow <= matchScore1 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore1
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)
			elif rangeScoreLow <= matchScore2 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore2
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore2'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)


		elif caseName in casesLoose:
			if rangeScoreMid <= matchScore1 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore1
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)


			elif rangeScoreMid <= matchScore2 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore2
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore2'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)

		# depending on the data, these cases can give a lot of noise (incorrect mappings). During test round, case 'Y' was detected as the noisiest. After testing with different matching algorithms
		# to find the one giving the lowest score for the wrong matches, I found that matchScore2 was causing the noise. Thus, here it's removed, and only matchScore1 is used.
		elif caseName in casesNoisy:
			if rangeScoreMid <= matchScore3 <= rangeScoreHigh:
				scoreNameString = dfA.loc[indexA, 'scoreNameString'] = matchScore1
				scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
				match_nameStringB = dfA.loc[indexA, 'match-personNameB'] = nameStringB
				match_dateBirthB = dfA.loc[indexA, 'match-dateBirthB'] = dateBirthB
				match_dateDeathB = dfA.loc[indexA, 'match-dateDeathB'] = dateDeathB
				match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
				match_personIdB = personIdB = dfA.loc[indexA, 'match-personIdB'] = personIdB
				dfC = dfC.append({
						  'scoreCase':caseName,
						  'scoreNameString':scoreNameString,
						  'scoreType':scoreType,
						  'match_nameStringB':match_nameStringB,
						  'match_dateBirthB':match_dateBirthB,
						  'match_dateDeathB':match_dateDeathB,
						  'match_dateFlB':match_dateFlB,
						  'nameStringA':nameStringA,
						  'dateBirthA':dateBirthA,
						  'dateDeathA':dateDeathA,
						  'dateFlA':dateFlA,
						  'personIdA': personIdA,
						  'match_personIdB':match_personIdB
						  # 'caseA':caseA,
						  # 'scoreTypeA':scoreTypeA
						  },ignore_index=True,sort=False)



# # Prepare mapping output for analysis

# #### Replace the .0 in person dates and convert to strings
dfC['dateBirthA'] = dfC['dateBirthA'].astype(str).replace('\.0', '', regex=True)
dfC['dateDeathA'] = dfC['dateDeathA'].astype(str).replace('\.0', '', regex=True)
dfC['dateFlA'] = dfC['dateFlA'].astype(str).replace('\.0', '', regex=True)
dfC['match_dateBirthB'] = dfC['match_dateBirthB'].astype(str).replace('\.0', '', regex=True)
dfC['match_dateDeathB'] = dfC['match_dateDeathB'].astype(str).replace('\.0', '', regex=True)
dfC['match_dateFlB'] = dfC['match_dateFlB'].astype(str).replace('\.0', '', regex=True)


# #### Create joined / unique names and fill the blanks
dfC['JoinedInitial'] = dfC['nameStringA'] + '^' + dfC['dateBirthA'] + '^' + dfC['dateDeathA'] + '^' + dfC['dateFlA']
dfC['JoinedMapped'] = dfC['match_nameStringB'] + '^' + dfC['match_dateBirthB']  + '^' + dfC['match_dateDeathB'] + '^' + dfC['match_dateFlB']

# Fill in blanks
dfC['JoinedMapped'] = dfC['JoinedMapped'].fillna('notmapped')



# #### Run the second script to detect variation in the mapped forms

# Convert these joined names to strings
dfC['JoinedInitial'] = dfC['JoinedInitial'].astype('string')
dfC['JoinedMapped'] = dfC['JoinedMapped'].astype('string')


for j in dfC.index:
    clear_output(wait=True)
    rowIndex = dfC.index[j]
    initialForm = dfC.iloc[j,13]
    mappedForm = dfC.iloc[j,14]
    matchScoreFinal = fuzz.ratio(initialForm, mappedForm)
    print("Current progress loop1:", np.round(j/len(dfC) *100, 2),"%")
    if 0 <= matchScoreFinal <=100:
        dfC.loc[rowIndex, 'ScoreMappedVersionsNotChangedis100'] = matchScoreFinal        
        

# Reorder the columns in a way that is easier to evaluate mapping

dfD = dfC[['JoinedInitial',
        'JoinedMapped',
#         'occupationsA',
#         'occupationsB',
#         'altNamesA',
#         'altNamesB',
#         'nickNamesB',
#         'correspondentsA',
#         'correspondentsB',
#         'EMLOIdB',
#         'VIAFIdB',
        'personIdA',
#         'personIdA',
        'match_personIdB',
#         'nodegoatId_str_B',
#         'nodegoatId',
#         'ndgPersonIdB',
#         'mappedSKpersonIdB',
#         'placeA',
#         'placeB',
#         'taalA',
#         'bioA',
        'nameStringA',
        'match_nameStringB',
        'dateBirthA',
        'match_dateBirthB',
        'dateDeathA',
        'match_dateDeathB',
        'dateFlA',
        'match_dateFlB',
        'scoreCase',
        'scoreType',
        'scoreNameString',
        'ScoreMappedVersionsNotChangedis100']]


# # Download the mappings file


# # This file will contain the mapping candidates, which is easier to evaluate externally, e.g., in OpenRefine
# # Once the right candidates are chosen, Step5 will continue with a mappings file (that contain only the mapped IDs)

datasetA = 'CEN'
datasetB = 'Epistolarium'
description = 'test2_round2'

timestr = time.strftime("%Y%m%d-%H%M%S")
fileNameMappingCandidates = (f"{pathFolder}processed/MappingsPersonsCandidates_{datasetA}vs{datasetB}_{description}_{timestr}.csv")
dfD.to_csv(fileNameMappingCandidates)
# dfC.to_csv(fileNameMappingCandidates)