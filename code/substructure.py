import csv
import enum
import random
from re import L, S
from aug_train import final_clean_output

IN_FILE = 'data/DATA_MISC.tsv'
MAX_ADDED_LINES = 10
CLASSES_NN = ['NN','DT']

OUT_FILE = open('results/substructure/train.tsv', 'w')

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
    final_row = cat+' - '+ '\t'.join((final_inp,final_out,dist))
    
    # OUT_FILE.write('\t'.join((inp,out))+'\n')
    # OUT_FILE.write('\t'.join((s_inp,s_out))+'\n')
    # OUT_FILE.write('-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
    
    OUT_FILE.write(final_row+'\n')
    # OUT_FILE.write('\n==================================================================================================================================================================================================================================================================================================================================================================\n')

        
def validate_np(np,inp,out):
    out_splits = out.split(' ')
    np_splits = np.split(' ')
    if 'NN' in np_splits:
        subs_word = np_splits[np_splits.index('NN')+1][:-3]
        for i,word in enumerate(out_splits):
            if word == subs_word and len(out_splits) > i+1 and out_splits[i+1] == '.': 
                return False
    return True

# returns part of the string starting with np and ending with a parenthesis
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
                if validate_np(np,inp,out):
                    nps_lst.append((np,np_pos))
                np_found = False
    return nps_lst

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
                if word == subs_word[:-3]:
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


    
    return out,strategy
    


def main():
    '''
    Iterates over dataset and select random rows to be modified
    '''
    with open(IN_FILE) as f:
        strategy = {'NN_NN':0, 'NNP_NNP':0,'NN_NNP':0,'NNP_NN':0}
        read_tsv = csv.reader(f, delimiter='\t')
        rows = list(read_tsv)
        cont = 0
        length = len(rows)
        added_rows = set()
        # DELETE LATER
        random.seed(1) 
        # DELETE LATER

        while (cont<MAX_ADDED_LINES):
            inp,out,dist = rows[random.randint(0,length-1)]
            s_inp,s_out,s_dist = rows[random.randint(0,length-1)]
            
            if inp == s_inp: continue
            nps = get_np(inp,out)
            s_nps = get_np(s_inp,s_out)
            if len(nps) == 0 or len(s_nps) == 0: continue

            if  len(nps) > len(s_nps):
                nps,s_nps = s_nps,nps
                inp,s_inp = s_inp,inp
                out,s_out = s_out,out
            

            s_nps = s_nps[::-1]
            new_inp,new_out = inp, out

            for i in range(len(nps)): 
                if nps[i][0] == s_nps[i][0]: 
                    random.shuffle(s_nps)

                np, np_pos = nps[i]
                s_np, snp_pos = s_nps[i]
                
                old_strategy = strategy.copy()
                res,strategy = modify_out(new_inp,new_out,np,s_np,strategy)
                if res != None: 
                    new_out = res
                    new_inp = new_inp.replace(np, s_np)

            
            if new_inp != None and new_out != None and old_strategy['NNP_NN'] != strategy['NNP_NN']:
                new_inp = validate_new_inp(new_inp)
                write_new_row(new_inp,new_out,dist,old_strategy,strategy)
                #added_rows.add(inp)
                cont+=1


        print(strategy)




if __name__ == '__main__':
    write_prev_rows()
    main()
    OUT_FILE.close()



