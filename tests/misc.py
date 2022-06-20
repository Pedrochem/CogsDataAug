import csv
import enum
IN_FILE = '../results/new_substructure/subs_05_10k.tsv'
GEN_FILE = '../data/substructure/gen.tsv'


with open(IN_FILE) as fi:
    with open(GEN_FILE) as fg:
        read_tsv = csv.reader(fi, delimiter='\t')
        gen_tsv = csv.reader(fg, delimiter='\t')
        gen = set()
        count=0
        for row in gen_tsv:
            inp,out,dist = row
            gen.add(inp)
        print(len(gen))
        for row in read_tsv:
            inp,out,dist = row
            print(inp)
            if inp in gen:
                count+=1
                print(inp)
        print(count)
# x=0
# for i in dic:
#     if 'IN to//I' in i or 'IN by//I' in i:
#         print(i)
#         x+=1
     

# print('len: ',len(dic)) 
# print('x: ',x) 


        
    