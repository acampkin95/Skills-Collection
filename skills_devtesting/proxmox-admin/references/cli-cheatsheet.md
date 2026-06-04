# Proxmox VE CLI Cheatsheet

---

## qm — QEMU/KVM VM Management

### VM Lifecycle
```bash
qm list                                    # list all VMs
qm status <vmid>                           # power state
qm start    <vmid>                         # power on
qm shutdown <vmid>                         # graceful shutdown (ACPI)
qm stop     <vmid>                         # hard power off
qm reboot   <vmid>                         # graceful reboot
qm reset    <vmid>                         # hard reset
qm suspend  <vmid>                         # suspend to disk
qm resume   <vmid>                         # resume from suspend
qm unlock   <vmid>                         # clear stuck lock
qm destroy  <vmid> --purge                 # delete VM + volumes + config
qm monitor  <vmid>                         # QEMU monitor console
qm terminal <vmid> --iface serial0         # serial console
```

### VM Configuration
```bash
qm config  <vmid>                          # show current config
qm pending <vmid>                          # show pending changes
qm set     <vmid> --cores 4 --memory 8192  # change CPU/RAM
qm set     <vmid> --name new-name          # rename
qm set     <vmid> --onboot 1               # start at boot
qm set     <vmid> --startup order=1,up=30  # startup ordering
qm set     <vmid> --cpu host               # CPU passthrough
qm set     <vmid> --machine q35            # machine type
qm set     <vmid> --ostype l26             # guest OS hint
qm set     <vmid> --balloon 0              # disable memory balloon
qm set     <vmid> --numa 1                 # enable NUMA
qm set     <vmid> --affinity 4-7           # CPU pin to host cores 4-7
qm set     <vmid> --hugepages 2            # 2MB hugepages
```

### Disk Management
```bash
qm set <vmid> --scsi0 local-lvm:32,iothread=1,ssd=1,discard=on
qm set <vmid> --scsihw virtio-scsi-single
qm set <vmid> --ide2 local:iso/ubuntu.iso,media=cdrom
qm set <vmid> --boot order=scsi0
qm resize   <vmid> scsi0 +20G             # extend disk by 20G
qm unlink   <vmid> --idlist scsi1 --force # detach & delete disk
qm importdisk <vmid> /tmp/disk.img local-lvm  # import image as disk
```

### Network
```bash
qm set <vmid> --net0 virtio,bridge=vmbr0,firewall=1
qm set <vmid> --net0 virtio,bridge=vmbr0,queues=4,mtu=9000
qm set <vmid> --net0 e1000,bridge=vmbr0   # emulated NIC (slower)
```

### Snapshots
```bash
qm snapshot     <vmid> snap-name --description "Before upgrade"
qm listsnapshot <vmid>
qm rollback     <vmid> snap-name
qm delsnapshot  <vmid> snap-name
qm delsnapshot  <vmid> snap-name --force
```

### Clone & Template
```bash
qm clone    <vmid> <newid> --name <name> --full --storage local-lvm
qm clone    <vmid> <newid> --name <name> --snapname snap-name
qm template <vmid>                         # convert to template
```

### Migration
```bash
qm migrate <vmid> <target-node>            # offline
qm migrate <vmid> <target-node> --online   # live (shared storage)
qm migrate <vmid> <target-node> --online --with-local-disks  # no shared storage
```

### Cloud-Init
```bash
qm set <vmid> --ide2 local-lvm:cloudinit
qm set <vmid> --ciuser ubuntu --cipassword 'pass' --sshkeys /root/.ssh/id_rsa.pub
qm set <vmid> --ipconfig0 ip=dhcp
qm set <vmid> --ipconfig0 ip=192.168.1.50/24,gw=192.168.1.1
qm set <vmid> --nameserver 1.1.1.1 --searchdomain example.com
qm cloudinit update <vmid>                 # regenerate cloud-init disk
qm cloudinit dump   <vmid> user            # show user-data
qm cloudinit dump   <vmid> network         # show network-data
```

### QEMU Guest Agent
```bash
qm agent <vmid> info                       # guest info
qm guest cmd    <vmid> network-get-interfaces  # get IPs
qm guest exec   <vmid> -- command args     # exec in guest
qm guest passwd <vmid> username            # set password
qm guest exec-status <vmid> <pid>          # check exec status
```

---

## pct — LXC Container Management

