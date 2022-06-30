import csv
import enum
import random
from re import L, S
from numpy import False_

from regex import P
from torch import det
from aug_train import final_clean_output

IN_FILE = 'data/train_pos.tsv'
MAX_ADDED_LINES = 20000
VERBS_COMP = ['agent','theme','recipient','xcomp','ccomp']

NMODS_PPS = ['in//i','beside//i','on//i']

AFTER_V = False

OUT_FILE = open('results/new_substructure/last_exp_pp_subs_05_20kadd.tsv', 'w')
# OUT_FILE = open('testing/substrucutre_both_03_with_nnp.tsv', 'w')


WAS_RESTRICTION = False
SAME_NOUN_RESTRICTION = True 



def write_prev_rows():
    with open(IN_FILE, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            inp,out,dist = row
            write_new_row(inp,out,dist,None,None,None,None)



def get_final_inp(inp):
    inp_splits = inp.split(' ')
    final_inp = ''
    for i,word in enumerate(inp_splits):
        if '//' in word:
            if inp_splits[i-1] == 'NNP': word = word[:-1]+'P'
            final_inp += word.replace('//',' ') + ' '
    return final_inp

def write_new_row(inp,out,dist,or_inp,or_out,nmod,subus_noun):
  

    final_inp = get_final_inp(inp)
    final_out = final_clean_output(out)

  
    final_inp = final_inp.strip()
    if dist != 'primitive':
        final_inp = final_inp[0].upper() + final_inp[1:]
    final_out = final_out.strip()
    final_out = final_out.replace('  ',' ')

    final_row = '\t'.join((final_inp,final_out,dist))

    OUT_FILE.write(final_row+'\n')



def valid_np_nmod(np_nmod):
    if np_nmod.count(' PP ') >= 2:
        return True
    if 'to//i' in np_nmod:
        return False
    
    
def get_nmods(inp,nmods):
    splits = inp.split(' ')
    brackets = None
    np_found = False

    for i,word in enumerate(splits):
        
        if not np_found and word == 'PP':
            np_found = True
            np_pos = i
            brackets = 1
        
        if  np_found:
            if word == '(':
                brackets+=1
            elif word == ')':
                brackets-=1
            if brackets == 0:
                np = '( ' + ' '.join(splits[np_pos:i+1])
                np_found = False
                if valid_np_nmod(np):
                    # np = np[5:]
                    nmods.append(np)

    return nmods

def get_word_pos(inp,word):
    splits = inp.split(' ')
    cont = 0
    for split in splits:
        if split == word:
            return cont
        if '//' in split: 
            cont+=1
        
def valid(inp,dist):
    if dist == 'primitive':
        return False
    if 'was//V' not in inp and WAS_RESTRICTION:
        return False
    splits = inp.split(' ')
    for i,w in enumerate(splits):
        if w == 'NN' and splits[i+1][0].isupper():
            return False

    return True

def valid_nmod(nmod,inp):
    if len(nmod) == 0: return False
    for word in nmod.split(' '):
        if '//n' in word.lower():
            if word.lower() in inp.lower():
                return False
    return True

def get_np(noun,inp):
    splits = inp.split(' ')
    np_found = False

    for i,word in enumerate(splits):

        if word == 'NP':
            np_found = True
            np_pos = i
            np_brackets = 1
        
        elif np_found:
            if word == '(':
                np_brackets+=1
            elif word == ')':
                np_brackets-=1
            if np_brackets == 0:
                np = '( ' + ' '.join(splits[np_pos:i+1])
                np_found = False
                if noun.lower() in np.lower(): 
                    return np

    return None

def add_nmod_inp(noun,inp,nmod):
    noun_np = get_np(noun,inp)
    inp_splits = inp.split(' ')
    np_ind = inp_splits.index(noun)
    new_inp = inp.replace(noun_np,nmod)
    return new_inp


def valid_pp(pp):
    if pp.count('PP') >=2:
        return False
    if 'by//I' in pp or 'to//I' in pp:
        return False
    return True

def get_possible_pp(inp):
    inp_splits = inp.split(' ')
    pp_found = False
    pp_brackets = None
    last_n = ''
    res = None, None
    for i,word in enumerate(inp_splits):
        if '//N' in word:
            last_n = word
        if word == 'PP':
            pp_noun = last_n
            pp_found = True
            pp_brackets = 1
            pp_pos = i
        if pp_found:
            if word == '(':
                pp_brackets += 1
            elif word == ')':
                pp_brackets -= 1
            if pp_brackets == 0:
                pp = '( ' + ' '.join(inp_splits[pp_pos:i+1])
                pp_found = False
                if valid_pp(pp):
                    res = pp,pp_noun
                    pp_found = False
    return res




def get_verb(inp):
    for word in inp.split(' '):
        if '//V' in word:
            verb = word
    return verb

def get_out_noun(pp):

    det = False
    splits = pp.split(' ')
    for i,word in enumerate(splits):
        if word.lower() == 'the//d':
            det = True
        if '//N' in word:
            if splits[i-1] == 'NN' or splits[i-1] == 'NNS':
                return word[:-3],'NN',det
            if splits[i-1] == 'NNP':
                return word[:-3],'NNP',det
    return None,None,None

def get_out_noun_pos(new_inp,out_noun):
    i=0
    for word in new_inp.split(' '):
        if '//' in word and word[:-3] == out_noun:
            return i
        if '//' in word:
            i+=1



def get_pos(word,new_inp):
    word = word.lower()
    pos = 0
    splits = new_inp.split(' ')
    for i,w in enumerate(splits):
        w = w.lower()
        if '//' in w:
            if w == word:
                return str(pos)
            pos +=1
    
    return None


def get_nmod_out(nmod,new_inp):
    
    nmod_splits = nmod.split(' ')
    nmod_out = ''
    det_out = ''
    cut_ind = None
    n_words = 0
    det_cut_ind = len(new_inp)

    for i,word in enumerate(nmod_splits):
        word = word.lower() # todo check lower

        if '//' in word:
            word_pos = get_pos(word,new_inp)
            if '//n' in word:
                if not last_det: 
                    nmod_out = ' '.join((nmod_out,'AND '+word[:-3]+' ( x _ '+word_pos+' )'))
                else:        
                    det_out =' '.join((det_out,'* '+word[:-3]+' ( x _ '+word_pos+' ) ;' ))
                    if det_cut_ind == len(new_inp): 
                        det_cut_ind = int(word_pos)

                if cut_ind is None: 
                    cut_ind = int(word_pos)    
                last_det = False
                last_noun = word[:-3]
                last_noun_pos = word_pos
            
            elif word in NMODS_PPS:
                nmod_fut_pos = None
                for w in nmod_splits[i+1:]:
                    w = w.lower()
                    if '//n' in w:
                        nmod_fut_pos = get_pos(w,new_inp)
                        break
                if nmod_fut_pos is None:
                    return None,None,None,None,None
                nmod_out =' '.join((nmod_out,'AND '+ last_noun +' . nmod . ' + word[:-3] + ' ( x _ '+last_noun_pos+' , x _ '+nmod_fut_pos+' )'))
            
            last_det = False
            if 'the//d' in word:
                last_det = True
            
            
            n_words +=1
    return det_out,nmod_out,det_cut_ind,cut_ind,n_words


def remove_out(subs_pp,out,last_n,new_inp):
    det_out = out.rsplit(';', 1)[0]
    if len(det_out) != len(out):
        out_splits = out.rsplit(';', 1)[1].split(' ')
        det_out +=';'
        
    else:
        out_splits = out.split(' ')
        removed_det_out = ''

    det_out_splits = det_out.split(' ')
    p_det = -1
    pp_splits = subs_pp.split(' ')
    removed_det = False
    pos_nmod = -1
    
    if ';' in out:
        for i,w in enumerate(det_out_splits):
            if ' '+w+'//N' in subs_pp:
                p_det = i
                break
        if p_det != -1:
            det_out_splits = det_out_splits[:i-1] + det_out_splits[i+7:]
            removed_det = True

        removed_det_out = ' '.join(det_out_splits)
        

    for i,w in enumerate(out_splits):
        if w == 'nmod' and out_splits[i-2] == last_n[:-3]:
            pos_nmod = i

    if removed_det:
        out_splits = out_splits[:pos_nmod] + ['??'] + out_splits[pos_nmod+12:]
    else:
        out_splits = out_splits[:pos_nmod] + ['??'] + out_splits[pos_nmod+19:]
    
    
    found_q = False
    for i,w in enumerate(out_splits):
        if w == '??': 
            found_q = True
        if found_q:
            if w.isdigit():
                out_splits[i] = get_pos(out_splits[i-4]+'//N',new_inp)

    
    removed_comp = ' '.join(out_splits)



    return removed_det_out,removed_comp


def get_n_words(noun,inp):
    np = get_np(noun,inp)
    n_words = 0
    for w in np.split(' '):
        if '//' in w:
            n_words+=1
    return n_words

def get_noun(nmod):
    noun = None
    for w in nmod.split(' '):
        if '//N' in w:
            noun = w[:-3]
            break
    return noun


def get_out_pp(pp,new_inp,last_n):
    pp_splits = pp.split(' ')
    is_det = False
    det_out = ''
    dets = []
    comp = ''
    pos_before = get_pos(last_n,new_inp)
    for i,w in enumerate(pp_splits):
        if '//' not in w:
            continue
        if is_det:
            det_out += '* '+w[:-3]+' ( x _ '+get_pos(w,new_inp) +' ) ; '
            dets.append(w)

        if 'the//D' in w:
            is_det = True
        else:
            is_det = False
    
    for i,w in enumerate(pp_splits):
        if '//' not in w:
            continue
        if 'on//I' in w:
            nmod = 'on'
        elif 'in//I' in w:
            nmod = 'in'
        elif 'beside//I' in w:
            nmod = 'beside'
        
        if '//N' in w:
            aux_pos = get_pos(w,new_inp)
            if w in dets:
                comp+='nmod . '+nmod+' ( x _ '+pos_before+' , x _ '+aux_pos+' ) AND '
            else:
                comp+='nmod . '+nmod+' ( x _ '+pos_before+' , x _ '+aux_pos+' ) AND '+w[:-3]+' ( x _ '+ aux_pos+' ) AND '
            pos_before = aux_pos
            
    comp = comp[:-4]
    det_out = det_out[:-1]
    return det_out,comp



def fix_removed_det(new_inp,removed_det):
    removed_det_splits = removed_det.split(' ')
    for i,w in enumerate(removed_det_splits):
        if w.isdigit():
            w_pos = get_pos(removed_det_splits[i-4]+'//N',new_inp)
            removed_det_splits[i] = w_pos
    return ' '.join(removed_det_splits)

def get_final_det(pp_det,removed_det):
    removed_det_splits = removed_det.split(' ')
    pp_det_splits = pp_det.split(' ')
    pp_det_value = None
    for w in pp_det_splits:
        if w.isdigit():
            pp_det_value = int(w)
            break

    cutted = False

    for i,w in enumerate(removed_det_splits):
        if w.isdigit() and int(w)>pp_det_value:
            final_det = removed_det_splits[:i-5] + [pp_det] + removed_det_splits[i-5:]
            final_det = ' '.join(final_det)
            cutted = True
    if not cutted:
        final_det = removed_det.strip() + ' ' + pp_det.strip()
    return final_det




def add_nmod_out(out,inp,new_inp,pp,subs_pp,last_n):
    pp_det, pp_comp = get_out_pp(pp,new_inp,last_n) 
    # fix index on nmods of nouns that are in the det
    removed_det,removed_comp = remove_out(subs_pp,out,last_n,new_inp) 

    if len(removed_det) != 0:
        removed_det = fix_removed_det(new_inp,removed_det)
        if len(pp_det) != 0:
            final_det = get_final_det(pp_det,removed_det)
        else:
            final_det = removed_det
    else:
        final_det = pp_det
    
    final_comp = removed_comp.replace('??',pp_comp)
    i=0
    
    


def main():
    with open(IN_FILE) as f:
        read_tsv = csv.reader(f, delimiter='\t')
        res = []
        rows = list(read_tsv)
        count = 0
        length = len(rows)
    
        # DELETE LATER
        random.seed(1) 
        # DELETE LATER
        nmods = []
        for row in rows:
            inp,out,dist = row
            nmods = get_nmods(inp,nmods)
            

        while (count<MAX_ADDED_LINES):
            inp,out,dist = rows[random.randint(0,length-1)]
            if not valid(inp,dist): 
                continue
            
            nmod = random.choice(nmods)

            subs_pp,last_n = get_possible_pp(inp)         
            if not subs_pp: continue


            new_inp = inp.replace(subs_pp,nmod)
            new_out = add_nmod_out(out,inp,new_inp,nmod,subs_pp,last_n) 

            if new_out is None:
                continue

            
            write_new_row(new_inp,new_out,dist,inp,out,nmod,subs_noun)
            count+=1
            
    return res





if __name__ == '__main__':
    write_prev_rows()
    res = main()
    OUT_FILE.close()


