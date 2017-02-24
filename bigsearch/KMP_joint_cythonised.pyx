import numpy as np
cimport numpy as np
cimport cython

data_type = np.uint8
data_type_2 = np.uint64
ctypedef np.uint8_t data_type_t
ctypedef np.uint64_t data_type_t_2

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#cython: boundscheck=False, wraparound=False, nonecheck=False

cpdef KMP_join(data_type_t_2 [:] indexes_of_exc_matches_of_subpart, data_type_t [:] reference_chr, data_type_t [:] pattern, data_type_t [:] subpattern, int k, int ind_pattern):

	cdef int exc_match_pos, i, n_mismatches
	cdef int offset = ind_pattern*len(subpattern)

	locations_k_mismatches = []

	for exc_match_pos in indexes_of_exc_matches_of_subpart:

		if exc_match_pos - offset < 0: continue #current index is outside (left) reference ?
		if exc_match_pos + len(pattern) - offset > len(reference_chr): continue #current index is outside (right) reference ?
		n_mismatches = 0
		for i in range(0, offset) + range(offset + len(subpattern), len(pattern)):
			if reference_chr[exc_match_pos - offset + i] <> pattern[i]:
				n_mismatches = n_mismatches + 1
				if n_mismatches > k: break

		if n_mismatches <= k:
			locations_k_mismatches.append(exc_match_pos-offset)

	return np.unique(locations_k_mismatches).astype(data_type_2)

