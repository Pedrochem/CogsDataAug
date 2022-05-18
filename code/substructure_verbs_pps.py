import csv
import enum
import random
from re import L, S
from aug_train import final_clean_output

IN_FILE = 'data/train_pos.tsv'
MAX_ADDED_LINES = 10000
CLASSES_NN = ['NN','DT']
VERB_PPS = ['by','to']
VERBS_COMP = ['agent','theme','recipient','xcomp','ccomp']

NOUN_PPS = ['in','beside','on']
OUT_FILE = open('results/substructure/res_no_pp_restriction.tsv', 'w')

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


    OUT_FILE.write(or_inp+'\n')
    OUT_FILE.write(pp+'\n')
    OUT_FILE.write('-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
    
    OUT_FILE.write(final_row+'\n')
    OUT_FILE.write('\n==================================================================================================================================================================================================================================================================================================================================================================\n')

def get_pps(inp,dic):
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
                    dic['to'].append(pp)
                elif 'in//I' in pp:
                    dic['in'].append(pp)
                elif 'beside//I' in pp:
                    dic['beside'].append(pp)
                elif 'by//I' in pp:
                    dic['by'].append(pp)
                elif 'on//I' in pp:
                    dic['on'].append(pp)


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
    return True

def add_pp_verb_inp(inp,pp_type,pp):
    splits = inp.split('PP')
    
    if pp_type == 'to' and 'by//I' in inp:
        for i,split in enumerate(splits): 
            if 'by' in split:
                new_inp = new_inp + ' ' + pp + 'PP' + 'PP'.join(splits[i])
                return new_inp
            new_inp = 'PP'.join((new_inp,split))
    else:

        new_inp = inp[:-10] + pp + ' ' + inp[-10:]
        return new_inp

    

def get_possible_pps_and_verb(out):
    splits = out.split(' ')
    verbs = set()
    for i,word in enumerate(splits):
        if word in VERBS_COMP:
            verbs.add(splits[i-2])
    if len(verbs) > 1: return ([],[]) # Todo: make it work for outputs with more than one verb


    dic = {'to':'recipient',
            'by':'agent',
            'beside':'beside',
            'in':'in',
            'on':'on'}
    
    possible_pps = ['to','in','on','beside','by']

    for key in dic.keys():
        if dic[key] in out:
            possible_pps.remove(key)
    
    if len(possible_pps)>1:
        random.shuffle(possible_pps)
        return possible_pps,[verbs.pop()] # todo: remove pop set()
    else: 
        return ([],[]) 

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
                cut_pos = len(inv_out_splits)+i-11
                break
            else:
                cut_pos = len(inv_out_splits)+i-9
                break
    
    if noun_type == 'NN':
        added_out = 'AND ' + verb + ' . agent ( x _ '+verb_pos+' , x _ '+str(out_noun_pos)+' ) '
        out_splits = out.split(' ')
        for i,word in enumerate(out_splits):
            if word.isdigit() and int(word)>=out_noun_pos:
                out_splits[i] = str(int(word)+2)
       
        new_out = out_splits[:cut_pos] + [added_out] + out_splits[cut_pos:]
        
        if det: 
            noun_out = '* '+out_noun+' ( x _ '+ (str(out_noun_pos))+' ) ; '
            i = 0
            while (out_splits[i] == '*' and int(out_splits[i+5])<out_noun_pos):
                i+=8
            new_out = new_out[:i] + [noun_out] + new_out[i:]
    

    if noun_type == 'NNP':  
        added_out ='AND ' + verb + ' . agent ( x _ '+verb_pos+' , '+ out_noun +' ) '
        splits = out.split(' ')
        for i,word in enumerate(splits):
            if word.isdigit() and int(word)>=out_noun_pos:
                splits[i] = str(int(word)+2)
       
        new_out = splits[:cut_pos] + [added_out] + splits[cut_pos:]
        

    return ' '.join(new_out)


def add_pp_verb_to_out(out,inp,pp_type,pp):
    # only works for to (now) and for PPs WITHOUT proper nouns
    inv_out = out[::-1]
    out_noun = get_out_noun(pp)

    splits = inv_out.split(' ')
    for i,word in enumerate(splits):
        if word in ['theme']:
            verb = splits[i+2]

            verb_pos = splits[i+4]
            if splits - 6 == 'x':
                cut_pos = len(splits)-i-9
            else:
                cut_pos = len(splits)-i-7
    
    added_out = verb + ' . agent ( x _ '+verb_pos+' , '+out_noun+' )'

    compl_splits = splits[cut_pos:]
    for i,split in enumerate(compl_splits):
        if split.isDigit():
            compl_splits[i] = str(int(split)+2)


    new_out = splits[:cut_pos] + [added_out] + compl_splits
    return ' '.join(new_out)


def get_rand_pp(pp_type,dic):
    rand_int = random.randint(0,len(dic[pp_type])-1)
    return dic[pp_type][rand_int]

    

def main():
    with open(IN_FILE) as f:
        read_tsv = csv.reader(f, delimiter='\t')
        res = []

        dic = {'to':[],
        'in':[],
        'beside':[],
        'by':[],
        'on':[]}
    
        rows = list(read_tsv)
        count = 0
        length = len(rows)
        

        # DELETE LATER
        random.seed(1) 
        # DELETE LATER

        for row in rows:
            inp,out,dist = row
            dic = get_pps(inp,dic)
        
       
        while (count<MAX_ADDED_LINES):
            inp,out,dist = rows[random.randint(0,length-1)]
            if not valid(inp,dist): 
                continue
            
            possible_pps,verbs = get_possible_pps_and_verb(out)

            #i = 0
            for verb in verbs:
                #possible_pp = possible_pps[i]
                i=0
                n_additions = random.randint(0,len(possible_pps))
                for i in range(n_additions):
                    pp_type = possible_pps[i]
                    i+=1
                    rand_pp = get_rand_pp(pp_type,dic) # return a random pp of type pp_type from dict

                    # if pp_type in VERB_PPS: #undelete
                    if pp_type != 'by': continue #delete
                    if pp_type in 'by': #delete

                        new_inp = add_pp_verb_inp(inp,pp_type,rand_pp)
                        new_out = add_pp_verb_by_out(out,new_inp,pp_type,rand_pp,verb) #only works for by
                        res.append((new_inp,new_out))
                        write_new_row(new_inp,new_out,dist,inp,rand_pp)
                        count+=1
                    elif pp_type in 'to':
                        new_inp = add_pp_verb_inp(inp,pp_type,rand_pp)
                        new_out = add_pp_verb_to_out(out,inp,pp_type,rand_pp) #only works for by    

                    # elif pp_type in NOUN_PPS:
                    #     new_inp = add_pp_noun_inp(inp,pp_type,rand_pp)
                    #     new_out = add_pp_noun_out(out,inp,pp_type,rand_pp)
    return res





if __name__ == '__main__':
    # write_prev_rows()
    res = main()
    OUT_FILE.close()
    j=25


