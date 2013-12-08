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


#[VAR LOCATION]

#-----------FUNCTIONS-----------------

#parse_ins function
#Parses the instruction string lists read in from CODE section
#Returns an instruction built from the line read
def parse_ins(ins_string, ins_num, branch_ref):
	
	if ins_string[0] == 'LD':
		a = ins_string[2].split('(')
		imm = int(a[0])
		dest = 0
		scr2 = ins_string[1]
		scr1 = re.sub("\)", "", a[1])
		instruction = Ins(ins_num, 'LD', scr1, scr2, dest, imm)

	elif ins_string[0] == 'SD':
		a = ins_string[2].split('(')
		imm = int(a[0])
		scr1 = a[1][0:2]
		scr2 = ins_string[1]
		instruction = Ins(ins_num, 'SD', scr1, scr2, 0, imm)
		
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
		branch_ref[ins_num] = ins_string[2]
		instruction = Ins(ins_num, 'BNEZ', scr1, 'NULL', 'NULL', imm)

	return instruction, branch_ref	

#Hazard checking

def RAW_hazard_check(rs, rt, ID_EX_reg):
	
	if rs == ID_EX_reg.dest or rt == ID_EX_reg.dest:
		return True
	else:
		return False

def WAW_hazard_check(dest, ID_EX_reg):
	
	if dest == ID_EX_reg.dest:
		return True
	else:
		return False


#---------------Pipeline Stages-----------------

#Instruction Fetch (IF1 & IF2)
def IF1(PC, IR, last_ins_num, last_inst_read_flag, branch_flag, stall_flag):

	if stall_flag:
		IF1_message = str('I' + str(IR.ins_num) + '-' + 'Stall' + ' ')	
	elif (PC/4 <= last_ins_num -1):
		IR = IMEM[PC/4]		
		IF1_message = str('I' + str(IR.ins_num) + '-' + 'IF1' + ' ')
	else:
		IR = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
		IF1_message = ''
		last_inst_read_flag = True
	
	return IF1_message, IR, PC, last_inst_read_flag


def IF2(inst, PC, NPC, stall_flag):
	
	if stall_flag:
		IF2_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
	else:
		NPC = PC + 4

		if inst.opcode == 'NOP':
			IF2_message = ''
		else:
			IF2_message = str('I' + str(inst.ins_num) + '-' + 'IF2' + ' ')
	
	return IF2_message, inst, NPC 
	

#Instruction Decode (ID)
def ID(inst, ID_EX_reg, stall_flag, A, B, imm, branch_labels, branch_ref, REG):

	if stall_flag:
		ID_message = str('I' + str(inst.ins_num) + '-' + 'Stall' + ' ')
	elif inst.opcode == 'NOP':
		ID_message = ''
	else:
		if inst.opcode == 'BNEZ':
			#print branch_labels
			#print branch_ref
			imm = int(branch_labels[str(branch_ref[inst.ins_num] + ':')])
			inst.imm = imm

		ID_message = str('I' + str(inst.ins_num) + '-' + 'ID' + ' ')

		#Decode instruction
		if inst.scr1 != 'NULL':
			#print str('inst.scr1 = ' + str(inst.scr1))
			A = REG[int(re.sub("[^0-9]", " ", inst.scr1))]
		else:
			A = 0
		if inst.scr2 != 'NULL':
			B = REG[int(re.sub("[^0-9]", " ", inst.scr2))]
		else:
			B = 0
		imm = inst.imm
		print 'ID: '
		print str('A = ' + str(A))
		print str('B = ' + str(B))
		print str('imm = ' + str(imm))
		
	return ID_message, inst, stall_flag, A, B, imm, REG

	
#Execution (EX)
def EX(inst, NPC, A, B, imm, ALU_Output, branch_flag, stall_flag):

	if inst.opcode == 'NOP':
		EX_message = ''
	else:
		print 'EX: '
		print str('A = ' + str(A))
		print str('B = ' + str(B))
		print str('imm = ' + str(imm))
		if inst.opcode == 'LD' or inst.opcode == 'SD':
			ALU_Output = A + imm
		elif inst.opcode == 'DADD':
			ALU_Output = A + B + imm
		elif inst.opcode == 'SUB':
			ALU_Output = A - B - imm
		elif inst.opcode == 'BNEZ':
			ALU_Output = imm
			branch_flag = (A == 0)
		print str('ALU_Output = ' + str(ALU_Output))
		EX_message = str('I' + str(inst.ins_num) + '-' + 'EX' + ' ')

	return EX_message, inst, B, ALU_Output, branch_flag


#Memory Access (MEM1, MEM2, MEM3)
def MEM1(inst, B, PC, NPC, LMD, ALU_Output, branch_flag, MEM):

	PC = NPC
	print 'MEM1: '
	print str('ALU_Output = ' + str(ALU_Output))

	if inst.opcode == 'NOP':
		MEM1_message = ''
	else:
		if inst.opcode == 'LD':
			LMD = MEM.retrieve(ALU_Output)
			print str('LMD = ' + str(LMD))
		elif inst.opcode == 'SD':
			print str('ALU_Output = ' + str(ALU_Output))
			print str('B = ' + str(B))
			MEM.write(ALU_Output, B)
		elif inst.opcode == 'BNEZ':
			if branch_flag:
				PC = ALU_Output * 4
				branch_flag = False

		MEM1_message = str('I' + str(inst.ins_num) + '-' + 'MEM1' + ' ')

	return MEM1_message, inst, PC, LMD, MEM, ALU_Output


