import xml.etree.ElementTree as ET
import sys

class Part:
    def __init__(self,type,id,name): #add cardinality
        self.type = type
        self.id = id
        self.name = name
        #self.cardinality = cardinality

    def __repr__(self):
        return 'Type: {}, UId: {}, Name: {}'.format(self.type, self.id, self.name)

class Wire:
    def __init__(self,id):
        self.id = id
        self.connections = {}
    def add_connection(self,partID,name):
        self.connections[partID] = name

def main():
    tree = ET.parse(sys.argv[1])
    print('Parsing {}'.format(sys.argv[1]))
    root = tree.getroot()

    data = root[2][1][1][0][0][0] # Parent node of all parts and wires
    print(data)
    parts = data[0]
    wires = data[1]
    parts_list = []
    wires_list = []

    for part in parts:
        name = 'Special'    # If no name is found, it is a special part
        id = ''
        type = 'GlobalVariable'
        #cardinality = -1
        if part.tag[-6:] == 'Access':                    # Standard Global variables
            name = part[0][0].attrib.get("Name")
        else:                                            # Coils and Contacts
            type = part.attrib.get("Name")
        id = part.attrib.get("UId")
        parts_list.append(Part(type,id,name))            # Add part to list of parts

    for wire in wires:
        id = ''
        name = 'IdentCon'   # If no name is found, it is a identcon
        id = wire.attrib.get('UId')
        temp_wire = Wire(id)
        for connection in wire:
            if 'Name' in connection.attrib:
                name = connection.attrib.get("Name")
            temp_wire.add_connection(id,name)
        wires_list.append(temp_wire)                     # Add wire to list of wires

    print('Parsed {} parts and {} wires'.format(len(parts_list),len(wires_list)))
    file_name = '{}.txt'.format(sys.argv[1][:-4])
    with open(file_name,'w') as file:
        file.write('Parts:\n')
        for part in parts_list:
            file.write('Type: {}, UId: {}, Name: {}\n'.format(part.type, part.id, part.name))

        file.write('\nWires:\n')
        for wire in wires_list:
            file.write('UId: {}, Connections: {}\n'.format(wire.id, wire.connections))

    print('Wrote file "{}"'.format(file_name))


if __name__ == '__main__':
    main()
