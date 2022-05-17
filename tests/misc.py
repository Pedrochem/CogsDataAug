import csv
import enum
IN_FILE = 'data/train_pos copy.tsv'

def make_pps_dic(inp,dic):
    splits = inp.split(' ')
    brackets = None
    pp_found = False
    
    for i,word in enumerate(splits):
        if word == 'PP':
            pp_found = True
            pp_pos = i
            brackets = 1
        elif pp_found:
            if word == '(':
                brackets+=1
            elif word == ')':
                brackets-=1
            if brackets == 0:
                pp = '( ' + ' '.join(splits[pp_pos:i+1])
                pp_found = False
                
                if 'to//I' in pp:
                    dic['to'].add(pp)
                elif 'in//I' in pp:
                    dic['in'].add(pp)
                elif 'beside//I' in pp:
                    dic['beside'].add(pp)
                elif 'by//I' in pp:
                    dic['by'].add(pp)
                elif 'on//I' in pp:
                    dic['on'].add(pp)


    return dic


with open(IN_FILE) as f:
    read_tsv = csv.reader(f, delimiter='\t')
    my_set = set()
    all_pps = set()
    dic = {'to':set(),
        'in':set(),
        'beside':set(),
        'by':set(),
        'on':set()}
    for row in read_tsv:
        inp,out,dist = row
        if dist == 'primitive': continue
        splits = out.split(' ')
        for i,word in enumerate(splits):
            if word == '.':
                my_set.add(splits[i+1])

        # pps,dic = get_pps(inp,dic)
        # [all_pps.add(pp) for pp in pps]


    i=0
    
        
    