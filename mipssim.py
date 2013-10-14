"""ACO Course Project
MIPS R4000 Simulator
Author: Joel Tanzi
Date: 10/6/2013
Version: 1.0"""

"""Registers"""
reg = [0] * 32


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

#Obtain input file name from user
fname = raw_input("Input file name: ")
print fname

#Open input file and start reading
f = open(fname, 'r')
buf = f.readline()
print buf
if (buf == 'REGISTERS\n'):
	while (buf != 'MEMORY\n'):
		buf = f.readline()
		print buf

"""
instreg = [Ins(0, 'ADD', 'R0', 'R1', 'R2', 0)]
instreg.append(Ins(1, 'SUB', 'R1', 'R2', 'R3', 0))

for r in range(len(instreg)):
	print instreg[r].ins_num, " ", instreg[r].opcode, " ", instreg[r].scr1, \
		" ", instreg[r].scr2, " ", instreg[r].dest, " ", instreg[r].imm
"""
f.close()
