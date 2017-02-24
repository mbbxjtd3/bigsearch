#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Profile the Matcher Module
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import time
import bigsearch
def profile_genome_search():
    """Profile the sort bucket step"""
    #genome_file  = 'Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz'
    start =  time.time()
    GENOME_PATH = "./bigsearch_dummy/data/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz"
    pattern = b'TGGATGTGAAATGAGTCAAG'
    maxmismatch = 3
    output_folder = "./bigsearch_dummy/results/"
    bigsearch.string_matching_fix_adjusted.KMP_genome_search(pattern, GENOME_PATH, maxmismatch, output_folder)
    print time.time()-start
    # TODO Your implementation

def main():
    profile_genome_search()

if __name__ == '__main__':
    main()
