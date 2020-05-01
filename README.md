# Senior design project 2020
### PLC to FPGA Converter
Don Blank, Janelle Ghanem, Tyler McGrew

This system converts Allen Bradley Ladder Logic to Verilog HDL.

### Features
* All boolean logic (XIC, XIO, OTE)
* Timers (TON)
* Counters (CTU)
* Counter Resets (RES)
* One Shots (ONS)
* Greater than or equal to (GEQ)
* Equality (EQU)
* Integer assignment (MOV)


### Current Limitations
* Only the features above are implemented at this point. More features will be implemented in the coming months.
* The following features must be on the left hand side of the ladder logic program: XIC, XIO, ONS, GEQ, EQU.
* The following features must be on the right hand side of the ladder logic program: OTE, TON, CTU, RES, MOV.
* All features on the right hand side of each rung must be in one parallel list. See [here](https://raw.githubusercontent.com/ghanemja/senior-design/master/misc/ex1.png) and [here](https://raw.githubusercontent.com/ghanemja/senior-design/master/misc/ex2.png) for examples.
* Currently, ONS only work following a single XIC or XIO that immediately follows the left power rail.

### How to Run
To use this system, you just need Python. It has only been tested with Python 3.7.3, but should work with any Python 3.X version.

1. Download GitHub Repository
1. Navigate to the folder pythonparser within the local copy of the repository. This has the Python script allenbradley_parser.py and a few Verilog template files. 
1. Export an Allen Bradley Ladder logic file into an L5X file and place that L5X file in the pythonparser folder. 
1. Run the Python script by: python allenbradley_parser.py [ladderlogic.L5X]
1. This will generate an intermediate .HSHG hashigo logic file using the logic and physical IOs from the L5X ladder logic.
1. The system will then attempt to generate a Verilog file from the created hashigo logic file.
1. Add the generated Verilog file to your FPGA project library. All inputs are automatically assigned to switches and all outputs to red LEDs for the DE2-115 board but these can easiliy be changed in the Verilog file.