```bash
pct list                                   # list containers
pct status  <ctid>                         # power state
pct start   <ctid>                         # start
pct stop    <ctid>                         # hard stop
pct shutdown <ctid>                        # graceful shutdown
pct reboot  <ctid>                         # reboot
pct suspend <ctid>                         # suspend (experimental)
pct resume  <ctid>                         # resume
pct destroy <ctid> --purge                 # delete CT + volumes

pct enter   <ctid>                         # shell into CT
pct exec    <ctid> -- <command>            # exec command in CT

pct config  <ctid>                         # show config
pct pending <ctid>                         # pending changes
pct set     <ctid> --memory 4096 --cores 4
pct set     <ctid> --onboot 1
pct set     <ctid> --hostname new-name

pct resize  <ctid> rootfs +10G            # extend root disk
pct snapshot <ctid> snap-name
pct rollback <ctid> snap-name
pct delsnapshot <ctid> snap-name
pct clone   <ctid> <newid> --full

pct create <ctid> <template> \
  --hostname ct-name \
  --cores 2 --memory 2048 --swap 512 \
  --rootfs local-lvm:10 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp,firewall=1 \
  --unprivileged 1 --onboot 1

# Template management
pveam update
pveam available
pveam download local <template>
pveam list local
```

---

## pvesh — REST API Shell

```bash
pvesh                                      # interactive shell
pvesh ls /                                 # list root paths
pvesh ls /nodes                            # browse tree
pvesh get /cluster/resources --output-format json-pretty
pvesh get /cluster/resources --type vm
pvesh get /nodes/pve/qemu/200/config
pvesh create /nodes/pve/qemu/200/status/start
pvesh set /nodes/pve/qemu/200/config -cores 4 -memory 8192
pvesh delete /nodes/pve/qemu/200          # delete VM via API
pvesh get /nodes/pve/storage
pvesh get /nodes/pve/disks/list
```

---

## pvecm — Cluster Management

```bash
pvecm create <cluster-name>               # create new cluster (first node)
pvecm create <cluster-name> --link0 <IP>  # with specific interface
pvecm add <existing-node-IP>              # join existing cluster
pvecm add <IP> --link0 <local-IP>

pvecm status                              # cluster health
pvecm nodes                               # list cluster nodes

# Node removal (run from a DIFFERENT node)
pvecm delnode <nodename>

# Quorum recovery (single-node only — sets expected votes to 1)
pvecm expected 1

# Cluster config
cat /etc/pve/corosync.conf
systemctl status corosync
systemctl status pve-cluster
```

---

## pveum — User & Access Management

```bash
# Users
pveum user list
pveum user add <user@realm> --password 'pass' --comment "Description"
pveum user modify <user@realm> --email user@example.com
pveum user delete <user@realm>

# Realms: pve (local), pam (Linux PAM), ldap, ad, openid
pveum realm list
pveum realm add ldap my-ldap --server ldap.example.com --base-dn "dc=example,dc=com"

# Roles
pveum role list
pveum role add CustomRole -privs "VM.PowerMgmt VM.Console"
pveum role modify CustomRole -privs "VM.PowerMgmt VM.Console VM.Monitor"
pveum role delete CustomRole

# ACLs
pveum acl list
pveum acl modify / -user admin@pve -role Administrator
pveum acl modify /nodes/pve -user ops@pve -role PVEAuditor
pveum acl modify /vms/200   -user dev@pve  -role PVEVMUser
pveum acl modify / -group   ops-team -role PVEVMAdmin
pveum acl delete /vms/200   -user dev@pve -role PVEVMUser

# Groups
pveum group list
pveum group add ops-team --comment "Operations team"
pveum group modify ops-team -users "alice@pve,bob@pve"
pveum group delete ops-team

# API tokens
pveum user token add <user@realm> <tokenid>
pveum user token add <user@realm> <tokenid> --privsep 0 --expire 2027-01-01
pveum user token modify <user@realm> <tokenid> --comment "Updated"
pveum user token remove <user@realm> <tokenid>
pveum user token list <user@realm>

# TFA
pveum user tfa add <user@realm> --type totp
pveum user tfa delete <user@realm>
```

---

## vzdump — Backup

