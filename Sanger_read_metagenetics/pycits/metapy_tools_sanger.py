#!/usr/bin/env python3
#
# metapy_tools.py
#
#
# (c) The James Hutton Institute 2016
# Author: Leighton Pritchard and Peter Thorpe

import os
import gzip
from .tools import convert_fq_to_fa
import sys
import subprocess
import numpy
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from collections import defaultdict
# for tests
# https://docs.scipy.org/doc/scipy/reference/
# tutorial/stats.html#t-test-and-ks-test
from scipy import stats
from scipy.stats import mannwhitneyu
import matplotlib
# this code added to prevent this error:
# self.tk = _tkinter.create(screenName, baseName,
# className, interactive, wantobjects, useTk, sync, use)
# _tkinter.TclError: no display name and
# no $DISPLAY environment variable
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab


# TODO: The PSL has the gzip library for this!!!!!
#       https://docs.python.org/3/library/gzip.html#examples-of-usage
def decompress(infile):
    """function to decompress gzipped reads"""
    cmd = ' '.join(["gunzip", infile])
    pipe = subprocess.run(cmd, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True)
    return os.path.splitext(infile)[0]


def convert_ab1_to_fq(in_file, out_file):
    """ Function to convert ab1 sanger seq file
    and convert to  fq
    requires biopython
    """
    SeqIO.convert(in_file, "abi", out_file, "fastq")


def sanger_extra_qc_trim(infname, outfname, NNN, logger):
    """splits the seq up based on N sequences. Then looks for the
    longest fragment. It takes this as the seq to use.
    Takes in a fasta and write the longest fragment back out
    to a new fasta.
    """
    NNN = int(NNN)
    bad = "N" * NNN  # this method now not used
    for seq_record in SeqIO.parse(infname, "fasta"):
        seq = str(seq_record.seq)
        try:
            # pick the longest chnuk without Ns"
            parts = seq.split("N")
            current_longest = 0
            for frags in parts:
                if len(frags) > current_longest:
                    current_longest = len(frags)
                    seq = frags
        except ValueError:
            # no NNN found
            logger.warning("NO NNNNs found")
        seq_record = SeqRecord(Seq(seq),
                     id=seq_record.id, name="",
                     description="")
        logger.info("length of longest sequence used = %d", len(seq))
        logger.info("sequence = %s\n%s", seq_record.id, seq)
        SeqIO.write(seq_record, outfname, "fasta")


def plot_trace(infname, outfile):
    """function to plot the sanger read trace
    https://github.com////biopython.github.io/blob/
    d6fc9bbb5fc9785c9dddaa0e6a938e7ba6471701/wiki/ABI_traces.md
    """
    record = SeqIO.read(infname, 'abi')
    record.annotations.keys()
    record.annotations['abif_raw'].keys()
    channels = ['DATA9', 'DATA10', 'DATA11', 'DATA12']
    trace = defaultdict(list)
    for ch in channels:
        trace[ch] = record.annotations['abif_raw'][ch]
    plt.plot(trace['DATA9'], color='blue')
    plt.plot(trace['DATA10'], color='red')
    plt.plot(trace['DATA11'], color='green')
    plt.plot(trace['DATA12'], color='yellow')
    plt.xlabel('Nucleotide', fontsize=12)
    plt.ylabel('Intensity', fontsize=12)
    plt.suptitle("Electropherogram for %s " % os.path.split(infname)[-1],
                 fontsize=16)
    plt.show()
    plt.savefig(outfile)
