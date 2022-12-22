[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7473692.svg)](https://doi.org/10.5281/zenodo.7473692)

Disclaimer: The data added to this repository is for testing purposes only

# Mapping historical persons names

The purpose of this project is to help historians who struggle in comparing person names. Often, they need to determine whether a person from 'ListA' is the same as a person from 'ListB'. This happens for instance, when a historian has a corpus of historical names which originated from printed letter edition A and another corpus of historical names which originated from a controlled authority list (for example VIAF). The researcher would like to see which of the names he is working with (ListA) map to the VIAF file (ListB). Because it is very common when working with historical data to come across different name variants for the same person, determining which names/persons are the same is not simple. It happens very often that persons with the same 'name string' may be different persons, born in different years, or that persons with different name strings are actually the same person.

With this script, person names from any ListA are compared to person names from any ListB, trying to identify which persons (based on their names) could be equivalent. This script uses string matching algorithms and rules based on the (if available) information of dates of birth/death or floriat (active year) of a person. It outputs a list of candidates with scores (explained in the "Running the script" section below). The user can then decide which of the candidates are valid and then obtain the mapped Ids with the benefits that this brings afterwards (reusability, adding extra information to the persons, finding works created by those persons, etc.).

This script has been developed during the course of the SKILLNET project. The SKILLNET project ("Sharing Knowledge in Learned and Literary Networks") is an European Research Council (ERC)-funded project led by Dirk van Miert at Utrecht University. This project investigates the ideals of sharing knowledge as a legacy of a bottom-up social network of scholars and scientists from the Early Modern period. These scholars transcended religious, political and linguistic boundaries through their correspondence with one another. From about 1500 to around 1800, the ‘citizens’ of this European knowledge-based civil society referred to their own community as the ‘Republic of Letters’. 

We mostly used this script to cluster person names from different letter datasets, and to assign mapped Ids from different authority lists/vocabularies to them. Because the script proved to be useful when comparing long lists of person names which were difficult to check manually, we offer it to the community of historians as a project deliverable.


# Usage

## Step1: Prepare your data for the mappings

This script will help you to compare two lists of person names. Thus, the first step is to prepare those lists. Each list should be in a separate .csv file (comma separated file). 

- Name each of the two files in this way: ListA.csv and ListB.csv

- Each file should have a minimum of five columns, with the column headers named as follows:

	- For ListA.csv --> personIdA,nameStringA,dateBirthA,dateDeathA,dateFlA
	- For ListB.csv --> personIdB,nameStringB,dateBirthB,dateDeathB,dateFlB

- Meaning of the columns
personId: any Id used to identify a person in listA. It can be a recognized ID (e.g., VIAF, wikidata, etc.) or your own Ids (e.g., skp001)
dateBirth: the year of birth of the person from ListA. Leave empty or use a zero '0' if not known. 
dateDeath: the year of death of the person from ListA. Leave empty or use a zero '0' if not known
dateFl: floriat date from person in ListA (year in which it is known a person without dates of birth/death was alive)

To take into account:

- Years have to be in the form YYYY. 

- Be careful of not having commas as part of the name string or, if they are, the name string should be wrapped in quotation marks (e.g., "Charles de Sainte-Maure, duc de Montausier"). Preferable, replace those commas by semicolons, otherwise, there may be a problem when parsing the data. Ideally, separate "duc de Montausier" to the name, and put that piece of information on a column called, for instance, "role".

- Notes, dates, roles, or uncertainty marks should NOT be added to the names themselves. For example, these strings below are NOT a good practice for names nor for dates: 
	- Johannes Henricus van der Palm (1763-1840)
	- Aarnout van Beaumont ca. 1605-1678
	- graaf Ernst von Kaunitz 1671 fl.
	- 174X

Instead, try to separate the data in the specific columns to which they belong (e.g., dateBirth), and add additional columns to indicate uncertainty (e.g., "is_dateBirth_certain", filled in with the value "y" or "n"). 

- The script works by default with the five columns described above, but of course more columns can be added to your data. In that case, take into account that, if extra columns are added in addition to the columns above, the script has to be adapted to incorporate them in the output.

- A limitation of this script is that, if a date is uncertain and there is a range within which the date of birth occurs (e.g., between 1630 anad 1635) the script won't handle those ranges. Thus, please choose a specific year, for example, 1632 as the year of birth, and then use the "buffers" added to the configuration file (more on this later) to indicate how many years of difference you would like to tolerate when evaluating the mapping between two persons.

- Place the two files in the folder: ./data/raw

## Step2: Decide how you will run the script

The script that runs the mappings is written in Python (v.3.9.7) via a jupyter notebook (anaconda version 1.9.0), it uses string matching algorithms from the fuzzywuzzy library (https://pypi.org/project/fuzzywuzzy/) (version 0.18.0). You have three options to choose from for running the script depending on your familiarity with scripts:

### Option1: if you are familiar with running scripts on your own

- install [Anaconda](https://docs.anaconda.com/anaconda/install) on your system
- clone the git repository to your machine, or simply download and extract the zip file
- create a new Anaconda environment that contains everything necessary to run the script (use the requirements.txt file)
```shell
conda env create
```
- starting Jupyter notebooks
```shell
conda activate personNames
jupyter notebook
```
This will open Jupyter in your default web browser.

### Option2: if you are not familiar with running scripts on your own

Instead of installing and using programs on your own computer, you can use a cloud service. We suggest, for example:

- go to Google Colaboratory (the Google cloud service for running jupyter notebooks): https://colab.research.google.com/
- use the option "Github" and enter the URL of this repository, and then click on the icon "open notebook in new tab"  (image below)

![Google Colaboratory](https://github.com/lilimelgar/mappingPersonNames/blob/main/docs/other/google_colab_screenshot.png?raw=true)


## Step3: Running the script

- Open the jupyter notebook available in the src folder, called "MappingPersonNames.ipynb" using one of the two options above.

- To use the script with your own lists of names, format the lists according to the structure explained in the section "Step1: Prepare your data for the mappings" above. and upload the .csv files to the folder "data/raw". Name the files: ListA.csv and ListB.csv. For testing purposes, we have added two sample lists to the data/raw folder.

- You can simply "run all cells", and then you will get as an output a .csv file with a list of mapping candidates (you can find the output file in the data/processed folder). These are the suggested mappings, which still require a manual check to determine which ones are actually correct.

### Step 3.1: Adjust the script

If you run the notebook as suggested above, you will be using the default settings. However, it is very important that you know your datasets very well in order to determine which parameters you should adapt. For example:

- You can set up the "buffers" that you want to allow in the mappings. For example, with names from the 15th or 16th century it is possible that, due to changes in the calendar (from the Julian to the Gregorian calendar), or also because uncertainty, the years of birth or death of the persons may not be exactly the same in two different lists. Thus, you can decide if you tolerate a difference of zero, one, two, or even more years. There are also other "buffers" that you can set up, for example, what is the maximum life expectancy (it could be 80, or even 100 years, depending on what you think it's common in your dataset). The configuration file is located here: /mappingPersonNames/src/config.py. You can also set up these parameters directly in the notebook (you will be pointed there to the cell where you can do this).

- You can also change the default settings in the main script. That script is located here: /mappingPersonNames/src/personMappingScript.py. When you run the jupyter notebook, this script is "called" from within the jupyter notebook. But you can go directly to the script and tweak some of the parameters, for example:

	- choose which string matching algorithm you want to use (these are included in the manual of the Fuzzy Wuzzy library (https://pypi.org/project/fuzzywuzzy) which we use in the script). For example, if in ListA your names are in the name + last name order (Christiaan Huygens), and in ListB your names are in inverted order (Huygens, Christiaan), you may want to use the "fuzz.token_sort_ratio" algorithm (which is specified in the section "# Algorithm to be used" of the script.

	- You can also change the scores that you want to use as mininum, middle or maximum. For this, it's important to understand that the core of the mapping script is based on the use of a very simple logics between the years of birth, death, and floriat (=active) years of a person. These rules were pre-written on a table, in order to account for all the possible combinations (the table with the cases is located here: /mappingPersonNames/docs/other/casesScriptPersonClusteringversion20220620.xlsx). The script written in Python uses those rules in order to classify the case to which a pair of personA-personB combination belongs to. Once the case is detected, it uses a letter to classify it (from A to Z, where A is the case with more information, for example: the case with richer information is that in which two persons have years of birth and death, which is named as case A). For the A cases, one can tolerate lower scores in the evaluation of the matching between the strings, because the years of birth and death can be used to assess whether they are good mapping candidates or not. For example:
		- having this row in ListA: p001,Chistiaan Huygens,1629,1695,0 and this row in ListB: p008,Ch. Huygens,1629,1695,0
		- if you use the algorithm fuzz.ratio, which compares the stings in order, you will get a score of 69 for the matching between the name strings "Christiaan Huygens" and "Ch. Huygens".
		- if you set up the range parameters in the script (section "# String score ranges") to the following:
			- rangeScoreVeryLow = 60 
			- rangeScoreLow = 70
			- rangeScoreMid = 80
			- rangeScoreHigh = 100
		- then this case will be detected as a good matching candidate, because it is a "caseVeryPrecise" (type A, due to the presence of the dates). 
		- on the contrary, if the name on ListB didn't have years of birth nor of death, it wouldn't be taken as a mapping candidate, because the pair would be classified as Case X, which falls into the "noisy" cases, that only take scores that are between the rangeScoreMid and the rangeScoreHigh.
		- of course, you can set the score ranges lower to also capture these case as a candidate, but then you will be faced with a longer list of candidates to evaluate manually.

## Step4: Evaluate the mapping candidates
- Once you run the script, you can locate the output file in the data/processed folder. This is also a .csv file which contains in every row a pair of names that are considered to be the same persons according to the parameters set above.
- To evaluate the mapping candidates, you could upload the resulting file to Open Refine (https://openrefine.org/), which makes it easier to filter, sort, and mark the correct candidates (e.g., using a star). But you can also use a spreadsheet, or the .csv file directly.
- You can determine whether two candidates are the correct mapping using the scores. There are three different types of scores: (a) the string matching score (which only looks at the similitud between the name string), (b) the scoreCase (which is the type of pair, named with a letter between A and Z depending on the amount of information available, as explained above), and (c) a verbose score called "ScoreMappedVersionsNotChangedis100" which compares the similitude between the name string plus the dates as a whole (as if they were an entire name string) between the two candidates.
- Once you have marked the correct mappings, you can decide what to do with the mappings depending on the purpose (e.g., if you used the mappings to know which persons were the same, or if you used to integrate the Ids of ListB into ListA, or if you used it to obtain dates of birth/death/floriat that were not present in your initial list...)


# Contributing

You can submit Github issues to us. These are useful, for instance, if you detect errors in the script, or if you want to contribute to improve the code, or if you have any questions or suggestions.

# Versioning

We name the versions of our data and scripts with the date of their latest update. The first version submitted to the python advisor has version date 20220621 (this is version 1).

# References

- Cohen, A. (2022). fuzzywuzzy: Fuzzy string matching in python (0.18.0) [Python]. Retrieved December 22, 2022, from https://github.com/seatgeek/fuzzywuzzy
- Soma, Jonathan (2017). "Fuzzing matching in Pandas with FuzzyWuzzy". http://jonathansoma.com/lede/algorithms-2017/classes/fuzziness-matplotlib/fuzzing-matching-in-pandas-with-fuzzywuzzy/
- Nehme, Adel (2020). "Fuzzy String Matching in Python". https://learn.datacamp.com/courses/cleaning-data-in-python


## License

This project is licensed under the terms of the [MIT License](/LICENSE.md)

# Credits and acknowledgments

## Authors responsibilities

- **Liliana Melgar-Estrada**: Author of the script, responsible for data preparation and depositing.
- **Jelte van Boheemen**: advisor and code reviewer from the Digital Humanities Center at Utrecht University (https://www.uu.nl/medewerkers/JvanBoheemen)

## Acknowledgements 
Contributors who participated in this project:
- Dirk van Miert (SKILLNET project funding)
- Ingeborg van Vugt (testing)
- Rosalie Versmissen (testing)
- RDM support Utrecht University (feedback during the course "Writing reproducible Code")
- Digital Humanities Center Utrecht University (for providing Python advisor)
