from utils.logger import Logger
from utils.files import split_file
from utils.hash import get_file_hash
from utils.sequence import get_seq_chunk

from socket import *


chunks = split_file('./files/A.file')
length = len(chunks)

print(get_seq_chunk('A', 7, 32, chunks[0][:10]))
print(length)
print(len(chunks[0]))
import queue


# print(len(my_chunks['front']))

print(get_file_hash('./files/B.file'))
print(get_file_hash('./result_files/1/resultB.file'))
# print(get_file_hash('./files/smallA.file'))
# print(get_file_hash('./result_files/2/resultA.file'))
# print(get_file_hash('./result_files/3/resultA.file'))
# print(get_file_hash('./result_files/4/resultA.file'))
# print('\n')
# print(get_file_hash('./files/smallB.file'))
# print(get_file_hash('./result_files/1/resultB.file'))
# print(get_file_hash('./result_files/3/resultB.file'))
# print(get_file_hash('./result_files/4/resultB.file'))
# print('\n')
# print(get_file_hash('./files/smallC.file'))
# print(get_file_hash('./result_files/1/resultC.file'))
# print(get_file_hash('./result_files/2/resultC.file'))
# print(get_file_hash('./result_files/4/resultC.file'))
# print('\n')
# print(get_file_hash('./files/smallD.file'))
# print(get_file_hash('./result_files/1/resultD.file'))
# print(get_file_hash('./result_files/2/resultD.file'))
# print(get_file_hash('./result_files/3/resultD.file'))

# print(length)

