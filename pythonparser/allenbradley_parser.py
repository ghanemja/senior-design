import xml.etree.ElementTree as ET
import sys
import re
import os

### Data Structure for nodes within logic rungs.
# Nodes can represent any function, represented by node_type
# All text within parentheses are converted into arguments list
# Ex: TON(timer1, PRE=100)     ->    Node: node_type = TON, arguments = ['timer1', 'PRE=100']
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






### Convert L5X (XML) to HSHG (Hashigo Logic File)
def parse_l5x(root, filename): 
    
    ### Determine logical rungs
    
    # Find rungs tag within XML
    MainProgram = root.find('Controller/Programs/Program[@Name="MainProgram"]') 
    rungs_data = MainProgram.find('Routines/Routine[@Name="MainRoutine"]/RLLContent')
    
    rungs = []  # String list
    counter = 0
    # For each rung, obtain rung logic and add to string rung_text
    for rung in rungs_data:
        # Get rung logic string, format, and remove spaces
        rung_text = rung.find('Text').text.strip()[:-1].replace(' ','')             
        # Add rung string to rungs (list) with formatting
        rungs.append('{}: {};\n'.format(counter, rung_text)) 
        counter += 1    
    
    
    
    
    ### Extract Timer information
    ### We need to find the timer preset values and edit the rung string to contain this information
    
    # Find "Tags" tag. This is where information resides regarding variables and functions such as Timers.
    Tags = MainProgram.find('Tags')
    
    # Each rung will be updated
    updated_rungs = []  # String list
    for rung in rungs:
        # Modify unedited timers to 'T~N' so we know which Timers have been updated
        updated_rung = rung.replace('TON','T~N')
        # Update every Timer
        while 'T~N' in updated_rung:  
            # Find string pos index for start of old Timer
            start_index = updated_rung.find('T~N')
            # Now find string pos index for end of old Timer
            end_index = start_index
            while updated_rung[end_index] != ')':
                end_index += 1
            # Get old Timer string
            timer_str = updated_rung[start_index:end_index+1][4:]
            # Get Timer's name
            timer_name = timer_str.split(',')[0]
            # Find the Timer's tag within the XML using the Timer's name
            timer_tag = Tags.find('Tag[@Name="{}"]'.format(timer_name))
            # Obtain Timer's preset value
            timerPRE_val = timer_tag.find('Data[@Format="Decorated"]/Structure/DataValueMember[@Name="PRE"]').attrib['Value']
            # Create new Timer string using preset value
            new_timer_str = 'TON({}, {}_PRE={})'.format(timer_name,timer_name,timerPRE_val)
            # Replace old rung string with new rung string consisting of updated Timer string
            updated_rung = updated_rung[:start_index] + new_timer_str + updated_rung[end_index+1:]
        updated_rungs.append(updated_rung)  
    # Replace rungs (list) with updated Timer rungs
    rungs = updated_rungs
    
    
    
    
    ### Extract Counter information
    ### We need to find the Counter preset values and edit the rung string to contain this information
    
    # Each rung will be updated
    updated_rungs = [] # String list
    for rung in rungs:
        # Modify unedited Counters to 'C~U' so we know which Counters have been updated
        updated_rung = rung.replace('CTU','C~U')
        # Update every Counter
        while 'C~U' in updated_rung:  
            # Find string pos index for start of old Counter
            start_index = updated_rung.find('C~U')
            # Now find string pos index for end of old Counter
            end_index = start_index
            while updated_rung[end_index] != ')':
                end_index += 1
            # Get old Counter string
            counter_str = updated_rung[start_index:end_index+1][4:]
            # Get Counter's name
            counter_name = counter_str.split(',')[0]
            # Find the Counter's tag within the XML using the Counter's name
            counter_tag = Tags.find('Tag[@Name="{}"]'.format(counter_name))
            # Obtain Counter's preset value
            counterPRE_val = counter_tag.find('Data[@Format="Decorated"]/Structure/DataValueMember[@Name="PRE"]').attrib['Value']
            # Create new Counter string using preset value
            new_counter_str = 'CTU({}, {}_PRE={})'.format(counter_name,counter_name,counterPRE_val)
            # Replace old rung string with new rung string consisting of updated Counter string
            updated_rung = updated_rung[:start_index] + new_counter_str + updated_rung[end_index+1:]
        updated_rungs.append(updated_rung) 
    # Replace rungs (list) with updated Timer rungs        
    rungs = updated_rungs
    
    
    
    
    ### Create Hashigo logic text from our rung strings
    hashigo_text = ''
    for rung in rungs:
        hashigo_text += rung
    
    
    
    
    ### Find physical inputs and outputs
    inputs = []  # String list
    outputs = [] # String list
        
    # Find Modules tag in XML. This is where information on physical inputs and outputs is located
    Modules = root.find('Controller/Modules') 
    
    # Find inputs tag
    input_tags = Modules.find('Module[@Name="Input_Module_16_PT"]/Communications/Connections/Connection/InputTag/Comments')
    # Populate inputs list from XML
    inputs = [input.text.strip() for input in input_tags] 
    
    # Find outputs tag
    output_tags = Modules.find('Module[@Name="Output_Module_16_PT"]/Communications/Connections/Connection/OutputTag/Comments') #gets location of variable in memory this is replaced later on, actual name of variable is extended in the comment which is actuallly what we are getting with the .text
    # Populate outputs list from XML
    outputs = [output.text.strip() for output in output_tags][1:] 
    
    # Add a line to the end of the Hashigo logic file each for inputs and outputs
    hashigo_text += 'I: {};\n'.format(', '.join(inputs))         
    hashigo_text += 'O: {};'.format(', '.join(outputs))
    
    
    
    
    ### Replace memory locations with variable names.
    ### Some variables in logic use memory locations instead of the variable's name. These need to be replaced with variables names. 
    ### This works for only one output and one input module on the Allen Bradley PLC but can be updated if needed.
    
    # Replace physical inputs with variable names
    i=0 
    for input in input_tags:
        index = input.attrib['Operand'][-1]
        hashigo_text = hashigo_text.replace('I.Data.{}'.format(index), inputs[i])
        i += 1
    
    # Replace physical outputs with variable names
    i = 0
    for output in output_tags:
        index = output.attrib['Operand'][-1]
        if index.isnumeric():
            hashigo_text = hashigo_text.replace('O.Data.{}'.format(index), outputs[i])
            i += 1
            
    # Remove memory location string artifacts
    # 100 is chosen as arbitrarily large value to ensure all artifacts are removed.
    for i in range(0,100):
        hashigo_text = hashigo_text.replace('Local:{}:'.format(i), '')
    
    # Replace all periods with underscores (Ex. timer1.PRE -> timer1_PRE). Verilog regs/wires cannot have periods.
    hashigo_text = hashigo_text.replace('.','_')
        
        
        
        
    ### Create Hashigo logic file from hashigo text string
    with open('{}.HSHG'.format(filename), 'w') as file:
        file.write(hashigo_text)

    # Print number of inputs, outputs, and rungs to console
    if inputs is None:
        inputs = []
    if outputs is None:
        outputs = []
    print('Created file: {}.HSHG with {} rungs, {} inputs, and {} outputs\n'.format(filename, counter, len(inputs), len(outputs))) 






