Pfizer Assingment:
Written by Joshua Kalapati

Python script that is able to create files in directory and then compares with 
files from older directory before sending them to an email of choice every 
24 hours. 

OLDUpdatedJSONs is a folder containing previous data. Usually this would be pulled
from yesterday to compare to updated values. 

UpdatedJSONs is a folder containing the recently grabbed data of JSONs from the
whois website. 

docker container is build by running the following command within this files:
    docker build -t image-name:image-tag .

to enter the following after build is done
    docker run -d image-name:image-tag