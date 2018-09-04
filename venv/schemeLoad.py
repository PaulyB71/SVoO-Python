import xml.etree.ElementTree as ET
path="C:\\Users\\paul_\\Documents\\SVoO\\Scheme.xml"
tree=ET.parse(path)
root=tree.getroot()
for ai in root.findall("./Scheme/Org/AV_ID"):
    avid=(ai.text)
    print(avid)
for cn in root.findall("./Scheme/Org/CH_NO"):
    crn=(cn.text)
    print(crn)
for hs in root.findall("./Scheme/Org/Client/Host"):
    host=(hs.text)
    print(host)
for cid in root.findall("./Scheme/Org/Client/ClientId"):
    sysclt=(cid.text)
    print(sysclt)
for sn in root.findall("./Scheme/Org/Contract/Code"):
    scno=(sn.text)
    print(scno)
for nm in root.findall("./Scheme/Org/Contract/Name"):
    scnm=(nm.text)
    print(scnm)
for sp in root.findall("./Scheme/Org/Contract/Product"):
    prod=(sp.text)
    print(prod)
for sr in root.findall("./Scheme/Org/Contract/Role"):
    scrl=(sr.text)
    print(scrl)
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
