"""ACO Course Project
MIPS R4000 Simulator
Author: Joel Tanzi
Date: 10/6/2013
Version: 1.0"""

import re
import os

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
mem_size = 128
MEM = Memory(mem_size)
for r in range(mem_size):
	MEM.Slots[r].addr = r * 8

""" TEST
for r in range(mem_size):
	print MEM.Slots[r].addr, " ", MEM.Slots[r].value
	END TEST """

"""Flow Control Variables"""
pc = 0
inst_count = 0
sim_cycle = 0
branch_flag =0
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

	def __init__(self):
		self.ins_num = 0
		self.opcode = 'NONE'
		self.scr1 = 'R0'
		self.scr2 = 'R1'
		self.dest = 'R1'
		self.imm = 0

	def write(self, ins_num, opcode, scr1 = 'NONE', scr2 = 'NONE', 
				dest = 'NONE', imm = 0):
		self.ins_num = ins_num
		self.opcode = opcode
			
#Create instruction register
INSTREG = [Ins() for each in range(32)]

#Obtain input file name from user
fname = raw_input("Input file name: ")
print fname
byte_count = os.path.getsize(fname)
print byte_count, " bytes"

#Open input file and start reading
f = open(fname, 'r')
buf = f.readline()
index = 0

#Initialize Registers
print 'REGISTERS'
if 'REGISTERS' in buf:
	while not 'MEMORY' in buf:
		buf = f.readline().rstrip()
		if buf != 'MEMORY':
			a = buf.split(" ")
			regnum = int(re.sub("[^0-9]", " ", a[0]))
			value = int(re.sub("[^0-9]", " ", a[1]))
			REG[regnum] = value
			print 'R'+str(regnum), REG[regnum]

#Initialize Memory
print 'MEMORY'
while not 'CODE' in buf:
	buf = f.readline().rstrip()
	if buf != 'CODE':
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
		for r in range(len(a)-1):  #Clean up instruction string
			if '' in a:
				del a[a.index('')]


	print str(ins_num)+':', a
	
	#Increment counters
	ins_num = ins_num + 1
	ins_count = ins_count + 1

print '\nBranches\n', branch_labels


f.close()



def parse_ins(ins_string, ins_num):
	
	if ins_string[0] == 'LD':
		pass
	elif ins_string[0] == 'DADD':
		pass
	
