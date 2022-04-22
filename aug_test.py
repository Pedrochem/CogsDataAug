
import ast
from collections import defaultdict
from dis import dis
from posixpath import split


NOUN = 'noun'
MAX_PERMS = 3

train_file = open("data/train_pos.tsv")
# train_file = open("data/test_train.tsv")

out_file = open("output2.tsv", "w")

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
        p_dic[key] = value_splits
    return


def get_fols(out):
    splits = out.split(' ')
    fol1 = set()
    fol2 = set()
    for i,split in enumerate(splits):
        if len(splits) >= i+2:
            if split=='.':
                fol1.add(splits[i+1])
                fol2.add(splits[i+2])
                
    return fol1,fol2


def clean_utt(utt,p,flag):
    splits = utt.split(' ')
    permuted_utt = ''
    for i,word in enumerate(splits):
        if '//' in word or (word == p and flag):
            if splits[i-1] == 'nnp': word = word[:-1]+'p'
            permuted_utt += word + ' '
    return permuted_utt

def get_fol_words(out,pos):
    pre1 = set()
    pre2 = set()
    split_word = '( x _ '+str(pos)+' ,'
    splits = out.split(' ')
    for i,_ in enumerate(splits):
        if ' '.join(splits[i:i+5]) == split_word:
            pre1.add(splits[i-1])
            if splits[i-3] == '.':
                print('deu ruim')
    return pre1


def main():
    s1 = set()
    s2 = set()
    for row in train_file:       
        row = row.lower()
        pos=0
        utt, output, distribution = row.split('\t')
        formated_utt = clean_utt(utt,'',False) 
        for word_class in formated_utt.split(' '):
            if '//' in word_class:  
                word, w_class = word_class.split("//")
                if  w_class in ('v'):
                    res = get_fol_words(output,pos)
                    for e in res:
                        s1.add(e)
                pos+=1

    print(s1)
    # print(s2)
make_p_dic()
main()

p_file.close()
train_file.close()
out_file.close()





