import xml.etree.ElementTree as ET
import py2neo
from pandas import DataFrame
import requests
import json
import datetime

td=datetime.datetime.now().strftime("%d/%m/%Y")
graph=py2neo.database.Graph("http://127.0.0.1:11001", password="neo")

path="C:\\Users\\paul_\\Documents\\SVoO\\Scheme.xml"
tree=ET.parse(path)
root=tree.getroot()
avid=root.find("./Scheme/Org/AV_ID")
gavid= avid.text
crn=root.find("./Scheme/Org/CH_NO")
gcrn=crn.text
host=root.find("./Scheme/Org/Client/Host")
ghost=host.text
sysclt=root.find("./Scheme/Org/Client/ClientId")
gsysclt=sysclt.text
scno=root.find("./Scheme/Org/Contract/Code")
gscno=scno.text
scnm=root.find("./Scheme/Org/Contract/Name")
gscnm=scnm.text
prod=root.find("./Scheme/Org/Contract/Product")
gprod=prod.text
scrl=root.find("./Scheme/Org/Contract/Role")
gscrl=scrl.text
query="match (c:Company_Registration_Number {Number:{crn}})-[r]-(o:Limited_Company) return o.AV_ID"
comp=DataFrame(graph.run(query,parameters={"crn":gcrn}).data())
res=comp.iat[0,0]
print(comp)
print(res)
burl = "https://api.companieshouse.gov.uk/company/"

url = burl+gcrn
resp = requests.get(url, auth=('tcMBImaEo0l0zwpZ_GZVHpju_hEBsHQc0nV9eobc', ''))
stat=resp.status_code
if stat == 200:
    data = resp.json()
    crn=data['company_name']
    chn=data['company_number']
    regad1 = data['registered_office_address']['address_line_1']
    if 'address_line_2' in data:
        regad2 = data['registered_office_address']['address_line_2']
    else:
        regad2 = None
    regadtown = data['registered_office_address']['locality']
    regadpostcode = data['registered_office_address']['postal_code']
    graph.run("merge (o:Limited_Company {AV_ID:{AVID}}) on match set o.Registered_Name = {chrn}", parameters={"AVID":res,"chrn":crn})
    graph.run("match (o:Limited_Company {AV_ID:{AVID}}) create (a:UK_Structured_Address {Address_Line_1:{AD1}, Address_Line_2:{AD2}, Post_Town:{TOWN}, Postcode:{POSTCODE}}) CREATE (o)-[:HAS_REGISTERED_ADDRESS_OF]->(a)", parameters={"AVID":res, "AD1":regad1, "AD2":regad2, "TOWN":regadtown, "POSTCODE":regadpostcode})
    graph.run("match (o:Limited_Company{AV_ID:{AVID}}) match (c:Company_Registration_Number {Number:{chn}}) merge (o)-[rel:IS_IDENTIFIED_BY]->(c) on match set rel.Validated=true, rel.Validated_Date={td}",parameters={"AVID": res, "chn": chn, "td":td})
else:
    print('Not found at Companies House')

addscheme="match (o:Limited_Company {AV_ID:{gavid}}) merge (s:Scheme {Scheme_Number:{gscno}, Scheme_Name:{gscnm}, Product:{gprod}}) merge (s)-[:IS_OWNED_BY]->(o)"
graph.run(addscheme,parameters={"gavid":gavid, "gscno":gscno, "gscnm":gscnm, "gprod":gprod})

pson=tree.findall(".//Policy")
nocli=len(pson)
print(nocli)
print(pson)
for i in range(nocli):
    print(i)
    pavid=pson[i].find("./Person/AV_PID")
    print(pavid.text)
    pni = pson[i].find("./Person/NI_NO")
    print(pni.text)
    phost = pson[i].find("./Person/Client/Host")
    print(phost.text)
    pclnt = pson[i].find("./Person/Client/ClientId")
    print(pclnt.text)
    pcode = pson[i].find("./Person/Contract/Code")
    print(pcode.text)
    pname = pson[i].find("./Person/Contract/Name")
    print(pname.text)
    pprod = pson[i].find("./Person/Contract/Product")
    print(pprod.text)
    prole = pson[i].find("./Person/Contract/Role")
    print(prole.text)
