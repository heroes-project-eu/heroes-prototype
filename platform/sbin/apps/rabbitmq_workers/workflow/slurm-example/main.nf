#!/usr/bin/env nextflow

params.str = 'Hello world!'

process SplitLetters {
    executor 'slurm'
    cpus = 1
    cluster = 'cluster1'

    output:
    file 'chunk_*' into letters

    """
    uname -a
    cat /etc/*release
    printf '${params.str}' | split -b 6 - chunk_

    """
}

process ConvertToUpper {
    executor 'slurm'
    cpus = 1
    cluster = 'cluster2'

    input:
    file x from letters.flatten()

    output:
    stdout result

    """
    uname -a
    cat /etc/*release
    cat $x | tr '[a-z]' '[A-Z]'
    """
}

result.view {it.trim()}
