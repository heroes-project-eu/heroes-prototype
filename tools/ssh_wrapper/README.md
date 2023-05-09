# js-ssh-wrapper

This SSH Wrapper is aiming to forward EnginFrame Job Scheduler commands to a remote cluster.

# Installation

## For SLURM

TODO

## For LSF

1. Edit the `./js-ssh-wrapper.sh` file with the appropriate values (cluster host, ...)
2. Run `./js-ssh-wrapper-LSF-install.sh` as root, it will ask for the installation directory (if you do not provide it as a script argument)
3. Put `js-ssh-wrapper.sh` inside the installation directory
4. Make the `js-ssh-wrapper.sh` executable by users (chmod +x `js-ssh-wrapper.sh`)

Note: If you already have installed EnginFrame, you should edit the `profile.lsf` file loaded by EnginFrame:
change `LSF_PROFILE=*` in `/opt/nice/enginframe/conf/plugins/lsf/ef.lsf.conf` to `LSF_PROFILE="/installation_dir/profile.lsf"`
Note: In the case of an EFTR installation, you have to update the LSF profile in the EFTR admin portal to `/installation_dir/profile.lsf` (or copy the content of the `/installation_dir/profile.lsf` into the profile used by EFTR)

# Usage

1. The user submitting jobs should use passwordless SSH to connect to the master node. The private key is by default `~/.ssh/id_rsa` but you can change it in `js-ssh-wrapper.sh`
2. From then, the user can launch jobs on the remote cluster from EnginFrame.

# Supported Job Schedulers

- SLURM (without the install script)
- LSF
