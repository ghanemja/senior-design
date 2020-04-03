import xml.etree.ElementTree as ET
import sys
import re
import os


class Node:
    def __init__(self, node_type, arguments = None):
        self.node_type = node_type
        if arguments is None:
            arguments = []
        self.arguments = arguments
    
    def __str__(self):
        n = 'no_arguments'
        if self.arguments is not '':
            n = '[{}]'.format(', '.join(self.arguments))
        return '{} {}'.format(self.node_type, n)

def parse_l5x():


    try:
        tree = ET.parse(sys.argv[1])
        print('\nParsing {}'.format(sys.argv[1]))
        root = tree.getroot()
        filename = sys.argv[1][:-4]
    except:
        print('\nPlease enter valid .L5X file in form "python allenbradley_parser.py example.L5X"\n')
        sys.exit()
    
    # Determine logical rungs
    try:
        MainProgram = root.find('Controller/Programs/Program[@Name="MainProgram"]')
        rungs_data = MainProgram.find('Routines/Routine[@Name="MainRoutine"]/RLLContent')
        rungs = []
        
        counter = 0
        for rung in rungs_data:
            rung_text = rung.find('Text').text.strip()[:-1].replace(' ','')
            rungs.append('{}: {};\n'.format(counter, rung_text))
            counter += 1    
    except:
        print('\nError Parsing Rungs\n')
        sys.exit()
    
    
    # Extract timer information
    Tags = MainProgram.find('Tags')
    for rung in rungs:
        parts = rung.split(')')[:-1]
        for part in parts:  
            while not part[0].isalpha():
                part = part[1:]
            if part[:3] == 'TON':
                timer_name = part[4:].split(',')[0]
                timer_tag = Tags.find('Tag[@Name="{}"]'.format(timer_name))
                timerPRE = timer_tag.find('Data[@Format="Decorated"]/Structure/DataValueMember[@Name="PRE"]')
                print(timer_name)
                print(timerPRE.attrib['Value'])
            
        
    # Combine rungs into text
    hashigo_text = ''
    for rung in rungs:
        hashigo_text += rung
    
    
    # Determine physical inputs and outputs
    inputs = []
    outputs = []
    try:
        Modules = root[0][4]
        inputs = Modules.find('Module[@Name="Input_Module_16_PT"]')[3][1][0][0][1]
        inputs = [input.text.strip() for input in inputs]
        outputs = Modules.find('Module[@Name="Output_Module_16_PT"]')[3][1][0][1][0]
        outputs = [output.text.strip() for output in outputs][1:]
        hashigo_text += 'I: {};\n'.format(','.join(inputs))
        hashigo_text += 'O: {};'.format(','.join(outputs))
        for i in range(0,len(inputs)):
            hashigo_text = hashigo_text.replace('Local:3:I.Data.{}'.format(i), inputs[i])
        for i in range(0,len(outputs)):
            hashigo_text = hashigo_text.replace('Local:4:O.Data.{}'.format(i), outputs[i])
    except:
        print('\nError finding inputs/outputs\n')
        
        
           
    with open('{}.hshg'.format(filename), 'w') as file:
        file.write(hashigo_text)
    print('Created file: {}.hshg with {} rungs, {} inputs, and {} outputs\n'.format(filename, counter, len(inputs), len(outputs)))
    return filename





