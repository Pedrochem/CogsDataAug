import csv
import enum
import random
from re import L
from aug_train import final_clean_output

FILES = ['test','dev','gen']



def write_prev_rows():
    for file in FILES:
        inp_path = 'data/'+file+'.tsv'
        out_path = 'results/substructure/'+file+'.tsv'
        with open(inp_path, 'r') as inp_file:
            with open(out_path, 'w') as out_file:
                reader = csv.reader(inp_file, delimiter='\t')
                for row in reader:
                    inp,out,dist = row
                    write_new_row(out_file,inp,out,dist)



def write_new_row(out_file,inp,out,dist):
    inp_splits = inp.split(' ')
    final_inp = ''
    for i,word in enumerate(inp_splits):
        if '//' in word:
            if inp_splits[i-1] == 'NNP': word = word[:-1]+'P'
            final_inp += word.replace('//',' ') + ' '
    final_out = final_clean_output(out)
    final_row = '\t'.join((final_inp,final_out,dist))
    out_file.write(final_row+'\n')


if __name__ == '__main__':
    write_prev_rows()