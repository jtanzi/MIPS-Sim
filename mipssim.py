"""ACO Course Project
MIPS R4000 Simulator
Author: Joel Tanzi
Date: 10/6/2013
Version: 1.0"""

import re
import os
import string

#---Function and Variable Declarations---

#parse_ins function
#Parses the instruction string lists read in from CODE section
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


"""Registers"""
REG = [0] * 32


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

#Contructing memory space, addresses are multiples of 8
mem_size = 125
MEM = Memory(mem_size)
for r in range(mem_size):
	MEM.Slots[r].addr = r * 8


"""Flow Control Variables"""
pc = 0
inst_count = 0
sim_cycle = 0
branch_flag = True
branch_labels = dict()

"""Instructions"""

#Ins class for handling instructions
#Consists of instruction number (ins_num), opcode, 
#source registers (scr1, scr2), destination (memory or register) dest,
# and optional immediate value (imm)
class Ins(object):

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
			
#Create instruction register
INSTREG = []

#Pipelining Functions
def IF1(ins_num):
	#TODO
	pass

def IF2(ins_num):
	#TODO
	pass

def ID(ins_num):
	#TODO
	pass

def EX(ins_num):
	#TODO
	pass

def MEM1(ins_num):
	#TODO
	pass

def MEM2(ins_num):
	#TODO
	pass

def MEM3(ins_num):
	#TODO
	pass

def WB(ins_num):
	#TODO
	pass

#---Simulation----

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
ins_num = 0
ins_count = 1

while (f.tell() < byte_count):  #Read to end of input file
	buf = f.readline().strip()
	buf = re.sub(',', '', buf)  #Gets rid of commas (makes parsing easier)
	if buf.find(':') == -1:  #No branch label read
		a = buf.split(" ")

	else:					 #Branch label read
		a = buf.split(" ")
		branch_labels[a[0]] = ins_num
		del a[0]
		for r in range(len(a)-1):  #Clean up spaces in instruction string
			if '' in a:
				del a[a.index('')]


	print str(ins_num)+':', a
	
	INSTREG.append(parse_ins(a, ins_num))

	#Increment counters
	ins_num = ins_num + 1
	ins_count = ins_count + 1



for r in range(len(INSTREG)):
	print (INSTREG[r].ins_num, INSTREG[r].opcode, INSTREG[r].scr1,
			INSTREG[r].scr2, INSTREG[r].dest, INSTREG[r].imm)

#Write to Output file
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

#---END---	
