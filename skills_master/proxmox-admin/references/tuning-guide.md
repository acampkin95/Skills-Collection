# Proxmox VE Advanced Tuning Guide

---

## Principles

1. **CPU**: `host` passthrough > specific model > emulated. Enable NUMA for multi-socket hosts.
2. **Memory**: Disable ballooning for latency-sensitive workloads. Use hugepages for databases/realtime.
3. **Disk**: `virtio-scsi-single` + `iothread=1` per disk. Cache `none` on ZFS; `writeback` on LVM with BBU.
4. **Network**: VirtIO + multiqueue (queues = vCPU count). Jumbo frames if switch supports it.
5. **Host**: Isolate CPUs from scheduler. Disable unnecessary services. Kernel parameters for performance.

---

## CPU Optimisation

### CPU Type Selection

| CPU Type | Use Case | Notes |
|---|---|---|
| `host` | Best performance, no migration between different CPU families | Exposes all host CPU features |
| `x86-64-v3` | Good performance + cross-node migration (Intel Haswell / AMD Zen 2+) | Recommended default |
| `x86-64-v2` | Broadest compatibility for older hardware | Lower performance |
| `kvm64` | Minimum compatibility | Slowest — avoid for production |

```bash
# Set CPU type
qm set <vmid> --cpu host
qm set <vmid> --cpu x86-64-v3,flags=+pcid

# CPU flags worth enabling on compatible hosts
# +pcid   = reduces Meltdown/Spectre mitigation overhead
# +spec-ctrl = Spectre v2 mitigation
# +md-clear  = MDS vulnerability mitigation
qm set <vmid> --cpu host,flags=+pcid
```

### CPU Pinning (Dedicated Cores)

CPU pinning eliminates vCPU scheduling latency and improves cache locality. Use for databases, real-time workloads, gaming VMs.

```bash
# Step 1: Identify NUMA topology
numactl --hardware
lscpu --extended | grep -E "^(CPU|NUMA|CORE)"

# Example output: 8-core host, cores 0-7
# Pin VM (4 vCPUs) to cores 4-7
qm set <vmid> --affinity 4-7

# For hyperthreaded systems: pin to physical core pairs
# Core 0 = threads 0,8 ; Core 1 = threads 1,9 etc.
qm set <vmid> --affinity 4,5,12,13  # physical cores 4 & 5 with HT siblings

# Verify pinning
cat /sys/fs/cgroup/cpuset/qemu.slice/qemu-<vmid>.scope/cpuset.cpus
```

### NUMA Configuration

```bash
# Enable NUMA topology awareness
qm set <vmid> --numa 1

# Bind vCPUs and memory to specific NUMA node
qm set <vmid> --numa0 cpus=0-3,hostnodes=0,memory=8192,policy=bind

# Multiple NUMA nodes (for large VMs spanning nodes)
qm set <vmid> --numa0 cpus=0-3,hostnodes=0,memory=8192,policy=bind
qm set <vmid> --numa1 cpus=4-7,hostnodes=1,memory=8192,policy=bind

# Inside guest: verify NUMA
numactl --hardware
numstat -v
```

### CPU Isolation on Host (Advanced)

For maximum VM performance: isolate host CPUs from OS scheduler entirely.

```bash
# /etc/default/grub — add to GRUB_CMDLINE_LINUX_DEFAULT
# isolcpus=4-7 nohz_full=4-7 rcu_nocbs=4-7
# Then: update-grub && reboot

# Verify
cat /sys/devices/system/cpu/isolated
```

---

## Memory Optimisation

### Hugepages

Reduces TLB pressure — significant for memory-intensive VMs (databases, in-memory caches).

```bash
# Check hugepage availability
cat /proc/meminfo | grep Huge

# Allocate 2MB hugepages (number = pages, not total MB)
# For 16GB VM: 16*1024/2 = 8192 pages
echo "vm.nr_hugepages = 8192" >> /etc/sysctl.d/99-hugepages.conf
sysctl -p /etc/sysctl.d/99-hugepages.conf

# Make persistent across reboots
echo "hugepages=8192" >> /etc/kernel/cmdline
proxmox-boot-tool refresh  # if using EFI/systemd-boot

# Enable for VM
qm set <vmid> --hugepages 2   # 2MB hugepages
qm set <vmid> --hugepages 1024 # 1GB hugepages (requires hardware support)

# Verify allocation
cat /proc/meminfo | grep HugePages_Free
```

