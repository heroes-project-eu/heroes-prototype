#!/usr/bin/env nextflow

nextflow.enable.dsl=2

process copy_files {

    cpus = 'HEROES_CPUS'
    memory = 'HEROES_MEMORY'

    input:
      path myFolder

    output:
      path 'motorBike', emit: unzipdir

    script:
    """
    tar -xf $myFolder
    """
}

process memory_intensive {

    cpus = 'HEROES_CPUS'
    memory = 'HEROES_MEMORY'

    input:
      path unzipdir

    echo true
    output:
      path 'motorBike/log.*', emit: p2result

    script:
    """
    export MPI_BUFFER_SIZE=20000000
    $unzipdir/Allrun1
    """
}

process cpu_intensive {

    cpus = 'HEROES_CPUS'
    memory = 'HEROES_MEMORY'

    input:
      path unzipdir
      path p2result

    echo true
    script:
    """
    export MPI_BUFFER_SIZE=20000000
    $unzipdir/Allrun2
    """
}


workflow {

    myFolder = Channel.fromPath("$workDir/motorBike.tar.gz")
    copy_files(myFolder)
    memory_intensive(copy_files.out.unzipdir)
    cpu_intensive(copy_files.out.unzipdir, memory_intensive.out.p2result)
}
