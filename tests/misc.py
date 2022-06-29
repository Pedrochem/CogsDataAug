import csv
import enum
import random

MAX_ADDED_LINES = 10000
IN_FILE = '/home/pedrochem/Dropbox/Pedro Chem - Dropbox/Lig Internship/lig/code/Data Aug/data/train_pos_no_aspas.tsv'
OUT_FILE = open('/home/pedrochem/Dropbox/Pedro Chem - Dropbox/Lig Internship/lig/code/Data Aug/results/new_substructure/subs_sentences.tsv','w')


def get_final_inp(inp):
    inp_splits = inp.split(' ')
    final_inp = ''
    for i,word in enumerate(inp_splits):
        if '//' in word:
            if inp_splits[i-1] == 'NNP': word = word[:-1]+'P'
            final_inp += word.replace('//',' ') + ' '
    return final_inp

def final_clean_output(out):
    splits = out.split(' ')
    for i,word in enumerate(splits):
        if word.isdigit():
            splits[i] = str(int(word)*2)
    return ' '.join(splits)
   


def write_new_row(inp,out,dist):
    final_inp = get_final_inp(inp)
    final_out = final_clean_output(out)

    final_inp = final_inp.strip()

    if dist != 'primitive':
        final_inp = final_inp[0].upper() + final_inp[1:]

    final_out = final_out.strip()
    final_row = '\t'.join((final_inp,final_out,dist))
    OUT_FILE.write(final_row+'\n')


def get_rec_s(inp,out,rec_lst):
    if inp.count(' S ')>=2 and inp.count(' SBAR ')>=1:
        rec_lst.append((inp,out))
        return rec_lst
    return rec_lst

def valid(inp,dist):
    # todo: finalize
    if dist == 'primitive':
        return False  
    if 'SBAR' not in inp:
        return False
    return True


def get_subs_s(inp):
    splits = inp.split(' ')
    brackets = None
    sbar_found = False

    for i,word in enumerate(splits):
        
        if  word == 'SBAR':
            sbar_found = True
            sbar_pos = i
            brackets = 1
        
        if  sbar_found:
            if word == '(':
                brackets+=1
            elif word == ')':
                brackets-=1
            if brackets == 0:
                sbar = '( ' + ' '.join(splits[sbar_pos:i+1])
                sbar_found = False
                return sbar

def get_first_v(rec_s):
    cont = -1
    for word in rec_s.split(' '):
        if '//' in word and word[-1] == 'V':
            return cont

        if '//' in word:
            cont+=1

def get_word_count(inp):
    cont = 0
    for w in inp.split(' '):
        if '//' in w:
            cont+=1
    return cont

def get_splited_out(out): 
    splits = out.split(' ')
    spl_pos = 0
    for i,word in enumerate(splits):
        if word == ';':
            spl_pos = i+1
    
    if spl_pos != 0:
        spl_det = ' '.join(splits[:spl_pos])
    else:
        spl_det = ''

    spl_comp = ' '.join(splits[spl_pos:])

    return spl_det,spl_comp

def update_pos(spl_rec_det,spl_rec_comp,word_count):
    splits_det = spl_rec_det.split(' ')
    splits_comp = spl_rec_comp.split(' ')

    for i,word in enumerate(splits_det):
        if word.isdigit():
            splits_det[i] = str(int(word) + word_count)
    splits_det = ' '.join(splits_det)

    for i,word in enumerate(splits_comp):
        if word.isdigit():
            splits_comp[i] = str(int(word) + word_count)
    splits_comp = ' '.join(splits_comp)

    return splits_det,splits_comp


def modify_out(inp,out,subs_s,rec_s,rec_out):
    new_out = None
    
    rec_first_verb = get_first_v(rec_s) 
    word_count = get_word_count(inp.replace(subs_s,'')) + 1 #+1 because rec_s dont start at 0

    updated_ccomp_pos = rec_first_verb + word_count 


    spl_out_det,spl_out_comp = get_splited_out(out)
    spl_rec_det,spl_rec_comp = get_splited_out(rec_out)
    spl_rec_comp = 'AND ' + spl_rec_comp

    comp_out_splits = spl_out_comp.split(' ')


    for i,word in enumerate(comp_out_splits):
        if word == 'ccomp' and 'ccomp' not in comp_out_splits[i+1:]:
            new_comp_out = comp_out_splits[:i+10]
            new_comp_out[-2] = str(updated_ccomp_pos)
            break
    
    new_comp_out = ' '.join(new_comp_out)
    spl_rec_det,spl_rec_comp = update_pos(spl_rec_det,spl_rec_comp,word_count)

    new_out_det = (spl_out_det + ' ' + spl_rec_det).strip()
    new_out_comp = (new_comp_out + ' ' + spl_rec_comp).strip()
    new_out = (new_out_det + ' ' + new_out_comp).strip()

    return new_out

                



def main():
    random.seed(1)
    count = 0
    i = -1 # todo: check
    rec_s_lst = []

    with open(IN_FILE) as fi:

        read_tsv = csv.reader(fi, delimiter='\t')
        rows = list(read_tsv)
        
        for row in rows:
            inp,out,dist = row
            rec_s_lst = get_rec_s(inp,out,rec_s_lst)
        
        while (i<len(rows)):
            inp,out,dist = rows[i]
            i+=1

            if not valid(inp,dist):
                continue

            subs_s = get_subs_s(inp)
            rec_s, rec_out = random.choice(rec_s_lst)
            rec_s = '( SBAR ( IN that//I ) '+rec_s+' )'

            new_inp = inp.replace(subs_s,rec_s)
            new_out = modify_out(inp,out,subs_s,rec_s,rec_out)
            write_new_row(new_inp,new_out,dist)
            count+=1
    print(count)


if __name__ == '__main__':
    main()
    OUT_FILE.close()