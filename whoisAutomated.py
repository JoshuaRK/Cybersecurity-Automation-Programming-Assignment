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

def createJSONFile(dict, n, directory):
    startLocal = os.getcwd() + "/"
    newLocal = startLocal+directory+"/"
    j = json.dumps(dict, indent=4)
    with open(f'updated_info{n}.json', 'w') as f:
        f.write(j)
        f.close()
    shutil.move(startLocal+f'updated_info{n}.json', newLocal+f'updated_info{n}.json')

def compareFolders(server,user):
    attatchmentList = []
    oldDirectory = os.getcwd() + "/OLDUpdatedJSONs"
    newDirectory = os.getcwd() + "/UpdatedJSONs"
    pathlistOld = Path(oldDirectory).rglob('*.json')
    pathListNew = Path(newDirectory).rglob('*.json')
    for newpath, oldpath in zip(pathlistOld, pathListNew):
        oldData = open(oldpath)
        newData = open(newpath)
        oldData = json.load(oldData)
        newData = json.load(newData)
        compareJSONs(oldData,newData,attatchmentList)
    sending_ts = datetime.now()
    send_message(server, user, 
        to=["barbequebarbequebarbeque@gmail.com"], 
        subject= "Updated JSON files %s" % sending_ts.strftime('%Y-%m-%d %H:%M:%S'), 
        body="Daily updates of JSON files",
        attachments=attatchmentList)

def compareJSONs(OldJSON, NewJSON, attatchmentList):
    if sorting(OldJSON) != sorting(NewJSON):
        attatchmentList.append(NewJSON)

def sorting(item):
    if isinstance(item, dict):
        return sorted((key, sorting(values)) for key, values in item.items())
    if isinstance(item, list):
        return sorted(sorting(x) for x in item)
    else:
        return item

def connect2server(user, password, host, port):
    """ Connect to an SMTP server. Note, this function assumes that the SMTP
        server uses TTLS connection """
    server = smtplib.SMTP(host=host,port=port)
    server.starttls()
    server.login(user=user, password=password)
    return server

def send_message(server, user, to, subject, body, attachments):
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

def GetRegistrantName(domain, client):
    res = client.data(domain)
    if res.registrar_name:
        nameRegistrant = res.registrar_name
    else:
        nameRegistrant = "N/A"
    return nameRegistrant

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

def GetDomainName(domain, client):
    res = client.data(domain)
    return res.domain_name

def main():
    with open("credentials.json", mode="r") as f:
        credentials = json.load(f)
        
    USER = credentials["user"]
    PASSWORD = credentials["password"]
    HOST = credentials["smtp_host"]
    PORT = credentials["smtp_port"]

    info = loadDomains('domains.yml')
    loadInfo(info)
    server = connect2server(user=USER,password=PASSWORD,host=HOST,port=PORT)
    compareFolders(server=server, user=USER)
    server.quit()

if __name__=="__main__":
    main()
