from lxml import etree
from io import BytesIO

path="C:\\Users\\paul_\\Documents\\SVoO\\Scheme.xml"
class FindClasses(object):
    @staticmethod
    def parse_xml(xml_string):
        parser = etree.XMLParser()
        fs = etree.parse(BytesIO(xml_string), parser)
        fstring = etree.tostring(fs, pretty_print=True)
        element = etree.fromstring(fstring)
        return element

    def find(self, xml_string):
        for parent in self.parse_xml(xml_string).getiterator('connection'):
            for child in parent:
                if child.tag == 'id':
                    print child.text
                    self.find_classes(child)

    @staticmethod
    def find_classes(child):
        for parent in child.getparent():  # traversing up -> connection
            for children in parent.getchildren():  # children of connection -> classes
                for child in children.getchildren():  # child of classes -> class
                    print child.text
        print

if __name__ == '__main__':
    xml_file = open('foo.xml', 'rb')  #foo.xml or path to your xml file
    xml = xml_file.read()
    f = FindClasses()
    f.find(xml)