def write_verilog(filename):
    try:
        with open('verilog_template.v', 'r') as file:
            v_text = file.read()
    except:
        print('Please restore file "verilog_template.v" to the directory\n')
        sys.exit()
        
    try:
        with open('{}.hshg'.format(filename), 'r') as file:
            hshg_text = file.read()
    except:
        print('Error reading created hashigo file')
        sys.exit()
    
    
    print('Attempting to create file {}.v'.format(filename))
    # Write title
    v_text = v_text.replace('{set_title}', filename)
    
    
    
    # Write wires (inputs)
    wires_text = ''
    i = 0
    inputs = hshg_text.split('\n')[-2][3:-1].split(',')
    outputs = hshg_text.split('\n')[-1][3:-1].split(',')
    rungs = hshg_text.split('\n')[:-2]
    rungs = [rung[:-1].split(' ')[1] for rung in rungs]

    
    for input in inputs:
        if input.lower() in 'reset rst':
            wires_text += 'wire rst = KEY[{}];\n'.format(i)
        else:
            wires_text += 'wire {} = !KEY[{}];\n'.format(input.lower(),i)
        i += 1
    v_text = v_text.replace('{set_wires}',wires_text)
    
    # Write regs (outputs)
    regs_text = ''
    for output in outputs:
        regs_text += '\t{},\n'.format(output)
    regs_text += '\n'
    for output in outputs:
        regs_text += '\tn_{},\n'.format(output)
    regs_text = '{}\n;'.format(regs_text[:-2])
    v_text = v_text.replace('{set_regs}',regs_text)
    
    # Write logic (rungs)
    rungs_text = ''
    rung_count = 0
    regs_list = []
    for rung in rungs:
        
        nodes = []
        i = 0
        
        node = Node('START',None)
        nodes.append(node)
        while not rung == '':
            i += 1
            # print(rung)
            if rung[0] == ',':
                nodes.append(Node('OR',None))
                rung = rung[1:]
            elif rung[0] == '[':
                if not nodes[i-1].node_type in ['LBRACKET', 'OR', 'AND', 'START']:
                    nodes.append(Node('AND',None))
                    i += 1
                nodes.append(Node('LBRACKET',None))
                rung = rung[1:]
            elif rung[0] == ']':
                nodes.append(Node('RBRACKET',None))
                rung = rung[1:]
            elif not rung == '':
                if ')' in rung:
                    [token,rung] = rung.split(')',1)
                else:
                    if rung[-1] == ']':
                        token = rung[:-1]
                        rung = rung[-1]
                    else:
                        token = rung
                        rung = ''
                if nodes[i-1].node_type not in ['LBRACKET','START','OR']:
                    nodes.append(Node('AND',None))
                    i += 1
                node_type = token.split('(')[0]
                arguments = token.split('(')[1].split(',')
                nodes.append(Node(node_type,arguments))
        nodes.append(Node('END',None))

        # for node in nodes:
            # print(node)
        # print('\n')

        output_arguments = []
        i = len(nodes)-2           # Arrlen - 1 - END
        if nodes[i].node_type == 'RBRACKET':
            while True:
                i = i-1
                current_node = nodes[i]
                # print(current_node)
                if current_node.node_type == 'LBRACKET':
                    nodes = nodes[1:i]
                    break
                if not current_node.node_type in ['AND', 'OR']:
                    output_arguments.append(current_node)
        else:
            output_arguments.append(nodes[-2])
            nodes = nodes[1:i]

        while nodes[-1].node_type in ['AND','OR','LBRACKET']:
            nodes = nodes[:-1]
        
        left_arguments = []
        mov_list = []
        add_list = []
        for l in output_arguments:
            print(l)
            if l.node_type == 'OTE':
                if not l.arguments[0] in regs_list:
                    regs_list.append([l.arguments[0],'bool'])
                left_arguments.append(l.arguments[0])
            elif l.node_type == 'MOV':
                if l.arguments[1] not in regs_list:
                    regs_list.append([l.arguments[1],'int'])
                mov_list.append(l.arguments)
            elif l.node_type == 'ADD':
                if not l.arguments[2] in regs_list:
                    regs_list.append([l.arguments[2],'int'])
                add_list.append(l.arguments)
                    
        # for node in nodes:
            # print(node)
        # print('\n')
        # for arg in left_arguments:
            # print(arg)
        # print('\n\n')
        
        
        right_text = ''
        for node in nodes:
            type = node.node_type
            if type == 'AND':
                right_text += '&& '
            elif type == 'OR':
                right_text += '|| '
            elif type == 'XIC':
                right_text += 'n_{} '.format(node.arguments[0])
            elif type == 'XIO':
                right_text += '!n_{} '.format(node.arguments[0])
            elif type == 'LBRACKET':
                right_text += '('
            elif type == 'RBRACKET':
                right_text += ')'
        
        rung_text = '\t\t\t'
        rung_text += '{}: begin'.format(rung_count)
        for l in left_arguments:
            rung_text += '\n\t\t\t\tn_{} <= {};'.format(l,right_text)
        for m in mov_list:
            rung_text += "\n\t\t\t\tn_{} <= 1'b{};".format(m[1], m[0])
        for a in add_list:
            rung_text += "\n\t\t\t\tn_{} <= ".format(a[2])
            if a[0].isnumeric():
                rung_text += "32'd{}".format(a[0])
            else:
                rung_text += a[0]
            if a[1].isnumeric():
                rung_text += " + 32'd{};".format(a[1])
            else:
                rung_text += " + {};".format(a[1])
        rung_text += '\n\t\t\tend\n\n'
        rungs_text += rung_text
        
        rung_count += 1
        
        
    # Rungs Text
    rungs_text += '\t\t\t{}: begin'.format(rung_count)
    for reg in regs_list:
        rungs_text += '\n\t\t\t\t{} <= n_{};'.format(reg[0],reg[0])
    rungs_text += '\n\t\t\tend\n'
        
    v_text = v_text.replace('{rungs_count}', str(rung_count+1))   
    v_text = v_text.replace('{set_rungs}',rungs_text)
    
    
    # Resets Text
    regs_list = sorted(regs_list)
    set_resets_text = ''
    for reg in regs_list:
        if reg[1] == 'int':
            set_resets_text += "\n\t\t{} <= 32'd0".format(reg[0])
        else:
            set_resets_text += "\n\t\t{} <= 1'b0".format(reg[0])
    v_text = v_text.replace('{set_resets}', set_resets_text)
    
    
    # Template Modules Text
    template_modules_text = ''
    
    template_modules_text += 'wire tick;\nDownClock down(clk, rst, tick);'
    if 'rst' not in inputs:
        template_modules_text += '    //########## "rst" not found in inputs, please add or rename "rst" in this module header'
    template_modules_text += '\n\n'
    
    v_text = v_text.replace('{set_template_modules}', template_modules_text);
    
    
    # Create Verilog file
    with open('{}.v'.format(filename), 'w') as file:
        file.write(v_text)
    print('Created file {}.v\n'.format(filename))





def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    filename = parse_l5x()
    #filename = 'andor'
    #write_verilog(filename)
    
if __name__ == '__main__':
    main()