# Nextflow

### Tech
[Nextflow](https://www.nextflow.io)
### Requirements
Nextflow >= 21.10
### Run
To invoke all (ansible) playbooks:
```
nextflow run main.nf -params-file params.yml
```
To invoke specific (ansible) tasks using tags:
```
nextflow run main.nf -params-file params.yml --ansibleTags <myTag1,myTag2> 
E.g.: nextflow run main.nf -params-file params.yml --ansibleTags segregation_check
```
To view (ansible) tags:
```
cat ../ansible/main.yml | grep tags
```