### Disable Memory Balloon

Ballooning allows the hypervisor to reclaim guest memory dynamically. Disable for latency-sensitive workloads.

```bash
qm set <vmid> --balloon 0
```

### KSM (Kernel Same-page Merging)

Beneficial when running many identical VMs. Enabled by default on PVE.

```bash
# Check KSM status
cat /sys/kernel/mm/ksm/run           # 1 = enabled

# Tune KSM scan rate (pages per scan interval)
echo 1000 > /sys/kernel/mm/ksm/pages_to_scan

# Disable for performance-sensitive hosts
echo 0 > /sys/kernel/mm/ksm/run
```

---

## Disk I/O Optimisation

### Disk Stack Best Practices

| Layer | Recommended | Notes |
|---|---|---|
| SCSI controller | `virtio-scsi-single` | One controller per disk = max parallelism |
| I/O thread | `iothread=1` | One thread per disk, off main VM thread |
| SSD flag | `ssd=1` | Disables rotational hints, enables TRIM |
| Discard | `discard=on` | Passes TRIM commands to host storage |
| Cache (ZFS) | `cache=none` | ZFS has ARC; page cache would double-buffer |
| Cache (LVM-thin) | `cache=writeback` | Fast; use only with BBU or UPS |
| Cache (NFS) | `cache=none` or `cache=directsync` | Depends on NFS server durability |
| AIO mode | `aio=native` | Use with `cache=none` for native async I/O |
| AIO mode | `aio=io_uring` | PVE 7.2+ / kernel 5.10+ — lower latency |

```bash
# High-performance disk config (ZFS backend)
qm set <vmid> --scsi0 local-zfs:XX,iothread=1,ssd=1,discard=on,cache=none,aio=io_uring

# High-performance disk config (LVM-thin, with BBU/UPS)
qm set <vmid> --scsi0 local-lvm:XX,iothread=1,ssd=1,discard=on,cache=writeback

# Multiple disks: each gets its own iothread
qm set <vmid> --scsi0 local-lvm:50,iothread=1,ssd=1
qm set <vmid> --scsi1 local-lvm:100,iothread=1,ssd=1
```

### Inside the Guest: I/O Scheduler

```bash
# Check scheduler for virtio disk
cat /sys/block/vda/queue/scheduler
# For NVMe-backed virtio: use 'none' (passthrough)
echo none > /sys/block/vda/queue/scheduler

# Persistent (systemd udev rule)
cat > /etc/udev/rules.d/60-scheduler.rules << 'EOF'
ACTION=="add|change", KERNEL=="vd[a-z]", ATTR{queue/scheduler}="none"
EOF
```

### Storage-Specific Tuning

**ZFS on host:**
```bash
# Tune ARC size (default is 50% RAM — lower if host needs memory)
echo "options zfs zfs_arc_max=8589934592" > /etc/modprobe.d/zfs.conf  # 8GB cap
update-initramfs -u

# Disable access time
zfs set atime=off tank/data

# Compression (transparent, CPU-cheap, saves space on text/log VMs)
zfs set compression=lz4 tank/vms
```

**LVM-thin:**
```bash
# Check thin pool usage
lvs -a | grep thin
# Extend thin pool if needed
lvextend -L +50G /dev/vg/data-pool
```

---

## Network Optimisation

### VirtIO + Multiqueue

```bash
# Set queue count = number of vCPUs
qm set <vmid> --net0 virtio,bridge=vmbr0,queues=4

# Inside guest: apply matching channel count
sudo ethtool -L ens18 combined 4

# Make persistent (Ubuntu netplan doesn't set queues; use udev or systemd service)
cat > /etc/networkd-dispatcher/configured.d/virtio-queues << 'EOF'
#!/bin/bash
if [[ "$(ethtool -i $IFACE | grep driver)" == *"virtio"* ]]; then
    ethtool -L $IFACE combined 4
fi
EOF
chmod +x /etc/networkd-dispatcher/configured.d/virtio-queues
```

### Jumbo Frames (MTU 9000)

Only beneficial if the physical switch and all paths support jumbo frames.

```bash
# On Proxmox host bridge
ip link set vmbr0 mtu 9000

# In /etc/network/interfaces
iface vmbr0 inet static
    ...
    mtu 9000

# VM config
qm set <vmid> --net0 virtio,bridge=vmbr0,mtu=9000

# Inside guest netplan
network:
  ethernets:
    ens18:
      mtu: 9000
```

