
import ast
from collections import defaultdict
from dis import dis
import re
from aug_train import *


NOUN = 'noun'
MAX_PERMS = 3



def make_output(output,distribution,words_to_change_out):
    for word,w_class,pos in words_to_change_out:
        output = modify_output(output,pos,w_class,word,distribution)
    output = final_clean_output(output)
    return output

def write_permutated_rows(row,distribution):
    if distribution[-1]!='\n': distribution+='\n'

    inp,out  = row.split('\t')
    inp = inp.replace('//',' ')
    row = '\t'.join((inp,out))
    final_row = '\t'.join((row.strip(),distribution.strip()))
    final_row = final_row.replace('\"','')
    out_file.write(final_row)
    out_file.write('\n')

def main():
    p_dic = make_p_dic()
    for row in train_file:
        utt, output, distribution = row.split('\t')
        formated_utt = clean_utt(utt,'',False) 
        count_perm = 0
        pos_word = 0
        initial_row = formated_utt+'\t'+output
        words_to_change_out = []
        for word_class in formated_utt.split(' '):
            if '//' in word_class:  
                word, w_class = word_class.split("//")
                aux = w_class
                if w_class == 'P': aux = 'N'
                if  w_class in ('N','V','P') and (word,aux) in p_dic.keys()  and (str(pos_word) in output or (word in output and w_class == 'P')):
                    words_to_change_out.append((word,w_class,pos_word))
                    count_perm+=1
                pos_word+=1

        final_out = make_output(output,distribution,words_to_change_out)
        formated_utt = formated_utt.replace('//',' ')
        final_utt_out = '\t'.join((formated_utt,final_out))
        write_permutated_rows(final_utt_out,distribution)


train_file = open("data/test.tsv")

out_file = open("results/aug/aug_test.tsv", "w")

p_file = open('helper/permutation_vocab_src.txt')


files = ['test','dev','gen']
for f in files:
    train_file = open("data/"+f+".tsv")
    out_file = open("results/aug/aug_"+f+".tsv", "w")
    main()
    train_file.close()
    out_file.close()






