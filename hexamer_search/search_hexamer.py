from Bio import Seq
import pysam
import unittest


"""This script tries to find a hexamer in the reference genome upstream to a given cleavage site"""

# numbers indicate their strengths, 1 is the strongest
CANDIDATE_HEXAMERS = [
    ('AATAAA', 1),
    ('ATTAAA', 2),
    ('AGTAAA', 3),
    ('TATAAA', 4),
    ('CATAAA', 5),
    ('GATAAA', 6),
    ('AATATA', 7),
    ('AATACA', 8),
    ('AATAGA', 9),
    ('AAAAAG', 10),
    ('ACTAAA', 11),
    ('AAGAAA', 12),
    ('AATGAA', 13),
    ('TTTAAA', 14),
    ('AAAACA', 15),
    ('GGGGCT', 16)
]


def fetch_seq(refseq, chrom, beg, end):
    """.fetch seems to be (beg, end]"""
    return refseq.fetch(chrom, beg, end)


def gen_coords(clv, strand, window=50):
    """
    generate the coordinates to be used for fetching sequence
    :param clv: 0-based
    """
    if strand == '+':
        beg = clv - window + 1
        # as clv is the last based of 3'UTR and 0-based, so it should be
        # included in search
        end = clv + 1
    elif strand == '-':
        beg = clv
        end = clv + window
    else:
        raise ValueError('unknown strand: {0}'.format(strand))
    return beg, end


def plus_search(seq, right_coord):
    """right_coord should be clv_coord - 1 """
    seq = seq.upper()
    left_coord = right_coord - len(seq) + 1
    for (hmr, hid) in CANDIDATE_HEXAMERS:
        idx = seq.rfind(hmr)
        if idx > -1:
            return hmr, hid, idx + left_coord


def minus_search(seq, left_coord):
    """left_coord should be clv_coord + 1"""
    seq = Seq.Seq(seq).reverse_complement().upper()
    for (hmr, hid) in CANDIDATE_HEXAMERS:
        idx = seq.rfind(hmr)
        if idx > -1:
            return hmr, hid, len(seq) - idx + left_coord - 1


def search_hexamer(region, strand, beg, end):
    """search for hexamer in the region"""
    if strand == '+':
        return plus_search(region, end)
    elif strand == '-':
        return minus_search(region, beg)
    else:
        raise ValueError('unknown strand: {0}'.format(strand))


def search(refseq, chrom, clv, strand, window=50):
    """
    :param refseq: an object returned by pysam.FastaFile, see TestSearch for
    its usage
    :param clv: 0-based
    """
    beg, end = gen_coords(clv, strand, window)
    seq = fetch_seq(refseq, chrom, beg, end)
    # -1 as it's 0-based
    res = search_hexamer(seq, strand, beg, end - 1)
    return res