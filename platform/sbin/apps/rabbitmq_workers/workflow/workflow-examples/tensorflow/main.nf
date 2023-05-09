#!/usr/bin/env nextflow

nextflow.enable.dsl=2

process copy_files {

    cpus = 'HEROES_CPUS'
    memory = 'HEROES_MEMORY'

    input:
      path myFolderTraining
      path myFolderClassify
      path myFolderCode

    output:
      path 'training_dataset', emit: trainingdir
      path 'classification_dataset_lite', emit: classifdir
      path 'code', emit: codedir

    script:
    """
    tar -xf $myFolderTraining
    tar -xf $myFolderClassify
    tar -xf $myFolderCode
    """
}

process training {

    cpus = 'HEROES_CPUS'
    memory = 'HEROES_MEMORY'

    input:
      path trainingdir
      path codedir

    echo true
    output:
      path 'tf_files', emit: result

    script:
    """
    python $codedir/retrain.py \
    --bottleneck_dir=tf_files/bottlenecks \
    --how_many_training_steps=500 \
    --model_dir=inception \
    --summaries_dir=tf_files/training_summaries/basic \
    --output_graph=tf_files/retrained_graph.pb \
    --output_labels=tf_files/retrained_labels.txt \
    --image_dir=training_dataset
    """
}

process classification {

    cpus = 'HEROES_CPUS'
    memory = 'HEROES_MEMORY'

    input:
      path classifdir
      path codedir
      path result

    echo true
    output:
      path 'tf_files', emit: result

    script:
    """
    python $codedir/classify_folder.py $classifdir
    """
}


workflow {
    myFolderTraining = Channel.fromPath("$workDir/training_dataset.tar.gz")
    myFolderClassify = Channel.fromPath("$workDir/classification_dataset_lite.tar.gz")
    myFolderCode = Channel.fromPath("$workDir/code.tar.gz")
    copy_files(myFolderTraining, myFolderClassify, myFolderCode)
    training(copy_files.out.trainingdir, copy_files.out.codedir)
    classification(copy_files.out.classifdir, copy_files.out.codedir,training.out.result)
}
