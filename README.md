## Disclaimer: This repository contains code and data for testing purposes only

# Mapping historical persons names

The purpose of this project is to help historians who struggle in comparing person names. Often, they need to determine whether a person from 'ListA' is the same as a person from 'ListB'. This happens for instance, when a historian has a corpus of historical names which originated from printed letter edition A and another corpus of historical names which originated from a controlled authority list (for example VIAF). The researcher would like to see which of the names he is working with (ListA) map to the VIAF file (ListB). Because it is very common when working with historical data to come across different name variants for the same person, determining which names/persons are the same is not simple. It happens very often that persons with the same 'name string' may be different persons, born in different years, or that persons with different name strings are actually the same person.

With this script, person names from any ListA are compared to person names from any ListB, trying to identify which persons (based on their names) could be equivalent. This script uses string matching algorithms and rules based on the (if available) information of dates of birth/death or floriat (active year) of a person. It outputs a list of candidates with scores (explained in the "Running the script" section below). The user can then decide which of the candidates are valid and then obtain the mapped Ids with the benefits that this brings afterwards (reusability, adding extra information to the persons, finding works created by those persons, etc.).

This script has been developed during the course of the SKILLNET project. The SKILLNET project ("Sharing Knowledge in Learned and Literary Networks") is an European Research Council (ERC)-funded project led by Dirk van Miert at Utrecht University. This project investigates the ideals of sharing knowledge as a legacy of a bottom-up social network of scholars and scientists from the Early Modern period. These scholars transcended religious, political and linguistic boundaries through their correspondence with one another. From about 1500 to around 1800, the ‘citizens’ of this European knowledge-based civil society referred to their own community as the ‘Republic of Letters’. 

We mostly used this script to cluster person names from different letter datasets, and to assign mapped Ids from different authority lists/vocabularies to them. Because the script proved to be useful when comparing long lists of person names which were difficult to check manually, we offer it to the community of historians as a project deliverable.


# Running the script

- The script is written in Python 3.7.10
- It uses string matching algorithms from the fuzzywuzzy library (https://pypi.org/project/fuzzywuzzy/) (version 0.18.0)
- To run this project, clone the repository to your machine (with git clone, or simply download the zip file)
- First, open the jupyter notebook available in the src folder, called "MappingPersonNames.ipynb"
- To use the script with your own lists of names, format the lists according to the structure explained in the section "Data formatting" below (also in the jupyter notebook there are explanations), and upload them as .csv files to the folder "data/raw". Name the files: ListA.csv and ListB.csv. For testing purposes, you can just simply use the provided sample lists in the Data/raw folder
- Before running the notebook, paste the core of the mapping script, available here ({your path to repository}/mappingPersonNames/src/personMappingScript-versionNo....py) in the cell indicated in Step5 of the notebook. The script works with data structured as indicated below. If changes are done (e.g., new columns are added), this core script, and the notebook code have to be adapted. Otherwise, if the structure below is followed, just pasting the script and running the notebook should provide the expected output with mapping candidates.
- Run the notebook
- Locate the output file in the data/processed folder
- To evaluate the mapping candidates, you could upload the resulting file to Open Refine (https://openrefine.org/), which makes it easier to filter, sort, and mark the correct candidates (e.g., using a star)
- You can determine whether two candidates are the correct mapping using the scores. There are three different types:
	- Score for the amount of data available: this is a one letter score (from A to Z) in which A means that person data was very complete in both lists. Complete means that, besides the name string, persons also had dates of birth and death. On the contrary, Z, indicates that there were only strings to map. Thus, a score of type D is better than a score of type H, since it means that there was more data available to compare the names and, then determine how equal they were. These scores were manually created using a table with all the combinatories possible between dates of birth, death, or floriat (which means the year in which a person was active). This table is available here: {repositoryPath}/mappingPersonNames/docs/other/casesScriptPersonClusteringversion20220620.xlsx.
	- String matching score: this is a number between 50 (usually the minimum score allowed) to 100, where 100 means that the strings were exactly the same (e.g., 'Sigismondo Chigi' = 'Sigismondo Chigi' --> 100). These scores are obtained using a Python library called Fuzzy Wuzzy (https://pypi.org/project/fuzzywuzzy/).
	- Full matching score: this is a number (up to 100) that indicates how similar the name from ListA is to the name from ListB using all available information: name string plus the dates (e.g., 'Sigismondo Chigi^1649^1678^0 compared to 'Sigismondo Chigi^0^1678^0 give a score of 91).
- Once you have marked the correct mappings, you can decide what to do with the mappings depending on the purpose (e.g., if you used the mappings to know which persons were the same, or if you used to integrate the Ids of ListB into ListA, or if you used it to obtain dates of birth/death/floriat that were not present in your initial list...)


# Data formatting
- Format the file as a .csv (comma separated file) as follows:
personIdA,nameStringA,dateBirthA,dateDeathA,dateFlA
- Meaning of the columns
personIdA: any Id used to identify a person in listA. It can be a recognized ID (e.g., VIAF, wikidata, etc.) or your own Ids (e.g., skp001)
personIdB: the same, but for listB
dateBirthA: the year of birth of the person from ListA. Leave empty or use a zero '0' if not known. 
dateBirthB: the year of birth of the person from ListB. Leave empty or use a zero '0' if not known
dateDeathA: the year of death of the person from ListA. Leave empty or use a zero '0' if not known
dateDeathB: the year of death of the person from ListB. Leave empty or use a zero '0' if not known
dateFlA: floriat date from person in ListA (year in which it is known a person without dates of birth/death was alive)
dateFlB: floriat date from person in ListB (year in which it is known a person without dates of birth/death was alive)

Notes:
- Years have to be in the form YYYY. Notes or uncertainty marks should NOT be added. If they exist, use a separated column. But, take into account that, if extra columns are added in addition to the columns above, the script has to be adapted to incorporate them in the output.
- Be careful of not having commas as part of the name string or, if they are, the name string should be wrapped in quotation marks (e.g., "Charles de Sainte-Maure, duc de Montausier"). Preferable, replace those commas by semicolons, otherwise, there may be a problem when parsing the data.

# Contributing

You can submit Github issues to us. These are useful, for instance, if you detect errors in the data, or if you want to contribute to improve the code, or if you have any questions or suggestions.

# Versioning

We name the versions of our data and scripts with the date of their latest update. The first version submitted to the python advisor has version date 20220621 (this is version 1).

# References

- t.b.d.

## License

This project is licensed under the terms of the [MIT License](/LICENSE.md)

# Credits and acknowledgments

## Authors responsibilities

- **Liliana Melgar-Estrada**: Author of the script, responsible for data preparation and depositing.
- **Jelte van Boheemen**: advisor... (t.b.d.)

## Acknowledgements 
Contributors who participated in this project:
- Dirk van Miert (SKILLNET project funding)
- Ingeborg van Vugt (testing)
- Rosalie Versmissen (testing)
- RDM support Utrecht University (feedback during the course "Writing reproducible Code")
- Digital Humanities Center Utrecht University (for providing Python advisor)
