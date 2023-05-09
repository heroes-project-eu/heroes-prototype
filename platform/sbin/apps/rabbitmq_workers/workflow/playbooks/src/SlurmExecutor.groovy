/*
 * Copyright 2020-2022, Seqera Labs
 * Copyright 2013-2019, Centre for Genomic Regulation (CRG)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package nextflow.executor
import java.nio.file.Path
import java.util.regex.Pattern

import groovy.util.logging.Slf4j
import nextflow.processor.TaskRun
/**
 * Processor for SLURM resource manager (DRAFT)
 *
 * See http://computing.llnl.gov/linux/slurm/
 *
 *
 * @author Paolo Di Tommaso <paolo.ditommaso@gmail.com>
 */
@Slf4j
class SlurmExecutor extends AbstractGridExecutor {

    static private Pattern SUBMIT_REGEX = ~/Submitted batch job (\d+)/

    /**
     * User, address and ssh_key needed later for squeue and scancel
     */
    private String clusterName
    private String sshUser
    private String sshAddress
    private String sshPort
    private String sshPath
    private String dataPath
    private String minioName
    private String bucketName
    private String userWorkDir
    private String singularityContainerPath
    private String inputDir

    private boolean hasSignalOpt(Map config) {
        def opts = config.clusterOptions?.toString()
        return opts ? opts.contains('--signal ') || opts.contains('--signal=') : false
    }


    /**
     * Gets the directives to submit the specified task to the cluster for execution
     *
     * @param task A {@link TaskRun} to be submitted
     * @param result The {@link List} instance to which add the job directives
     * @return A {@link List} containing all directive tokens and values.
     */
    protected List<String> getDirectives(TaskRun task, List<String> result) {

        result << '-D' << quote(task.workDir)
        result << '-J' << getJobNameFor(task)
        result << '-o' << quote(task.workDir.resolve(TaskRun.CMD_LOG))     // -o OUTFILE and no -e option => stdout and stderr merged to stdout/OUTFILE
        result << '--no-requeue' << '' // note: directive need to be returned as pairs

        if( !hasSignalOpt(task.config) ) {
            // see https://github.com/nextflow-io/nextflow/issues/2163
            // and https://slurm.schedmd.com/sbatch.html#OPT_signal
            result << '--signal' << 'B:USR2@30'
        }

        if( task.config.cpus > 1 ) {
            result << '-c' << task.config.cpus.toString()
        }

        if( task.config.time ) {
            result << '-t' << task.config.getTime().format('HH:mm:ss')
        }

        if( task.config.getMemory() ) {
            //NOTE: Enforcement of memory limits currently relies upon the task/cgroup plugin or
            // enabling of accounting, which samples memory use on a periodic basis (data need not
            // be stored, just collected). In both cases memory use is based upon the job's
            // Resident Set Size (RSS). A task may exceed the memory limit until the next periodic
            // accounting sample. -- https://slurm.schedmd.com/sbatch.html
            result << '--mem' << task.config.getMemory().toMega().toString() + 'M'
        }

        // the requested partition (a.k.a queue) name
        if( task.config.queue ) {
            result << '-p' << (task.config.queue.toString())
        }

        // -- at the end append the command script wrapped file name
        if( task.config.clusterOptions ) {
            result << task.config.clusterOptions.toString() << ''
        }

        return result
    }

    String getHeaderToken() { '#SBATCH' }

    /**
     * The command line to submit this job
     *
     * @param task The {@link TaskRun} instance to submit for execution to the cluster
     * @param scriptFile The file containing the job launcher script
     * @return A list representing the submit command line
     */
    @Override
    List<String> getSubmitCommandLine(TaskRun task, Path scriptFile ) {

        clusterName = ""
        sshUser = ""
        sshAddress = ""
        sshPort = ""
        sshPath = ""
        dataPath = ""
        minioName = ""
        bucketName = ""
        userWorkDir = ""
        singularityContainerPath = ""
        inputDir = ""

        clusterName = task.config.getCluster()[0]
        sshUser = task.config.getCluster()[1]
        sshAddress = task.config.getCluster()[2]
        sshPort = task.config.getCluster()[3]
        sshPath = task.config.getCluster()[4]

        dataPath = task.config.getData()
        minioName = task.config.getMinio()
        bucketName = task.config.getBucket()
        userWorkDir = task.workDirStr.split("/").dropRight(2).join("/")
        singularityContainerPath = task.config.getSingularityContainer()
        inputDir = task.config.getInputDir()

        // send an empty list if the transfer returns error. It will force NF to crash
        // from now the functions returns always true. TODO make them return error if the cmd returns False
        if (!dataTransferLocalToMinio() || !dataTransferMinioToCluster() || !singularityToCluster(task.container) || !inputDirTransferMinioToCluster())
            return []
        else
             log.trace("file transfer before execution finished")

        ['ssh', '-i', sshPath, sshUser + '@' + sshAddress, '-p', sshPort, 'sbatch', scriptFile]

	/* def script = "/home/ubuntu/hpcnow_nextflow/wrapper.sh"
        def script = "/opt/rabbitmq/playbooks/src/wrapper.sh"

        def sout = new StringBuilder(), serr = new StringBuilder()
        def clusterConfig = task.config.getCluster()
        clusterConfig = clusterConfig.replaceAll(" ","")
        def cmd = script + " " + "submit" + " " + task.workDir + " " + clusterConfig + " " + task.container
        Process proc = cmd.execute()
        proc.waitForProcessOutput(sout, serr)
        def script_output = sout.split()
        // Set variables to be used later in the other slurm commands
        ssh_key = script_output[0]
        ssh_user_address = script_output[1]

        ['ssh', '-i', ssh_key, ssh_user_address, 'sbatch', script_output[2]]*/


    }