### Convert HSHG (Hashigo Logic File) to Verilog
def write_verilog(filename):
    
    ### Open the verilog file template
    try:
        with open('verilog_template.v', 'r') as file: 
            # This will be the string for our new Verilog file
            v_text = file.read()
    except: 
        print('Please restore file "verilog_template.v" to the directory\n')
        sys.exit()
        
    try:
        with open('{}.hshg'.format(filename), 'r') as file:
            hshg_text = file.read()
    except:
        print('Error: Could not read hashigo file')
        sys.exit()
    
    print('Attempting to create file {}.v'.format(filename))
    
    
    
    
    ### Begin by setting the title in v_text
    ### This pattern will be repeated of replacing template sections with a string containing the actual info
    v_text = v_text.replace('{set_title}', filename)
    
    
    

    ### Parse the Hashigo Logic text to get rungs and physical IOs
    # Split the Hashigo Logic text into a list of lines
    hshg_text_lines = hshg_text.split('\n')
    # Create lists for rungs, physical inputs, and physical outputs
    rungs   = [] # String list
    inputs  = [] # String list
    outputs = [] # String list
    
    # Each line is either a logical rung, the list of physical inputs, or the list of physical outputs.
    # Go through each line, extract info, and add info to respective list
    for line in hshg_text_lines:
        if line[0] == 'I': 
            inputs = line[3:-1].split(',')
        elif line[0] == 'O':
            outputs = line[3:-1].split(',')
        else:
            rungs.append(''.join(line[:-1].split(':')[1:])[1:]) # rungs are just strings in ladder logic
    
    
    
    
    ### Set wires (physical IOs)
    # Create wires_text string which we will update and then eventually use to replace the {set_wires} placeholder in v_text
    wires_text = ''
    # SW (FPGA switches) counter
    i = 0  
    
    # Create a standard master 'rst' switch input to enable the FPGA operation if not already in the PLC program
    if 'rst' not in inputs:
        wires_text += 'wire rst = SW[0];\n'
        i += 1
        
    # Assign each physical input to a switch on the FPGA
    for input in inputs:
        wires_text += 'wire n_{} = SW[{}];\n'.format(input.strip(),i) 
        i += 1
            
    wires_text += '\n'
    
    # LEDR (FPGA red LEDs counter)
    i = 0;
    # Assign each physical output to a red LED on the FPGA
    for output in outputs:
        wires_text += 'assign LEDR[{}] = {};\n'.format(i,output.strip())
        i += 1
   
    # Replace placeholder in Verilog file text with actual wires text
    v_text = v_text.replace('{set_wires}',wires_text)
    

    
    
    ### This section parses every rung in the ladder logic into Verilog, stores information on timers, counters, and registers,
    ### and creates the Verilog logical equivalent text (rungs_text)
    # The string that will contain the entire set of Verilog logic for this Ladder logic program
    rungs_text = ''
    # Counter to keep track of which rung we are on
    rung_count = 0
    # A list of all registers found within the Ladder Logic rungs
    # Each item in the list is in the form [name (str), dataType (str)] where dataType is either 'bool' or 'int' 
    regs_list = []
    # A list of the names of each Timer we find
    timer_list = []  # [String list, int] list
    # A dicttionary of Timer names as keys and their corresponding Timer preset values as values
    timer_presets = {}
    # A list of the names of each Counter we find
    counter_list = []   # [String list, int] list
    # A dictionary of Counter names as keys and their corresponding Counter preset values as values
    counter_presets = {}
    
    # Going through each ladder logic rung
    for rung in rungs:

        ### First, convert ladder logic rung into a list of Node objects (nodes)
        nodes = []   # Node list
        # nodes list length counter
        i = 0
        
        # Always begin with a 'START' Node
        node = Node('START',None)
        nodes.append(node)
        
        # Keep making passes through the ladder logic rung until all functions have been converted to Nodes
        # General approach: add a new node to the node list then chop it off from that part of the string
        while not rung == '':

            # There must be another Node since the 'rung' string isn't empty
            i += 1
            
            # Always start from left side of the rung string
            # There is a comma on the left side, append an 'OR' Node to the nodes list
            if rung[0] == ',':
                nodes.append(Node('OR',None))
                rung = rung[1:]
            
            # There is a left bracket
            elif rung[0] == '[':
                # If previous node was not one of these below then add an AND before the left bracket
                # There are implied ANDs in the ladder logic before left brackets and after right brackets, with exceptions for the four node_types shown below
                if not nodes[i-1].node_type in ['LBRACKET', 'OR', 'AND', 'START']:
                    nodes.append(Node('AND',None))
                    i += 1   # Adding an extra Node, so update the Node counter an extra time
                # Always add the left bracket here
                nodes.append(Node('LBRACKET',None))
                rung = rung[1:]
                
            # There is a right bracket
            # This is simpler than left bracket, just add the bracket
            elif rung[0] == ']':
                nodes.append(Node('RBRACKET',None))
                rung = rung[1:]
                
            # There is something other than a comma or bracket, most functions are dealt with here    
            elif not rung == '':
                # First we split the remaining rung string into a token and a rung.
                # The token is what we will convert to a Node and remove the rung.
                # The rung will be the updated rung without the token.
                [token,rung] = rung.split(')',1)
 
                # Same case as for the left bracket, there are implied ANDs between most Nodes except after these four node_types
                if nodes[i-1].node_type not in ['LBRACKET','START','OR']:
                    nodes.append(Node('AND',None))
                    i += 1   # Adding an extra Node, so update the Node counter an extra time
                
                # The node_type is the text before the parentheses, (Ex. XIC(var1) -> node_type = XIC)
                node_type = token.split('(')[0]
                # The arguments are the comma-seperated strings within the parentheses, (Ex. TON(timer1, PRE=100) -> arguments = ['timer1', 'PRE=100']
                # The function/variable name is often the first argument
                arguments = token.split('(')[1].split(',')
                arguments = [arg.strip() for arg in arguments]
                # Create a new Node from the node_type and arguments and append to nodes list
                nodes.append(Node(node_type,arguments))
        
        # Always end with an 'END' Node        
        nodes.append(Node('END',None))




        ### With our list of Nodes, we will create a list of outputs and a logical expression as the input for this rung
        # List of Nodes which are outputs (right side of ladder logic rung, left side of Verilog assignment) in this rung
        output_arguments = []
        # Counter pointing to the last node in the nodes list. Subtract 2 because of 0-indexing and to skip the 'END' node
        i = len(nodes)-2

        # Currently, all output arguments for a rung must be in a parallel list or only a singular output argument
        # If this is true, it means there is a parallel list of output arguments
        # General approach: Work from right to left, adding nodes to list of output arguments and removing them from the nodes list
        if nodes[i].node_type == 'RBRACKET':
            while True:
                i = i-1
                # Get right-most Node 
                current_node = nodes[i]
                # If Node is left bracket, we have arrived at the end of the left side of the parallel list of output arguments, we are done here
                if current_node.node_type == 'LBRACKET':
                    nodes = nodes[1:i]
                    break
                # These should only be in the logical expression side of the rung. If we come across one of them, it means the rung is formatted in a way we cannot parse
                if current_node.node_type in ['RBRACKET', 'XIC', 'XIO', 'ONS', 'GEQ', 'EQU']:
                    print('\n############# ERROR ###############')
                    print('Fatal formatting error in rung {}. Either an improper list of outputs or a disallowed functionon in the right-hand side of the rung\n'.format(rung_count))
                    print('#####################################\n')
                    sys.exit(1)
                # Otherwise, add the valid output argument to the list, ignoring ANDs and ORs which are meaningless in this context
                if not current_node.node_type in ['AND', 'OR']:
                    output_arguments.append(current_node)
        
        # There is only one output argument
        else:
            output_arguments.append(nodes[-2])
            nodes = nodes[1:i]

        # Finish by removing any extra fluff Nodes
        if len(nodes) > 0:
            while nodes[-1].node_type in ['AND','OR','LBRACKET']:
                nodes = nodes[:-1]
                
                
                
                
        ### Parse through our list of output arguments and categorize them into lists
        # Basic binary coils (OTE)
        ote_list = []   # String list
        # Integer assignment (MOV) functions
        mov_list = []   # [String, String] list
        # Integer addition (ADD) functions
        add_list = []   # [String, String, String] list
        # Timer (TON) functions, note this is different from the master timer_list
        timer_list_current_rung = []   # [String list, int] list
        # Counter (CTU) functions, note this is different from the master counter_list
        counter_list_current_rung = [] # [String list, int] list

        # General approach: Identify node_type, then append to respective list. Also, check each output Node for registers which are not already
        # in regs_list. If not already, add them along with their dataType (int/bool) which is determined by the type of function the reg is found in.
        # Do something similar for Timers and Counters by adding their preset values to their dictionaries for later use
        for output_node in output_arguments:
        
            # Ensure reg in regs_list and add reg to ote_list for this rung
            if output_node.node_type == 'OTE':
                tmp = output_node.arguments[0]
                if not [tmp, 'bool'] in regs_list:
                    regs_list.append([tmp,'bool'])
                ote_list.append(tmp)
             
            # Ensure reg in regs_list and add [assignment_value, reg] to mov_list for this rung
            elif output_node.node_type == 'MOV':
                tmp = output_node.arguments[1]
                if not [tmp, 'int'] in regs_list:
                    regs_list.append([tmp,'int'])
                mov_list.append([output_node.arguments[0],tmp])
            
            # Ensure each reg is in regs_list and add [a, b, c] to add_list for this rung
            elif output_node.node_type == 'ADD':
                for tmp in output_node.arguments:
                    if not tmp.isnumeric():
                        if not [tmp, 'int'] in regs_list:
                            regs_list.append([tmp,'int'])
                add_list.append([output_node.arguments[0], output_node.arguments[1], output_arguments[2]])
            
            # Ensure Timer is in master timer_list, corresponding regs are in regs_list, 
            # add Timer's preset to dictionary, and add Timer to timer_list_current_rung
            elif output_node.node_type == 'TON':
                if not [output_node.arguments,rung_count] in timer_list:
                    timer_list.append([output_node.arguments,rung_count])
                    regs_list.append(['{}_IN'.format(output_node.arguments[0]),'bool'])
                    if not ['{}_PRE'.format(output_node.arguments[0]),'int'] in regs_list:
                        regs_list.append(['{}_PRE'.format(output_node.arguments[0]),'int'])
                timer_list_current_rung.append([output_node.arguments,rung_count])
                timer_presets[output_node.arguments[0]] = output_node.arguments[1].split('=')[1]
            
            # Ensure Counter is in master counter_list, corresponding regs are in regs_list, 
            # add Counter's preset to dictionary, and add Counter to counter_list_current_rung
            elif output_node.node_type == 'CTU':
                if not [output_node.arguments,rung_count] in counter_list:
                    counter_list.append([output_node.arguments,rung_count])
                    regs_list.append(['{}_IN'.format(output_node.arguments[0]),'bool'])
                    if not ['{}_PRE'.format(output_node.arguments[0]),'int'] in regs_list:
                        regs_list.append(['{}_PRE'.format(output_node.arguments[0]),'int'])
                    if not ['{}_RES'.format(output_node.arguments[0]),'bool'] in regs_list:
                        regs_list.append(['{}_RES'.format(output_node.arguments[0]),'bool'])
                counter_list_current_rung.append([output_node.arguments,rung_count])
                counter_presets[output_node.arguments[0]] = output_node.arguments[1].split('=')[1]
            
            # Add reg to ote_list. RES is already in the regs_list because of the Counter code above
            elif output_node.node_type == 'RES':
                tmp = output_node.arguments[0]
                ote_list.append('{}_RES'.format(tmp))
            


        
        ### Create logical expression for this rung which will serve as the right-hand side of the Verilog assignment statements
        # This string will contain the logical Verilog expression
        logical_expression = ''
        # One Shots need to be tracked, they are a unique case in which assignment happens in the left-hand side of a ladder logic rung
        ons_list = []

        # General approach: Go from left to right through the Nodes remaining in the nodes_list. Convert the Node to a Verilog equivalent string
        # and append this string segment to the greater logical_expression (Verilog logical expression). 
        # We need the i counter because One Shots will use information from previous Nodes 
        for i in range(0,len(nodes)):
            # Basic info for Node
            node = nodes[i]
            type = node.node_type
            
            # Based on the node_type, add a string segment to the logical_expression
            # This is where Ladder Logic -> Verilog conversion occurs at its most basic level
            if type == 'AND':
                logical_expression += '&& '
                
            elif type == 'OR':
                logical_expression += '|| '
                
            elif type == 'XIC':
                logical_expression += 'n_{} '.format(node.arguments[0])
            
            elif type == 'XIO':
                logical_expression += '!n_{} '.format(node.arguments[0])
            
            elif type == 'LBRACKET':
                logical_expression += '('
            
            elif type == 'RBRACKET':
                logical_expression += ')'
            
            # Greater than or equal to function (>=). Both arguments can be either a fixed integer (String) or the name of an integer register (String).
            elif type == 'GEQ':
                # A and B are the arguments in the function where out = (A>=B).
                A = node.arguments[0]   # String
                B = node.arguments[1]   # String
                
                # Four cases:
                # (int,int)
                if A.isnumeric() and B.isnumeric():
                    logical_expression += "(32'd{} >= 32'd{}) ".format(A,B)
                # (int, reg)
                elif A.isnumeric() and not B.isnumeric():
                    logical_expression += "(32'd{} >= n_{}) ".format(A,B)
                # (reg, int)
                elif not A.isnumeric() and B.isnumeric():
                    logical_expression += "(n_{} >= 32'd{}) ".format(A, B)
                # (reg, reg)
                else:
                    logical_expression += "(n_{} >= n_{}) ".format(A,B)
                
                # Ensure regs are in regs_list.
                if not A.isnumeric():
                    if not [A, 'int'] in regs_list:
                        if A[-4:] != '_ACC':
                            regs_list.append([A, 'int'])
                if not B.isnumeric():
                    if not [B, 'int'] in regs_list:
                        if B[-4:] != '_ACC':
                            regs_list.append([B, 'int'])
            
            # Equality function (==). Both arguments can be either a fixed integer (String) or the name of an integer register (String).
            elif type == 'EQU':
                # A and B are the arguments in the function where out = (A==B).
                A = node.arguments[0]   # String
                B = node.arguments[1]   # String
                
                # Four cases:
                # (int,int)
                if A.isnumeric() and B.isnumeric():
                    logical_expression += "(32'd{} == 32'd{}) ".format(A,B)
                # (int, reg)
                elif A.isnumeric() and not B.isnumeric():
                    logical_expression += "(32'd{} == n_{}) ".format(A,B)
                # (reg, int)
                elif not A.isnumeric and B.isnumeric():
                    logical_expression += "(n_{} == 32'd{}) ".format(A, B)
                # (reg, reg)
                else:
                    logical_expression += "(n_{} == n_{}) ".format(A,B)
                    
                # Ensure regs are in regs_list.
                if not A.isnumeric():
                    if not [A, 'int'] in regs_list:
                        if A[-4:] != '_ACC':
                            regs_list.append([A, 'int'])
                if not B.isnumeric():
                    if not [B, 'int'] in regs_list:
                        if B[-4:] != '_ACC':
                            regs_list.append([B, 'int'])
            
            # One Shot function, when input is true, output is true for one cycle, then false until input is reset back to false and true again
            # Implemeting this function properly neccesitates a completely different conversion method that is more complex than the current system.
            # Current workaround uses the previous Node's XIC or XIO status as the input, though this does not work in many scenarios.
            elif type == 'ONS':
                # One Shot will not work in this case
                if i < 2:
                    prev_node = None
                # Find previous XIC or XIO node (skipping AND/OR node in between)
                else:
                    prev_node = nodes[i-2]
                if prev_node is None:
                    print('\n############# WARNING ###############')
                    print('ONS one shot variable connected to power rail or parallel combination in rung {}\n'.format(rung_count))
                    print('#####################################\n')
                if prev_node.node_type not in ['XIC', 'XIO']:
                    print('\n############# ERROR ###############')
                    print('ONS in an improper location in rung {}. Currently, ONS may only follow an XIC or XIO immediately following the left power rail.\n'.format(rung_count))
                    print('#####################################\n')
                
                # Use previous XIC or XIO as input for the One Shot
                logical_expression += '(n_{} && !prev_{}) '.format(prev_node.arguments[0], prev_node.arguments[0])
                # Add a new reg to the regs_list to track the One Shot's input's previous state
                if not ['prev_{}'.format(prev_node.arguments[0]), 'bool'] in regs_list:
                    regs_list.append(['prev_{}'.format(prev_node.arguments[0]), 'bool'])
                # Add One Shot to the ons_list so its previous value will be updated at the correct time
                ons_list.append('{}'.format(prev_node.arguments[0]))
        
        # Format logical expression and if there is no expression, set the expression to always be true
        logical_expression = logical_expression.strip()
        if logical_expression == '':
            logical_expression = "1'b1"
        
        
        
        
        ### Create the rung_text (Verilog code for this ladder logic rung)
        # This text will contain all the assignments within this rung using our logical_expression for this rung
        rung_text = '\t\t\t'
        rung_text += '{}: begin'.format(rung_count)
        
        # Basic reg assignments
        for l in ote_list:
            rung_text += '\n\t\t\t\tn_{} <= {};'.format(l,logical_expression)
        
        # Basic (32 bit) reg assignments
        if len(mov_list) > 0:
            rung_text += "\n\t\t\t\tif (({}) == 1'b1)\n\t\t\t\tbegin".format(logical_expression)
            for m in mov_list:
                rung_text += "\n\t\t\t\t\tn_{} <= 32'd{};".format(m[1], m[0])
            rung_text += '\n\t\t\t\tend'
        
        # 32 bit reg assignments in the form C = A + B
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
        
        # Basic reg assignments, where '_IN' denotes the input enable of a Timer
        for t in timer_list_current_rung:
            rung_text += '\n\t\t\t\tn_{}_IN <= {};'.format(t[0][0], logical_expression)
            
        # Basic reg assignments, where '_IN' denotes the input of a Counter    
        for c in counter_list_current_rung:
            rung_text += '\n\t\t\t\tn_{}_IN <= {};'.format(c[0][0], logical_expression)
            
        # Update the previous value of the One Shot's input
        for o in ons_list:
            rung_text += '\n\t\t\t\tprev_{} <= n_{};'.format(o, o)
            
        # Append this rung's Verilog text to the whole rungs_text and increment rung counter
        rung_text += '\n\t\t\tend\n\n'
        rungs_text += rung_text
        rung_count += 1
        
        
        
        
    ### "Bonus" Rung assignments.
    # This is an extra rung to assign all variables from their n_variables (temporary variable) values
    regs_list = sorted(regs_list)
    rungs_text += '\t\t\t{}: begin'.format(rung_count)
    for reg in regs_list:
        if reg[1] == 'bool':
            if 'prev_' not in reg[0]:
                rungs_text += '\n\t\t\t\t{} <= n_{};'.format(reg[0],reg[0])
    rungs_text += '\n'
    for reg in regs_list:
        if reg[1] == 'int':
            rungs_text += '\n\t\t\t\t{} <= n_{};'.format(reg[0],reg[0])    
    rungs_text += '\n\n\t\t\tend\n'

    
    
    
    ### Replacing the rungs_count and set_rungs placeholders with their actual strings within the Verilog file's text
    v_text = v_text.replace('{rungs_count}', str(rung_count+1))   
    v_text = v_text.replace('{set_rungs}', rungs_text)
    
    
    
    
    ### Create regs text
    ### Creating list of registers with the temporary (n_variable) and actual/physical registers
    ### For each register, create declaration and assignment with default value if not 0
    # Begin with an empty string to hold all regs text
    regs_text = ''
    
    # For binary registers, we don't need to specify default values
    for reg in regs_list:
        if reg[1] == 'bool':
            regs_text += "\nreg {};".format(reg[0])
    
    # For integer (32 bit) registers, we specify default values if the register is a Timer or Counter preset
    for reg in regs_list:
        if reg[1] == 'int':
            if reg[0][-4:] == '_PRE':
                if reg[0][:-4] in timer_presets:
                    timer_preset = timer_presets[reg[0][:-4]]
                    regs_text += "\nreg [31:0]{} = 32'd{};".format(reg[0], timer_preset)
                elif reg[0][:-4] in counter_presets:
                    counter_preset = counter_presets[reg[0][:-4]]
                    regs_text += "\nreg [31:0]{} = 32'd{};".format(reg[0], counter_preset)
            else:
                regs_text += "\nreg [31:0]{};".format(reg[0])
                
    regs_text += '\n'  

    # Repeat above, but for temporary (n_variable) registers
    # For binary registers, we don't need to specify default values
    for reg in regs_list:
        if reg[1] == 'bool':
            if 'prev_' not in reg[0]:
                regs_text += "\nreg n_{};".format(reg[0])
                
    # For integer (32 bit) registers, we specify default values if the register is a Timer or Counter preset
    for reg in regs_list:
        if reg[1] == 'int':
            if reg[0][-4:] == '_PRE':
                if reg[0][:-4] in timer_presets:
                    timer_preset = timer_presets[reg[0][:-4]]
                    regs_text += "\nreg [31:0]n_{} = 32'd{};".format(reg[0], timer_preset)
                elif reg[0][:-4] in counter_presets:
                    counter_preset = counter_presets[reg[0][:-4]]
                    regs_text += "\nreg [31:0]n_{} = 32'd{};".format(reg[0], counter_preset)
            else:
                regs_text += "\nreg [31:0]n_{};".format(reg[0])
                
    # Replace set_regs placeholder with actual regs_text string in Verilog file's text
    v_text = v_text.replace('{set_regs}', regs_text)
    
    
    
    
    ### Create resets text
    ### This is very similar to the previous section (Create regs text), except we assign a value for every variable.
    ### This is for the Verilog case where the rst switch is flipped low (not active) and the entire "program" is reset
    resets_text = ''
    
    # Binary registers
    for reg in regs_list:
        if reg[1] == 'bool':
            resets_text += "\n\t\t{} <= 1'b0;".format(reg[0])
            
    # Integer Registers
    for reg in regs_list:
        if reg[1] == 'int':
            if reg[0][-4:] == '_PRE':
                if reg[0][:-4] in timer_presets:
                    timer_preset = timer_presets[reg[0][:-4]]
                    resets_text += "\n\t\t{} <= 32'd{};".format(reg[0], timer_preset)
                elif reg[0][:-4] in counter_presets:
                    counter_preset = counter_presets[reg[0][:-4]]
                    resets_text += "\n\t\t{} <= 32'd{};".format(reg[0], counter_preset)
            else:
                resets_text += "\n\t\t{} <= 32'd0;".format(reg[0])
    
    resets_text += '\n'            
    
    # Binary temporary registers
    for reg in regs_list:
        if reg[1] == 'bool':
            if 'prev_' not in reg[0]:
                resets_text += "\n\t\tn_{} <= 1'b0;".format(reg[0])
    
    # Integer temporary registers
    for reg in regs_list:
        if reg[1] == 'int':
            if reg[0][-4:] == '_PRE':
                if reg[0][:-4] in timer_presets:
                    timer_preset = timer_presets[reg[0][:-4]]
                    resets_text += "\n\t\tn_{} <= 32'd{};".format(reg[0], timer_preset)
                elif reg[0][:-4] in counter_presets:
                    counter_preset = counter_presets[reg[0][:-4]]
                    resets_text += "\n\t\tn_{} <= 32'd{};".format(reg[0], counter_preset)
            else:
                resets_text += "\n\t\tn_{} <= 32'd0;".format(reg[0])
    
    # Replace set_resets placeholder with actual regs_text string in Verilog file's text 
    v_text = v_text.replace('{set_resets}', resets_text)
    
    
    
    
    # Create template modules text
    # For more advanced functions such as Timers and Counters, the logic is handled in another module. 
    # We need to wire these modules into the main module by instantiating the boilerplate function module as many
    # times as is needed with the proper input and output wires and registers for each instantiation.
    
    # Begin with an empty string
    template_modules_text = ''
    
    # Always add DownClock Module. This is never affected by the PLC program, so no wires are needed to interact with the ladder logic.
    template_modules_text += '// Make a slowed-down (1kHz) clock\nwire tick;\nDownClock down(clk, rst, tick);'
    template_modules_text += '\n\n'
    
    # Add Counters if needed
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
                template_modules_text += 'wire [31:0]n_{}_ACC;\n'.format(timer_name, timer_name)
                template_modules_text += 'wire n_{}_DN, n_{}_TT, n_{}_EN;\n'.format(timer_name, timer_name, timer_name)
                template_modules_text += "Timer t{}(clk, rst, tick, n_{}_PRE, n_{}_IN, n_{}_DN, n_{}_TT, n_{}_EN, n_{}_ACC);\n\n" \
                    .format(timer_cnt,timer_name,timer_name,timer_name,timer_name,timer_name,timer_name)
    
    # Add Counters if needed
    counter_cnt = 0
    for i in range(rung_count):
        flg = 0
        for counter in counter_list:
            if counter[1] == i:
                counter_cnt += 1
                if flg == 0:
                    template_modules_text += '/* Rung {} */\n'.format(i)
                    flg = 1
                counter_name = counter[0][0]
                template_modules_text += '// Counter: {}\n'.format(counter_name)
                template_modules_text += 'wire [31:0]n_{}_ACC;\n'.format(counter_name, counter_name)
                template_modules_text += 'wire n_{}_DN, n_{}_CU;\n'.format(counter_name, counter_name)
                template_modules_text += "Counter c{}(clk, rst, n_{}_PRE, n_{}_IN, n_{}_RES, n_{}_DN, n_{}_CU, n_{}_ACC);\n\n" \
                    .format(counter_cnt,counter_name,counter_name,counter_name,counter_name,counter_name,counter_name)
    
    # Replace placeholder with actual template modules text
    v_text = v_text.replace('{set_template_modules}', template_modules_text);
    
    
    
    
    #### Create the Verilog file
    with open('{}.v'.format(filename), 'w') as file:
        file.write(v_text)
    print('Created file {}.v\n'.format(filename))




def main():
    try:
        file = sys.argv[1]
        # Remove / or \ or . at beginning of file name
        while not file[0].isalnum():
            file = file[1:]
        [filename, filetype] = file.split('.') # taking second item from argv
    except: # if it is a bad file, can't be read by xml parser tree, file doesn't exist it, or no file argument at all: cancels program
        print('\nPlease enter valid .L5X or .HSHG file in form "python allenbradley_parser.py example.L5X"\n')
        sys.exit(1)
    
    if filetype.upper() not in ['L5X', 'XML', 'HSHG']:
        print('\nInvalid filetype, please enter valid .L5X or .HSHG file in form "python allenbradley_parser.py example.L5X"\n')
        sys.exit(1)
        
    if filetype.upper() in ['L5X', 'XML']:
        # Taking second command-line argument (filename), doing element tree parse on that to get the root of the XML tree
        tree = ET.parse(sys.argv[1]) 
        print('\nParsing {}'.format(sys.argv[1]))
        root = tree.getroot()
        parse_l5x(root, filename)
        
    write_verilog(filename)
    
    
    
    
if __name__ == '__main__':
    main()
