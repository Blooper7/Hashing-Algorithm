#!/bin/python3
import random
import string
import sys

def generateSalt(length=16):
	return ''.join(random.choices(string.ascii_letters+string.digits, k=length))

def msg2ord(msg):
	return list(map(ord,[*msg]))


def rotListLeft(data):
	data.append(data.pop(0))

	
def mix(state, chunk, salt):
	new_state=[0]*len(state)
	
	for i in range(len(state)):
		#Add state and chunk (mod 256)
		s=(state[i]+chunk[i])%256
		
		#XOR the salt with the accumulation to cause the salt to diffuse widely
		s=s^salt[i]
		
		#Use neighbor value to introduce non-linearity into the hash and create dependency across the hash..
		#Use (i+1)%len(state) to wrap around.
		neighbor=state[(i+1)%len(state)]
		
		#Rotate the neighbor left by (i&8)
		rotation=((neighbor << (i % 8)) & 0xFF) | (neighbor >> (8 - (i % 8)))
		'''
		The code above effectively demonstrates a bitwise left rotation, which is a shift with preservation of the high bits by wrapping them around instead of allowing them to go past the 8th bit.
		1. (i % 8) : ensures the number of bits to rotate is between 0 and 7
		2. (neighbor << (i % 8)) & 0xFF : shifts bits in neighbor left by the above (i%8) value. The & 0xFF following ensures that, after the shift, only the lower 8 bits are kept. Any past 8 are temporarily discarded. This is called a mask.
		3. (8 - (i % 8)) : Calculates how many positions to shift right in order to catch the bits that "fell off" the left end
		4. neighbor >> (8 - (i % 8)) shifts the original value to the right by the above amount. With the right shift, they're now in the lower bits
		5. | : merge both the masked left shift and the right shift
		
		reminder of bitwise operators:
		>> : shift right
		<< : shift left
		&  : Bitwise AND
		|  : Bitwise OR
		
		'''
		new_state[i]=s^rotation
	return new_state

def chunk(byteList, chunkByteSize=16):
	# pad message
	data=byteList
	while len(data)%16!=0:
		data.append(0)
	# chunk message
	chunked=[data[(i*chunkByteSize):(i*chunkByteSize)+chunkByteSize] for i in range(len(data)//chunkByteSize)]
	return chunked
	
def hashAlg(chunkList, salt, rounds=40):
	# initialize hash
	hash=[]
	for i in range(len(chunkList[0])):
		hash.append(0)
	# shift each chunk
	for i in range(len(chunkList)):
		orig=chunkList[i].copy()
		for j in range(i):
			rotListLeft(chunkList[i])
	
	# Hash
	for r in range(rounds):
		for i in range(len(chunkList)):
			hash=mix(hash,chunkList[i],salt)
	return hash

def cleanupHash(hash:list):
	cleaned=list(map(chr,hash))
	cleaned=''.join(cleaned)
	return cleaned

def hash(message, chunkLength=16, salt=None):
	message=msg2ord(message)
	if salt!=None and len(salt)!=chunkLength:
		raise Exception(f"Salt length must be {chunkLength} bytes long (Salt {salt} is only {len(salt)})")
	if salt==None:
		salt=generateSalt(chunkLength)

	saltOrds=msg2ord(salt)
	
	chunks=chunk(message, chunkLength)
	return (cleanupHash(hashAlg(chunks, saltOrds)),salt)

def str2hex(string):
	return bytes([ord(i) for i in string]).hex()

if __name__ == "__main__":
	try:
		msg=sys.argv[1]
	except:
		print("Usage: ./hash.py <message> <salt>\n")
		print("Takes in a string message parameter and an optional string salt parameter and produces a hash output. If a salt isn't provided, one is generated.\n")
		print("Examples:\n\t./hash.py \"Hello World!\"\n\t./hash.py \"Foo\" \"3GZO9NUL67pABvIZ\"")
		exit()
	try:
		salt=sys.argv[2]
	except:
		salt=None
	
	out=hash(msg, salt=salt)
	print(f"Hash: {str2hex(out[0])}\nSalt: {out[1]}")
