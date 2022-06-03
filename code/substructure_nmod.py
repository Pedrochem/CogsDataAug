import csv
import enum
import random
from re import L, S
from numpy import False_

from regex import P
from torch import det
from aug_train import final_clean_output

IN_FILE = 'data/train_pos.tsv'
MAX_ADDED_LINES = 10000
VERBS_COMP = ['agent','theme','recipient','xcomp','ccomp']

NMODS_PPS = ['in//i','beside//i','on//i']

AFTER_V = False
PP_REST = True

OUT_FILE = open('results/new_substructure/subs_both_after_nmod_bug_pp_rest_05simplecomplex_10kadd.tsv', 'w')
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
    # or_inp = get_final_inp(or_inp).strip()
    # or_inp_splits = or_inp.split(' ')
    # for i,w in enumerate(or_inp_splits):
    #     if w == subus_noun[:-3]:
    #         or_inp_splits[i] = '|'+w+'|'
    # or_inp = ' '.join(or_inp_splits)

    # nmod = get_final_inp(nmod)

    final_inp = get_final_inp(inp)
    final_out = final_clean_output(out)

    # nmod = nmod.strip()
    # or_inp = or_inp.strip()

    final_inp = final_inp.strip()
    final_inp = final_inp[0].upper() + final_inp[1:]
    final_out = final_out.strip()
    final_out = final_out.replace('  ',' ')

    final_row = '\t'.join((final_inp,final_out,dist))


    # OUT_FILE.write(or_inp+'\t'+or_out+'\n')
    # OUT_FILE.write(nmod+'\n')
    # OUT_FILE.write('-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
    
    OUT_FILE.write(final_row+'\n')
    # OUT_FILE.write('\n==================================================================================================================================================================================================================================================================================================================================================================\n')


def validate_simple_np(np,inp,out):
    out_splits = out.split(' ')
    np_splits = np.split(' ')
    if 'NN' in np_splits:
        subs_word = np_splits[np_splits.index('NN')+1][:-3]
        for i,word in enumerate(out_splits):
            if word == subs_word and len(out_splits) > i+1 and out_splits[i+1] == '.': 
                return False
    return True


def get_simple_nps(inp,out,simple_nps):
    nps_lst = []
    splits = inp.split(' ')
    brackets = None
    np_found = False
    np_pos = None

    words = 0
    pp_found = False
    pp_brackets = None

    for i,word in enumerate(splits):
        if '//' in word:
            words+=1
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
        # if word == 'NP' and not pp_found and splits[i+2] != 'NNP':
        if word == 'NP':
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
                # if validate_simple_np(np,inp,out) and words>=2:
                if validate_simple_np(np,inp,out) and (words==2 or (words==1 and 'NNP' in np)):
                    np = np[:10] + np[10].lower() + np[11:]
                    nps_lst.append(np)
                np_found = False
    [simple_nps.append(np) for np in nps_lst]
    return simple_nps

def valid_np_nmod(np_nmod):
    if ' to//I ' in np_nmod or ' by//I ' in np_nmod or 'NNP' in np_nmod:
        return False
    return True
    
def get_nmods(inp,nmods):
    splits = inp.split(' ')
    brackets = None
    pp_found = False
    np_found = False
    last_np = None

    for i,word in enumerate(splits):
        
        if not pp_found and word == 'NP':
            np_found = True
            np_pos = i
            np_brackets = 1
        
        if not pp_found and np_found:
            if word == '(':
                np_brackets+=1
            elif word == ')':
                np_brackets-=1
            if np_brackets == 0:
                last_np = '( ' + ' '.join(splits[np_pos:i+1])
                np_found = False

        if not pp_found and word == 'PP' and splits[i+3].lower() in NMODS_PPS:
            pp_found = True
            pp_pos = i
            brackets = 1
        if pp_found:
            if word == '(':
                brackets+=1
            elif word == ')':
                brackets-=1
            if brackets == 0:
                nmod = '( ' + ' '.join(splits[pp_pos:i+1])
                np_nmod = last_np + ' ' + nmod
                pp_found = False 
                if valid_np_nmod(np_nmod): 
                    nmods.append(np_nmod)


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


