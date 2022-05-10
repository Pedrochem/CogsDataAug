import csv
IN_FILE = 'data/train_pos.tsv'

def get_np(inp,out):
    nps_lst = []
    splits = inp.split(' ')
    brackets = None
    np_found = False
    np_pos = None

    pp_found = False
    pp_brackets = None

    for i,word in enumerate(splits):
        if word == 'PP':
            pp_found = True
            pp_brackets = 1
        if pp_found:
            if word == '(':
                pp_brackets += 1
            elif word == ')':
                pp_brackets -= 1
            if pp_brackets == 0:
                pp_found = False
        if word == 'NP' and not pp_found:
            np_found = True
            np_pos = i
            brackets = 1
        elif np_found:
            if word == '(':
                brackets+=1
            elif word == ')':
                brackets-=1
            if brackets == 0:
                np = '( ' + ' '.join(splits[np_pos:i+1])
                
                nps_lst.append((np,np_pos))
                np_found = False
    return nps_lst



with open(IN_FILE) as f:
    read_tsv = csv.reader(f, delimiter='\t')
    lst = 0
    inps = set()
    for row in read_tsv:
        inp,out,dist = row
        if '*' not in out and ' the ' in inp.lower():
            lst+=1
            inps.add(inp)
    print(lst)
    print(inps)