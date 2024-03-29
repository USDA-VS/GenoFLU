# GenoFLU

This tool uses BLAST to identify segments from a curated database. Pre-defined genotypes are cross-referenced with the top segment identifications, and a genotype is assigned. A cutoff of 2% difference from the closest curated sequence identifies new reassortment. New reassortment is reviewed using segment-based phylogenetic trees. If appropriate, new segment sequences will be added to the curated database and new genotype assignments updated.

# Installation

```
conda install GenoFlU -c conda-forge -c bioconda
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

# Database Segment Comparison (Internal use only)

When new segs are added to the database, we may be asked to run a similarity comparison of the reference segs. This is done using the following command:

```
sbatch ~/git/gitlab/genoflu/internal/db_compare.sh
```

This will output an excel file with percent identity of each segment to each other segment.

# Database Location

```
/project/diagnostic_virology_laboratory/MKillian/Analysis/results/influenza/HPAI/hpai_genotyping_blast
```

If you need to update the database, run this block of code:

```
rsync -avu --delete --progress /project/diagnostic_virology_laboratory/MKillian/Analysis/results/influenza/HPAI/hpai_genotyping_blast/*.fasta ${HOME}/git/gitlab/genoflu/dependencies/fastas/
cp -v -u /project/diagnostic_virology_laboratory/MKillian/Analysis/results/influenza/HPAI/hpai_genotyping_blast/genotype_key.xlsx ${HOME}/git/gitlab/genoflu/dependencies
```