```bash
# Single VM
vzdump <vmid> --mode snapshot --compress zstd --storage local

# Multiple VMs
vzdump 100 101 200 --mode snapshot --compress zstd --storage pbs-main

# All VMs/CTs on this node
vzdump --all --mode snapshot --compress zstd --storage pbs-main

# Backup modes:
# snapshot  = online backup with consistent disk snapshot (preferred)
# suspend   = brief suspension for RAM snapshot
# stop      = stop, backup, restart (longest downtime)

# Compression: none, lzo, gzip, zstd (zstd = best speed/ratio)

# Restore VM
qmrestore <backup-file.vma.zst> <newvmid> --storage local-lvm
qmrestore <backup-file.vma.zst> <newvmid> --storage local-lvm --unique  # new MACs

# Restore CT
pct restore <newctid> <backup-file.tar.zst> --storage local-lvm

# PBS restore (using storage plugin name)
qmrestore "pbs-main:backup/vm/200/2026-06-01T03:00:00Z" 200 --storage local-lvm
```

---

## ha-manager — High Availability

```bash
ha-manager status                         # HA cluster status
ha-manager add vm:<vmid>                  # add VM to HA
ha-manager add vm:<vmid> --group ha-grp --max_restart 3 --max_relocate 2
ha-manager set vm:<vmid> --state started  # ensure HA keeps it running
ha-manager set vm:<vmid> --state stopped  # allow HA to stop it
ha-manager remove vm:<vmid>               # remove from HA

ha-manager add ct:<ctid>                  # LXC container HA
```

---

## pvesm — Storage Management

```bash
pvesm status                              # all storage status
pvesm list <storage>                      # list contents
pvesm path <storage>:<volume>             # resolve volume path
pvesm alloc <storage> <vmid> <name> <size>G  # allocate volume
pvesm free  <storage>:<volume>            # free volume

pvesm add dir    mydir  --path /mnt/data --content images,backup
pvesm add nfs    nfs-bk --server 192.168.1.5 --export /backup --content backup
pvesm add lvm    my-lvm --vgname vg0 --content images,rootdir
pvesm add lvmthin lvmt  --vgname vg0 --thinpool data --content images,rootdir
pvesm add zfspool zfs-t --pool tank --content images,rootdir
pvesm add pbs    pbs-1  --server pbs.example.com --datastore vmstore \
                          --username backup@pbs! --password SECRET --content backup
pvesm add cephfs cephfs-s --monhost "10.0.0.1 10.0.0.2" --path /cephfs --content images

pvesm set <storage> --disable 1          # disable storage
pvesm remove <storage>                    # remove (no data deleted)
pvesm scan nfs 192.168.1.5               # scan NFS exports
pvesm scan iscsi 192.168.1.20            # scan iSCSI targets
```

---

## Useful Node Commands

```bash
# Version info
pveversion -v
pveversion --verbose

# System maintenance
apt update && apt full-upgrade -y         # update PVE
pve-manager --version                     # management UI version

# Network
ip link show
ip addr show
bridge link show
ifreload -a                               # reload /etc/network/interfaces

# Disk info
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
pvdisplay                                 # LVM physical volumes
vgdisplay                                 # volume groups
lvdisplay                                 # logical volumes

# ZFS
zpool status
zpool list
zfs list
zpool scrub <pool>
zpool iostat -v 2

# Ceph
ceph status
ceph osd status
ceph df
pveceph status

# Corosync / cluster
corosync-cfgtool -s                       # ring status
corosync-quorumtool -s                    # quorum status

# Task logs
cat /var/log/pve/tasks/active
journalctl -u pvedaemon --since "1 hour ago"
journalctl -u pveproxy -f
```

---

## Common Config File Locations

| File | Purpose |
|---|---|
| `/etc/pve/qemu-server/<vmid>.conf` | VM config |
| `/etc/pve/lxc/<ctid>.conf` | CT config |
| `/etc/pve/storage.cfg` | Storage definitions |
| `/etc/pve/corosync.conf` | Cluster config |
| `/etc/pve/user.cfg` | Users, roles, ACLs |
| `/etc/pve/nodes/<node>/pve-ssl.pem` | Node TLS cert |
| `/etc/network/interfaces` | Network config |
| `/etc/default/pveproxy` | Web proxy settings |
| `/var/lib/vz/dump/` | Default backup storage |
| `/var/lib/vz/images/<vmid>/` | Default VM disk storage |
| `/var/lib/vz/template/iso/` | ISO storage |
| `/var/lib/vz/template/cache/` | LXC templates |
