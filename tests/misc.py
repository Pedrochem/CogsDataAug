import csv
import enum
IN_FILE = 'data/train_pos copy.tsv'




with open(IN_FILE) as f:
    read_tsv = csv.reader(f, delimiter='\t')
    lst = 0
    inps = set()
    conts = set()
    for row in read_tsv:
        inp,out,dist = row
        splits = inp.split(' ')
        for i,w in enumerate(splits):
            if w == 'PP' and splits[i+3] == '(':
                conts.add(splits[i+3])
        # for np in get_np(inp,out):
        #     if ' NN ' in np:
        #         cont = 0
        #         for word in np.split(' '):
        #             if '//' in word:
        #                 cont+=1
        #         conts.add(cont)
    
        # if '*' not in out and ' the ' in inp.lower():
        #     lst+=1
        #     inps.add(inp)
    print(conts)
    # print(lst)
    # print(inps)
