import requests
import json
import py2neo
import datetime
from pandas import DataFrame

td=datetime.datetime.now().strftime("%d/%m/%Y")
AVID="AVCO102"
graph=py2neo.database.Graph("http://127.0.0.1:11001", password="neo")
burl = "https://api.companieshouse.gov.uk/company/"

query="match (o:Limited_Company {AV_ID:{AV}})-[:IS_IDENTIFIED_BY]->(c:Company_Registration_Number) return c.Number"

comp = DataFrame(graph.run(query, parameters={"AV":AVID}).data())
res=comp.iat[0,0]
url = burl+res
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
    graph.run("merge (o:Limited_Company {AV_ID:{AVID}}) on match set o.Registered_Name = {chrn}", parameters={"AVID":AVID,"chrn":crn})
    graph.run("match (o:Limited_Company {AV_ID:{AVID}}) create (a:UK_Structured_Address {Address_Line_1:{AD1}, Address_Line_2:{AD2}, Post_Town:{TOWN}, Postcode:{POSTCODE}}) CREATE (o)-[:HAS_REGISTERED_ADDRESS_OF]->(a)", parameters={"AVID":AVID, "AD1":regad1, "AD2":regad2, "TOWN":regadtown, "POSTCODE":regadpostcode})
    graph.run("match (o:Limited_Company{AV_ID:{AVID}}) match (c:Company_Registration_Number {Number:{chn}}) merge (o)-[rel:IS_IDENTIFIED_BY]->(c) on match set rel.Validated=true, rel.Validated_Date={td}",parameters={"AVID": AVID, "chn": chn, "td":td})
else:
    print('Not found at Companies House')

