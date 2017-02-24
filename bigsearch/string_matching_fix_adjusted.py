import numpy as np
import multiprocessing
from multiprocessing import Pool
import os
import time
import re
from . import KMP_cythonised
from . import KMP_joint_cythonised
import pysam
from sys import argv
import gzip

import sys


import itertools
from sys import platform
from . import headers
#sys.path.insert(0, './tests/data/')

#@profile
#from guppy import hpy 

#h = hpy() 

#print h.heap()

#--------------
#see how to force a function of more that two variables to unpickle http://blog.wisatbff.com/2016/03/22/python-multiprocessing.html
class WithExtraArgs(object):
	def __init__(self, func, *args):
		self.func = func
		self.args = args
	def __call__(self, idx):
		return self.func(idx, *self.args)

	#Sequencially opens each of the local assemblies to do the search for matches. 

def search_in_chrom(pattern__, subpatterns__, reference_chr__, k):

	start = time.time()
	locations = []
	

	for ind_pattern, subpattern_ in enumerate(subpatterns__):
		#Use an exact matching algorithm (I chose KMP) to find exact matches for the current subpattern (one of p1, p2, ..., pk+1 subpatterns of the pattern ps). 
		indexes_of_exc_match_matches_of_subpart = KMP_cythonised.KMP(subpattern_, reference_chr__)


		#-----------
		#Look for a longer approximate match in the vicinity of the exact match
		locations_k_mismatches_of_part_of_subpart = KMP_joint_cythonised.KMP_join(indexes_of_exc_match_matches_of_subpart, reference_chr__, pattern__, subpattern_, k, ind_pattern)
			
		locations = np.unique(np.r_[locations, locations_k_mismatches_of_part_of_subpart]).astype(int)

	#print "Time elapsed ", time.time()-start
	#print "Finished\n"
	return locations


def worker2(idx, two_pattern__, two_subpatterns__, reference_chr__, k): 
	return (idx, search_in_chrom(two_pattern__[idx], two_subpatterns__[idx], reference_chr__, k))

def worker2_parallel(idx, jobs_id, two_pattern__, two_subpatterns__, reference_chr__, k):

	start = time.time()
	idx_pattern = jobs_id[idx][0]
	idx_subpattern = jobs_id[idx][1]

	pattern__, subpatterns__ = two_pattern__[idx_pattern], two_subpatterns__[idx_pattern]

	subpattern_ = subpatterns__[idx_subpattern]
	
	exc_matches_of_subpart = KMP_cythonised.KMP(subpattern_, reference_chr__)

	locations_k_mismatches_of_part_of_subpart = KMP_joint_cythonised.KMP_join(exc_matches_of_subpart, reference_chr__, pattern__, subpattern_, k, idx_subpattern)

	return (jobs_id[idx], locations_k_mismatches_of_part_of_subpart)

def split_pattern(pattern__, k_):
	
	subpaterns__ = np.array_split(pattern__, k_+1)

	return subpaterns__


def assertions_decompressions_headers_folder_creations(assembly, output_folder):

	if assembly[-2:] == "gz": assembly = assembly[:-3]

	if not os.path.isfile(assembly): # if assembly isn't already decompressed.
		#print "sorry but due to Pysam incompatibility with ".gz" files I'm decompressing your fasta"
		os.popen("gunzip -k {}.gz".format(assembly), "r").readline()

	#Creates a FASTA file specific folder for storing the results of running the code on it. 
	#output_folder = "./results/"
	if not os.path.exists(output_folder): os.makedirs(output_folder)


	name_of_header_file = assembly + ".headers.txt"
	file_with_headers_exists = os.path.exists(name_of_header_file)

	if platform in ["linux", "linux2", "darwin"] and not(file_with_headers_exists):
		os.popen('grep "^>" {} > {}'.format(assembly, name_of_header_file), "r").readline()
		# linux or OS X
	elif platform == "win32":
		
		headers.find_headers(assembly, ">", name_of_header_file) # I don't have means to test Windows' <findstr pattern  filename>


	Fasta_chrom_header_title = [head[1:] for head in np.loadtxt(name_of_header_file,dtype = str, usecols = (0,))]

	return Fasta_chrom_header_title, assembly
	#-----------

def create_anty_pattern(pattern_):
	#pattern = "CTTGACTCATTTCACATCCA"
	#apattern ="TGGATGTGAAATGAGTCAAG"

	#In [19]: np.fromstring("ATCG", np.uint8)
	#Out[19]: array([65, 84, 67, 71], dtype=uint8)

	anty_pattern = np.ones(len(pattern_), dtype="|S1")
	anty_pattern[np.where(pattern_ == 65)[0]] = "T" # A --> T
	anty_pattern[np.where(pattern_ == 84)[0]] = "A" # T --> A
	anty_pattern[np.where(pattern_ == 67)[0]] = "G" # C --> G
	anty_pattern[np.where(pattern_ == 71)[0]] = "C" # G --> C
	anty_pattern = "".join(anty_pattern[::-1]) # I want antypattern to be a string just so that I can use it as the header in the output file.
	# used np.where() instead of arrays of bools because: console says that using a boolean instead of an integer will result in an error in the future
	return anty_pattern

