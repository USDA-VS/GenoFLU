#!/usr/bin/env python

__version__ = "1.03"

import os
import sys
import re
import shutil
import glob
import argparse
import textwrap
import pandas as pd
import operator
import time
from collections import defaultdict
from collections import Counter
from datetime import datetime

from Bio import SeqIO


class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE='\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class Excel_Stats:

    def __init__(self, sample_name):
        self.sample_name = sample_name
        date_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.excel_filename = f'{sample_name}_{date_stamp}_stats.xlsx'
        excel_dict = {}
        excel_dict['sample'] = sample_name
        excel_dict['date'] = date_stamp
        self.excel_dict = excel_dict 

    def post_excel(self,):
        df = pd.DataFrame.from_dict(self.excel_dict, orient='index').T
        df = df.set_index('sample')
        df.to_excel(self.excel_filename)

class Blast_Fasta(bcolors):
    ''' 
    '''
    def __init__(self, FASTA=None, format="6 qseqid sacc bitscore pident stitle", num_alignment=3, blast_db="nt", num_threads=8):
        FASTA_abs_path = FASTA
        FASTA_name = os.path.basename(FASTA_abs_path)
        sample_name = re.sub('[_.].*', '', FASTA_name)
        self.sample_name = sample_name
        self.blast_db = blast_db
        blastout_file = f'{sample_name}_blast_out.txt'
        os.system(f'blastn -query {FASTA_abs_path} -db {blast_db} -word_size 11 -out {blastout_file} -outfmt "{format}" -num_alignments {num_alignment} -num_threads={num_threads} 2> /dev/null')
        self.blastout_file = blastout_file

        blast_dict = defaultdict(list)
        with open(blastout_file, 'r') as blast_file:
            for line in blast_file:
                line = line.rstrip()
                line = line.split('\t')
                blast_dict.setdefault(line[0], []).append(line[1:])
        
        top_hit_acc=[]
        descriptions={}
        with open(f'{sample_name}_blast_all.txt', 'w') as all_blast:
            for item, value in blast_dict.items():
                print(f'{item}', file=all_blast)
                for val in value:
                    print(f'\t{val[0]} {val[1]} {val[2]} {val[3]}', file=all_blast)
                print(f'', file=all_blast)

        acc_frequency = []
        top_hit_acc_norm = []
        norm_dict = {}
        descriptions = {}
        for header, description in blast_dict.items():
            #Get accession frequencies
            acc_frequency.append(description[0][0]) #top hit, 1st item in hit
            acc_count = Counter()
            for acc in acc_frequency:
                acc_count[acc] += 1
            #Get FASTA sizes per accessions
            fasta_dict = SeqIO.to_dict(SeqIO.parse(FASTA, "fasta"))
            seq_length = len(fasta_dict[header])
            top_hit_acc_norm.append((description[0][0], seq_length))
            acc_size_collection = defaultdict(list)
            for acc, size in top_hit_acc_norm: #collect sizes by accession
                acc_size_collection[acc].append(size)
            for acc, sizes in acc_size_collection.items(): #add sizes by accession
                norm_dict[acc] = sum(sizes)
            #Get accession descriptions
            descriptions[description[0][0]] = description[0][3]
        sorted_norm_dict = {k: v for k, v in sorted(norm_dict.items(), key=lambda item: item[1])}

        for value in blast_dict.values():
            top_hit_acc.append(value[0][0]) #top hit, 1st item in hit
            descriptions[value[0][0]] = value[0]
        cnt = Counter()
        for acc in top_hit_acc:
            cnt[acc] += 1

        summary_dict={}
        summary_list=[] # list of tuples (nt rep, contigs, description list)
        with open(f'{sample_name}_blast_summary.txt', 'w') as summary_blast:
            for acc, count in sorted_norm_dict.items():
                summary_dict[f'{acc} {descriptions[acc]}'] = f'{count}'
                summary_list.append((f'{count:,}', f'{acc_count[acc]:,}', descriptions[acc]))
                print(f'{count:,}\t{acc_count[acc]:,}\t{acc} {descriptions[acc]}', file=summary_blast)
                # print(f'{bcolors.YELLOW}{count:,}{bcolors.ENDC} nt\t{bcolors.RED}{acc_count[acc]:,}{bcolors.ENDC} contigs\t{bcolors.BLUE}{int(round(count/acc_count[acc])):,}{bcolors.ENDC} nt mean length')
        # Get highest hit on most nucleotide identifing as a single accession
        try:
            highest_hit_accession = max(sorted_norm_dict.items(), key=operator.itemgetter(1))[0]
            self.highest_hit_description_list = descriptions[highest_hit_accession]
            self.summary_dict = summary_dict
            self.summary_list = summary_list
        except ValueError:
            highest_hit_accession = "BLAST Failed - Assembly"

