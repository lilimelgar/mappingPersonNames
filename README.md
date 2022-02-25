# Mapping historical persons names

The purpose of this project is to help historians who struggle in comparing person names in two lists, trying to identify which persons (names) could be equivalent. This happens for instance, when a historian has a corpus of historical names which originated from printed letter edition A and another corpus of historical names which originated from a controlled authority list (for example VIAF). The researcher would like to see which of the names he is working with (listA) map to the VIAF file (listB), to obtain their Ids with the benefits that this brings afterwards (reusability, adding extra information to the persons, finding works created by those persons, etc.).

This package outputs a list of candidates with scores (ToDo: explain what the scores mean). The user can then decide which of the candidates are valid matches.

# Installation

- The script is written in Python 3.7.10
- It uses string matching algorithms from the fuzzywuzzy library (link here to library) (version 0.18.0)
- To run this project, clone the repository to your machine (with git clone, or simply download the zip file)
- If you use a Python IDE (e.g., Visual studio), open the script in the src file (see structure below) called "personMapping_complete.py"
- To use the script with your own lists of names, format the lists according to the structure explained in the section "Data formatting" below, and upload them as .csv files to the folder "data/raw". Name the files: listA.csv and listB.csv. For testing purposes, you can just simply use the provided sample lists in the Data/raw folder.


# Data formatting
- Format the file as follows:
personIdA,personStrIdA,nameStringA,dateBirthA,dateDeathA,dateFlA
- Meaning of the columns
personIdA: any Id used to identify a person in listA. It can be a recognized ID (e.g., VIAF, wikidata, etc.) or your own Ids (e.g., skp001)
personIdB: the same, but for listB
personStrIdA: it is a joined column of nameStringA + dateBirthA + dateDeathA + dateFlA. ##ToDo: this is not needed for the mappings, take it out of the script
personStrIdB: same as personStrIdA but for persons in listB
dateBirthA: the date of birth of the person. Leave empty if not known
dateBirthB:
dateDeathA:
dateDeathB:
dateFlA: floriat date (year in which it is known a person without dates of birth/death was alive)
dateFlB: 


## Project organization
- PG = project-generated
- HW = human-writable
- RO = read only
```
.
├── .gitignore
├── CITATION.md
├── LICENSE.md
├── README.md
├── requirements.txt
├── bin                <- Compiled and external code, ignored by git (PG)
│   └── external       <- Any external source code, ignored by git (RO)
├── config             <- Configuration files (HW)
├── data               <- All project data, ignored by git
│   ├── processed      <- The final, canonical data sets for modeling. (PG)
│   ├── raw            <- The original, immutable data dump. (RO)
│   └── temp           <- Intermediate data that has been transformed. (PG)
├── docs               <- Documentation notebook for users (HW)
│   ├── manuscript     <- Manuscript source, e.g., LaTeX, Markdown, etc. (HW)
│   └── reports        <- Other project reports and notebooks (e.g. Jupyter, .Rmd) (HW)
├── results
│   ├── figures        <- Figures for the manuscript or reports (PG)
│   └── output         <- Other output for the manuscript or reports (PG)
└── src                <- Source code for this project (HW)

```


## License

This project is licensed under the terms of the [MIT License](/LICENSE.md)