### Bridge Performance

```bash
# Disable bridge netfilter (improves forwarding throughput if PVE firewall is disabled)
echo "net.bridge.bridge-nf-call-iptables=0"  >> /etc/sysctl.d/pve-net.conf
echo "net.bridge.bridge-nf-call-ip6tables=0" >> /etc/sysctl.d/pve-net.conf
sysctl -p /etc/sysctl.d/pve-net.conf
```

---

## Host Kernel Tuning

```bash
# /etc/sysctl.d/99-pve-tuning.conf
cat > /etc/sysctl.d/99-pve-tuning.conf << 'EOF'
# VM memory overcommit
vm.overcommit_memory = 1
vm.swappiness = 10

# Increase inotify limits (needed for many small VMs)
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512

# Network buffers for high-throughput VMs
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Reduce dirty page writeback lag
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
EOF
sysctl -p /etc/sysctl.d/99-pve-tuning.conf
```

---

## Ubuntu Guest Checklist

After every new Ubuntu VM, run through this list:

```bash
# 1. Update system
sudo apt update && sudo apt full-upgrade -y

# 2. Install QEMU guest agent
sudo apt install -y qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# 3. Enable TRIM for SSD-backed disks
sudo systemctl enable --now fstrim.timer

# 4. Set I/O scheduler to 'none' for virtio disks
echo none | sudo tee /sys/block/vda/queue/scheduler

# 5. Set virtio NIC queues to match vCPU count (e.g. 4 vCPUs)
sudo ethtool -L ens18 combined 4

# 6. Install useful agents / tools
sudo apt install -y htop iotop nethogs sysstat ncdu

# 7. Configure NTP
sudo timedatectl set-ntp true
timedatectl status

# 8. If using ZFS storage on Proxmox host, ensure in-guest filesystem respects discard
sudo cat /etc/fstab  # check nobarrier is NOT set for ext4 (barrier needed for integrity)
```

---

## PCI/GPU Passthrough (VFIO)

```bash
# Step 1: Enable IOMMU in GRUB
# Intel: add "intel_iommu=on" to GRUB_CMDLINE_LINUX_DEFAULT
# AMD:   add "amd_iommu=on"
nano /etc/default/grub
update-grub && reboot

# Step 2: Load VFIO modules
echo "vfio" >> /etc/modules
echo "vfio_iommu_type1" >> /etc/modules
echo "vfio_pci" >> /etc/modules
echo "vfio_virqfd" >> /etc/modules
update-initramfs -u -k all

# Step 3: Blacklist host driver for GPU
echo "blacklist nouveau"   >> /etc/modprobe.d/blacklist.conf  # NVIDIA
echo "blacklist radeon"    >> /etc/modprobe.d/blacklist.conf  # AMD
echo "blacklist amdgpu"    >> /etc/modprobe.d/blacklist.conf

# Step 4: Find GPU PCI IDs
lspci -nn | grep -i "vga\|audio"
# e.g. 0000:01:00.0 VGA [10de:2204]

# Step 5: Bind GPU to VFIO
echo "options vfio-pci ids=10de:2204,10de:1aef" > /etc/modprobe.d/vfio.conf
update-initramfs -u && reboot

# Step 6: Add to VM
qm set <vmid> --machine q35
qm set <vmid> --cpu host,hidden=1  # hide KVM from NVIDIA driver
qm set <vmid> --hostpci0 0000:01:00,pcie=1,x-vga=1

# Verify IOMMU groups
for g in /sys/kernel/iommu_groups/*; do echo "Group $(basename $g)"; ls $g/devices/; done
```

---

## Monitoring & Performance Metrics

```bash
# Node-level performance
pvesh get /nodes/pve/status            # CPU, memory, load
pvesh get /nodes/pve/rrddata --timeframe hour --cf AVERAGE

# VM performance (1-hour average)
pvesh get /nodes/pve/qemu/200/rrddata --timeframe hour --cf AVERAGE | jq

# Storage I/O
iostat -x 1 5
iotop -o

# Network
iftop -i vmbr0
nethogs vmbr0

# Prometheus + Grafana (recommended for ongoing monitoring)
# PVE has built-in InfluxDB and Prometheus exporters:
# Datacenter > Metric Server > Add
pvesh post /cluster/metrics/server \
  --server prometheus-host --port 9091 \
  --type influxdb --proto http
```
