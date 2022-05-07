import smtplib,yaml, json, os, shutil, ssl
from pathlib import Path
from yaml.loader import SafeLoader
from datetime import datetime
from whoisapi import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

#Loads domains from domains.yml
def loadDomains(file):
    with open(file) as f:
        data = yaml.load(f, Loader=SafeLoader)
        list_of_dict_values = list(data.values())
        readList = list_of_dict_values[0]
    return readList

# takes in domains of readList and begins collecting information for JSON file creation per domain
# directory is created to pointto right folder to store with createJSONFile
# API key must be changed after some time due to using limited trial version
def loadInfo(readList):
    updatedInfo = {} 
    emails = {}
    client = Client(api_key='at_N0Ba1y2hfEWwzMmYBuz2DKepxYf5f')
    directory = "/UpdatedJSONs"
    fileNumber = 0
    for domain in readList:
        whoisCreatedDate = GetCreatedDate(domain, client)
        whoisUpdatedDate = GetUpdatedDate(domain, client)
        whoisExpiresDate = GetExpiresDate(domain, client)
        registrantName = GetRegistrantName(domain, client)
        registrant, administrativeContact, technicalContact, contactEmail = GetEmails(domain, client)
        domainName = GetDomainName(domain, client)
        emails["registrant"] = registrant
        emails["administrativeContact"] = administrativeContact
        emails["technicalContact"] = technicalContact
        emails["contactEmail"] = contactEmail
        updatedInfo["whoisCreatedDate"] = whoisCreatedDate
        updatedInfo["whoisUpdatedDate"] = whoisUpdatedDate
        updatedInfo["whoisExpiresDate"] = whoisExpiresDate
        updatedInfo["registrantName"] = registrantName
        updatedInfo["emails"] = emails
        updatedInfo["domainName"] = domainName
        createJSONFile(updatedInfo, fileNumber, directory)
        fileNumber = fileNumber+1

# takes in dictionary of information along with current directory to create JSON files
# and put each JSON file into the right UpdatedJSONs folder
def createJSONFile(dict, n, directory):
    startLocal = os.getcwd() + "/"
    newLocal = startLocal+directory+"/"
    j = json.dumps(dict, indent=4)
    with open(f'updated_info{n}.json', 'w') as f:
        f.write(j)
        f.close()
    shutil.move(startLocal+f'updated_info{n}.json', newLocal+f'updated_info{n}.json')

# compares the folders of UpdatedJSONs and OLDUpdatedJSONs through compareJSONs method
# attachment list is created and updated through compareJSONs method before pushing 
# to sendEmail method with a given email that is currently but should be replaced.
def compareFolders(server,user):
    attachmentList = []
    oldDirectory = os.getcwd() + "/OLDUpdatedJSONs"
    newDirectory = os.getcwd() + "/UpdatedJSONs"
    pathlistOld = Path(oldDirectory).rglob('*.json')
    pathListNew = Path(newDirectory).rglob('*.json')
    for newpath, oldpath in zip(pathlistOld, pathListNew):
        oldData = open(oldpath)
        newData = open(newpath)
        oldData = json.load(oldData)
        newData = json.load(newData)
        compareJSONs(oldData,newData,attachmentList)
    sending_ts = datetime.now()
    sendEmail(server, user, 
        to=["barbequebarbequebarbeque@gmail.com"], 
        subject= "Updated JSON files %s" % sending_ts.strftime('%Y-%m-%d %H:%M:%S'), 
        body="Daily updates of JSON files",
        attachments=attachmentList)

# Compares old and new JSON files and if there is a difference, add it to attachmentList
# Uses sorting method to reorder dictionary for easier comparison
def compareJSONs(OldJSON, NewJSON, attachmentList):
    if sorting(OldJSON) != sorting(NewJSON):
        attachmentList.append(NewJSON)

