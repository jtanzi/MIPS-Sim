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
		self.ins_count = 0

	def __init__(self, ins_num, opcode, scr1, scr2, dest, imm, ins_count = 0):
		self.ins_num = ins_num
		self.opcode = opcode
		self.scr1 = scr1
		self.scr2 = scr2
		self.dest = dest
		self.imm = imm
		self.ins_count = ins_count

	def write(self, ins_num, opcode, scr1 = 'NULL', scr2 = 'NULL', 
				dest = 'NULL', imm = 0, ins_count = 0):
		self.ins_num = ins_num
		self.opcode = opcode
		self.scr1 = scr1
		self.scr2 = scr2
		self.dest = dest
		self.imm = imm
		self.ins_count = ins_count

	def flush(self):
		self.opcode = 'NOP'
		self.scr1 = 'NULL'
		self.scr2 = 'NULL'
		self.dest = 'NULL'
		self.imm = 0
		self.ins_count = 0


#[VAR LOCATION]

#-----------FUNCTIONS-----------------

#parse_ins function
#Parses the instruction string lists read in from CODE section
#Returns an instruction built from the line read
def parse_ins(ins_string, ins_num, branch_ref):
	
	if ins_string[0] == 'LD':
		a = ins_string[2].split('(')
		imm = int(a[0])
		dest = 'NULL'
		scr2 = ins_string[1]
		scr1 = re.sub("\)", "", a[1])
		instruction = Ins(ins_num, 'LD', scr1, scr2, dest, imm)

	elif ins_string[0] == 'SD':
		a = ins_string[2].split('(')
		imm = int(a[0])
		dest = 'NULL'
		scr1 = a[1][0:2]
		scr2 = ins_string[1]
		instruction = Ins(ins_num, 'SD', scr1, scr2, dest, imm)
		
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




#---------------Pipeline Stages-----------------

#Instruction Fetch (IF1 & IF2)
def IF1(PC, IR, last_ins_num, last_inst_read_flag, branch_flag, stall_flag, prev_branch, inst_count):
	
	print str('len(IMEM) = ' + str(len(IMEM)))
	print str('branch_flag = ' + str(branch_flag))

	if branch_flag:
		IR = Ins(0, 'NOP', 'NULL', 'NULL', 'NULL', 0)
		IF1_message = ''
		branch_flag = False
		prev_branch = True
		last_inst_read_flag = False
	elif (PC/4 < last_ins_num - 1) and not prev_branch:
		IR = IMEM[PC/4]
		
		if stall_flag:
			IF1_message = ''
		else:
			inst_count += 1
			IR.ins_count = inst_count	
			IF1_message = str('I' + str(IR.ins_count) + '-' + 'IF1' + ' ')
	elif prev_branch:
		if (PC/4 <= last_ins_num - 1):
			IR = IMEM[PC/4]
			inst_count += 1
			IR.ins_num = inst_count
		IF1_message = str('I' + str(IR.ins_count) + '-' + 'IF1' + ' ')
		last_inst_read_flag = False
		prev_branch = False
	else:  #Last instruction read
		IR = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
		IF1_message = ''
		last_inst_read_flag = True

	#Uncomment for debugging
	print ''
	print 'IF1:'
	print IF1_message
	print str(IR.opcode + " " + IR.scr1 + " " + IR.scr2 + " " + IR.dest)
	print str('PC = ' + str(PC))
	print str('last_inst_read_flag = ' + str(last_inst_read_flag))
	print str('prev_branch = ' + str(prev_branch))
	print str('inst_count = ' + str(inst_count))	
	return IF1_message, IR, PC, last_inst_read_flag, prev_branch, inst_count


def IF2(inst, PC, NPC, stall_flag, branch_flag):
	
	if branch_flag:
		#inst.flush()
		IF2_message = str('I' + str(inst.ins_count) + '-' + 'IF2' + ' ')
		inst =  Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
	elif stall_flag:
		if inst.ins_num != 0:
			IF2_message = str('I' + str(inst.ins_count) + '-' + 'Stall' + ' ')
		else:
			IF2_message = ''
	else:
		NPC = PC + 4

		if inst.opcode == 'NOP':
			IF2_message = ''
		else:
			IF2_message = str('I' + str(inst.ins_count) + '-' + 'IF2' + ' ')

	#Uncomment for debugging
	"""
	print ''
	print 'IF2:'	
	print IF2_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('NPC: ' + str(NPC))
	"""

	return IF2_message, inst, NPC 

	

