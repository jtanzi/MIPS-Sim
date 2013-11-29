"""ACO Course Project
MIPS R4000 Simulator
Author: Joel Tanzi
Date: 10/6/2013
Version: 1.0"""

import re
import os
import string

#---Function and Variable Declarations---


#----------------CLASSES-----------------
"""Memory"""

#Slot class
#Contains address (addr) and value for that memory slot
class Slot(object):  

	def __init__(self):
		self.addr = 0
		self.value = 0


#Memory class
#Consists of Slot instances in array the size of desired memory space
class Memory(object): 

	def __init__(self, num_Slots):
		self.Slots = [Slot() for each in range(num_Slots)]
	
	def write(self, addr, value):
		for r in range(len(self.Slots)):
			if self.Slots[r].addr == addr:
				self.Slots[r].value = value
				break

	def retrieve(self, addr):
		for r in range(len(self.Slots)):
			if self.Slots[r].addr == addr:
				value = self.Slots[r].value
		return value

"""Instructions"""

#Ins class for handling instructions
#Consists of instruction number (ins_num), opcode, 
#source registers (scr1, scr2), destination (memory or register) dest,
# and optional immediate value (imm)
class Ins(object):

	def __init__(self):
		self.ins_num = 0
		self.opcode = 'NOP'
		self.scr1 = 'NULL'
		self.scr2 = 'NULL'
		self.dest = 'NULL'
		self.imm = 0

	def __init__(self, ins_num, opcode, scr1, scr2, dest, imm):
		self.ins_num = ins_num
		self.opcode = opcode
		self.scr1 = scr1
		self.scr2 = scr2
		self.dest = dest
		self.imm = imm

	def write(self, ins_num, opcode, scr1 = 'NULL', scr2 = 'NULL', 
				dest = 'NULL', imm = 0):
		self.ins_num = ins_num
		self.opcode = opcode
		self.scr1 = scr1
		self.scr2 = scr2
		self.dest = dest
		self.imm = imm

	def flush(self):
		self.opcode = 'NOP'
		self.scr1 = 'NULL'
		self.scr2 = 'NULL'
		self.dest = 'NULL'
		self.imm = 0


#Contructing memory space, addresses are multiples of 8
mem_size = 125
MEM = Memory(mem_size)
for r in range(mem_size):
	MEM.Slots[r].addr = r * 8

"""Registers"""
REG = [0] * 32
IR = []

"""Flow Control Variables"""
PC = 0
inst_count = 0
sim_cycle = 1
branch_flag = False
branch_labels = dict()

#Create instruction register


#Pipeline Registers
IF1_IF2_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
IF2_ID_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
ID_EX_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
EX_MEM1_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
MEM1_MEM2_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
MEM2_MEM3_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
MEM3_WB_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)

#Pipeline Register Change Flags
IF1_IF2_changed = False
IF2_ID_changed = False
ID_EX_changed = False
EX_MEM1_changed = False
MEM1_MEM2_changed = False
MEM2_MEM3_changed = False
MEM3_WB_changed = False


#-----------FUNCTIONS-----------------

#parse_ins function
#Parses the instruction string lists read in from CODE section
#Returns an instruction built from the line read
def parse_ins(ins_string, ins_num):
	
	if ins_string[0] == 'LD':
		a = ins_string[2].split('(')
		imm = int(a[0])
		dest = a[1][0:2]
		scr1 = ins_string[1]
		instruction = Ins(ins_num, 'LD', scr1, 'NULL', dest, imm)

	elif ins_string[0] == 'SD':
		a = ins_string[2].split('(')
		imm = int(a[0])
		scr1 = a[1][0:2]
		dest = ins_string[1]
		instruction = Ins(ins_num, 'SD', scr1, 'NULL', dest, imm)
		
	elif ins_string[0] == 'DADD':
		for r in range(len(ins_string)):
			if string.find(ins_string[r],'#') == -1:
				scr1 = ins_string[2]
				scr2 = ins_string[3]
				dest = ins_string[1]			
				instruction = Ins(ins_num, 'DADD', scr1, scr2, dest, 0)
			else:
				scr1 = ins_string[2]
				scr2 = 'NULL'
				dest = ins_string[1]
				imm = int(re.sub(r'\W+', " ", ins_string[3]))
				instruction = Ins(ins_num, 'DADD', scr1, scr2, dest, imm)

	elif ins_string[0] == 'SUB':
		for r in range(len(ins_string)):
			if string.find(ins_string[r],'#') == -1:
				scr1 = ins_string[2]
				scr2 = ins_string[3]
				dest = ins_string[1]			
				instruction = Ins(ins_num, 'SUB', scr1, scr2, dest, 0)

			else:
				scr1 = ins_string[2]
				scr2 = 'NULL'
				dest = ins_string[1]
				imm = int(re.sub(r'\W+', " ", ins_string[3]))
				instruction = Ins(ins_num, 'SUB', scr1, scr2, dest, imm)

	elif ins_string[0] == 'BNEZ':
		imm = 0
		scr1 = ins_string[1]
		instruction = Ins(ins_num, 'BNEZ', scr1, 'NULL', 'NULL', imm)

	return instruction		