def KMP_genome_search(pattern, assembly, k, output_folder):

	""" Use the pigeonhole principle together with KMP to find approximate matches with up to a specified number of mismatches. See: https://courses.cs.washington.edu/courses/cse427/16au/slides/approximate_matching.pdf """


	#----------------
	start_t = time.time()

	Fasta_chrom_header_title, assembly = assertions_decompressions_headers_folder_creations(assembly, output_folder)

	fastafile = pysam.Fastafile(assembly)

	#changes encoding of the pattern and the reference strings
	pattern_ = np.fromstring(pattern, np.uint8)			
	#-----------

	anty_pattern = create_anty_pattern(pattern_)

	anty_pattern_ = np.fromstring(anty_pattern, np.uint8)

	subpatterns_ = split_pattern(pattern_, k) # creates subpatterns of the user specified pattern. The subpatterns are used to search for exact matches (see pigeonhole principle)

	anty_subpatterns_ = split_pattern(anty_pattern_, k)

	locations = {} # creates dictionary to store outputs of the code.

	#chroms = np.r_[np.arange(1,23).astype(str), np.array(["X","Y"])].tolist()
	chroms = Fasta_chrom_header_title
	

	for chrom in chroms: locations[chrom] = {}# initialises cells for locations of the matches in each local chromosomal/non-chromosomal assembly 


	#--------------


	pool = Pool(2) # change that to 8 if you want to use the multi-multiparallel version
	for chrom in chroms:

		#print  "Start: matching {} in chrom {} with k = {} mismaches. ".format(pattern, chrom, k)
		reference_chr_ = np.fromstring(fastafile.fetch(chrom), np.uint8)

		#------------------------------------------------
		#uncomment to run the script with one core

		#locations[chrom][pattern] = search_in_chrom(pattern_, subpatterns_, reference_chr_, k) # 

		#locations[chrom][anty_pattern] = search_in_chrom(anty_pattern_, anty_subpatterns_, reference_chr_, k)

		#----------------------------------------------
		#uses two cores. One per strand
		chrom_results_two_strands = pool.map(WithExtraArgs(worker2, (pattern_, anty_pattern_), (subpatterns_, anty_subpatterns_), reference_chr_, k), range(2))
		for idx, strand_res in chrom_results_two_strands: locations[chrom][(pattern, anty_pattern)[idx]] = strand_res

		# ------------------------------------
		#you can uncomment the lines if you want the code to be run on 8 processors 2 strands, 4 subpatterns at once.

		#jobs_id = [[i, j] for i in range(2) for j in range(len(subpatterns_))]
		#chrom_results_two_strands = list(pool.imap_unordered(WithExtraArgs(worker2_parallel, jobs_id, (pattern_, anty_pattern_), (subpatterns_, anty_subpatterns_), reference_chr_, k), range(2*len(subpatterns_))))

		#locations[chrom][pattern] = np.unique(list(itertools.chain.from_iterable([res for job_id, res in chrom_results_two_strands if job_id[0] == 0])))
		#locations[chrom][anty_pattern] = np.unique(list(itertools.chain.from_iterable([res for job_id, res in chrom_results_two_strands if job_id[0] == 1])))
			# ------------------------------------

	#------------ 
	#concatenate outputs
	total_output_2 = np.array([], dtype = "|S21").reshape(0,3)
	for patt in [pattern, anty_pattern]:

		indexes = np.cumsum([0] + [len(locations[chrom_][patt]) for chrom_ in chroms])
		total_output = np.zeros((indexes[-1], 3), dtype = "|S21")
		#save output
		for start, end, chrom__ in zip(indexes[:-1], indexes[1:], np.array(chroms)):
	
			total_output[start:end, 0] = chrom__
			total_output[start:end, 1] = (locations[chrom__][patt] + 1).astype("|S21")# + 1 because by convention bases in genome are 0 indexed
			total_output[start:end, 2] = np.array([patt], dtype = "|S21")


		total_output_2 = np.r_[total_output_2, total_output]

	total_output_2 = total_output_2[np.lexsort((total_output_2[:,1].astype(int), total_output_2[:,0]))]

	output_name_ = "{0}_{1}_{2}_k{3}".format(output_folder, "ALL", pattern, k)
	header_ = "Starting positions of matches of {0} in {1} with {2} mismatches".format(pattern, output_folder, k)

	np.savetxt(output_name_, total_output_2, fmt = "%s", header = header_, delimiter = "\t")
	#------------

	#print "RESULTS in {} !".format(output_name_)
	#print time.time()-start_t

#def main():
#    KMP_genome_search(pattern, assembly, k)

#if __name__ == '__main__':

#	#----------------
#	#loads parameters
#	#argv = ["script.py","TGGATGTGAAATGAGTCAAG", "./tests/data/Homo_sapiens.GRCh38.dna.primary_assembly.fa", 3]
#	assert (len(argv) == 4), "The function needs pattern, reference (i.e. FASTA), and number of mismatches. Please, rerun when you have those."
	
#	pattern, assembly, k = argv[1], argv[2], int(argv[3])
#	
#	main()



