
from aug_train import *
import ast
from collections import defaultdict
from dis import dis
import re
import random
from regex import W
import os
import spacy
from spacy.lemmatizer import Lemmatizer, ADJ, NOUN, VERB
nlp = spacy.load('en')

lemmatizer = nlp.vocab.morphology.lemmatizer


max_count = 100
CONT = 0
differents_words = set()
NOUN = 'noun'
MAX_PERMS = 3

train_file = open("data/train_pos.tsv")
original_file = open('data/train.tsv')

out_file = open("tests.tsv", "w")



# todo: lemma / proper nouns

def generate_output(inp,out):
    new_out = out
    inp_splits =  inp.split(' ')
    if out[0] == '\"': out = out[1:]
    if out[-1] == '\"': out = out[:-1]
    splits =  out.split(' ')
    
    if 'LAMBDA' in out: return out
    for i,split in enumerate(splits): 
        v_flag = False
        if ''.join(splits[i:i+4]) == 'N(x_':
            pos = int(splits[i+4])      
        elif split == 'N' and splits[i+2] == 'nmod':
            pos = int(splits[i+8])
        elif split == 'V':
            pos = int(splits[i+6])
            v_flag=True
        elif split == 'P':
            pos = int(splits[i+2])
            splits[i+1] = ''
            splits[i+2] = ''
        else: continue
        word = inp_splits[int(pos/2)]
        word=word[:-3]
        if v_flag:
            word = lemmatizer(word, 'VERB')[0]
        splits[i] = word

    new_out = ' '.join(splits)
    new_out = new_out.replace('  ','')
    return new_out

def gn_write_permutated_rows(original_row,permuted_rows,distribution,row_number):
    global CONT
    # if CONT > max_count: return
    # n = random.randint(0,100)
    # if n > 5: return


    or_utt, or_output,or_distribution = original_row.split('\t')
    
    if distribution[-1]!='\n': distribution+='\n'
    out_file.write('Cont: '+str(CONT)+'\n')
    #out_file.write('Row Number: '+str(row_number)+'\n')
    out_file.write('Original input: '+or_utt+'\n')
    out_file.write('Original output: '+or_output+'\n')

    first_row = permuted_rows[0]
    utt, out = first_row.split('\t')
    deterministic_out = generate_output(utt,out)
    deterministic_out = deterministic_out.replace('  ',' ')

    # print('ut:',utt)
    # print('out:',out)
    
    out_file.write('Deterministic output: '+deterministic_out+'\n')
    changed_out = ''
    for word in deterministic_out.split(' '):
        if word.isdigit():
            changed_out+=str(int(int(word)/2)) + " "
        else: changed_out+=word + " "
    outputs_match = changed_out[:-1].lower() == or_output.lower()

    if not outputs_match:
        for word in deterministic_out.split(' '):
            if word not in or_output and not word.isdigit():
                differents_words.add(word)

    out_file.write('Outputs match: '+str(outputs_match)+'\n')
    out_file.write('Original distribution: '+or_distribution+'\n')

    for row in permuted_rows:
        final_row = '\t'.join((row.strip(),distribution.strip()))
        final_row = final_row.replace('\"','')
        out_file.write(final_row)
        out_file.write('\n')
    out_file.write('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n')
    CONT += 1
    return

def main():
    p_dic = make_p_dic()
    CONT = 0
    row_number=1
    for row in train_file:
        original_row = original_file.readline()
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
        gn_write_permutated_rows(original_row,permuted_rows,distribution,row_number)
        row_number+=1

main()

train_file.close()
out_file.close()
original_file.close()
print('Differents words: ',differents_words)