def get_possible_noun(inp,out,pp_rest):
    out_splits = out.split(' ')
    inp_splits = inp.split(' ')
    verb_found = not AFTER_V
    pp_found = False
    pp_brackets = None
    nouns = []
   
    for i,word in enumerate(inp_splits):
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

        if word == 'VP':
            verb_found = True

        if not verb_found or (pp_found and pp_rest): 
            continue

        if '//N' in word and inp_splits[i-1] == 'NN':
            nouns.append(word)
    res = nouns.copy()

    for i,word in enumerate(out_splits):
        
        if word == 'nmod':
            pos1 = out_splits[i+6]
            pos2 = out_splits[i+10]

            for n in nouns:
                if get_pos(n,inp) in (pos1,pos2) and n in res:
                    res.remove(n)
    
    
    if len(res) != 0:
        return random.choice(res)
    else:
        return None



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


def remove_out(out,inp,new_inp,subs_noun,nmod):
    out_splits = out.split(' ')
    subs_noun_pos = get_pos(subs_noun,inp)
    
    if out_splits[0] != '*':
        out_splits = ['BEG'] + out_splits

    new_out_splits = out_splits.copy()
    
    nmod_noun_pos = None
    for w in nmod.split(' '):
        w = w.lower()
        if '//n' in w :
            nmod_noun_pos = get_pos(w,new_inp)
            break
    if nmod_noun_pos is None:
        return None

    for i,word in enumerate(out_splits):
        if word == '*' and len(out_splits[i:]) >= 5 and out_splits[i+5].isdigit() and out_splits[i+5] == subs_noun_pos:
            new_out_splits = new_out_splits[:i] + new_out_splits[i+8:]

        if word == 'AND' and (len(out_splits[i:]) >= 5 and out_splits[i+5].isdigit() and out_splits[i+5] == subs_noun_pos):
            new_out_splits = new_out_splits[:i] + new_out_splits[i+7:]
        
        if word == ';' and (len(out_splits[i:]) >= 5 and out_splits[i+5].isdigit() and out_splits[i+5] == subs_noun_pos):
            new_out_splits = new_out_splits[:i+1] + new_out_splits[i+7:]
        
        if word == 'BEG' and (len(out_splits[i:]) >= 5 and out_splits[i+5].isdigit() and out_splits[i+5] == subs_noun_pos):
            new_out_splits = new_out_splits[:i] + new_out_splits[i+7:]
        


    if new_out_splits[0] == 'BEG':
        new_out_splits = new_out_splits[1:]

       
    for i,word in enumerate(new_out_splits):
        word = word.lower()
        if word == subs_noun_pos or word == subs_noun[:-3]:
            new_out_splits[i] = nmod_noun_pos
        
    return ' '.join(new_out_splits)


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

