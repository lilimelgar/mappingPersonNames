# Buffer values for name comparison
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