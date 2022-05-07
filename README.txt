Pfizer Assingment:
Written by Joshua Kalapati

Python script that is able to create files in directory and then compares with 
files from older directory before sending them to an email of choice every 
24 hours. 

domain.yml is the yaml file where domains are collected to be updated for

OLDUpdatedJSONs is a folder containing previous data. Usually this would be pulled
from yesterday to compare to updated values. 
NOTE: Program works so long as there was previously collected data of some sort within
this folder.

UpdatedJSONs is a folder containing the recently grabbed data of JSONs from the
whois website. 

credentials.json is used to get user, password, port, and host for smtp mailing server
to be used within main program of method sendEmail. Please replace with desired email and password 
for credentials to be read proeprly within main method. CUrrent password is a randomly genreate password 
and email.

requirements.txt is just used incase there are other libraries needed when modifications
to the program arise.

docker container is build by running the following command within this files:
    docker build -t image-name:image-tag .

to enter the following after build is done
    docker run -d image-name:image-tag