def add_nmod_out(out,inp,new_inp,nmod,subs_noun):
  
    removed_out = remove_out(out,inp,new_inp,subs_noun,nmod)
        
    if removed_out is None: return None
    
    if 'NNP' in nmod:
        nmod_noun = get_noun(nmod)
        subs_nmod_pos = get_pos(nmod_noun+'//N',new_inp)
        final_out = removed_out.replace('x _ '+subs_nmod_pos,nmod_noun)
        if final_out[:3] == 'AND':
            final_out = final_out[3:]
        final_out = final_out.replace('; AND',';')

        np_nwords = get_n_words(subs_noun,inp)
        nmod_nwords = get_n_words(nmod,new_inp)

        splits = final_out.split(' ')


        if nmod_nwords == 1 and np_nwords == 2:
            for i,word in enumerate(splits):
                if word.isdigit() and int(word) > int(subs_nmod_pos):
                    splits[i] = str(int(word)-1) 
        
            final_out = ' '.join(splits)

        elif nmod_nwords != np_nwords:
            return None
        return final_out
    

    det_out,nmod_out,det_cut_ind,cut_ind,n_words = get_nmod_out(nmod,new_inp)
    
    if nmod_out is None:
        return None

    cutted = False
    det_cut_pos = 0
    cut_pos = 0
    out_splits = removed_out.split(' ')
    subs_noun_n_words = get_n_words(subs_noun,inp)
    
    if out_splits[0] != '*':
        out_splits = ['AND'] + out_splits

    for i,word in enumerate(out_splits):
        if word == '*' and len(out_splits[i:]) >= 5 and out_splits[i+5].isdigit() and int(out_splits[i+5]) < det_cut_ind:
            det_cut_pos = i+8
        if word == 'AND' and (len(out_splits[i:]) >= 7 and out_splits[i+5].isdigit() and int(out_splits[i+5]) < cut_ind):
            cut_pos = i+7
            cutted = True
        if word == 'AND' and len(out_splits[i:])>=11 and out_splits[i+7].isdigit() and int(out_splits[i+7]) < cut_ind:
            cut_pos = i+13
            cutted = True
        if word == 'AND' and len(out_splits[i:])>=15 and out_splits[i+9].isdigit() and int(out_splits[i+9]) < cut_ind:
            cut_pos = i+15
            cutted = True

        if word.isdigit() and int(word) > cut_ind:
            out_splits[i] = str(int(out_splits[i])+n_words-subs_noun_n_words)

    if out_splits[0] == 'AND':
        out_splits = out_splits[1:]
        if cut_pos != 0:
            cut_pos = cut_pos-1
    
    end_det_pos = 0
    for i,word in enumerate(out_splits):
        if word == ';':
            end_det_pos = i+1
    
    if end_det_pos > cut_pos:
        cut_pos = end_det_pos

    if end_det_pos > det_cut_pos:
        new_det_out_beg = ' '.join(out_splits[:det_cut_pos])
        new_det_out_end = ' '.join(out_splits[det_cut_pos:end_det_pos])
        final_det_out = new_det_out_beg + ' ' + det_out + ' ' + new_det_out_end

    else: 
        new_det_out_beg = ' '.join(out_splits[:det_cut_pos])
        final_det_out = new_det_out_beg + ' ' + det_out


    nmod_out = nmod_out.strip()
    splits = nmod_out.split(' ')
    if splits[0] == 'AND' and cut_pos == end_det_pos:
        splits = splits[1:]
        nmod_out = ' '.join(splits)

    new_beg_out = ' '.join(out_splits[end_det_pos:cut_pos])
    new_compl_out = ' '.join(out_splits[cut_pos:])
    new_compl_out = new_compl_out.strip()
    if splits[-1] != 'AND' and len(new_compl_out) > 0 and new_compl_out.split(' ')[0] != 'AND':
        nmod_out = nmod_out + ' AND'

    
    new_nmod_out = new_beg_out + ' ' + nmod_out + ' ' + new_compl_out
    new_nmod_out = new_nmod_out.strip()
    
    if new_nmod_out[:4] == 'AND ':
        new_nmod_out = new_nmod_out[4:]
    final_out = final_det_out.strip() + ' ' + new_nmod_out.strip()
   
    final_out = final_out.replace('  ',' ')
    return final_out


def main():
    with open(IN_FILE) as f:
        read_tsv = csv.reader(f, delimiter='\t')
        res = []
        dic = []
        test = {}
        test2 = {}

        
        control_1 = 0
        control_2 = 0

    
        simple_nps = []

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
            simple_nps = get_simple_nps(inp,out,simple_nps)
        
        simple_nps_dic = {i:simple_nps.count(i) for i in simple_nps}
        for k,v in simple_nps_dic.items(): 
            simple_nps_dic[k] = 1/v
        
        nmods_dic = {i:nmods.count(i) for i in nmods}
        for k,v in nmods_dic.items():
            nmods_dic[k] = 1/v

        set_1 = set(simple_nps)
        set_2 = set(nmods)

        set_1 = list(set_1)
        set_2 = list(set_2)

        while (count<MAX_ADDED_LINES):
            inp,out,dist = rows[random.randint(0,length-1)]
            if not valid(inp,dist): 
                continue
        
            rand_int = random.random()

            if rand_int <= 0.5:
                if control_1 < 1000:                 
                    nmod = random.choices(population=list(simple_nps_dic.keys()),weights = simple_nps_dic.values(), k =1)[0]
                    control_1 +=1
                else:
                    nmod = random.choice(set_1)
               
                if nmod in test:
                    test[nmod] += 1
                else:
                    test[nmod] = 1
                subs_noun = get_possible_noun(inp,out,pp_rest=True)

            else:
                if control_2 < 1000:
                    nmod = random.choices(population=list(nmods_dic.keys()),weights = nmods_dic.values(), k =1)[0]
                    control_2 +=1
                else:
                    nmod = random.choice(set_2)
                if nmod in test2:
                    test2[nmod] += 1
                else:
                    test2[nmod] = 1
                subs_noun = get_possible_noun(inp,out,pp_rest=False)
                
            
            if not subs_noun: continue


            if not valid_nmod(nmod,inp): 
                continue

            new_inp = add_nmod_inp(subs_noun,inp,nmod)
            new_out = add_nmod_out(out,inp,new_inp,nmod,subs_noun) 

            if new_out is None:
                continue

            
            write_new_row(new_inp,new_out,dist,inp,out,nmod,subs_noun)
            count+=1
            
    return res





if __name__ == '__main__':
    write_prev_rows()
    res = main()
    OUT_FILE.close()