    /**
     * Parse the string returned by the {@code sbatch} command and extract the job ID string
     *
     * @param text The string returned when submitting the job
     * @return The actual job ID string
     */
    @Override
    def parseJobId(String text) {

        for( String line : text.readLines() ) {
            def m = SUBMIT_REGEX.matcher(line)
            if( m.find() ) {
                return m.group(1).toString()
            }
        }

        // customised `sbatch` command can return only the jobid
        def id = text.trim()
        if( id.isLong() )
            return id

        throw new IllegalStateException("Invalid SLURM submit response:\n$text\n\n")
    }

    @Override
    protected List<String> getKillCommand() { ['ssh', '-i', sshPath, sshUser + '@' + sshAddress, '-p', sshPort, 'scancel'] }

    @Override
    protected List<String> queueStatusCommand(Object queue) {

        // Todo: Use the wrapper to get the ssh_key, user and address only
        final result = ['ssh', '-i', sshPath, sshUser + '@' + sshAddress, '-p', sshPort, 'squeue','--noheader','-o','\"%i %t\"', '-t', 'all']

        if( queue )
            result << '-p' << queue.toString()

        if( sshUser )
            result << '-u' << sshUser
        else
            log.debug "Cannot retrieve current user"

        return result
    }

    /*
     *  Maps SLURM job status to nextflow status
     *  see http://slurm.schedmd.com/squeue.html#SECTION_JOB-STATE-CODES
     */
    static private Map STATUS_MAP = [
            'PD': QueueStatus.PENDING,  // (pending)
            'R': QueueStatus.RUNNING,   // (running)
            'CA': QueueStatus.ERROR,    // (cancelled)
            'CF': QueueStatus.PENDING,  // (configuring)
            'CG': QueueStatus.RUNNING,  // (completing)
            'CD': QueueStatus.DONE,     // (completed)
            'F': QueueStatus.ERROR,     // (failed),
            'TO': QueueStatus.ERROR,    // (timeout),
            'NF': QueueStatus.ERROR,    // (node failure)
            'S': QueueStatus.HOLD,      // (job suspended)
            'ST': QueueStatus.HOLD,     // (stopped)
            'PR': QueueStatus.ERROR,    // (Job terminated due to preemption)
            'BF': QueueStatus.ERROR,    // (boot fail, Job terminated due to launch failure)
    ]

    @Override
    protected Map<String, QueueStatus> parseQueueStatus(String text) {

        def result = [:]

        text.eachLine { String line ->
            def cols = line.split(/\s+/)
            if( cols.size() == 2 ) {
                result.put( cols[0], STATUS_MAP.get(cols[1]) )
            }
            else {
                log.debug "[SLURM] invalid status line: `$line`"
            }
        }

        return result
    }

    // Uses Rclone to transfer data from local nextflow executor to minio
    protected boolean dataTransferLocalToMinio() {

        def cmd = "rclone copy " + userWorkDir + " " + minioName + ":" + bucketName + "/" + userWorkDir.split("/").drop(5).join("/") + " --config " + dataPath

        return runProc(cmd)
    }

    // Uses Rclone to transfer the container from local to the cluster
    protected boolean singularityToCluster(String container) {

        container = container.split("/").drop(6).join() // Considering a .sif container
        def cmd = "rclone copy " + minioName + ":" + singularityContainerPath + " " + clusterName + ":" + userWorkDir + " --config " + dataPath

        println("singularityToCluster")
        println(clusterName)
        println(cmd)

        return runProc(cmd)
    }

    // Uses RClone to transfer the inputDir from minio to the cluster
    protected boolean inputDirTransferMinioToCluster(String container) {

        def cmd = "rclone copy " + minioName + ":" + inputDir + " " + clusterName + ":" + userWorkDir + " --config " + dataPath

        println("inputDirTransferMinioToCluster")
        println(inputDir)
        println(cmd)

        return runProc(cmd)
    }

    // Uses Rclone to transfer data from minio to the cluster
    protected boolean dataTransferMinioToCluster() {

        def cmd = "rclone copy " + minioName + ":" + bucketName + "/" + userWorkDir.split("/").drop(5).join("/") + " " + clusterName + ":" + userWorkDir + " --config " + dataPath

        return runProc(cmd)
    }

    // Piece of code to launch a Process without repeating code
    protected boolean runProc(String cmd) {

        def sout = new StringBuilder(), serr = new StringBuilder()

        Process proc = cmd.execute()
        proc.waitForProcessOutput(sout, serr)

        return true
    }
}
