import numpy as np
cimport numpy as np
cimport cython
data_type = np.uint8
ctypedef np.uint8_t data_type_t

#----------------------------
#  Returns a vector containing the zero based index of 
#  the start of each match of the string K in S.
#  Matches may overlap
#----------------------------

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#cython: boundscheck=False, wraparound=False, nonecheck=False

cpdef KMP(data_type_t [:] K, data_type_t [:] S):

	cdef int K_size = K.shape[0]
	cdef int S_size = S.shape[0]
	cdef int i, pos

	cdef int sp = 0
	cdef int kp = 0

	cdef np.ndarray[np.int32_t, ndim=1] T = np.zeros(K_size + 1, dtype=np.int32) - 1
	cdef matches = []
	
	if K_size == 0:  
		matches.append(0)
		return matches		

	for i in range(1, K_size + 1): # smaller or equal to K_size
		pos = T[i - 1]

		while (pos <> -1 and K[pos] <> K[i - 1]): 
			pos = T[pos]

		T[i] = pos + 1


	while sp < S_size:

		while kp <> -1 and (kp == K_size or K[kp] <> S[sp]): 
			kp = T[kp]

		kp = kp + 1
		sp = sp + 1
		if kp == K_size: matches.append(sp - K_size)

	return np.array(matches,).astype(np.uint64)

