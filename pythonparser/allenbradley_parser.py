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
            new_timer_str = 'TON({}, {}_PRE={})'.format(timer_name,timer_name,timerPRE_val)
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
    
    hashigo_text = hashigo_text.replace('.','_')
        
    # have new hashigo text and this creates a new file same filename as earlier just different extension
    with open('{}.hshg'.format(filename), 'w') as file:
        file.write(hashigo_text)
    # prints how many of them there are becuase it makes sure it worked correctly
    if inputs is None:
        inputs = []
    if outputs is None:
        outputs = []
    print('Created file: {}.hshg with {} rungs, {} inputs, and {} outputs\n'.format(filename, counter, len(inputs), len(outputs))) 




# hashigo to verilog
def write_verilog(filename):
    try:
        with open('verilog_template.v', 'r') as file: # like verilog value but has wires/inputs and registers/vars etc. set (putting anything complicated in its own module)
            v_text = file.read()
    except: # if missing the file
        print('Please restore file "verilog_template.v" to the directory\n')
        sys.exit()
        
    try:
        with open('{}.hshg'.format(filename), 'r') as file:
            hshg_text = file.read()
    except:
        print('Error: Could not read hashigo file')
        sys.exit()
    
    
    print('Attempting to create file {}.v'.format(filename))
    # Write title
    v_text = v_text.replace('{set_title}', filename) #title
    
    
    
    # Write wires (inputs)
    # Going thru verilog template
    wires_text = ''# comes down to text bc replacing test
    i = 0 #counter
    hshg_text_lines = hshg_text.split('\n') #split text into lines
    rungs = [] #making lists, R/i/o are all we have in hashigo
    inputs = []
    outputs = []
    for line in hshg_text_lines:
        if line[0] == 'I': 
            inputs = line[3:-1].split(',')
        elif line[0] == 'O':
            outputs = line[3:-1].split(',')
        else:
            rungs.append(''.join(line[:-1].split(':')[1:])[1:]) # rungs are just strings in ladder logic
    
    for input in inputs:
        if input.lower() in 'reset rst': # for every input get wires text and add the following text
            wires_text += 'wire rst = KEY[{}];\n'.format(i)
        else: # i variable keeps track of which input it is
        # all lowercase for convention, doesn't actually matter
            wires_text += 'wire {} = !KEY[{}];\n'.format(input.lower(),i) # have to invert input because that is how it works in verilogs for physical buttons on FPGA
        i += 1
    v_text = v_text.replace('{set_wires}',wires_text) # verilog text output file
    

    
    # Write logic (rungs)
    rungs_text = ''
    rung_count = 0
    regs_list = [] # keeps track of all variables we find in entire program
    # every time we encounter new var if not found in regs_list we add it
    # regs = registers, register is a variable in verilog
    # every item in regs list is a list itself (a list of sets, each list has 2 arguments, first is name then data type), this is general not unique to each rung
    timer_list = [] # add timers as we find them
    for rung in rungs:
    # goes left to right through the rung and parses the string into a data structure that we can use for verilog
        # going into each rungs
        nodes = []
        i = 0
        #Node class has type of string and arguments (list of strings)
        # creating node object and putting it in pointer, Node type
        node = Node('START',None)
        # arguments is if you have timer with multiple pieces of information (everything in parenthesis)
        # List of nodes that goes from left to right
        nodes.append(node)
        # Always start with start node
        while not rung == '':
        # while it is not an empty string increment i because we added a start node
        # i is a counter
            i += 1
            
            # general approach: add a new node to the node list then chop it off from that part of the string
            
            # print(rung)
            # like bison and flex but manual !! :o
            if rung[0] == ',':
                nodes.append(Node('OR',None))
                rung = rung[1:]
            elif rung[0] == '[':
            # if previous node was not one of these below then add an AND and a left bracket
            # implied AND between left bracket and first thing if there is an XIC and then a left bracket anything before a left bracket thats not a left bracket or those 3 things then put an AND there)
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
                # create a token which is current thing we are trying to parse which is a rung
                # separating token from rung by splitting on right parenthese
                # gets you the node that you are currently on
                    [token,rung] = rung.split(')',1)
                else:
                # sometimes there is not a right parenthese because at end of line we have a square bracket
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
                arguments = token.split('(')[1].split(',') # multiple arguments are separated by commas in verilog
                arguments = [arg.strip() for arg in arguments] # get rid of spaces
                nodes.append(Node(node_type,arguments))  # make a new node with node type and arguments
        nodes.append(Node('END',None)) # parse all nodes and add final node which doesn't really do anything

        # for node in nodes:
            # print(node)
        # print('\n')
        # have to figure out for each rung the logic of the run and the outputs of the rung
        # each rung is entirely independent from the other rungs
        output_arguments = []
        i = len(nodes)-2           # Arrlen - 1 - END, length of nodes - 1 and then another -1 because we skip the dummy end node (starting w second to last node we created that is always an output)
        # But sometimes have multiple outputs, can have a list of multiple parallel outputs
        # If that variable is positive then execute all those outputs
        if nodes[i].node_type == 'RBRACKET':
         # assume we have one output if the last node is not a right bracket
            while True:
                i = i-1
                # starting from end if it is a right bracket and going backwards
                # change current node and if it is a left bracket and this means we have hit all the outputs
                # so keep going until you hit a left bracket
                # stop if Left bracket because that means we have hit all of our outputs
                current_node = nodes[i]
                # print(current_node)
                if current_node.node_type == 'LBRACKET':
                    nodes = nodes[1:i]
                    break
                    # if its not a left bracket and also not an and or an or then we add it to output arguments list because that means it is a valid output
                if not current_node.node_type in ['AND', 'OR']: # skip and and or bc those don't mean anything in this scenario that is more input logic
                    output_arguments.append(current_node)
        else:
        # chop off anything that is left because it doesn't mean anything it is just between inputs and outputs so it is meaningless
        # every rung should have inputs and outputs
            output_arguments.append(nodes[-2])
            nodes = nodes[1:i]

        # chop them off
        while nodes[-1].node_type in ['AND','OR','LBRACKET']:
            nodes = nodes[:-1]
        # now we just have input arguments left
        left_arguments = []
        # ladder logic has logic on left and setting on the right
        mov_list = [] # outputs can be basic variable or move function or time function
        add_list = []
        timer_list_current_rung = []
        # list of outputs and we are separating them into lists based on what type of output they are
        # can be function
        for l in output_arguments: # l is a node
            # print(l)
            # for each of them :
            # 1. all vars within output if that var which is first arg of node is not in registers list then we need to add it to registers list (add name of varaible and data type)
            # depending on which function it is in it determines var type (ex. OTE is bool, MOV is int, ADD int, TON is not delt with here)
            # 2. append the variable to the list of right args, move, list, timer list, etc for each type of outputs
            # each rung has a list for different types of outputs
            if l.node_type == 'OTE':
                if not l.arguments[0] in regs_list:
                    tmp = l.arguments[0].replace('.','_')
                    regs_list.append([tmp,'bool'])
                left_arguments.append(l.arguments[0])
            elif l.node_type == 'MOV':
                if l.arguments[1] not in regs_list:
                    tmp = l.arguments[1].replace('.','_')
                    regs_list.append([tmp,'int'])
                mov_list.append(l.arguments)
            elif l.node_type == 'ADD':
                if not l.arguments[2] in regs_list:
                    tmp = l.arguments[2].replace('.','_')
                    regs_list.append([tmp,'int'])
                add_list.append(l.arguments)
            elif l.node_type == 'TON': # ton is for timer
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
        
        # getting input logic which we have in node form, need to change it into verilog form
        # have right text string for each rung which is the logic for that rung
        right_text = ''
        for node in nodes:
            type = node.node_type
            if type == 'AND':
                right_text += '&& '
            elif type == 'OR':
                right_text += '|| '
            elif type == 'XIC': # just add variable, XIC just means look at variable
                right_text += 'n_{} '.format(node.arguments[0])
            elif type == 'XIO': #XIO is variable inverted
                right_text += '!n_{} '.format(node.arguments[0])
            elif type == 'LBRACKET':
                right_text += '('
            elif type == 'RBRACKET':
                right_text += ')'
        right_text = right_text.strip()
        
        # have logic now and have to create the text from it
        # have 4 lists and they each have different formatting
        # l is variable, right text is logic used in every one
        rung_text = '\t\t\t'
        rung_text += '{}: begin'.format(rung_count)
        for l in left_arguments:
            rung_text += '\n\t\t\t\tn_{} <= {};'.format(l,right_text)
        if len(mov_list) > 0:
            rung_text += "\n\t\t\t\tif (({}) == 1'b1)\n\t\t\t\tbegin".format(right_text)
            for m in mov_list:
                rung_text += "\n\t\t\t\t\tn_{} <= 32'd{};".format(m[1], m[0])
            rung_text += '\n\t\t\t\tend'
        for a in add_list:
            rung_text += "\n\t\t\t\tn_{} <= ".format(a[2])
            if a[0].isnumeric(): #32 bit decimal is integer
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
    # after we do all the rungs independently n_varname is like a temporary variable and in last rung we add a bonus rung which moves temporary variables into the actual variables which correspond to the actual physical outputs
    # actual outputs only updated after it goes through the entire ladder in ladder logic because physical hardware is slower than computer mem if you change temp vars multiple times
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
    
    # replacing rungs count variable to the output text file
    # rungs text is what we have been working on the entire time
    v_text = v_text.replace('{rungs_count}', str(rung_count+1))   
    v_text = v_text.replace('{set_rungs}',rungs_text)
    
    # Write regs (outputs)
    # creating list of registers with the temporary and actual vars and bools and ints
    # collect registers as we go so we have to add them after
    # if not in the list then they don't matter because they are not used
    # as long as it is in ladder logic somewhere then it will be in the verilog
    regs_text = ''
    #changing regs_list to regs_text
    for reg in regs_list:
    # based on regs_list we created a regs_text for verilog file
    # go through list and based on data types you separate and format accordingly
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
    # in verilog FPGA if machine is switched off then you have states where you have your resets assignments / where everything is 0
    # default to 0 for all of our variables
    regs_list = sorted(regs_list)
    set_resets_text = ''
    for reg in regs_list:
        if reg[1] == 'bool':
            set_resets_text += "\n\t\t{} <= 1'b0;".format(reg[0])
    set_resets_text += '\n'
    for reg in regs_list:
        if reg[1] == 'int':
            set_resets_text += "\n\t\t{} <= 32'd0;".format(reg[0])
    v_text = v_text.replace('{set_resets}', set_resets_text)
    
    
    # Template Modules Text
    # for timers or other functions like a DownClock
    # internal clock on FPGA is 50MHz
    # if you do timer wait for 9 units that is 9ms so timer module creates 1kHz clock from 50MHz clock
    # everything is parallel in an FPGA
    template_modules_text = ''
    # Always add DownClock Module
    template_modules_text += '// Make a slowed-down (1kHz) clock\nwire tick;\nDownClock down(clk, rst, tick);' # tick is 1kHz clock wire
    if 'rst' not in inputs:
    # DownClock takes reset input to turn on and off
    # if you don't have a reset variable it prints something to the terminal
        print('\n############# WARNING ###############')
        print('Variable "rst" not found in list of inputs, please add a "rst" variable or find and replace "rst" with the name of the reset/enable variable')
        print('#####################################\n')
    template_modules_text += '\n\n'
    # Add timers if needed
    timer_cnt = 0
    # for each timer figure out which rung it is associated to bc they are separated by rungs
    # for each timer we have to make more wires bc timer module has a lot of inputs and outputs
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
                template_modules_text += 'wire [31:0]{}_ACC;\n'.format(timer_name, timer_name)
                template_modules_text += 'wire {}_DN, {}_TT, {}_EN;\n'.format(timer_name, timer_name, timer_name)
                template_modules_text += "Timer t{}(clk, rst, tick, 32'd{}, {}_IN, {}_DN, {}_TT, {}_EN, {}_ACC);\n\n" \
                    .format(timer_cnt,timer[0][1].split('=')[1],timer_name,timer_name,timer_name,timer_name,timer_name)
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
        # Remove / or \ or . at beginning of file name
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