class GenoFLU():
    ''' 
    '''
    def __init__(self, FASTA=None, FASTA_dir=None, cross_reference=None, sample_name=None, debug=False):
        '''
        Use file_setup to get the routine done
        '''
        self.debug = debug
        self.FASTA_abs_path = FASTA
        FASTA_name = os.path.basename(self.FASTA_abs_path)
        with open(FASTA_name, 'r') as f:
            fastas_in_file = 0
            for line in f:
                if line.startswith('>'):
                    fastas_in_file += 1
        self.fastas_in_file = fastas_in_file
        if sample_name:
            sample_name = sample_name
        else:
            sample_name = re.sub('[_.].*', '', FASTA_name)
        self.sample_name = sample_name

        if FASTA_dir:
            self.FASTA_dir = FASTA_dir
            self.cross_reference = cross_reference
        else:
            script_path = os.path.dirname(os.path.realpath(__file__))
            self.FASTA_dir = os.path.abspath(f'{script_path}/../dependencies/fastas')
            self.cross_reference = os.path.abspath(f'{script_path}/../dependencies/genotype_key.xlsx')

    def get_metadata(self,):
        import dvl_metadata_capture
        sample_name = self.sample_name
        root_name = re.sub('-submissionfile', '', sample_name)
        metadata_dict = dvl_metadata_capture.get_metadata(root_name)
        if metadata_dict:
            pass
        else: # will be None if sample isn't found therefore will need to instantiate dictionary
            metadata_dict={}
        try:
            metadata_dict["Collection Year"] = int(metadata_dict["Collection Year"])
        except (TypeError, ValueError, KeyError) as e:
            metadata_dict["Collection Year"] = "n/a"
        try:
            metadata_format_string = f'A/{metadata_dict["species"]}/{metadata_dict["state"]}/{root_name}/{metadata_dict["Collection Year"]}'
        except (TypeError, ValueError, KeyError) as e:
            metadata_format_string = 'No Metadata'
        self.metadata_dict = metadata_dict
        self.metadata_format_string = metadata_format_string

    def blast_hpai_genomes(self,):
        os.system(f'cat {self.FASTA_dir}/*.fasta | makeblastdb -dbtype nucl -out hpai_geno_db -title hpai_geno_db > /dev/null 2>&1')
        blast_hpai_genotyping = Blast_Fasta(FASTA=self.FASTA_abs_path, format="6 qseqid qseq length nident pident mismatch evalue bitscore sacc stitle", num_alignment=1, blast_db='hpai_geno_db', num_threads=2)

        blast_genotyping_hpia={}
        fasta_name=""
        with open(blast_hpai_genotyping.blastout_file, 'r') as blastout:
            for line in blastout:
                ind_blast_result = line.rstrip().split('\t')
                '''
                BLAST will split identification, and make multiple identifications for single FASTA (even if num_alignment=1), if assembly is not congruent.  Only the top hit is needed for each FASTA if multiple identification are returned.  Without if statement below the lowest bit score would return for an individual FASTA.  Here the highest bit score identification is applied (first blast item).  This also produces a blast_result dictionary with only one blast identification per FASTA assembled.
                '''
                if fasta_name != ind_blast_result[0]:
                    fasta_name = ind_blast_result[0]
                    each_blast={}
                    each_blast['blast_length'] = ind_blast_result[2]
                    each_blast['nident'] = ind_blast_result[3]
                    each_blast['pident'] = ind_blast_result[4]
                    each_blast['mismatch'] = ind_blast_result[5]
                    each_blast['evalue'] = ind_blast_result[6]
                    each_blast['bitscore'] = ind_blast_result[7]
                    each_blast['sacc'] = ind_blast_result[8]
                    each_blast['stitle'] = ind_blast_result[9]
                    each_blast['gene'] = ind_blast_result[-1].split()[2]
                    blast_genotyping_hpia[ind_blast_result[-1].split()[2]] = each_blast #just the gene as key
                    self.irma_failed = False
        list_order = ['PB2', 'PB1', 'PA', 'HA', 'NP', 'NA', 'MP', 'NS', 'SARS-CoV-2']
        remove_items = list(set(list_order) - set(blast_genotyping_hpia.keys()))
        for item in remove_items:
            list_order.remove(item)
        blast_genotyping_hpia_temp={}
        for item in list_order:
            blast_genotyping_hpia_temp[item] = blast_genotyping_hpia[item] 
        self.blast_results = blast_genotyping_hpia_temp
        self.blast_genotyping_hpia = blast_genotyping_hpia
        blast_dir = f'{self.sample_name}_blast_hpia_genotyping_dir'
        os.makedirs(blast_dir)
        files_grab = []
        for files in ('*_blast*txt', 'batch.sh',):
            files_grab.extend(glob.glob(files))
        for each in files_grab:
            shutil.move(each, blast_dir)
        if self.debug:
            pass
        else:
            shutil.rmtree(blast_dir)

        df = pd.read_excel(self.cross_reference)
        dictionary_of_genotypes = {}
        for index, row in df.iterrows():
            dictionary_of_genotypes[row['Genotype']] = {'PB2':row['PB2'], 'PB1':row['PB1'], 'PA':row['PA'], 'HA':row['HA'], 'NP':row['NP'], 'NA':row['NA'], 'MP':row['MP'], 'NS':row['NS'], }

        sample_dict={}
        hpai_genotype={}
        self.result_genotyping_hpia={}
        for key, value in blast_genotyping_hpia.items():
            try:
                genotype, sample, gene = re.split('[ ]', value["stitle"])
            except ValueError:
                sys.exit(f'SEE TYPO in Database Input File with Header: {value["stitle"]}')
            if float(blast_genotyping_hpia[gene]['pident']) >= 98.0: # update excel print value if threshold changed
                sample_dict[gene] = genotype
        matching_genotype = False
        for key, value in dictionary_of_genotypes.items():
            if sample_dict == value:
                matching_genotype = True
                hpai_genotype[key] = value
                self.result_genotyping_hpia['matching_genotype'] = True
                self.result_genotyping_hpia['genotype'] = key
                self.result_genotyping_hpia['genotyped_segments'] = value
        if matching_genotype:
            pass
            # for key, value in hpai_genotype.items():
            #     print(f'{key}: {value}')
        else:
            # print("Genotype not found")
            self.result_genotyping_hpia['matching_genotype'] = False
            self.result_genotyping_hpia['genotype'] = "No Match"
            self.result_genotyping_hpia['genotyped_segments'] = "No Findings"
        self.matching_genotype = matching_genotype
        self.hpai_genotype = hpai_genotype
        self.genotype_list_used=[]
        for gene, genotype in sample_dict.items():
            self.genotype_list_used.append(f'{gene}:{genotype}')

    def excel_metadata(self, excel_dict):
        try:
            excel_dict['Metadata'] = self.metadata_format_string
        except:
            pass

    def excel(self, excel_dict):
        genotype_list=[]
        full_sample_title=[]
        pident_list=[]
        mismatch_list=[]
        coverage_list=[]
        for key, value in self.blast_genotyping_hpia.items():
            genotype, sample, gene = re.split('[ ]', value["stitle"])
            genotype_list.append(f'{gene}:{genotype}')
            full_sample_title.append(f'{genotype}:{sample}:{gene}')
            pident_list.append(f'{float(value["pident"]):0.2f}%')
            mismatch_list.append(f'{int(float(value["mismatch"])):,}')
            try:
                coverage_list.append(f'{value["ave_cov_depth"]:0.1f}X')
            except (ValueError, KeyError):
                pass
        if not coverage_list:
            coverage_list.append(f'ave_cov_depth_na')

        segment_count = len(self.genotype_list_used)
        if self.matching_genotype:
            excel_dict['Genotype'] = self.result_genotyping_hpia['genotype']
        else:
            if segment_count == 8:
                excel_dict['Genotype'] = "Not assigned: No Matching Genotypes"
            else:
                excel_dict['Genotype'] = f'Not assigned: Only {segment_count} segments >98% match found of total {self.fastas_in_file} segments in input file'
        excel_dict['Genotype List Used, >=98%'] = ', '.join(self.genotype_list_used)
        excel_dict['Genotype Sample Title List'] = ', '.join(full_sample_title)
        excel_dict['Genotype Percent Match List'] = ', '.join(pident_list)
        excel_dict['Genotype Mismatch List'] = ', '.join(mismatch_list)
        excel_dict['Genotype Average Depth of Coverage List'] = ', '.join(coverage_list)



