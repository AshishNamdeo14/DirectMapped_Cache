import random

f = open('memory.dat', 'w')
a = []

for i in range(10**6):
    f.write(str(random.randint(0, 256))+'\n')
f.close()