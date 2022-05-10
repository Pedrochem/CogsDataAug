
import ast
from collections import defaultdict
from dis import dis
import re


NOUN = 'noun'
MAX_PERMS = 3

train_file = open("data/train_pos.tsv")
# train_file = open("data/test_train.tsv")

out_file = open("results/aug/aug_train.tsv", "w")

# p_file = open('perms.txt')
# p_file = open('test_perms.txt')

def final_clean_output(out):
    splits = out.split(' ')
    for i,word in enumerate(splits):
        if word.isdigit():
            splits[i] = str(int(word)*2)
    return ' '.join(splits)
   


def make_p_dic():
    p_file = open('helper/permutation_vocab_src.txt')
    p_dic = {}
    for row in p_file:
        splits = row.split(':')
        key = ast.literal_eval(splits[0])
        value_splits = splits[1].split(' ')[1:]
        value_splits[-1] = value_splits[-1].rstrip("\n")
        p_dic[key] = value_splits[:-1]
    p_file.close()
    return p_dic

def modify_output(out,pos,w_class,word,distribution):
    
    # case its a proper name have to include pos
    if w_class == 'P':
        return re.sub(r'\b%s\b' % word , 'P _ '+str(pos), out)

    elif w_class == 'N':
        new_string = re.sub(r'\b%s\b' % word , 'N', out)
        return new_string
    
    elif w_class == 'V':        
        split_word = '( x _ '+str(pos)+' ,'
        splits = out.split(' ')
        for i,_ in enumerate(splits):
            if ' '.join(splits[i+3:i+8]) == split_word:
                splits[i] = 'V'
        new_out = ' '.join(splits)
        return new_out
    
    else: 
        return out

def clean_utt(utt,p,flag):
    splits = utt.split(' ')
    permuted_utt = ''
    for i,word in enumerate(splits):
        if '//' in word or (word == p and flag):
            if splits[i-1] == 'NNP': word = word[:-1]+'P'
            permuted_utt += word + ' '
    return permuted_utt

def make_new_row(utt,output,word,w_class,pos,p):
        splits = utt.split(' ')
        splits[pos] = p+'//'+w_class
        permuted_utt = (' ').join(splits)
        if output[-1]=='\n': output = output[:-1]
        final_row = ('\t').join((permuted_utt.strip(),output.strip()))
        return final_row

def write_permutated_rows(permuted_rows,distribution):
    if distribution[-1]!='\n': distribution+='\n'

    for row in permuted_rows:
        inp,out  =row.split('\t')
        inp = inp.replace('//',' ')
        row = '\t'.join((inp,out))
        final_row = '\t'.join((row.strip(),distribution.strip()))
        final_row = final_row.replace('\"','')
        out_file.write(final_row)
        out_file.write('\n')

def make_permutations(words_to_be_permuted,utt,output,initial_row,distribution,words_to_change_out,p_dic):
    permuted_rows = [initial_row]

    for word,w_class,pos in words_to_change_out:
        output = modify_output(output,pos,w_class,word,distribution)
    output = final_clean_output(output)
    for word,w_class,pos in words_to_be_permuted:
        temp_rows = []
        aux = w_class 
        if w_class == 'P': aux = 'N'
        for p in p_dic[(word,aux)]:
            for row in permuted_rows:
                utt, _= row.split('\t')
                p_row = make_new_row(utt,output,word,w_class,pos,p)
                temp_rows.append(p_row)
        
        permuted_rows = list(temp_rows)
    return permuted_rows

def main():
    p_dic = make_p_dic()
    for row in train_file:
        # row = row.lower()
        utt, output, distribution = row.split('\t')
        words_to_change_out = []
        formated_utt = clean_utt(utt,'',False) 
        count_perm = 0
        pos_word = 0
        initial_row = formated_utt+'\t'+output
        words_to_be_permuted = []
        for word_class in formated_utt.split(' '):
            if '//' in word_class:  
                word, w_class = word_class.split("//")
                aux = w_class
                if w_class == 'P': aux = 'N'
                if  w_class in ('N','V','P') and (word,aux) in p_dic.keys()  and (str(pos_word) in output or (word in output and w_class == 'P')):
                    words_to_change_out.append((word,w_class,pos_word))
                    if count_perm <3:
                        words_to_be_permuted.append((word,w_class,pos_word))
                        count_perm+=1
                pos_word+=1

        permuted_rows = make_permutations(words_to_be_permuted,formated_utt,output,initial_row,distribution,words_to_change_out,p_dic)
        write_permutated_rows(permuted_rows,distribution)


if __name__ == '__main__':
    main()
    train_file.close()
    out_file.close()





