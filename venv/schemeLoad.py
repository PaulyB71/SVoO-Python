import xml.etree.ElementTree as ET
import py2neo
from pandas import DataFrame
import requests
import json
import datetime

td=datetime.datetime.now().strftime("%d/%m/%Y")
graph=py2neo.database.Graph("http://127.0.0.1:11001", password="neo")
#Read in XML
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
#Find Company ID from Companies House Number provided in XML
query="match (c:Company_Registration_Number {Number:{crn}})-[r]-(o:Limited_Company) return o.AV_ID"
comp=DataFrame(graph.run(query,parameters={"crn":gcrn}).data())
res=comp.iat[0,0]
print(comp)
print(res)
#Call Companies House API with provided Companies House Number
burl = "https://api.companieshouse.gov.uk/company/"

url = burl+gcrn
resp = requests.get(url, auth=('tcMBImaEo0l0zwpZ_GZVHpju_hEBsHQc0nV9eobc', ''))
stat=resp.status_code
#Check response to ensure Company was found
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
    #Add registered address and set CHN to verified with today's date
    graph.run("merge (o:Limited_Company {AV_ID:{AVID}}) on match set o.Registered_Name = {chrn}", parameters={"AVID":res,"chrn":crn})
    graph.run("match (o:Limited_Company {AV_ID:{AVID}}) merge (a:UK_Structured_Address {Address_Line_1:{AD1}, Post_Town:{TOWN}, Postcode:{POSTCODE}}) ON CREATE set o.Address_Line_2={AD2} MERGE (o)-[:HAS_REGISTERED_ADDRESS_OF]->(a)", parameters={"AVID":res, "AD1":regad1, "AD2":regad2, "TOWN":regadtown, "POSTCODE":regadpostcode})
    graph.run("match (o:Limited_Company{AV_ID:{AVID}}) match (c:Company_Registration_Number {Number:{chn}}) merge (o)-[rel:IS_IDENTIFIED_BY]->(c) on match set rel.Validated=true, rel.Validated_Date={td}",parameters={"AVID": res, "chn": chn, "td":td})
else:
    print('Not found at Companies House')
#Add Scheme info from XML to Graph and build relationship to holding Company along with system client ID
addscheme="match (o:Limited_Company {AV_ID:{gavid}}) merge (s:Scheme {Scheme_Number:{gscno}, Scheme_Name:{gscnm}, Product:{gprod}}) merge (sid:Host_ID {ID:{gsysclt}, Host:{ghost}}) merge (s)-[:IS_OWNED_BY]->(o) MERGE (o)-[:HAS_CLIENT_ID_OF]->(sid)"
graph.run(addscheme,parameters={"gavid":gavid, "gscno":gscno, "gscnm":gscnm, "gprod":gprod, "gsysclt":gsysclt, "ghost":ghost})
#Retreive each policy within the scheme from xml
pson=tree.findall(".//Policy")
nocli=len(pson)
print(nocli)
print(pson)
for i in range(nocli):
    print(i)
    pavi=pson[i].find("./Person/AV_PID")
    pavid=pavi.text
    pn = pson[i].find("./Person/NI_NO")
    pni=pn.text
    phos = pson[i].find("./Person/Client/Host")
    phost=phos.text
    pcln = pson[i].find("./Person/Client/ClientId")
    pclnt=pcln.text
    pcod = pson[i].find("./Person/Contract/Code")
    pcode=pcod.text
    pnam = pson[i].find("./Person/Contract/Name")
    pname=pnam.text
    ppro = pson[i].find("./Person/Contract/Product")
    pprod=ppro.text
    tempprole = pson[i].find("./Person/Contract/Role")
    tprole=tempprole.text
    prole=tprole.upper()
    relrole="HAS_"+prole+"_OF"
    #Add policy to graph with relationship to person and scheme
    addpol = "match (p:Person {AV_PID:{pavid}}) merge (pol:Policy {Policy_Number:{pcode}, Policy_Name:{pname}, Product:{pprod}}) merge (sid:Host_ID {ID:{pclnt}, Host:{phost}}) merge (pol)-[:HAS_POLICYHOLDER_OF]->(p) MERGE (p)-[:HAS_CLIENT_ID_OF]->(sid)"
    graph.run(addpol, parameters={"pavid": pavid, "pcode": pcode, "pname": pname, "pprod": pprod, "pclnt": pclnt,"phost": phost, "prole":relrole})
    po2sc = "match (p:Policy {Policy_Number:{pcode}}), (s:Scheme {Scheme_Number:{gscno}}) merge (p)-[:IS_A_POLICY_IN]->(s)"
    graph.run(po2sc, parameters={"pcode":pcode, "gscno":gscno})