#---------------Pipeline Stages-----------------

#Instruction Fetch (IF1 & IF2)
def IF1(ins_num, last_ins_num, last_inst_read_flag, IF1_IF2_changed, branch_flag):
	
	#print str('ins_num/4 = ' + str(ins_num/4))
	#print str('last_ins_num = ' + str(last_ins_num))
	if (ins_num/4 != last_ins_num):
		inst = IR[ins_num/4]
		if branch_flag:
			inst.flush()
		ins_num +=4
		IF1_message = str('I' + str(inst.ins_num) + '-' + 'IF1' + ' ')
		IF1_IF2_changed = True

	else:
		inst = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
		IF1_message = ''
		IF1_IF2_changed = False
		last_inst_read_flag = True

	return IF1_message, inst, ins_num, IF1_IF2_changed, last_inst_read_flag


def IF2(inst, IF1_IF2_changed):
	if IF1_IF2_changed:
		IF2_message = str('I' + str(inst.ins_num) + '-' + 'IF2' + ' ')
		IF2_ID_changed = True
	else:
		if inst.opcode == 'NOP':
			IF2_message = ''
			IF2_ID_changed = False
		else:
			IF2_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
			IF2_ID_changed = False

	return IF2_message, inst, IF2_ID_changed

#Instruction Decode (ID)
def ID(inst, IF2_ID_changed):

	if IF2_ID_changed:
		ID_message = str('I' + str(inst.ins_num) + '-' + 'ID' + ' ')
		ID_EX_reg = inst
		ID_EX_changed = True
	else:
		if inst.opcode == 'NOP':
			ID_message = ''
			ID_EX_changed = False
		else:
			ID_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
			ID_EX_changed = False

	return ID_message, inst, ID_EX_changed
	
#Execution (EX)
def EX(inst, ID_EX_changed):

	if ID_EX_changed:
		EX_message = str('I' + str(inst.ins_num) + '-' + 'EX' + ' ')
		EX_MEM1_reg = inst
		EX_MEM1_changed = True
	else:
		if inst.opcode == 'NOP':
			EX_message = ''
			EX_MEM1_changed = False
		else:
			EX_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
			EX_MEM1_changed = False

	return EX_message, inst, EX_MEM1_changed

#Memory Access (MEM1, MEM2, MEM3)
def MEM1(inst, EX_MEM1_changed):
	
	if EX_MEM1_changed:
		MEM1_message = str('I' + str(inst.ins_num) + '-' + 'MEM1' + ' ')
		MEM1_MEM2_reg = inst
		MEM1_MEM2_changed = True
	else:
		if inst.ins_num == 'NOP':
			MEM1_message = ''
			MEM1_MEM2_changed = False
		else:
			MEM1_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
			MEM1_MEM2_changed = False

	return MEM1_message, inst, MEM1_MEM2_changed

def MEM2(inst, MEM1_MEM2_changed):
	
	if MEM1_MEM2_changed:
		MEM2_message = str('I' + str(inst.ins_num) + '-' + 'MEM2' + ' ')
		MEM2_MEM3_reg = inst
		MEM2_MEM3_changed = True
	else:
		if inst.opcode == 'NOP':
			MEM2_message = ''
			MEM2_MEM3_changed = False
		else:
			MEM2_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
			MEM2_MEM3_changed = False
		
	return MEM2_message, inst, MEM2_MEM3_changed

def MEM3(inst, MEM2_MEM3_changed):
	
	if MEM2_MEM3_changed:
		MEM3_message = str('I' + str(inst.ins_num) + '-' + 'MEM3' + ' ')
		MEM3_WB_reg = inst
		MEM3_WB_changed = True
	else:
		if inst.opcode == 'NOP':
			MEM3_message = ''
			MEM3_WB_changed = False
		else:
			MEM3_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
			MEM3_WB_changed = False
			
	return MEM3_message, inst, MEM3_WB_changed

#Write Back (WB)
def WB(inst, last_ins_num, last_inst_write_back, MEM3_WB_changed):
	
	if inst.ins_num == last_ins_num:
		last_inst_write_back = True

	if MEM3_WB_changed:
		WB_message = str('I' + str(inst.ins_num) + '-' + 'WB')
	else:
		if inst.opcode == 'NOP':
			WB_message = ''
		else:
			WB_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')

	return WB_message, last_inst_write_back