#Instruction Decode (ID)
def ID(inst, ID_EX_reg, stall_flag, A, B, imm, branch_labels, branch_ref, REG):

	if branch_flag:
		#inst.flush()
		ID_message = str('I' + str(inst.ins_count) + '-' + 'ID' + ' ')
		inst = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)

	elif stall_flag:
		if inst.ins_num != 0:
			ID_message = str('I' + str(inst.ins_count) + '-' + 'Stall' + ' ')
		else:
			ID_message = ''
		
	elif inst.opcode == 'NOP':
		ID_message = ''		
	else:
		if inst.opcode == 'BNEZ':
			imm = int(branch_labels[str(branch_ref[inst.ins_num] + ':')])
			inst.imm = imm

		ID_message = str('I' + str(inst.ins_count) + '-' + 'ID' + ' ')

		#Decode instruction
		if inst.scr1 != 'NULL':
			A = REG[int(re.sub("[^0-9]", " ", inst.scr1))]
		else:
			A = 0
		if inst.scr2 != 'NULL':
			B = REG[int(re.sub("[^0-9]", " ", inst.scr2))]
		else:
			B = 0
		imm = inst.imm

	#Uncomment for debugging
	"""
	print ''
	print 'ID:'		
	print ID_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('A = ' + str(A))
	print str('B = ' + str(B))
	print str('imm = ' + str(imm))
	"""

	return ID_message, inst, stall_flag, A, B, imm, REG

	
#Execution (EX)
def EX(inst, NPC, A, B, imm, ALU_Output, branch_flag, stall_flag, REG_ready):

	#branch_flag = False

	if stall_flag:
		if inst.ins_num != 0:
			EX_message = str('I' + str(inst.ins_count) + '-' + 'Stall' + ' ')
		else:
			EX_message = ''
	elif branch_flag:
		#inst.flush()
		inst = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
		EX_message = ''
	elif inst.opcode == 'NOP':
		EX_message = ''
	else:
		if inst.opcode == 'LD' or inst.opcode == 'SD':
			ALU_Output = A + imm
		elif inst.opcode == 'DADD':
			ALU_Output = A + B + imm
		elif inst.opcode == 'SUB':
			ALU_Output = A - B - imm
		elif inst.opcode == 'BNEZ':
			ALU_Output = imm
			branch_flag = (A != 0)
			#PC = ALU_Output * 4

		#Data Forwarding
		if inst.dest != 'NULL':
			REG[int(re.sub("[^0-9]", " ", inst.dest))] = ALU_Output
			#REG_ready[int(re.sub("[^0-9]", " ", inst.dest))] = True

		EX_message = str('I' + str(inst.ins_count) + '-' + 'EX' + ' ')

	#Uncomment for debugging
	"""
	print ''
	print 'EX:'
	print EX_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('A = ' + str(A))
	print str('B = ' + str(B))
	print str('imm = ' + str(imm))
	print str('ALU_Output = ' + str(ALU_Output))
	print str('branch_flag = ' + str(branch_flag))
	"""

	return EX_message, inst, B, ALU_Output, branch_flag, REG_ready


#Memory Access (MEM1, MEM2, MEM3)
def MEM1(inst, B, PC, NPC, LMD, ALU_Output, branch_flag, MEM):

	PC = NPC

	if stall_flag:
		inst = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
	if inst.opcode == 'NOP':
		MEM1_message = ''
	else:
		if inst.opcode == 'LD':
			LMD = MEM.retrieve(ALU_Output)
			REG[int(re.sub("[^0-9]", " ", inst.scr2))] = LMD
		elif inst.opcode == 'SD':
			MEM.write(ALU_Output, B)
		elif inst.opcode == 'BNEZ':
			if branch_flag:
				PC = ALU_Output * 4

		branch_flag = False
		
		MEM1_message = str('I' + str(inst.ins_count) + '-' + 'MEM1' + ' ')

	#Uncomment for debugging
	"""
	print ''
	print 'MEM1:'
	print MEM1_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('B = ' + str(B))
	print str('PC = ' + str(PC))
	print str('NPC = ' + str(NPC))
	print str('LMD = ' + str(LMD))
	print str('ALU_Output = ' + str(ALU_Output))
	print str('branch_flag = ' + str(branch_flag))
	"""

	return MEM1_message, inst, PC, LMD, MEM, ALU_Output, branch_flag


def MEM2(inst, ALU_Output):

	if inst.opcode == 'NOP':
		MEM2_message = ''
	else:
		MEM2_message = str('I' + str(inst.ins_count) + '-' + 'MEM2' + ' ')

	#Uncomment for debugging
	"""
	print ''
	print 'MEM2:'
	print MEM2_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('ALU_Output = ' + str(ALU_Output))
	"""
	
	return MEM2_message, inst, ALU_Output
	