# sorts given dictionary type item to be used for sorting
def sorting(item):
    if isinstance(item, dict):
        return sorted((key, sorting(values)) for key, values in item.items())
    if isinstance(item, list):
        return sorted(sorting(x) for x in item)
    else:
        return item

# Connects to server with user, password, host, and port
# Connect to an SMTP server. Note, this function assumes that the SMTP server uses TTLS connection
def connectToServer(user, password, host, port):
    server = smtplib.SMTP(host=host,port=port)
    server.starttls()
    server.login(user=user, password=password)
    return server

# Sends Email with attachments of all JSON files that have been found to been updated
def sendEmail(server, user, to, subject, body, attachments):
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = ", ".join(to)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for data in attachments:
        attachment = MIMEText(json.dumps(data))
        attachment.add_header('Content-Disposition', 'attachment', 
            filename="updated_info.json")
        msg.attach(attachment)

    return server.sendmail(user, to, msg.as_string())

# Gets Creation Date of domain along with client info
def GetCreatedDate(domain, client):
    res = client.data(domain)
    if res.created_date_raw:
            dateCreation = res.created_date_raw
    else:
        if(res.registry_data['created_date_raw']):
            dateCreation = res.registry_data['created_date_raw']
        else:
            dateCreation = res.audit['created_date_raw']
    return dateCreation

# Gets Update Date of domain along with client info
def GetUpdatedDate(domain, client):
    res = client.data(domain)
    if res.updated_date_raw:
            dateUpdate = res.updated_date_raw
    else:
        if(res.audit):
            dateUpdate = res.audit['updated_date_raw']
        else:
            dateUpdate = "N/A"
    return dateUpdate

# Gets Expiration Date of domain along with client info
def GetExpiresDate(domain, client):
    res = client.data(domain)
    if res.expires_date_raw:
            ExpiresDate = res.expires_date_raw
    else:
        if(res.registry_data['expires_date_raw']):
            ExpiresDate = res.registry_data['expires_date_raw']
        else:
            ExpiresDate = "N/A"
    return ExpiresDate

# Gets Registrant Name of domain along with client info
def GetRegistrantName(domain, client):
    res = client.data(domain)
    if res.registrar_name:
        nameRegistrant = res.registrar_name
    else:
        nameRegistrant = "N/A"
    return nameRegistrant

# Gets Get all possible emails of domain along with client info
def GetEmails(domain, client):
    res = client.data(domain)
    if res.registrant:
        if res.registrant["email"]:
            regEmail = res.registrant["email"]
        else:
            regEmail = "N/A"
    else:
        regEmail = "N/A"
    if res.administrative_contact:
        if res.administrative_contact["email"]:
            adminEmail = res.administrative_contact["email"]
        else:
            adminEmail = "N/A"
    else:
        adminEmail = "N/A"
    if res.technical_contact:
        if res.technical_contact["email"]:
            techEmail = res.technical_contact["email"]
        else:
            techEmail = "N/A"
    else:
        techEmail = "N/A"
    if res.contact_email:
        contactEmail = res.contact_email
    else:
        contactEmail = "N/A"
    
    return regEmail, adminEmail, techEmail, contactEmail

# Gets Domain Name of domain along with client info
def GetDomainName(domain, client):
    res = client.data(domain)
    return res.domain_name

# main method for nicer look of program
# Opens credentials.json to create dictionary with user, password, host, and port
# loads the domains of the yml file to be used in loadInfo
# open the server through connectToServer method and then runs compareFolders method
# once all done, close server
def main():
    with open("credentials.json", mode="r") as f:
        credentials = json.load(f)
        
    USER = credentials["user"]
    PASSWORD = credentials["password"]
    HOST = credentials["smtp_host"]
    PORT = credentials["smtp_port"]

    info = loadDomains('domains.yml')
    loadInfo(info)
    server = connectToServer(user=USER,password=PASSWORD,host=HOST,port=PORT)
    compareFolders(server=server, user=USER)
    server.quit()

if __name__=="__main__":
    main()
