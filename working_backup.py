
import ast
from collections import defaultdict
from dis import dis


NOUN = 'noun'
MAX_PERMS = 3

train_file = open("Data/train_pos.tsv")
# train_file = open("Data/test_train.tsv")

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
        else: return out 
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
        if output[-1]=='\n': output = output[:-1]
        final_row = ('\t').join((permuted_utt,output))
        return final_row

def write_permutated_rows(permuted_rows,distribution):
    if distribution[-1]!='\n': distribution+='\n'
    

    for row in permuted_rows:
        if row[0] == '\"': row=row[1:]
        if row[-1] == '\"': row=row[:-1]
        final_row = '\t'.join((row,distribution))
        out_file.write(final_row)

def make_permutations(words_to_be_permuted,utt,output,initial_row):
    permuted_rows = [initial_row]

    for word,w_class,pos in words_to_be_permuted:
        output = modify_output(output,pos,w_class,word)
    
    for word,w_class,pos in words_to_be_permuted:
        temp_rows = []
        for p in p_dic[(word,w_class)]:
            for row in permuted_rows:
                utt, _= row.split('\t')
                p_row = make_new_row(utt,output,word,w_class,pos,p)
                temp_rows.append(p_row)
        
        permuted_rows = list(temp_rows)
    return permuted_rows

def main():
    for row in train_file:
        row = row.lower()
        utt, output, distribution = row.split('\t')
        formated_utt = clean_utt(utt,'',False) 
        count_perm = 0
        pos_word = 0
        initial_row = formated_utt+'\t'+output
        words_to_be_permuted = []
        for word_class in utt.split(' '):
            if '//' in word_class:  
                word, w_class = word_class.split("//")
                if count_perm <=3 and w_class in ('n','v') and (word,w_class) in p_dic.keys() and (str(pos_word) in output or word in output): # word to be permuted
                    words_to_be_permuted.append((word,w_class,pos_word))
                    count_perm+=1
                pos_word+=1

        permuted_rows = make_permutations(words_to_be_permuted,formated_utt,output,initial_row)
        write_permutated_rows(permuted_rows,distribution)


make_p_dic()
main()
p_file.close()
train_file.close()
out_file.close()