def MEM3(inst, ALU_Output):

	if inst.opcode == 'NOP':
		MEM3_message = ''
	else:
		MEM3_message = str('I' + str(inst.ins_count) + '-' + 'MEM3' + ' ')

	#Uncomment for debugging
	"""
	print ''
	print 'MEM3:'
	print MEM3_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('ALU_Output = ' + str(ALU_Output))	
	"""

	return MEM3_message, inst, ALU_Output



#Write Back (WB)
def WB(inst, inst_count, last_inst_write_back, last_inst_read_flag, ALU_Output, LMD, REG):
	
	if last_inst_read_flag:
		last_inst_write_back = True

	if inst.opcode == 'NOP':
		WB_message = ''
	else:
		if inst.opcode == 'DADD' or inst.opcode == 'SUB':
			REG[int(re.sub("[^0-9]", " ", inst.dest))] = ALU_Output
		if inst.opcode == 'LD':
			REG[int(re.sub("[^0-9]", " ", inst.scr2))] = LMD
		
		WB_message = str('I' + str(inst.ins_count) + '-' + 'WB' + ' ')

	#Uncomment for debugging
	"""
	print ''
	print 'WB:'
	print WB_message
	print str(inst.opcode + " " + inst.scr1 + " " + inst.scr2 + " " + inst.dest)
	print str('ALU_Output = ' + str(ALU_Output))	
	print str('LMD = ' + str(LMD))
	print str('last_inst_write_back = ' + str(last_inst_write_back))
	"""

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
	REG_ready = [True] * 32
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
	stall_scr2 = ''
	prev_branch = False

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
			#addr = int(a[0])
			#value = int (a[1])
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
		print branch_ref
		IMEM.append(next_inst)

		#Increment counters
		ins_num = ins_num + 1
		ins_count = ins_count + 1


	#Write to Output file
	last_ins_num = IMEM[len(IMEM)-1].ins_num
	last_inst_read_flag = False
	last_inst_write_back = False
	write_str = ''

	run_count = 0	
	
	#MIPS Operation Loop - Main Program
	while not last_inst_write_back and run_count < 100:

		run_count += 1

		print ''
		print str('sim_cycle = ' + str(sim_cycle))
		print '************'

		log_str = str('c#' + str(sim_cycle) +  ' ')

		#Write Back Stage
		WB_message, last_inst_write_back, REG = WB(MEM3_WB_reg, inst_count, 
			last_inst_write_back, last_inst_read_flag, ALU_Output_3, LMD, REG)

		#MEM3 Stage
		MEM3_message, MEM3_WB_reg, ALU_Output_3 = MEM3(MEM2_MEM3_reg, ALU_Output_2)

	
		#MEM2 Stage
		MEM2_message, MEM2_MEM3_reg, ALU_Output_2 = MEM2(MEM1_MEM2_reg, ALU_Output_1)
	
		#Forward from MEM2
		if MEM2_MEM3_reg.scr2 == ID_EX_reg.scr1 and ID_EX_reg.scr1 != 'NULL':
			A = LMD
			#stall_flag = False
			#REG[int(re.sub("[^0-9]", " ", ID_EX_reg.scr1))] = LMD

		elif MEM2_MEM3_reg.scr2 == ID_EX_reg.scr2 and ID_EX_reg.scr2 != 'NULL':
			B = LMD
			#stall_flag = False
			#REG[int(re.sub("[^0-9]", " ", ID_EX_reg.scr2))] = LMD

		#MEM1 Stage
		MEM1_message, MEM1_MEM2_reg, PC, LMD, MEM, ALU_Output_1, branch_flag = MEM1(EX_MEM1_reg, B_pass, PC, NPC, 
			LMD, ALU_Output, branch_flag, MEM)

		#Forward from MEM1
		if MEM1_MEM2_reg.scr2 == ID_EX_reg.scr1 and ID_EX_reg.scr1 != 'NULL':
			A = LMD
			#stall_flag = False
			#REG[int(re.sub("[^0-9]", " ", ID_EX_reg.scr1))] = LMD
			#REG_ready[int(re.sub("[^0-9]", " ", ID_EX_reg.scr1))] = True
		elif MEM1_MEM2_reg.scr2 == ID_EX_reg.scr2 and ID_EX_reg.scr2 != 'NULL':
			B = LMD
			#stall_flag = False
			#REG[int(re.sub("[^0-9]", " ", ID_EX_reg.scr2))] = LMD
			#REG_ready[int(re.sub("[^0-9]", " ", ID_EX_reg.scr2))] = True

		#Hazard Check
		if (EX_MEM1_reg.scr2 == ID_EX_reg.scr1 or 
			EX_MEM1_reg.scr2 == ID_EX_reg.scr2) and (EX_MEM1_reg.opcode == 'LD'):
			stall_flag = True
			stall_scr2 = EX_MEM1_reg.scr2
			print str('stall_scr2 aft = ' + stall_scr2)
			EX_MEM1_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
		elif (MEM2_MEM3_reg.scr2 == stall_scr2 and 
			MEM2_MEM3_reg.opcode == 'LD'):
			stall_flag = True
			#MEM1_MEM2_reg = Ins(0,'NOP','NULL', 'NULL', 'NULL', 0)
		else:
			stall_flag = False
		"""
		#Hazard Check
		if EX_MEM1_reg.scr1 != 'NULL':
			rs = int(re.sub("[^0-9]", " ", EX_MEM1_reg.scr1))
		else:
			rs = 0
		
		if EX_MEM1_reg.scr2 != 'NULL':
			rt = int(re.sub("[^0-9]", " ", EX_MEM1_reg.scr2))
		else:
			rt = 0

		if (REG_ready[rs] and REG_ready[rt]):
			stall_flag = False
		#elif ID_EX_reg.ins_num > 1:
		else:
			stall_flag = True
		"""
		print ''
		print str('stall_flag bef EX = ' + str(stall_flag))
		#print str('REG[' + str(rs) + ']')
		#print str('REG[' + str(rt) + ']')
		#print str('REG_ready[' + str(rs) + '] = ' + str(REG_ready[rs]))
		#print str('REG_ready[' + str(rt) + '] = ' + str(REG_ready[rt]))

		#Execution Stage
		if stall_flag:
			EX_message, ID_EX_reg, B_pass, ALU_Output, branch_flag, REG_ready = EX(ID_EX_reg, 
				NPC, A, B, imm, ALU_Output, branch_flag, stall_flag, REG_ready)
			"""			
			if ID_EX_reg.scr1 != 'NULL':
				REG_ready[int(re.sub("[^0-9]", " ", ID_EX_reg.scr1))] = True
			if ID_EX_reg.scr2 != 'NULL':
				REG_ready[int(re.sub("[^0-9]", " ", ID_EX_reg.scr2))] = True
			"""
		else:
			EX_message, EX_MEM1_reg, B_pass, ALU_Output, branch_flag, REG_ready = EX(ID_EX_reg, 
				NPC, A, B, imm, ALU_Output, branch_flag, stall_flag, REG_ready)

		#print str('IF1_IF2_reg.ins_num = ' + str(IF1_IF2_reg.ins_num))
		#if ID_EX_reg.dest != 'NULL' and ID_EX_reg.ins_num > 1:
		#	REG_ready[int(re.sub("[^0-9]", " ", ID_EX_reg.dest))] = False		
		
		#Instruction Decode Stage
		if stall_flag:
			ID_message, IF2_ID_reg, stall_flag, A, B, imm, REG  = ID(IF2_ID_reg, 
				ID_EX_reg, stall_flag, A, B, imm, branch_labels, branch_ref, REG)
		else:
			ID_message, ID_EX_reg, stall_flag, A, B, imm, REG  = ID(IF2_ID_reg, 
				ID_EX_reg, stall_flag, A, B, imm, branch_labels, branch_ref, REG)
			#if ID_EX_reg.opcode == 'LD':
			#	REG_ready[int(re.sub("[^0-9]", " ", ID_EX_reg.scr2))] = False

		#Instruction Fetch 2 Stage
		if stall_flag:
			IF2_message, IF1_IF2_reg, NPC = IF2(IF1_IF2_reg, PC, NPC, stall_flag, branch_flag)
		else:
			IF2_message, IF2_ID_reg, NPC = IF2(IF1_IF2_reg, PC, NPC, stall_flag, branch_flag)

		#Instruction Fetch 1 Stage
		if stall_flag:
			IF1_message, IR, PC, last_inst_read_flag, prev_branch, inst_count = IF1(PC, IR, 
				last_ins_num, last_inst_read_flag, branch_flag, stall_flag, prev_branch, inst_count)
		else:
			IF1_message, IF1_IF2_reg, PC, last_inst_read_flag, prev_branch, inst_count = IF1(PC, IR, 
				last_ins_num, last_inst_read_flag, branch_flag, stall_flag, prev_branch, inst_count)


		#Write to output file
		#write_str = (log_str + IF1_message + IF2_message + ID_message + EX_message
		#	+ MEM1_message + MEM2_message + MEM3_message + WB_message)
		write_str = (log_str + WB_message + MEM3_message + MEM2_message
			+ MEM1_message + EX_message + ID_message + IF2_message
			+ IF1_message)

		o.write(write_str + '\n')

		sim_cycle += 1


	o.write('REGISTERS\n')
	for r in range(len(REG)):
		if REG[r] != 0:
			wbuf = str('R'+str(r) +' ' + str(REG[r]) + '\n')
			o.write(wbuf)

	o.write('MEMORY\n')
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
