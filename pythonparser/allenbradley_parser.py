import xml.etree.ElementTree as ET
import sys
import re
import os

#parsing data structure
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

# L5X/XML to hashigo(.hshg)
# physical input and outpus modules
# progorams r info
# tags has info on all vvars and funct
# routins has every rung and text
#reads file
def parse_l5x(root, filename): 
    
    # Determine logical rungs
    try:
        # get main program thats a part of xml file format for finding things in xml
        # since there are 2 programs, use square bracket to specify which one to use
        MainProgram = root.find('Controller/Programs/Program[@Name="MainProgram"]') 
        rungs_data = MainProgram.find('Routines/Routine[@Name="MainRoutine"]/RLLContent')
        # empty list for rungs to start with as pointer counter to count how many rungs we have
        rungs = []
        counter = 0
        # r_d points to sections we just opened it lists all of the children, each rung corresponds to rung section (node) in xml
        for rung in rungs_data:
            #find('Text') retrieves xml node with tag 'Text', .text gets the actual text, .strip() gets rid of whitespace on outside of text, cut off last character (semi-colon), get rid of spaces
            rung_text = rung.find('Text').text.strip()[:-1].replace(' ','')             
            # rungs list at top, each rung is added to rungs list. rung is a string, rungs is a list of strings. This is string formatting: put string first and wherever 
            # you have curly braces it is like printf %d and put any varaible as an argument and when you . format each one corresponds to one of the curly braces
            rungs.append('{}: {};\n'.format(counter, rung_text)) 
            counter += 1    
    except:
        print('\nError Parsing Rungs\n')
        sys.exit()
    
    
    # Extract timer information
    Tags = MainProgram.find('Tags')
    updated_rungs = []
    for rung in rungs:
        updated_rung = rung.replace('TON','T~N')
        while 'T~N' in updated_rung:  
            start_index = updated_rung.find('T~N')
            end_index = start_index
            while updated_rung[end_index] != ')':
                end_index += 1
            timer_str = updated_rung[start_index:end_index+1][4:]
            timer_name = timer_str.split(',')[0]
            timer_tag = Tags.find('Tag[@Name="{}"]'.format(timer_name))
            timerPRE_val = timer_tag.find('Data[@Format="Decorated"]/Structure/DataValueMember[@Name="PRE"]').attrib['Value']
            new_timer_str = 'TON({}, {}.PRE={})'.format(timer_name,timer_name,timerPRE_val)
            updated_rung = updated_rung[:start_index] + new_timer_str + updated_rung[end_index+1:]
        updated_rungs.append(updated_rung)
        
    rungs = updated_rungs
    
    # Combine rungs into text each rung is a string combining that into one bit string
    hashigo_text = ''
    for rung in rungs:
        hashigo_text += rung
    
    
    # Determine physical inputs and outputs
    inputs = []
    outputs = [] # initialize lists
    try:
        # in modules section of xml
        Modules = root.find('Controller/Modules') 
        inputs = Modules.find('Module[@Name="Input_Module_16_PT"]/Communications/Connections/Connection/InputTag/Comments')
        # .text gets the text, strip just in case newline at end or space, and add to the inputs list
        # list comprehension [] arround logic piece is like doing a for loop but on one line- creates a list with all those for loop results in one line
        inputs = [input.text.strip() for input in inputs] 
        outputs = Modules.find('Module[@Name="Output_Module_16_PT"]/Communications/Connections/Connection/OutputTag/Comments') #gets location of variable in memory this is replaced later on, actual name of variable is extended in the comment which is actuallly what we are getting with the .text
        #.DATA is a fake variable it doesn't have anything after it so skip the first output
        outputs = [output.text.strip() for output in outputs][1:] 
        # gives physical inputs and outputs, last 2 lines of .hshg file: I are physical inputs and O are physical outputs. If it its not one of those then it is just a memory variable, getting names of variables
        hashigo_text += 'I: {};\n'.format(', '.join(inputs))         
        hashigo_text += 'O: {};'.format(', '.join(outputs))
        # have to replace variable locations with memory names we can do this since there is only one input and output module, Local:3:I.Data replaces with actual name which is in the same order we got it earlier, 
        # using input names to replace names of locations. looks at entire text as a whole
        for i in range(0,len(inputs)): 
            hashigo_text = hashigo_text.replace('Local:3:I.Data.{}'.format(i), inputs[i])
        for i in range(0,len(outputs)):
            hashigo_text = hashigo_text.replace('Local:4:O.Data.{}'.format(i), outputs[i])
    # Just to say where erroredout
    except:
        print('\nError finding inputs/outputs\n')
        
        
    # have new hashigo text and this creates a new file same filename as earlier just different extension
    with open('{}.hshg'.format(filename), 'w') as file:
        file.write(hashigo_text)
    # prints how many of them there are becuase it makes sure it worked correctly
    if inputs is None:
        inputs = []
    if outputs is None:
        outputs = []
    print('Created file: {}.hshg with {} rungs, {} inputs, and {} outputs\n'.format(filename, counter, len(inputs), len(outputs))) 




