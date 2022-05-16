import csv
import enum
import random
from re import L, S
from aug_train import final_clean_output

IN_FILE = 'data/train_pos.tsv'
MAX_ADDED_LINES = 10000
CLASSES_NN = ['NN','DT']
VERB_PPS = ['by','to']
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

def write_new_row(inp,out,dist,old_strategy,strategy):
    cat = 'Normal'
    if old_strategy != None: 
        for k in strategy.keys():
            if old_strategy[k] != strategy[k]:
                cat = k
        
    inp_splits = inp.split(' ')
    final_inp = ''
    for i,word in enumerate(inp_splits):
        if '//' in word:
            if inp_splits[i-1] == 'NNP': word = word[:-1]+'P'
            final_inp += word.replace('//',' ') + ' '
    final_out = final_clean_output(out)
    # final_row = cat+' - '+ '\t'.join((final_inp,final_out,dist))
    final_row = '\t'.join((final_inp,final_out,dist))


    # OUT_FILE.write('\t'.join((inp,out))+'\n')
    # OUT_FILE.write('\t'.join((s_inp,s_out))+'\n')
    # OUT_FILE.write('-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
    
    OUT_FILE.write(final_row+'\n')
    # OUT_FILE.write('\n==================================================================================================================================================================================================================================================================================================================================================================\n')


def get_pps(inp,dic):
    splits = inp.split(' ')
    brackets = None
    pps = set()
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
                pps.add(pp)
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


    return pps,dic

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
        new_inp = inp[:-10] + pp + inp[-10:]
        return new_inp

    

def get_possible_pps(out):
    dic = {'to':'recipient',
            'by':'agent',
            'beside':'beside',
            'in':'in',
            'on':'on'}
    
    possible_pps = ['to','in','on','beside','by']

    for key in dic.keys():
        if dic[key] in out:
            possible_pps.remove(key)
    
    random.shuffle(possible_pps)
    return possible_pps

def get_verb(inp):
    for word in inp.split(' '):
        if '//V' in word:
            verb = word
    return verb

def add_pp_verb_by_out(out,inp,pp_type,pp):
    # only works for by (now)
    inv_out = out[::-1]
    out_noun = get_out_noun(pp)

    splits = inv_out.split(' ')
    for i,word in enumerate(splits):
        if word in ['theme','recipient']:
            verb = splits[i+1]
            verb_pos = splits[i+4]
            if splits - 6 == 'x':
                cut_pos = len(splits)-i-9
            else:
                cut_pos = len(splits)-i-7
    
    added_out = verb + ' . agent ( x _ '+verb_pos+' , '+out_noun+' )'
    new_out = splits[:cut_pos] + [] + splits[cut_pos:]


def main():
    with open(IN_FILE) as f:
        read_tsv = csv.reader(f, delimiter='\t')
        
        rows = list(read_tsv)
        cont = 0
        length = len(rows)
        dic = {'to':set(),
        'in':set(),
        'beside':set(),
        'by':set(),
        'on':set()}

        # DELETE LATER
        random.seed(1) 
        # DELETE LATER

        for row in read_tsv:
            inp,out,dist = row
            pps,dic = get_pps(inp,dic)
        
        while (cont<MAX_ADDED_LINES):
            inp,out,dist = rows[random.randint(0,length-1)]
            
            if not valid(inp,dist): 
                continue
            
            possible_pps = get_possible_pps(out)
            n_additions = random.randint(0,len(possible_pps)-1)
            for i in range(n_additions):
                pp_type = possible_pps[i]
                rand_pp = get_rand_pp(pp_type) # return a random pp of type pp_type from dict

                if pp_type in VERB_PPS:
                    new_inp = add_pp_verb_inp(inp,pp_type,rand_pp)
                    new_out = add_pp_verb_by_out(out,inp,pp_type,rand_pp) #only works for by
                
                elif pp_type in NOUN_PPS:
                    new_inp = add_pp_noun_inp(inp,pp_type,rand_pp)
                    new_out = add_pp_noun_out(out,inp,pp_type,rand_pp)





if __name__ == '__main__':
    write_prev_rows()
    main()
    OUT_FILE.close()



