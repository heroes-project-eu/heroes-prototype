#!/usr/bin/env nextflow

// Dump some info
log.info "=================================="
log.info "Current home: $HOME"
log.info "Current user: $USER"
log.info "Current path: $PWD"
log.info "Script dir:   $baseDir"
log.info "Working dir:  $workDir"
log.info "=================================="


process runAnsible {

    input:
    path ansibleDir from params.ansibleDir
    val ansibleMain from params.ansibleMain
    val ansibleTags from params.ansibleTags

    output:
    stdout result

    script:
    template 'ansible.sh'
}

result.view { it.trim() }
