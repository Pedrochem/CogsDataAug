
import ast
from collections import defaultdict
from dis import dis
import re


NOUN = 'noun'
MAX_PERMS = 3

# train_file = open("Data/train_pos.tsv")
train_file = open("data/dev.tsv")

out_file = open("new_results/up_aug_dev.tsv", "w")

p_file = open('helper/permutation_vocab_src.txt')
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
        p_dic[key] = value_splits[:-1]
    return


def modify_output(out,pos,w_class,word,distribution):
    if distribution == 'primitive\n': 
        return re.sub(r'\b%s\b' % word , '?'+w_class, out)

    if w_class == 'n':
        new_string = re.sub(r'\b%s\b' % word , '?n', out)
        return new_string
    elif w_class == 'v':        
        split_word = '( x _ '+str(pos)+' ,'
        splits = out.split(' ')
        for i,_ in enumerate(splits):
            if ' '.join(splits[i+3:i+8]) == split_word:
                splits[i] = '?v'
        new_out = ' '.join(splits)
        return new_out
    else: 
        return out

def clean_utt(utt,p,flag):
    splits = utt.split(' ')
    permuted_utt = ''
    for word in splits:
        if '//' in word or (word == p and flag):
            # if '//' in word:
            #     word=word[:-3]
            permuted_utt += word + ' '
    return permuted_utt

def make_new_row(utt,output,word,w_class,pos,p):
        splits = utt.split(' ')
        splits[pos] = p+'//'+w_class
        permuted_utt = (' ').join(splits)
        #permuted_utt = clean_utt(permuted_utt,p,True)
        if output[-1]=='\n': output = output[:-1]
        final_row = ('\t').join((permuted_utt.strip(),output.strip()))
        return final_row

def write_permutated_rows(row,distribution):
    if distribution[-1]!='\n': distribution+='\n'
    final_row = '\t'.join((row.strip(),distribution.strip()))
    final_row = final_row.replace('\"','')
    out_file.write(final_row)
    out_file.write('\n')
    return

def make_output(words_to_be_permuted,utt,output,initial_row,distribution,words_to_change_out):
    
    for word,w_class,pos in words_to_change_out:
        output = modify_output(output,pos,w_class,word,distribution)

    return output

def main():
    for row in train_file:
        row = row.lower()
        utt, output, distribution = row.split('\t')
        formated_utt = clean_utt(utt,'',False) 
        count_perm = 0
        pos_word = 0
        initial_row = formated_utt+'\t'+output
        words_to_change_out = []
        for word_class in utt.split(' '):
            if '//' in word_class:  
                word, w_class = word_class.split("//")
                if w_class in ('n','v') and (word,w_class) in p_dic.keys() and (str(pos_word) in output or word in output): # word to be permuted
                    words_to_change_out.append((word,w_class,pos_word))
                    count_perm+=1
                pos_word+=1

        final_out = make_output([],formated_utt,output,initial_row,distribution,words_to_change_out)
        final_utt_out = '\t'.join((formated_utt,final_out))
        write_permutated_rows(final_utt_out,distribution)


make_p_dic()
main()
p_file.close()
train_file.close()
out_file.close()





