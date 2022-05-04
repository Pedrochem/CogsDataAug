
import ast
from collections import defaultdict
from dis import dis
import re
from aug_train import *


NOUN = 'noun'
MAX_PERMS = 3

train_file = open("data/train_pos.tsv")
out_file = open("results/perms/noun_train.tsv", "w")

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
                    if count_perm <3 and w_class != 'V':
                        words_to_be_permuted.append((word,w_class,pos_word))
                        count_perm+=1
                pos_word+=1

        permuted_rows = make_permutations(words_to_be_permuted,formated_utt,output,initial_row,distribution,words_to_change_out,p_dic)
        write_permutated_rows(permuted_rows,distribution)


main()
train_file.close()
out_file.close()





