# GenoFLU

This tool uses BLAST to identify segments from a curated database. Pre-defined genotypes are cross-referenced with the top segment identifications, and a genotype is assigned. A cutoff of 2% difference from the closest curated sequence identifies new reassortment. New reassortment is reviewed using segment-based phylogenetic trees. If appropriate, new segment sequences will be added to the curated database and new genotype assignments updated.

# Installation

## GitHub install with necessary dependencies

Clone this repository
```
export PATH="<path to this clone repository>/GenoFLU/bin:$PATH"
```

While in conda base, make new environment from .yml file in dependencies folder
```
conda env create -f <path to this clone repository>/GenoFLU/dependencies/genoflu.yml
```

```
conda activate genoflu
```



## Not yet available.  Will be available when repo is made public.
```
conda install GenoFlU -c conda-forge -c bioconda
```

# Usage

FASTA file containing a segmented influenza genome, with each segment having its own individually named header.
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