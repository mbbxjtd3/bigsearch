The installer requires numpy, cython.
The package requires pysam

The code was written in Python 2.7.6 and tested on linux2 -- Python 2.7.6, pytest-3.0.6, py-1.4.32, pluggy-0.4.0

It may not be compatible with python 3.

TO INSTALL RUN
sudo python setup.py install

The code has been added to /usr/local/lib/python2.7/dist-packages/bigsearch and can be imported into python from any location on your disk.

in order to test the package:

1) place:

Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
TGGATGTGAAATGAGTCAAG-results.sam
vegfa-site1-results.sam
to ./big_search_setup/bigsearch/data/ where ./ is your home directory

2) rename the folder ./big_search_setup/bigsearch/ to ./big_search_setup/bigsearch_dummy/ 
otherwise import bigsearch in python would import local files in ./big_search_setup/bigsearch/ 
to load the bigsearch package not the ones in /usr/local/lib/python2.7/dist-packages/bigsearch

3) copy ./big_search_setup/bigsearch/test_search.py and ./big_search_setup/bigsearch/profile_search.py to ./big_search_setup/

4) go to:
./big_search_setup/

run
pytest test_search.py
python profile_search.py

In order to run the local version no the one you have in /usr/local/lib/python2.7/dist-packages/bigsearch
you still need to compile *.pyx files.