def MEM2(inst, ALU_Output):

	if inst.opcode == 'NOP':
		MEM2_message = ''
	else:
		MEM2_message = str('I' + str(inst.ins_num) + '-' + 'MEM2' + ' ')

	return MEM2_message, inst, ALU_Output
	

def MEM3(inst, ALU_Output):

	if inst.opcode == 'NOP':
		MEM3_message = ''
	else:
		MEM3_message = str('I' + str(inst.ins_num) + '-' + 'MEM3' + ' ')

	return MEM3_message, inst, ALU_Output



#Write Back (WB)
def WB(inst, last_ins_num, last_inst_write_back, ALU_Output, LMD, REG):
	
	if inst.ins_num == last_ins_num:
		last_inst_write_back = True

	if inst.opcode == 'NOP':
		WB_message = ''
	else:
		if inst.opcode == 'DADD' or inst.opcode == 'SUB':
			print 'WB: '
			print str('ALU_Output_pass = ' + str(ALU_Output))
			REG[int(re.sub("[^0-9]", " ", inst.dest))] = ALU_Output
		if inst.opcode == 'LD':
			REG[int(re.sub("[^0-9]", " ", inst.scr2))] = LMD
		
		WB_message = str('I' + str(inst.ins_num) + '-' + 'WB')

	return WB_message, last_inst_write_back, REG


#----------------SIMULATION--------------------


prompt_response = ''

while True:

	#Contructing memory space, addresses are multiples of 8
	mem_size = 125
	MEM = Memory(mem_size)
	for r in range(mem_size):
		MEM.Slots[r].addr = r * 8

	"""Registers"""
	REG = [0] * 32
	IMEM = []  #instruction memory
	PC = 0  #program counter
	IR = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
	NPC = 0  #next program counter
	LMD = 0  #load memory data
	
	"""Flow Control Variables"""
	inst_count = 0
	sim_cycle = 1
	branch_flag = False
	branch_labels = dict()
	branch_ref = dict()
	stall_flag = False

	#ALU operators
	A = 0
	B = 0
	B_pass = 0
	imm = 0
	ALU_Output = 0
	ALU_Output_1 = 0
	ALU_Output_2 = 0
	ALU_Output_3 = 0

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
		print buf
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

		#print branch_labels

		next_inst, branch_ref = parse_ins(a, ins_num, branch_ref)
		IMEM.append(next_inst)

		#Increment counters
		ins_num = ins_num + 1
		ins_count = ins_count + 1

	"""
	#TEST - print PC
	for r in range(len(IMEM)):
		print (IMEM[r].ins_num, IMEM[r].opcode, IMEM[r].scr1,
				IMEM[r].scr2, IMEM[r].dest, IMEM[r].imm)
	"""

	#Write to Output file
	last_ins_num = IMEM[len(IMEM)-1].ins_num
	last_inst_read_flag = False
	last_inst_write_back = False
	write_str = ''

	
	#TODO Prompt to run again, loop until user input is 'no'

	while not last_inst_write_back:
		print str('sim_cycle = ' + str(sim_cycle))

		log_str = str('c#' + str(sim_cycle) +  ' ')
	
		#Write Back Stage
		WB_message, last_inst_write_back, REG = WB(MEM3_WB_reg, last_ins_num, 
			last_inst_write_back, ALU_Output_3, LMD, REG)

		#MEM3 Stage
		MEM3_message, MEM3_WB_reg, ALU_Output_3 = MEM3(MEM2_MEM3_reg, ALU_Output_2)

		#Forward from MEM2
		#ALU_Output = ALU_Output2
	
		#MEM2 Stage
		MEM2_message, MEM2_MEM3_reg, ALU_Output_2 = MEM2(MEM1_MEM2_reg, ALU_Output_1)
	
		#Forward from MEM1
		#ALU_Output = ALU_Output1

		#MEM1 Stage
		MEM1_message, MEM1_MEM2_reg, PC, LMD, MEM, ALU_Output_1 = MEM1(EX_MEM1_reg, B_pass, PC, NPC, 
			LMD, ALU_Output, branch_flag, MEM)
		"""
		X = ID_EX_reg.scr1
		Y = ID_EX_reg.scr2
		T = EX_MEM1_reg.dest
		if X == T and X != 'NULL':
			A = ALU_Output
		elif Y == T and Y != 'NULL':
			B = ALU_Output		
		"""
		#Execution Stage
		EX_message, EX_MEM1_reg, B_pass, ALU_Output, branch_flag = EX(ID_EX_reg, NPC, A, 
			B, imm, ALU_Output, branch_flag, stall_flag)

		#Instruction Decode Stage
		ID_message, ID_EX_reg, stall_flag, A, B, imm, REG  = ID(IF2_ID_reg, 
			ID_EX_reg, stall_flag, A, B, imm, branch_labels, branch_ref, REG)
		"""
		#Hazard Check
		X = ID_EX_reg.scr1
		Y = ID_EX_reg.scr2
		T = IF2_ID_reg.scr1
		U = IF2_ID_reg.scr2
		if (X == T or X == U or Y == T or Y == U) and (X != 0 or Y != 0):
			stall_flag = True
		else:
			staff_flag = False
		"""
		#Instruction Fetch 2 Stage
		IF2_message, IF2_ID_reg, NPC = IF2(IF1_IF2_reg, PC, NPC, stall_flag)

		#Instruction Fetch 1 Stage
		IF1_message, IF1_IF2_reg, PC, last_inst_read_flag = IF1(PC, IR, 
			last_ins_num, last_inst_read_flag, branch_flag, stall_flag)

		#Write to output file
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

	prompt_response = raw_input("Do you want to execute another program? (y/n)")
	print prompt_response
	if prompt_response == 'n':
		break
#---END---	
