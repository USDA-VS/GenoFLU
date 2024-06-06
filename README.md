# GenoFLU

This tool uses BLAST to identify segments from a curated database. Pre-defined genotypes are cross-referenced with the top segment identifications, and a genotype is assigned. A cutoff of 2% difference from the closest curated sequence identifies new reassortment. New reassortment is reviewed using segment-based phylogenetic trees. If appropriate, new segment sequences will be added to the curated database and new genotype assignments updated.

# Installation

```
conda create -c conda-forge -c bioconda -n genoflu genoflu
```

# Usage

FASTA file containing a single segmented influenza genome, with each segment having its own individually named header.

```
genoflu.py -f <*.fasta>
```

# Output

Genotype summary as Excel and tab delimited text file.

# Test

Test genome available at test/test-genome-A1.fasta

```
genoflu.py -f test-genome-A1.fasta
```

test-genome-A1 Genotype --> A1: PB2:ea1, PB1:ea1, PA:ea1, HA:ea1, NP:ea1, NA:ea1, MP:ea1, NS:ea1
