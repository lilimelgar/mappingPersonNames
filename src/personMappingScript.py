# This python script detects the string similarity between two lists of person names, and uses rules based on the dates of birth/death/floriat of those persons.
# It's meant to be used with the Jupyter notebook available in the repository.

# NOTE: before running this script, run the script with validations for dates of birth/date and fl. It includes:
# dates have 4 digits
# the absolute difference between the date of flourish and the date of death cannot be higher than 100

# This Excel sheet has the explanation of the so-called "cases", i.e., all possible combinations of date of birth/death/floriat between the two lists (https://timelessfuture.stackstorage.com/s/AUmqSrqJDUyHKwOT)

from tqdm import tqdm
from time import sleep
from fuzzywuzzy import fuzz
import pandas as pd
import config


def compare_names(dfA, dfB, buf1=config.buf1, buf2=config.buf2, buf3=config.buf3, buf4=config.buf4, buf5=config.buf5, buf6=config.buf6):
    '''Processes and maps candidate names
    Inputs are two dataframes of names
    Outputs a dataframe of candidates
    '''

    # create an empty dataframe
    mapped_candidates = pd.DataFrame()

    ############################## CAPTURE VARIABLES FROM DFs #######################################
    # for indexB, rowB in dfB.iterrows():
    for indexB, rowB in tqdm(dfB.iterrows(), total=dfB.shape[0]):
        # Capture basic standard columns for the mapping dataset B (to be mapped) as variables
        personIdB = dfB.loc[indexB, 'personIdB']
        # personStrIdB = dfB.loc[indexB,'personStrIdB']
        nameStringB = dfB.loc[indexB, 'nameStringB']
        dateBirthB = dfB.loc[indexB, 'dateBirthB']
        dateDeathB = dfB.loc[indexB, 'dateDeathB']
        dateFlB = dfB.loc[indexB, 'dateFlB']
        # # Optional columns, activate if the dataset has these columns and write lines to add them to mapped_candidates
        # placeB = dfB.iloc[indexB,'placeB']
        # caseB = dfB.loc[indexB,'caseB']
        # scoreTypeB = dfB.loc[indexB,'scoreTypeB']
        sleep(0.01)
        for indexA, rowA in dfA.iterrows():
            # Capture basic standard columns for the mapping dataset A (to be mapped to) as variables
            personIdA = dfA.loc[indexA, 'personIdA']
            # personStrIdA = dfA.loc[indexA,'personStrIdA']
            nameStringA = dfA.loc[indexA, 'nameStringA']
            dateBirthA = dfA.loc[indexA, 'dateBirthA']
            dateDeathA = dfA.loc[indexA, 'dateDeathA']
            dateFlA = dfA.loc[indexA, 'dateFlA']
            # # Optional columns, activate if the dataset has these columns and write lines to add them to mapped_candidates
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
            # matchScore3 = fuzz.partial_ratio(nameStringA, nameStringB) # USE WITH casesNoisy (edit below) if names in both datasets are very similar. It compares parts of strings, low score is useful to avoid matches like this (('Carlieri Jacopo', 'Jacopo Battieri'))

            # String score ranges
            rangeScoreVeryLow = 50
            rangeScoreLow = 60
            rangeScoreMid = 80
            rangeScoreHigh = 100

            # ############################## CLASSIFICATION OF CASES #######################################
            # classification of the cases depending on how precise the mapping should be
            # casesPrecise: is for the cases in which dates exist or are more complete, thus, the string score can be lower
            # caseLoose is the opposite (string score has to be higher because dates are not so complete or straight to match)
            caseName = ''
            caseVeryPrecise = {'A'}
            casesPrecise = {'B1', 'B2', 'C1', 'C2',
                            'D', 'E', 'F', 'H', 'J', 'K', 'M'}
            casesLoose = {'A-', 'A--', 'B1-', 'B2-', 'C1-', 'C2-', 'D-', 'D--', 'D---',
                          'E-', 'F-', 'G', 'H-', 'I1', 'I2', 'K-', 'K--', 'L', 'L-', 'M-', 'M--'}
            casesNoisy = {'X', 'Y', 'Z'}

    ############################## CAPTURE CASES (i.e., Score types) (see link to Excel sheet above) #######################################
        # SCORES TYPE A
            # definition Score typeA: persons in both datasets (A and B) have complete dates of birth and death (in these cases Fl. date is not taken into account, actually, it shouldn't be added to the original data if there is db and dd)
            if ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
                # A -> exactly the same dates of birth/date
                if (dateBirthA == dateBirthB) and (dateDeathA == dateDeathB):
                    caseName = 'A'
                # A- -> with buffer: one of the two dates is the same, and the other one has difference defined in buffer
                elif (dateBirthA == dateBirthB and (0 < abs(dateDeathB - dateDeathA) <= buf1)) or (dateDeathA == dateDeathB and (0 < abs(dateBirthB - dateBirthA) <= buf1)):
                    caseName = 'A-'
                # A-- -> with buffer in both: both dates have difference defined in buffer
                elif (0 < abs(dateDeathB - dateDeathA) <= buf1) and (0 < abs(dateBirthB - dateBirthA) <= buf1):
                    caseName = 'A--'

        # SCORES TYPE B
            # definition ScoreB: persons in either dataset A or B have complete dates of birth and death, and the mapping dataset has either of the two plus Flourished date (uses rules: either dates of birth or death are the same or with buffer, and date of Flourished is between dates of birth and/or death)
            # B1
            elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
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
            # B2 -> dates of death complete (applying rule for dateFl in relation to date of death of the other set)
            elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
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

        # SCORES TYPE C
            # definition ScoreC: persons in either dataset A or B have complete dates of birth and death, and the mapping dataset has either of the two but flourished date is not be present in the set with incomplete dates (rules: either dates of birth or death are the same, and Florished date is not used)
            # C1 -> dates of birth complete
            elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
                # C1 -> dates of birth equal (applying rule for dateFl in relation to date of death of the other set)
                if (dateBirthA == dateBirthB):
                    caseName = 'C1'
                # C1- -> with buffer in db
                elif (0 < abs(dateBirthB - dateBirthA) <= buf1):
                    caseName = 'C1-'
            # C2 -> dates of death complete
            elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
                # C2 -> dates of death equal (applying rule for dateFl in relation to date of death of the other set)
                if (dateDeathA == dateDeathB):
                    caseName = 'C2'
                # C1- -> with buffer in db
                elif (0 < abs(dateDeathB - dateDeathA) <= buf1):
                    caseName = 'C2-'

        # SCORES TYPE D
            # definition ScoreD: persons in either dataset A or dataset B have either dates (of birth and/ordeath) and also both datasets have the Flourished date (uses rules: either dates of birth or death are the same (or have buffer), and date of Flourished is between dates of birth and/or death following some rules)
            # D with date of birth
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)):
                # D -> case with same db and smallest difference in flourished dates
                if (dateBirthA != 0 and dateBirthB != 0):
                    if ((dateBirthA == dateBirthB) and (abs(dateFlA - dateFlB) <= buf6)):
                        caseName = 'D'
                    # D- -> case when dates of birth are the same but bigger difference than in the previous case in the flourished dates
                    elif ((dateBirthA == dateBirthB) and (buf6 < abs(dateFlA - dateFlB) <= buf3)):
                        caseName = 'D-'
                    # D-- ->case with db with buffer and smallest difference in flourished dates
                    elif ((0 < abs(dateBirthB - dateBirthA) <= buf1) and (abs(dateFlA - dateFlB) <= buf6)):
                        caseName = 'D--'
                    # D--- ->case when dates of birth have buffer and there is big difference in the fl. dates
                    elif ((0 < abs(dateBirthB - dateBirthA) <= buf1) and (buf6 < abs(dateFlA - dateFlB) <= buf3)):
                        caseName = 'D---'
            # D with date of death
            elif ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
                # D -> case with same dd and smallest difference in flourished dates
                if (dateDeathA != 0 and dateDeathB != 0):
                    if ((dateDeathA == dateDeathB) and (abs(dateFlA - dateFlB) <= buf6)):
                        caseName = 'D'
                    # D- -> case when dates of death are the same but bigger difference than in the previous case in the flourished dates
                    elif ((dateDeathA == dateDeathB) and (buf6 < abs(dateFlA - dateFlB) <= buf3)):
                        caseName = 'D-'
                    # D-- ->case with dates with buffer and smallest difference in flourished dates
                    elif ((0 < abs(dateDeathB - dateDeathA) <= buf1) and (abs(dateFlA - dateFlB) <= buf6)):
                        caseName = 'D--'
                    # D--- ->case when dates of birth or death have buffer and and there is big difference in the fl. dates
                    elif ((0 < abs(dateDeathB - dateDeathA) <= buf1) and (buf6 < abs(dateFlA - dateFlB) <= buf3)):
                        caseName = 'D---'

        # SCORES TYPE E
            # definition ScoreE: none of the persons in either datasets A or B have complete dates of birth and death, one set has Flourished date the other don't (rules = either dates of birth are the same, or dates of death are the same)
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
                # E when db is present
                if (dateBirthA != 0 and dateBirthB != 0):
                    # E -> same db
                    if (dateBirthA == dateBirthB):
                        caseName = 'E'
                    # E- -> db with buffer
                    elif (0 < abs(dateBirthB - dateBirthA) <= buf1):
                        caseName = 'E-'
                # E when dd is present
                elif (dateDeathA != 0 and dateDeathB != 0):
                    # E -> same dd
                    if (dateDeathA == dateDeathB):
                        caseName = 'E'
                    # E- -> dd with buffer
                    elif (0 < abs(dateDeathB - dateDeathA) <= buf1):
                        caseName = 'E-'

        # SCORES TYPE F
            # definition ScoreF: none of the persons in datasets A or B have complete dates of birth and death, they don't have Flourished date either (rules = either dates of birth are the same, or dates of death are the same, or with buffer)
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)):
                # F with db
                if (dateBirthA != 0 and dateBirthB != 0):
                    # F -> exact match between dates of birth
                    if (dateBirthA == dateBirthB):
                        caseName = 'F'
                    # F- -> with buffer
                    if 0 < abs(dateBirthB - dateBirthA) <= buf1:
                        caseName = 'F-'
                # F with dd
                if (dateDeathA != 0 and dateDeathB != 0):
                    # F -> exact match between dates of death
                    if (dateDeathA == dateDeathB):
                        caseName = 'F'
                    # F- -> with buffer
                    if 0 < abs(dateDeathB - dateDeathA) <= buf1:
                        caseName = 'F-'

        # SCORES TYPE G
            # definition ScoreG: persons in one of the datasets have complete dates of birth and death (Flourished date is not taken into account) and persons to map have only Flourished date
            # dataset A has both dates, dataset B only Fl
            elif ((dateBirthA != 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)):
                # dflB has to be between db and dd of A but taking into account the min age at which someone writes (buf4)
                if (dateBirthA + buf4 <= dateFlB <= dateDeathA):
                    caseName = 'G'
            # dataset B has both dates, dataset A only Fl
            elif ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB != 0 and dateFlB == 0)):
                # dflA has to be between db and dd of B but taking into account the min age at which someone writes (buf4)
                if (dateBirthB + buf4 <= dateFlA <= dateDeathB):
                    caseName = 'G'

        # SCORES TYPE H
            # definition ScoreH: persons in both datasets have incomplete dates of birth and death (either of the two in contrary way), but Flourished date is there
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)):
                # H-> Fl. dates match exactly
                if dateFlA == dateFlB:
                    caseName = 'H'
                # H- -> Fl. dates don't match (applies rules with the available dates) - with dbA available
                elif (dateBirthA != 0 and dateDeathB != 0):
                    if ((abs(dateDeathB - dateBirthA) <= buf5)) and ((abs(dateFlA - dateFlB) <= buf3)):
                        caseName = 'H-'
                # H- -> Fl. dates don't match (applies rules with the available dates) - with dbB available
                elif (dateDeathA != 0 and dateBirthB != 0):
                    if ((abs(dateDeathA - dateBirthB) <= buf5)) and ((abs(dateFlA - dateFlB) <= buf3)):
                        caseName = 'H-'

        # SCORES TYPE I
            # definition Score I: persons in both datasets have incomplete dates of birth and death (either of the two in contrary way), and Flourished date is only in one of the sets
            # I for when dataset A has db
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
                # I1 -> logics for Fl. date A when is present
                if dateFlA != 0:
                    if (dateDeathB - dateBirthA) <= buf5:
                        if (dateBirthA + buf4) <= dateFlA <= dateDeathB:
                            caseName = 'I1'
                elif dateFlB != 0:
                    if (dateDeathB - dateBirthA) <= buf5:
                        if (dateBirthA + buf4) <= dateFlB <= (dateDeathB):
                            caseName = 'I1'
            # I for when dataset B has db
            elif ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)):
                # I2 -> logics for Fl. date A when is present
                if dateFlA != 0:
                    if (dateDeathA - dateBirthB) <= buf5:
                        if (dateBirthB + buf4) <= dateFlA <= dateDeathA:
                            caseName = 'I2'
                # I2 -> logics for Fl. date Bwhen is present
                elif dateFlB != 0:
                    if (dateDeathA - dateBirthB) <= buf5:
                        if (dateBirthB + buf4) <= dateFlB <= (dateDeathA):
                            caseName = 'I2'

        # SCORES TYPE J
            # definition ScoreJ: persons in both datasets have incomplete dates of birth and death (either of the two) in the opposite way, and none has Flourished date
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)):
                # only logics for dates of birth or death
                if (dateBirthA != 0 and dateDeathB != 0):
                    if (dateBirthA + buf4) <= (dateDeathB - dateBirthA) <= buf5:
                        caseName = 'J'
                elif (dateBirthB != 0 and dateDeathA != 0):
                    if (dateBirthB + buf4) <= (dateDeathA - dateBirthB <= buf5):
                        caseName = 'J'

        # SCORES TYPE K
            # definition ScoreK: persons in one dataset have incomplete dates of birth and death (either of the two) plus Flourished date, and persons in the other dataset have none of the two, only Flourished date
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)):
                # K -> Fl. dates match exactly
                if dateFlA == dateFlB:
                    caseName = 'K'
                # K- -> Fl. dates don't match, applies rules when db is present
                elif dateBirthA != 0:
                    if (dateBirthA + buf4) <= dateFlB <= (dateBirthA + buf5):
                        caseName = 'K-'
                elif dateBirthB != 0:
                    if (dateBirthB + buf4) <= dateFlA <= (dateBirthB + buf5):
                        caseName = 'K-'
                # K- -> Fl. dates don't match, applies rules when dd is present
                elif dateDeathA != 0:
                    if (dateDeathA - buf5) <= dateFlB:
                        caseName = 'K-'
                elif dateDeathB != 0:
                    if (dateDeathB - buf5) <= dateFlA:
                        caseName = 'K-'
                # K-- -> Fl. dates don't match (applies rules with the available dates)
                elif (abs(dateFlA - dateFlB) <= buf3):
                    caseName = 'K--'

        # SCORES TYPE L
            # definition ScoreL: persons in one dataset have incomplete dates of birth and death (either of the two) and no Flourished date, persons in the other dataset have no date of birth nor death, but do have Flourished date
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)):
                # L -> when db is present
                if dateBirthA != 0:
                    if (dateBirthA + buf4) <= dateFlB <= (dateBirthA + buf5):
                        caseName = 'L'
                elif dateBirthB != 0:
                    if (dateBirthB + buf4) <= dateFlA <= (dateBirthB + buf5):
                        caseName = 'L'
                # L -> when ddA is present
                elif dateDeathA != 0:
                    # date of Fl. in relation to ddA
                    if dateFlB <= dateDeathA:
                        caseName = 'L-'
                # L -> when ddA is present
                elif dateDeathB != 0:
                    # date of Fl. in relation to ddA
                    if dateFlA <= dateDeathB:
                        caseName = 'L-'

        # SCORES TYPE M
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

        # SCORES TYPE Y
            # definition ScoreY: persons in one dataset have either date, and in the other dataset no dates at all
            elif ((dateBirthA != 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA != 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA != 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA != 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB != 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB != 0 and dateDeathB == 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB != 0 and dateFlB == 0)) or ((dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB != 0)):
                caseName = 'Y'

        # SCORES TYPE Z
            # definition ScoreZ: this group includes persons with no dates at all in both datasets, scores rely on string matching only (no other rules)
            elif (dateBirthA == 0 and dateDeathA == 0 and dateFlA == 0) and (dateBirthB == 0 and dateDeathB == 0 and dateFlB == 0):
                caseName = 'Z'

    # ############################## RUN STRING MATCHING #######################################
            # this rule only applies to cases of type A when the dates are exactly the same (e.g., to match 'Olivarius Vredius' with 'Olivier de Wree')
            if caseName in caseVeryPrecise:
                if rangeScoreVeryLow <= matchScore1 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore1
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
                elif rangeScoreVeryLow <= matchScore2 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore2
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore2'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
            # this part works for the cases that allow for low string matching scores, since there are dates of birth/death/fl to use
            elif caseName in casesPrecise:
                if rangeScoreLow <= matchScore1 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore1
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
                elif rangeScoreLow <= matchScore2 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore2
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore2'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
            # this part works for the cases that don't have many dates available, thus, the string matching has to be higher
            elif caseName in casesLoose:
                if rangeScoreMid <= matchScore1 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore1
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
                elif rangeScoreMid <= matchScore2 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore2
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore2'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
            # depending on the data, these cases can give a lot of noise (incorrect mappings). During test round, case 'Y' was detected as the noisiest. After testing with different matching algorithms
            # to find the one giving the lowest score for the wrong matches, I found that matchScore2 was causing the noise. Thus, here it's removed, and only matchScore1 is used.
            elif caseName in casesNoisy:
                if rangeScoreMid <= matchScore1 <= rangeScoreHigh:
                    scoreNameString = dfA.loc[indexA,
                                              'scoreNameString'] = matchScore1
                    scoreType = dfA.loc[indexA, 'scoreType'] = 'matchScore1'
                    match_nameStringB = dfA.loc[indexA,
                                                'match-personNameB'] = nameStringB
                    match_dateBirthB = dfA.loc[indexA,
                                               'match-dateBirthB'] = dateBirthB
                    match_dateDeathB = dfA.loc[indexA,
                                               'match-dateDeathB'] = dateDeathB
                    match_dateFlB = dfA.loc[indexA, 'match-dateFlB'] = dateFlB
                    match_personIdB = personIdB = dfA.loc[indexA,
                                                          'match-personIdB'] = personIdB
                    mapped_candidates = mapped_candidates.append({
                        'scoreCase': caseName,
                        'scoreNameString': scoreNameString,
                        'scoreType': scoreType,
                        'match_nameStringB': match_nameStringB,
                        'match_dateBirthB': match_dateBirthB,
                        'match_dateDeathB': match_dateDeathB,
                        'match_dateFlB': match_dateFlB,
                        'nameStringA': nameStringA,
                        'dateBirthA': dateBirthA,
                        'dateDeathA': dateDeathA,
                        'dateFlA': dateFlA,
                        'personIdA': personIdA,
                        'match_personIdB': match_personIdB
                        # 'caseA':caseA,
                        # 'scoreTypeA':scoreTypeA
                    }, ignore_index=True, sort=False)
    return mapped_candidates


######
# Personal note Liliana: v44:used for testing this script in cy15 (test7), last use: 21 June, 2022
