import csv
import enum
import random
from re import L
from aug_train import final_clean_output

IN_FILE = 'data/train_pos.tsv'
MAX_ADDED_LINES = 10000
CLASSES_NN = ['NN','DT']

OUT_FILE = open('results/substructure/train10.tsv', 'w')


def write_prev_rows():
    with open(IN_FILE, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            inp,out,dist = row
            write_new_row(inp,out,dist)



def validate_new_inp(new_inp):
    first = True
    splits = new_inp.split(' ')
    for i,word in enumerate(splits):
        if '//' in word and first:
            splits[i] = word[0].upper() + word[1:]
            first = False
    return ' '.join(splits)

def write_new_row(inp,out,dist):
    inp_splits = inp.split(' ')
    final_inp = ''
    for i,word in enumerate(inp_splits):
        if '//' in word:
            if inp_splits[i-1] == 'NNP': word = word[:-1]+'P'
            final_inp += word.replace('//',' ') + ' '
    final_out = final_clean_output(out)
    final_row = '\t'.join((final_inp,final_out,dist))

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
    new_out_splits = out_splits.copy()

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
            #raise ValueError('Deu merda com o DT')
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
            raise ValueError('Deu merda com o DT dnv, só tem 1')

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
        
    return out,strategy
    


def main():
    '''
    Iterates over dataset and select random rows to be modified
    '''
    with open(IN_FILE) as f:
        strategy = {'NN_NN':0, 'NNP_NNP':0,'NN_NNP':0}
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
            
            #if inp in added_rows: continue

            s_nps = s_nps[::-1]
            new_inp,new_out = None, None

            for i in range(len(nps)): 
                if nps[i] == s_nps[i]: 
                    random.shuffle(s_nps)
                
                if ' NNP ' in nps[i][0] and ' NN ' in s_nps[i][0]: continue

                new_inp = inp.replace(nps[i][0], s_nps[i][0])
                new_out,strategy = modify_out(inp,out,nps[i][0],s_nps[i][0],strategy)
            
            if new_inp != None and new_out != None:
                new_out = '\"'+new_out+'\"'
                new_inp = validate_new_inp(new_inp)
                write_new_row(new_inp,new_out,dist)
                #added_rows.add(inp)
                cont+=1


        print(strategy)




if __name__ == '__main__':
    write_prev_rows()
    main()
    OUT_FILE.close()




    # case both nps have same lenght
    # if len(np_splits) == len(s_np_splits):
    #     for i,word in enumerate(np_splits):
    #         np_w, s_np_w = np_splits[i], s_np_splits[i]
    #         if np_w in ['NNP','NN']:
    #             if np_w == s_np_w == 'NN':
    #                 return out   
    #             if np_w == s_np_w == 'NNP':
    #                 np_nnp = np_splits[i+1][:-3]
    #                 s_np_nnp = s_np_splits[i+1][:-3]
    #                 return out.replace(np_nnp,s_np_nnp)
    # case they have different lenght