#----------------SIMULATION--------------------

#Obtain input file name from user
fname = raw_input("Input file name: ")
print fname
oname = raw_input("Output file name: ")
print oname

byte_count = os.path.getsize(fname)
print byte_count, " bytes"

#Open input and output files and start reading from input file
f = open(fname, 'r')
o = open(oname, 'w')

buf = f.readline()
index = 0

#Initialize Registers
print 'REGISTERS'
if 'REGISTERS' in buf:
	while not 'MEMORY' in buf:
		buf = f.readline().rstrip()
		if buf == '':
			pass
		elif buf != 'MEMORY':
			a = buf.split(" ")
			regnum = int(re.sub("[^0-9]", " ", a[0]))
			value = int(re.sub("[^0-9]", " ", a[1]))
			if regnum != 0:	 #Prevent writing to R0		
				REG[regnum] = value
			print 'R'+str(regnum), REG[regnum]

#Initialize Memory
print 'MEMORY'
while not 'CODE' in buf:
	buf = f.readline().rstrip()
	if buf == '':
		pass
	elif buf != 'CODE':
		a = buf.split(" ")
		addr = int(re.sub("[^0-9]", " ", a[0]))
		value = int(re.sub("[^0-9]", " ", a[1]))
		MEM.write(addr, value)
		print addr, MEM.retrieve(addr)


#Initialize instruction register
#print 'CODE'
ins_num = 1
ins_count = 1

while (f.tell() < byte_count):  #Read to end of input file
	buf = f.readline().strip()
	buf = re.sub(',', '', buf)  #Gets rid of commas (makes parsing easier)
	if buf.find(':') == -1:  #No branch label read
		a = buf.split(" ")

	else:					 #Branch label read
		a = buf.split(" ")
		branch_labels[a[0]] = ins_num-1
		del a[0]
		for r in range(len(a)-1):  #Clean up spaces in instruction string
			if '' in a:
				del a[a.index('')]


	#print str(ins_num-1)+':', a
	
	IR.append(parse_ins(a, ins_num))

	#Increment counters
	ins_num = ins_num + 1
	ins_count = ins_count + 1


#TEST - print PC
for r in range(len(IR)):
	print (IR[r].ins_num, IR[r].opcode, IR[r].scr1,
			IR[r].scr2, IR[r].dest, IR[r].imm)

#Write to Output file
last_ins_num = IR[len(IR)-1].ins_num
last_inst_read_flag = False
last_inst_write_back = False
write_str = ''
stall = False

while not last_inst_write_back:

	log_str = str('c#' + str(sim_cycle) +  ' ')

	WB_message, last_inst_write_back = WB(MEM3_WB_reg, last_ins_num, 
		last_inst_write_back, MEM3_WB_changed)

	MEM3_message, MEM3_WB_reg, MEM3_WB_changed = MEM3(MEM2_MEM3_reg,  
		MEM2_MEM3_changed)

	MEM2_message, MEM2_MEM3_reg, MEM2_MEM3_changed = MEM2(MEM1_MEM2_reg, 
		MEM1_MEM2_changed)

	MEM1_message, MEM1_MEM2_reg, MEM1_MEM2_changed = MEM1(EX_MEM1_reg, 
		EX_MEM1_changed)

	EX_message, EX_MEM1_reg, EX_MEM1_changed = EX(ID_EX_reg, ID_EX_changed)

	ID_message, ID_EX_reg, ID_EX_changed = ID(IF2_ID_reg, IF2_ID_changed)

	IF2_message, IF2_ID_reg, IF2_ID_changed = IF2(IF1_IF2_reg, IF1_IF2_changed)

	IF1_message, IF1_IF2_reg, PC, IF1_IF2_changed, last_inst_read_flag = IF1(
		PC, last_ins_num, last_inst_read_flag, IF1_IF2_changed, branch_flag)

	write_str = (log_str + IF1_message + IF2_message + ID_message + EX_message
				+ MEM1_message + MEM2_message + MEM3_message + WB_message)
	
	o.write(write_str + '\n')

	sim_cycle += 1

o.write('\nREGISTERS\n')
for r in range(len(REG)):
	if REG[r] != 0:
		wbuf = str('R'+str(r) +' ' + str(REG[r]) + '\n')
		o.write(wbuf)

o.write('\nMEMORY\n')
for r in range(mem_size):
	if MEM.retrieve(r*8) != 0:
		wbuf = str(str(r*8) + ' ' + str(MEM.retrieve(r*8)) + '\n')
		o.write(wbuf)

#Print branch addresses for testing
#print '\nBranches\n', branch_labels

f.close()
o.close()

#---END---	