#hashigo to verilog
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
    hshg_text_lines = hshg_text.split('\n')
    rungs = []
    inputs = []
    outputs = []
    for line in hshg_text_lines:
        if line[0] == 'I': 
            inputs = line[3:-1].split(',')
        elif line[0] == 'O':
            outputs = line[3:-1].split(',')
        else:
            rungs.append(''.join(line[:-1].split(':')[1:])[1:])
    
    for input in inputs:
        if input.lower() in 'reset rst':
            wires_text += 'wire rst = KEY[{}];\n'.format(i)
        else:
            wires_text += 'wire {} = !KEY[{}];\n'.format(input.lower(),i)
        i += 1
    v_text = v_text.replace('{set_wires}',wires_text)
    

    
    # Write logic (rungs)
    rungs_text = ''
    rung_count = 0
    regs_list = []
    timer_list = []
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
                arguments = [arg.strip() for arg in arguments]
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
        timer_list_current_rung = []
        for l in output_arguments:
            # print(l)
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
            elif l.node_type == 'TON':
                if not [l.arguments,rung_count] in timer_list:
                    timer_list.append([l.arguments,rung_count])
                    regs_list.append(['{}_IN'.format(l.arguments[0]),'bool'])
                timer_list_current_rung.append([l.arguments,rung_count])
                
                    
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
        right_text = right_text.strip()
        
        rung_text = '\t\t\t'
        rung_text += '{}: begin'.format(rung_count)
        for l in left_arguments:
            rung_text += '\n\t\t\t\tn_{} <= {};'.format(l,right_text)
        if len(mov_list) > 0:
            rung_text += "\n\t\t\t\tif (({}) == 1'b1)\n\t\t\t\tbegin".format(right_text)
            for m in mov_list:
                rung_text += "\n\t\t\t\t\tn_{} <= 1'b{};".format(m[1], m[0])
            rung_text += '\n\t\t\t\tend'
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
        for t in timer_list_current_rung:
            rung_text += '\n\t\t\t\tn_{}_IN <= {};'.format(t[0][0], right_text)
        rung_text += '\n\t\t\tend\n\n'
        rungs_text += rung_text
        
        rung_count += 1
        
        
    # Rungs Text
    regs_list = sorted(regs_list)
    rungs_text += '\t\t\t{}: begin'.format(rung_count)
    for reg in regs_list:
        if reg[1] == 'bool':
            rungs_text += '\n\t\t\t\t{} <= n_{};'.format(reg[0],reg[0])
    rungs_text += '\n'
    for reg in regs_list:
        if reg[1] == 'int':
            rungs_text += '\n\t\t\t\t{} <= n_{};'.format(reg[0],reg[0])
    rungs_text += '\n\t\t\tend\n'
        
    v_text = v_text.replace('{rungs_count}', str(rung_count+1))   
    v_text = v_text.replace('{set_rungs}',rungs_text)
    
    # Write regs (outputs)
    regs_text = ''
    for reg in regs_list:
        if reg[1] == 'bool':
            regs_text += "\nreg {};".format(reg[0])
    for reg in regs_list:
        if reg[1] == 'int':
            regs_text += "\nreg [31:0]{};".format(reg[0])
    regs_text += '\n'        
    for reg in regs_list:
        if reg[1] == 'bool':
            regs_text += "\nreg n_{};".format(reg[0])
    for reg in regs_list:
        if reg[1] == 'int':
            regs_text += "\nreg [31:0]n_{};".format(reg[0])
    v_text = v_text.replace('{set_regs}', regs_text)
    
    # Resets Text
    regs_list = sorted(regs_list)
    set_resets_text = ''
    for reg in regs_list:
        if reg[1] == 'bool':
            set_resets_text += "\n\t\t{} <= 1'b0".format(reg[0])
    set_resets_text += '\n'
    for reg in regs_list:
        if reg[1] == 'int':
            set_resets_text += "\n\t\t{} <= 32'd0".format(reg[0])
    v_text = v_text.replace('{set_resets}', set_resets_text)
    
    
    # Template Modules Text
    template_modules_text = ''
    # Always add DownClock Module
    template_modules_text += '// Make a slowed-down (1kHz) clock\nwire tick;\nDownClock down(clk, rst, tick);'
    if 'rst' not in inputs:
        print('\n############# WARNING ###############')
        print('Variable "rst" not found in list of inputs, please add a "rst" variable or find and replace "rst" with the name of the reset/enable variable')
        print('#####################################\n')
    template_modules_text += '\n\n'
    # Add timers if needed
    timer_cnt = 0
    for i in range(rung_count):
        flg = 0
        for timer in timer_list:
            if timer[1] == i:
                timer_cnt += 1
                if flg == 0:
                    template_modules_text += '/* Rung {} */\n'.format(i)
                    flg = 1
                timer_name = timer[0][0]
                template_modules_text += '// Timer: {}\n'.format(timer_name)
                template_modules_text += 'wire [31:0]{}_PRE, {}_ACC;\n'.format(timer_name, timer_name)
                template_modules_text += 'wire {}_EN, {}_TT, {}_DN;\n'.format(timer_name, timer_name, timer_name)
                template_modules_text += "Timer t{}(clk, rst, tick, 32'd{}, {}_IN, n_timer_{}_done_wire);\n\n" \
                    .format(timer_cnt,timer[0][1].split('=')[1],timer_name,timer_cnt)
        # 
        # template_modules_text += 'timer yee haw {} {} \n'.format(timer_list[i][0], i)
    
    v_text = v_text.replace('{set_template_modules}', template_modules_text);
    
    # Create Verilog file
    with open('{}.v'.format(filename), 'w') as file:
        file.write(v_text)
    print('Created file {}.v\n'.format(filename))




# main
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        file = sys.argv[1]
        while not file[0].isalnum():
            file = file[1:]
        [filename, filetype] = file.split('.') # taking second item from argv
    
    except: # if it is a bad file, can't be read by xml parser tree, file doesn't exist it, or no file argument at all: cancels program
        print('\nPlease enter valid .L5X or .hshg file in form "python allenbradley_parser.py example.L5X"\n')
        sys.exit(1)
    
    if filetype.upper() not in ['L5X', 'XML', 'HSHG']:
        print('\nInvalid filetype, please enter valid .L5X or .hshg file in form "python allenbradley_parser.py example.L5X"\n')
        sys.exit(1)
    if filetype.upper() in ['L5X', 'XML']:
        tree = ET.parse(sys.argv[1]) # taking second cml argument (filename), doing element tree parse on that which is xml to get the root
        print('\nParsing {}'.format(sys.argv[1]))
        root = tree.getroot()
        parse_l5x(root, filename)
    write_verilog(filename)
    
if __name__ == '__main__':
    main()
