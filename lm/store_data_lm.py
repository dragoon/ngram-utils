import subprocess

p = subprocess.Popen('hdfs dfs -cat /user/roman/ngrams_merged/*', shell=True, stdout=subprocess.PIPE)

VOCAB_FILE = open('1gms/vocab_cs', 'w')
N_2_FILE = open('2gms/2gm-0001', 'w')
N_3_FILE = open('3gms/3gm-0001', 'w')

for line in p.stdout:
    line_len = len(line.split('\t')[0].split())
    if line_len == 1:
        VOCAB_FILE.write(line)
    elif line_len == 2:
        N_2_FILE.write(line)
    elif line_len == 3:
        N_3_FILE.write(line)

VOCAB_FILE.close()
N_2_FILE.close()
N_3_FILE.close()