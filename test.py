
import ast
from collections import defaultdict


NOUN = 'noun'
MAX_PERMS = 3

#train_file = open("Data/train_pos.tsv")
train_file = open("Data/test_train.tsv")

out_file = open("output.tsv", "w")

p_file = open('permutation_vocab_src.txt')
# p_file = open('perms.txt')
# p_file = open('test_perms.txt')


p_dic = {}


def make_p_dic():
    for row in p_file:
        row = row.lower()
        splits = row.split(':')
        key = ast.literal_eval(splits[0])
        value_splits = splits[1].split(' ')[1:]
        value_splits[-1] = value_splits[-1].rstrip("\n")
        p_dic[key] = value_splits
    return

def write_permutations(dic_perms):
        
    return 
def modify_output(out,pos,w_class,word):
    if w_class == 'n':
        split_word = ' ( x _ '+str(pos)+' )'
        if split_word in out:
            splits = out.split(split_word)
            words_before = splits[0].split(' ')
            words_before[-1] = '?n'+str(pos)
            splits[0] = ' '.join(words_before)
            new_out = split_word.join(splits)
            return new_out
        elif word in out: #case its a name
            return out.replace(word,'?n'+str(pos))
    elif w_class == 'v':        
        split_word = '( x _ '+str(pos)+' ,'
        splits = out.split(' ')
        for i,_ in enumerate(splits):
            if ' '.join(splits[i+3:i+8]) == split_word:
                splits[i] = '?v'+str(pos)
        new_out = ' '.join(splits)
        return new_out

    else: 
        return out

def clean_utt(utt,p,flag):
    splits = utt.split(' ')
    permuted_utt = ''
    for word in splits:
        if '//' in word or (word == p and flag):
            if '//' in word:
                word=word[:-3]
            permuted_utt += word + ' '
    return permuted_utt

def make_new_row(utt,output,word,w_class,pos,p):
        splits = utt.split(' ')
        splits[pos] = p
        permuted_utt = (' ').join(splits)
        #permuted_utt = clean_utt(permuted_utt,p,True)
        if output[-1]!='\n': output+='\n'
        final_row = ('\t').join((permuted_utt,output))
        return final_row

def main():
    for row in train_file:
        row = row.lower()
        utt, output, distribution = row.split('\t')
        formated_utt = clean_utt(utt,'',False) 
        count_perm = 0
        pos_symbol = 0
        pos_word = 0
        new_output = output
        found_perm = False
        dic_perms = defaultdict(list)
        dic_final_new_rows = defaultdict(list)
        new_sentences = [formated_utt+'\t'+output]
        control = True
        for word_class in utt.split(' '):
            if '//' in word_class:  
                word, w_class = word_class.split("//")
                if w_class in ('n','v') and (word,w_class) in p_dic.keys() and (str(pos_word) in output or word in output): # word to be permuted
                    old_sentences = new_sentences.copy()
                    for sentence in old_sentences:
                        perm_utt,perm_out = sentence.split('\t')
                        # found_perm = True 
                        new_output = modify_output(perm_out,pos_word,w_class,word)
                        for p in p_dic[(word,w_class)]:
                            new_row = make_new_row(perm_utt,new_output,word,w_class,pos_word,p)
                            # out_file.write(new_row)
                            dic_perms[(word,w_class)].append(new_row)
                            if control: 
                                new_sentences.pop()
                                control = False
                            new_sentences.append(new_row)
                            if new_row not in dic_final_new_rows[utt]:
                                dic_final_new_rows[utt].append(new_row)
                            
                    
                    # count_perm+=1
                pos_word+=1
            pos_symbol+=1
            # if count_perm >= MAX_PERMS:
            #     break
        
        write_permutations(dic_perms)
        print(dic_final_new_rows.keys())

        
        if not found_perm:
            formated_row = ('\t').join((formated_utt,new_output))
            out_file.write(formated_row+'\n')



make_p_dic()
main()
p_file.close()
train_file.close()
out_file.close()





