#!/usr/bin/env python

import os
import re

import ruffus as R

from config import CONFIG
import logging.config
logging.config.dictConfig(CONFIG['logging'])
logger = logging.getLogger(__name__)

import utils as U

import pprint
logger.info('\n{0}'.format(pprint.pformat(CONFIG)))

@R.mkdir(CONFIG['input_gs_bam'], R.formatter(),
         os.path.join(CONFIG['output_dir'], 'download_bam'))
@R.originate(
    os.path.join(CONFIG['output_dir'], 'download_bam', os.path.basename(CONFIG['input_gs_bam'])),
    # use extra param to store the flag filename
    [os.path.join(CONFIG['output_dir'], 'download_bam', 'download_bam.log'),
     os.path.join(CONFIG['output_dir'], 'download_bam', 'download_bam.COMPLETE')],
)
@U.timeit
def download_bam(output_bam, extras):
    log, flag = extras
    cmd = ('{auth_gsutil} -m cp {bam} {outdir} 2>&1 | tee {log}').format(
        auth_gsutil=CONFIG['auth_gsutil'],
        bam=CONFIG['input_gs_bam'],
        outdir=os.path.dirname(output_bam),
        log=log)
    U.execute(cmd, flag)

# This task cannot be merged with download_bam because otherwise following
# tasks (e.g. bam2fastq will take gtf as a bam file
@R.mkdir(CONFIG['input_gs_gtf'], R.formatter(),
         os.path.join(CONFIG['output_dir'], 'download_gtf'))
@R.originate(
    os.path.join(CONFIG['output_dir'], 'download_gtf', os.path.basename(CONFIG['input_gs_gtf'])),
    # use extra param to store the flag filename
    [os.path.join(CONFIG['output_dir'], 'download_gtf', 'download_gtf.log'),
     os.path.join(CONFIG['output_dir'], 'download_gtf', 'download_gtf.COMPLETE')],
)
@U.timeit
def download_gtf(output_gtf, extras):
    log, flag = extras
    cmd = ('{auth_gsutil} -m cp {gtf} {outdir} 2>&1 | tee {log}').format(
        auth_gsutil=CONFIG['auth_gsutil'],
        gtf=CONFIG['input_gs_gtf'],
        outdir=os.path.dirname(output_gtf),
        log=log)
    U.execute(cmd, flag)


@R.mkdir(CONFIG['input_gs_star_index'], R.formatter(),
         os.path.join(CONFIG['output_dir'], 'download_star_index'))
@R.originate(
    os.path.join(CONFIG['output_dir'], 'download_star_index', os.path.basename(CONFIG['input_gs_star_index'])),
    # use extra param to store the flag filename
    [os.path.join(CONFIG['output_dir'], 'download_star_index', 'download_star_index.log'),
     os.path.join(CONFIG['output_dir'], 'download_star_index', 'download_star_index.COMPLETE')],
)
@U.timeit
def download_star_index(output_star_index, extras):
    log, flag = extras
    cmd = ('{auth_gsutil} -m cp -r {star_index} {outdir} 2>&1 | tee {log}').format(
        auth_gsutil=CONFIG['auth_gsutil'],
        star_index=CONFIG['input_gs_star_index'],
        outdir=os.path.dirname(output_star_index),
        log=log)
    U.execute(cmd, flag)


@R.mkdir(download_bam, R.formatter(), '{subpath[0][1]}/bam2fastq')
@R.transform(download_bam, R.formatter(), [
    '{subpath[0][1]}/bam2fastq/cba_1.fastq',
    '{subpath[0][1]}/bam2fastq/cba_2.fastq',
    '{subpath[0][1]}/bam2fastq/bam2fastq.log',
    '{subpath[0][1]}/bam2fastq/bam2fastq.COMPLETE'
])
@U.timeit
def bam2fastq(input_bam, outputs):
    fq1, fq2, log, flag = outputs
    output_dir = os.path.dirname(fq1)
    num_cpus = CONFIG['num_cpus']
    cmd = ("picard-tools SamToFastq I={input_bam} "
           "FASTQ={fq1} "
           "SECOND_END_FASTQ={fq2} "
           "UNPAIRED_FASTQ=discarded.fastq "
           "| tee {log} ".format(**locals()))
    U.execute(cmd, flag)

# @R.mkdir(fastqc, R.formatter(), '{subpath[0][1]}/upload')
# @R.transform(fastqc, R.formatter(), [
#     '{subpath[0][1]}/upload/upload.log',
#     '{subpath[0][1]}/upload/upload.COMPLETE',
# ])
# @U.timeit
# def upload(inputs, outputs):
#     # e.g. /top_dir/first_subdir/second_subdir/somefile.log => /top_dir
#     top_dir = re.search(r'/[^/]+', os.path.abspath(inputs[0])).group(0)
#     # e.g. /top_dir => top_dir
#     top_dir_name = top_dir.lstrip('/')
#     log, flag = outputs
#     cfg = CONFIG['steps']['upload']
#     auth_gsutil=CONFIG['auth_gsutil']
#     bucket_dir = os.path.join(cfg['output_gs_bucket'], top_dir_name)

#     # don't upload input bam
#     re_files_to_exclude = '|'.join([r'.*\.bam$'])
#     cmd = ("{auth_gsutil} -m rsync -x '{re_files_to_exclude}' -r "
#            "{top_dir} {bucket_dir}").format(**locals())

#     # -x '' would be invalid and cause error
#     # cmd = ("{auth_gsutil} -m rsync -r -d "
#     #        "{top_dir} {bucket_dir}").format(**locals())

#     U.execute(cmd, flag)


# @R.follows(upload)
# @U.timeit
# def cleanup():
#     """remove the output folder to save disk space"""
#     cmd = "rm -rfv {0}".format(CONFIG['output_dir'])
#     U.execute(cmd)

if __name__ == "__main__":
    R.pipeline_run()
