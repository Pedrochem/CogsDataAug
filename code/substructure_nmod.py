import csv
import enum
import random
from re import L, S
from numpy import False_

from regex import P
from aug_train import final_clean_output

IN_FILE = 'data/train_pos.tsv'
MAX_ADDED_LINES = 10000
NMODS = ['in','by','on']
VERBS_COMP = ['agent','theme','recipient','xcomp','ccomp']

NOUN_PPS = ['in','beside','on']
OUT_FILE = open('results/substructure/res_no_pp_restriction.tsv', 'w')

WAS_RESTRICTION = False
SAME_NOUN_RESTRICTION = True 

def get_outsplits_word_info(outsplits):
    pos = None
    found = False
    for i,x in enumerate(outsplits):
        if x.isdigit() and not found:
            pos = int(x)
            found = True
        if x == 'AND':
            ind = i+1
            return pos,ind,False
    
    return pos,None,True

def validate_nn(nn_splits):
    'Returns true only if nn is composed by 2 words (article + noun)'
    cont = 0
    det = False
    for word in nn_splits:
        if '//' in word:
            cont+=1
        if word.lower() == 'the':
            det = True
    return cont==2,det

def write_prev_rows():
    with open(IN_FILE, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            inp,out,dist = row
            write_new_row(inp,out,dist,None,None)

def validate_new_inp(new_inp):
    first = True
    splits = new_inp.split(' ')
    for i,word in enumerate(splits):
        if '//' in word and not first:
            splits[i] = word[0].lower() + word[1:]
        if '//' in word and first:
            splits[i] = word[0].upper() + word[1:]
            first = False

    return ' '.join(splits)

def write_new_row(inp,out,dist,or_inp,pp):
    inp_splits = inp.split(' ')
    final_inp = ''
    for i,word in enumerate(inp_splits):
        if '//' in word:
            if inp_splits[i-1] == 'NNP': word = word[:-1]+'P'
            final_inp += word.replace('//',' ') + ' '
    final_out = final_clean_output(out)
    final_row = '\t'.join((final_inp,final_out,dist))


    # OUT_FILE.write(or_inp+'\n')
    # OUT_FILE.write(pp+'\n')
    # OUT_FILE.write('-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
    
    OUT_FILE.write(final_row+'\n')
    # OUT_FILE.write('\n==================================================================================================================================================================================================================================================================================================================================================================\n')

def get_nmods(inp,dic):
    splits = inp.split(' ')
    brackets = None
    pp_found = False
    
    for i,word in enumerate(splits):
        last_np = None
        
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


        if word == 'PP' and splits[i+3][:-3].lower() in NMODS:
            pp_found = True
            pp_pos = i
            brackets = 1
        elif pp_found:
            if word == '(':
                brackets+=1
            elif word == ')':
                brackets-=1
            if brackets == 0:
                nmod = '( ' + ' '.join(splits[pp_pos:i+1])
                np_nmod = last_np + ' ' + nmod
                pp_found = False 

                if 'in//I' in np_nmod:
                    dic['in'].append(np_nmod)
                elif 'beside//I' in np_nmod:
                    dic['beside'].append(np_nmod)
                elif 'on//I' in np_nmod:
                    dic['on'].append(np_nmod)


    return dic

def get_word_pos(inp,word):
    splits = inp.split(' ')
    cont = 0
    for split in splits:
        if split == word:
            return cont
        if '//' in split: 
            cont+=1
        
def modify_out(inp,out, np, s_np,strategy):
    np_splits = np.split(' ')
    s_np_splits = s_np.split(' ')
    out_splits = out.split(' ')
    new_out_splits = None

    if 'NNP' in np_splits and 'NNP' in s_np_splits:
        if 'NN' in np_splits or 'NN' in s_np_splits or np_splits.count('NNP') > 1 or s_np_splits.count('NNP') > 1: 
            return '',strategy
            #raise ValueError('Ué')
        np_nnp = np_splits[np_splits.index('NNP')+1][:-3]
        s_np_nnp = s_np_splits[s_np_splits.index('NNP')+1][:-3]
        strategy['NNP_NNP'] += 1
        return out.replace(np_nnp,s_np_nnp),strategy

    if 'NN' in np_splits and 'NN' in s_np_splits:
        if 'NNP' in np_splits or 'NNP' in s_np_splits or np_splits.count('NNP') > 1 or s_np_splits.count('NNP') > 1: 
            return None,strategy
            #raise ValueError('Ué2')
        if np_splits.count('DT') != s_np_splits.count('DT'):
            return None,strategy
            #raise ValueError('Deu ruim com o DT')
        if ('The//D' in np_splits or 'the//D' in np_splits) and not('The//D' in s_np_splits or 'the//D' in s_np_splits):
            return None,strategy
        
        if ('The//D' in s_np_splits or 'the//D' in s_np_splits) and not('The//D' in np_splits or 'the//D' in np_splits):
            return None,strategy
            #raise ValueError('problema com as frase definitiva olhar paper')
        np_nn = np_splits[np_splits.index('NN')+1][:-3]
        s_np_nn = s_np_splits[s_np_splits.index('NN')+1][:-3]
        strategy['NN_NN'] += 1
        return out.replace(np_nn,s_np_nn), strategy

    if 'NN' in np_splits and 'NNP' in s_np_splits:
        if 'NNP' in np_splits or 'NN' in s_np_splits: 
            raise ValueError('Ué3')
        s_np_nnp = s_np_splits[s_np_splits.index('NNP')+1][:-3]

        if np_splits.count('DT') != 1:
            return None,strategy
            raise ValueError('Deu ruim com o DT dnv, só tem 1')

        subs_word = np_splits[np_splits.index('NN')+1]
        subs_word_pos = int(get_word_pos(inp,subs_word))
        if 'DT' in np_splits:
            for i, word in enumerate(out_splits):
                if word.lower() == subs_word[:-3].lower():
                    if out_splits[i-1] in ['*',';','AND']: 
                        new_out_splits = out_splits[:i-1]
                    else:
                        new_out_splits = out_splits[:i]

                    if len(out_splits) > i+6 and out_splits[i+6] in [';','AND']:
                        new_out_splits+=out_splits[i+7:]
                    else:
                        new_out_splits+=out_splits[i+6:]                    

            for i,word in enumerate(new_out_splits):
                if word.isdigit() and int(word) > subs_word_pos:
                    new_out_splits[i] = str(int(word)-1)
                
                if word == str(subs_word_pos) and new_out_splits[i-4] != subs_word:
                    new_out_splits[i] = s_np_nnp
                    new_out_splits[i-1],new_out_splits[i-2] = '',''
            res = ' '.join(new_out_splits).replace('   ',' ')
            strategy['NN_NNP']+=1
            return res, strategy
    
    if 'NNP' in np_splits and 'NN' in s_np_splits:
        subs_word = s_np_splits[s_np_splits.index('NN')+1][:-3]

        valid,det = validate_nn(s_np_splits)
        if not valid:
            return None,strategy

        if 'NN' in np_splits or 'NNP' in s_np_splits: 
            raise ValueError('Ué3')

        np_nnp = np_splits[np_splits.index('NNP')+1]
        
        subs_pos = get_word_pos(inp,np_nnp)
        if det: 
            subs_out = '* '+subs_word+'( x _ '+ (subs_pos)+'; '
            i = 0
            if out_splits[i] == '*' and int(out_splits[5])<subs_word:
                i = 5
                word_pos = int(out_splits[i])
                while word_pos < subs_pos and out_splits[i+3]=='*':
                    i+=8
            new_out_splits = out_splits[:i+3] + [subs_out] + out_splits[i+3:]
    
        
        else: #not det
            i = 0
            while out_splits[i] == '*':
                i+=8

            last_end_ind = i
            j = 0
            for x,word in enumerate(out_splits[i:]):
                word_pos,end_ind,final_word = get_outsplits_word_info(out_splits[i+j:])
                if word_pos == None:
                    return None,strategy
                if word_pos > subs_pos:
                    new_out_splits = out_splits[:last_end_ind] + (subs_word+' ( x _ '+ str(subs_pos)+' ) AND').split(' ') + out_splits[last_end_ind:]
                    break
                if final_word:
                    new_out_splits = out_splits + ('AND '+(subs_word+' ( x _ '+ str(subs_pos)+' )')).split(' ')
                    break
                j+=end_ind
                last_end_ind = end_ind

       
        for i,word in enumerate(new_out_splits):
            if word.isdigit() and int(word)>=subs_pos:
                new_out_splits[i] = str(int(word)+1)

        final_out = ' '.join(new_out_splits)
        final_out = final_out.replace(np_nnp[:-3],'x _ '+str(subs_pos+1))
        strategy['NNP_NN']+=1

        return final_out,strategy


    
    return None,strategy
    
def valid(inp,dist):
    if dist == 'primitive':
        return False
    if 'was//V' not in inp and WAS_RESTRICTION:
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

def add_nmod_inp(noun,inp,nmod_type,nmod):
    noun_np = get_np(noun,inp)


    inp_splits = inp.split(' ')
    np_ind = inp_splits.index(noun)


    new_inp = inp.replace(noun_np,nmod)
    return new_inp

def get_possible_nouns_and_nmods_type(inp,out):
    out_splits = out.split(' ')
    inp_splits = inp.split(' ')
    verb_found = False

    nouns = []
    for i,word in enumerate(inp_splits):
        if word == 'VP': 
            verb_found: True
        
        if not verb_found: 
            continue

        if '//N' in word and inp_splits[i-1] == 'NN':
            nouns.append(word)
    
    possible_nmods = ['in','on','beside']
    
    dic = {}
    for n in nouns: 
        dic[n] = possible_nmods

    for i,word in enumerate(out_splits):
        if word == 'nmod':
            dic[out_splits-2] = dic[out_splits-2].remove(out_splits[i+2])
    
    return dic

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

def add_pp_verb_by_out(out,new_inp,pp_type,pp,verb):
    # only works for by (now) and for PPs WITHOUT proper nouns
    out_noun,noun_type,det = get_out_noun(pp)
    out_noun_pos = get_out_noun_pos(new_inp,out_noun)

    inv_out_splits = out.split(' ')[::-1]
    cut_pos = len(inv_out_splits)-1
    new_out = out.split(' ')
    for i,word in enumerate(inv_out_splits):
        if word == verb:
            verb_pos = inv_out_splits[i-6]
            if inv_out_splits[i-8] == 'x':
                cut_pos = len(inv_out_splits)-i+11
                break
            else:
                cut_pos = len(inv_out_splits)-i+9
                break
    
    if noun_type == 'NN':
        
        added_out = 'AND ' + verb + ' . agent ( x _ '+verb_pos+' , x _ '+str(out_noun_pos)+' )'
        out_splits = out.split(' ')
        
        for i,word in enumerate(out_splits):
            if word.isdigit() and int(word)>=out_noun_pos:
                out_splits[i] = str(int(word)+2)
       
        new_out = out_splits[:cut_pos] + [added_out] + out_splits[cut_pos:]
        
        if det: 
            noun_out = '* '+out_noun+' ( x _ '+ (str(out_noun_pos))+' ) ;'
            i = 0
            while (out_splits[i] == '*' and int(out_splits[i+5])<out_noun_pos):
                i+=8
            new_out = new_out[:i] + [noun_out] + new_out[i:]
        else:
            noun_out = 'AND '+out_noun+' ( x _ '+ (str(out_noun_pos))+' )'
           

            i=cut_pos+1
            stop = False
            while(not stop):
                stop = True
                if len(new_out) > i+5 and new_out[i+5].isdigit():
                    i+=7
                    stop = False
                elif len(new_out) > i+9 and new_out[i+3] == 'nmod' and new_out[i+9].isdigit(): 
                    i+=15
                    stop = False
                    
            new_out = new_out[:i] + [noun_out] + new_out[i:]

   
    if noun_type == 'NNP':  
        added_out ='AND ' + verb + ' . agent ( x _ '+verb_pos+' , '+ out_noun +' )'
        splits = out.split(' ')
        for i,word in enumerate(splits):
            if word.isdigit() and int(word)>=out_noun_pos:
                splits[i] = str(int(word)+2)
       
        new_out = splits[:cut_pos] + [added_out] + splits[cut_pos:]
        

    res =  ' '.join(new_out)
    return res

def get_rand_nmod(nmod_types,dic):
    rand_type = random.choice(nmod_types)
    return random.choice(dic[rand_type])

def valid_pp(pp,inp):
    noun = None
    for word in pp.split(' '):
        if '//N' in word:
            noun = word
    if noun != None and noun in inp and SAME_NOUN_RESTRICTION:
        return False_
    
    return True

def main():
    with open(IN_FILE) as f:
        read_tsv = csv.reader(f, delimiter='\t')
        res = []

        dic = {'in':[],
        'beside':[],
        'on':[]}
    
        rows = list(read_tsv)
        count = 0
        length = len(rows)
        

        # DELETE LATER
        random.seed(1) 
        # DELETE LATER

        for row in rows:
            inp,out,dist = row
            dic = get_nmods(inp,dic)
        
       
        while (count<MAX_ADDED_LINES):
            inp,out,dist = rows[random.randint(0,length-1)]
            if not valid(inp,dist): 
                continue
            
            nouns_nmods = get_possible_nouns_and_nmods_type(inp,out)

            for noun,nmod_type in nouns_nmods.items():
                nmod = get_rand_nmod(nmod_type,dic)
                
                new_inp = add_nmod_inp(noun,inp,nmod_type,nmod)
                new_out = add_nmod_out(out,new_inp,nmod_type,nmod,noun) 
               
                write_new_row(new_inp,new_out,dist,inp,rand_pp)
                count+=1
              
    return res





if __name__ == '__main__':
    write_prev_rows()
    res = main()
    OUT_FILE.close()


