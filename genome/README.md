# Reference Genome

The reference genome files are not included in this repository because they exceed GitHub's file size limit.

The pipeline requires the following files:

| File | Download |
|------|----------|
| **GRCh38.primary_assembly.genome.fa** | https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_49/GRCh38.primary_assembly.genome.fa.gz |
| **gencode.v49.primary_assembly.annotation.gtf** | https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_49/gencode.v49.primary_assembly.annotation.gtf.gz |

Both files originate from **GENCODE Human Release 49**:

https://www.gencodegenes.org/human/release_49.html

After downloading and decompressing the files, place them in the following directory:

```
genome/
├── GRCh38.primary_assembly.genome.fa
└── gencode.v49.primary_assembly.annotation.gtf
```

The STAR genome index is not included in this repository and should be generated locally using the downloaded reference genome and annotation files.
