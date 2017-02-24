#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the search module
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import pytest
import logging
import pysam

import sys
#from . import string_matching_fix_adjusted
import bigsearch


@pytest.mark.parametrize(("pattern", 'mismatches', 'exphits', 'GENOME_PATH', "output_folder"), [
    (b'TGGATGTGAAATGAGTCAAG', 3, 'bigsearch_dummy/data/TGGATGTGAAATGAGTCAAG-results.sam', 'bigsearch_dummy/data/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz', "bigsearch_dummy/results/"),
    (b'GGGTGGGGGGAGTTTGCTCC', 3, 'bigsearch_dummy/data/vegfa-site1-results.sam', 'bigsearch_dummy/data/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz', "./bigsearch_dummy/results/"),
])
def test_search(pattern, mismatches, exphits, GENOME_PATH, output_folder):

    try:
        assert os.path.exists(GENOME_PATH)
    except AssertionError:
        LOG.error('Human reference genome file not found. Download the human reference genome')
        raise

    # TODO
    #hits = np.loadtxt(exphits_path, skiprows = 2, usecols = (2,3,-5), dtype = str, delimiter = "\t")
    #print "I'm here"
    bigsearch.string_matching_fix_adjusted.KMP_genome_search(pattern, GENOME_PATH, mismatches, output_folder)
    hits_path = "{}_ALL_{}_k{}".format(output_folder, pattern, mismatches)	
	#hits_path = "./results/_ALL_GGGTGGGGGGAGTTTGCTCC_k3"

    result = set()
    expected_hits = set()


    with open(exphits, 'r') as exphits_:
        for exphit in exphits_.readlines()[2:]:
            li = exphit.split("\t")
            exphit_ = " ".join([li[2], li[3], li[-5]])
            expected_hits.add(exphit_)


    with open(hits_path, 'r') as hits_:
        for hit in hits_.readlines()[1:]:
            li_2 = hit.split("\t")
            hit_ = " ".join([li_2[0], li_2[1],li_2[2][:-1]])
            result.add(hit_)

    # TODO implement a more details comparison function if needed
    assert not len(expected_hits.difference(result))