if __name__ == "__main__": # execute if directly access by the interpreter
    parser = argparse.ArgumentParser(prog='PROG', formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\

    ---------------------------------------------------------
    Usage:
        genoflu.py -f sample.fasta # -i and -c are optional and default to genoflu/dependencies
    -f is the input FASTA file which the genotype will be determined
    -i is the directory containing FASTAs to BLAST against.  Headers must follow specific format.  "genotype<space>sample<space>gene"
    -c is the excel file to cross-reference BLAST findings and identification to genotyping results.  Default genoflu/dependencies
    -n is the sample name to force output files to this sample name versus taking the name to be anything before [_.]

    Summary:
        FASTA files with formated headers are used to build BLAST database.  The input FASTA is BLASTed against the database.  The top hit for each segment is used to determine the genotype.  The genotype is determined by cross-referencing the top hits to a excel file.  If the top hit for each segment matches a genotype, then the genotype is assigned.  If the top hit for each segment does not match a genotype, then the genotype is not assigned.  If the top hit for each segment matches a genotype, but the genotype is not complete (i.e. only 7 segments match), then the genotype is not assigned.  If the top hit for each segment matches a genotype, and the genotype is complete (i.e. all 8 segments match), then the genotype is assigned.  

    '''), epilog='''---------------------------------------------------------''')

    parser.add_argument('-f', '--fasta', action='store', dest='FASTA', required=True, help='Assembled FASTA')
    parser.add_argument('-i', '--FASTA_dir', action='store', dest='FASTA_dir', default=None, help='Directory containing FASTAs to BLAST against.  Headers must follow specific format.  genoflu/dependencies/fastas')
    parser.add_argument('-c', '--cross_reference', action='store', dest='cross_reference', default=None, help='Excel file to cross-reference BLAST findings and identification to genotyping results.  Default genoflu/dependencies.  9 column Excel file, first column Genotype, followed by 8 columns for each segment and what those calls are for that genotype.')
    parser.add_argument('-n', '--sample_name', action='store', dest='sample_name', required=False, help='Force output files to this sample name')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', default=False, help='keep temp file')
    parser.add_argument('-v', '--version', action='version', version=f'{os.path.basename(__file__)}: version {__version__}')
    args = parser.parse_args()

    print(f'\n{os.path.basename(__file__)} set arguements:\n')
    for key, value in vars(args).items():
        print(f'\t{key}:  {value}')
    # print(args)
    print("\n")

    # Get the absolute path to the file
    FASTA_abs_path = os.path.abspath(args.FASTA)
    try:
        FASTA_dir = os.path.abspath(args.FASTA_dir)
    except TypeError:
        FASTA_dir = args.FASTA_dir
    try:
        cross_reference = os.path.abspath(args.cross_reference)
    except TypeError:
        cross_reference = args.cross_reference

    genoflu = GenoFLU(FASTA=FASTA_abs_path, FASTA_dir=FASTA_dir, cross_reference=cross_reference, sample_name=args.sample_name, debug=args.debug)
    try:
        genoflu.get_metadata()
    except:
        pass
    genoflu.blast_hpai_genomes()

    #Excel Stats
    excel_stats = Excel_Stats(genoflu.sample_name)
    genoflu.excel(excel_stats.excel_dict)
    FASTA_name = os.path.basename(FASTA_abs_path)
    excel_stats.excel_dict["File Name"] = FASTA_name
    genoflu.excel_metadata(excel_stats.excel_dict)
    excel_stats.excel_dict["Genotype Average Depth of Coverage List"] = "Ran on FASTA - No Coverage Report"
    try: # reorder stats columns
        column_order = list(excel_stats.excel_dict.keys())
        column_order.remove('File Name')
        column_order.insert(2, 'File Name')
        excel_stats.excel_dict = {k: excel_stats.excel_dict[k] for k in column_order}
    except ValueError:
        pass
    excel_stats.post_excel()
    df = pd.read_excel(excel_stats.excel_filename, sheet_name="Sheet1")
    df.to_csv(excel_stats.excel_filename.replace('.xlsx', '.tsv'), sep='\t', index=False)
    print(f'\n{genoflu.sample_name} Genotype --> {excel_stats.excel_dict["Genotype"]}: {excel_stats.excel_dict["Genotype List Used, >=98%"]}\n')

    temp_dir = f'{FASTA_abs_path}.temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    files_grab = []
    for files in ('hpai_geno_db.*', 'slurm*.out'):
        files_grab.extend(glob.glob(files))
    for each in files_grab:
        shutil.move(each, temp_dir)

    if args.debug is False:
        shutil.rmtree(temp_dir)

# Created 2023 by Tod Stuber
