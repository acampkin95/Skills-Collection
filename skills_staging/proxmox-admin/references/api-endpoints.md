# Proxmox VE REST API Endpoint Reference

> Base URL: `https://<host>:8006/api2/json`  
> Auth header: `Authorization: PVEAPIToken=USER@REALM!TOKENID=SECRET`  
> All endpoints also accessible via `pvesh` on the node.

---

## Access / Authentication

| Method | Path | Description |
|---|---|---|
| POST | `/access/ticket` | Obtain session ticket + CSRF token |
| GET | `/access/ticket` | Verify current ticket |
| PUT | `/access/password` | Change user password |
| GET | `/access/users` | List users |
| POST | `/access/users` | Create user |
| GET | `/access/users/{userid}` | Get user details |
| PUT | `/access/users/{userid}` | Update user |
| DELETE | `/access/users/{userid}` | Delete user |
| GET | `/access/users/{userid}/token` | List API tokens |
| POST | `/access/users/{userid}/token/{tokenid}` | Create API token |
| PUT | `/access/users/{userid}/token/{tokenid}` | Update token |
| DELETE | `/access/users/{userid}/token/{tokenid}` | Revoke token |
| GET | `/access/groups` | List groups |
| POST | `/access/groups` | Create group |
| GET | `/access/roles` | List roles |
| POST | `/access/roles` | Create role |
| GET | `/access/acl` | Get ACL tree |
| PUT | `/access/acl` | Set ACL entry |
| GET | `/access/realms` | List auth realms |

---

## Cluster

| Method | Path | Description |
|---|---|---|
| GET | `/cluster/resources` | All cluster resources (VMs, nodes, storage) |
| GET | `/cluster/status` | Cluster health summary |
| GET | `/cluster/nextid` | Suggest next available VMID |
| GET | `/cluster/config/nodes` | Cluster node list |
| GET | `/cluster/ha/status/current` | HA status |
| GET | `/cluster/ha/resources` | HA-managed resources |
| POST | `/cluster/ha/resources` | Add HA resource |
| PUT | `/cluster/ha/resources/{sid}` | Update HA resource |
| DELETE | `/cluster/ha/resources/{sid}` | Remove HA resource |
| GET | `/cluster/ha/groups` | HA groups |
| POST | `/cluster/ha/groups` | Create HA group |
| GET | `/cluster/firewall/rules` | Cluster firewall rules |
| POST | `/cluster/firewall/rules` | Create firewall rule |
| GET | `/cluster/firewall/options` | Cluster firewall options |
| PUT | `/cluster/firewall/options` | Update firewall options |
| GET | `/cluster/backup` | Backup job list |
| POST | `/cluster/backup` | Create backup job |
| GET | `/cluster/sdn/vnets` | SDN virtual networks |
| GET | `/cluster/sdn/zones` | SDN zones |
| GET | `/cluster/options` | Datacenter options |
| PUT | `/cluster/options` | Update datacenter options |
| GET | `/cluster/notifications/targets` | Notification targets |

---

## Nodes

| Method | Path | Description |
|---|---|---|
| GET | `/nodes` | List nodes |
| GET | `/nodes/{node}` | Node info |
| GET | `/nodes/{node}/status` | Node hardware status |
| POST | `/nodes/{node}/status` | Reboot / shutdown node |
| GET | `/nodes/{node}/time` | Node time |
| GET | `/nodes/{node}/version` | PVE version on node |
| GET | `/nodes/{node}/tasks` | Task history |
| GET | `/nodes/{node}/tasks/{upid}/status` | Task status |
| GET | `/nodes/{node}/tasks/{upid}/log` | Task log |
| GET | `/nodes/{node}/subscription` | Subscription status |
| GET | `/nodes/{node}/network` | Network interfaces |
| POST | `/nodes/{node}/network/reload` | Apply network config |
| GET | `/nodes/{node}/dns` | DNS config |
| PUT | `/nodes/{node}/dns` | Update DNS config |
| GET | `/nodes/{node}/certificates/info` | TLS certificates |
| POST | `/nodes/{node}/certificates/acme/certificate` | Order ACME cert |
| DELETE | `/nodes/{node}/certificates/custom` | Remove custom cert |
| GET | `/nodes/{node}/disks/list` | Physical disks |
| GET | `/nodes/{node}/disks/smart` | SMART data |
| POST | `/nodes/{node}/disks/initgpt` | Init disk GPT |
| GET | `/nodes/{node}/storage` | Storage on this node |
| GET | `/nodes/{node}/storage/{storage}/content` | Storage content |
| POST | `/nodes/{node}/storage/{storage}/upload` | Upload ISO/template |
| DELETE | `/nodes/{node}/storage/{storage}/content/{volume}` | Delete volume |

---

## QEMU/KVM Virtual Machines

| Method | Path | Description |
|---|---|---|
| GET | `/nodes/{node}/qemu` | List VMs |
| POST | `/nodes/{node}/qemu` | Create VM |
| GET | `/nodes/{node}/qemu/{vmid}/config` | VM config (current) |
| PUT | `/nodes/{node}/qemu/{vmid}/config` | Update VM config |
| POST | `/nodes/{node}/qemu/{vmid}/config` | Update (async) |
| DELETE | `/nodes/{node}/qemu/{vmid}` | Delete VM |
| GET | `/nodes/{node}/qemu/{vmid}/status/current` | Runtime status |
| POST | `/nodes/{node}/qemu/{vmid}/status/start` | Start VM |
| POST | `/nodes/{node}/qemu/{vmid}/status/stop` | Hard stop |
| POST | `/nodes/{node}/qemu/{vmid}/status/shutdown` | Graceful shutdown |
| POST | `/nodes/{node}/qemu/{vmid}/status/reboot` | Reboot |
| POST | `/nodes/{node}/qemu/{vmid}/status/reset` | Hard reset |
| POST | `/nodes/{node}/qemu/{vmid}/status/suspend` | Suspend |
| POST | `/nodes/{node}/qemu/{vmid}/status/resume` | Resume |
| POST | `/nodes/{node}/qemu/{vmid}/migrate` | Migrate VM |
| POST | `/nodes/{node}/qemu/{vmid}/clone` | Clone VM |
| POST | `/nodes/{node}/qemu/{vmid}/template` | Convert to template |
| GET | `/nodes/{node}/qemu/{vmid}/snapshot` | List snapshots |
| POST | `/nodes/{node}/qemu/{vmid}/snapshot` | Create snapshot |
| POST | `/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/rollback` | Rollback |
| DELETE | `/nodes/{node}/qemu/{vmid}/snapshot/{snapname}` | Delete snapshot |
| GET | `/nodes/{node}/qemu/{vmid}/resize` | — |
| PUT | `/nodes/{node}/qemu/{vmid}/resize` | Resize disk |
| GET | `/nodes/{node}/qemu/{vmid}/cloudinit` | Cloud-init config |
| PUT | `/nodes/{node}/qemu/{vmid}/cloudinit` | Update cloud-init |
| GET | `/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces` | Guest IPs |
| POST | `/nodes/{node}/qemu/{vmid}/agent/exec` | Exec in guest |
| GET | `/nodes/{node}/qemu/{vmid}/firewall/rules` | VM firewall rules |
| POST | `/nodes/{node}/qemu/{vmid}/firewall/rules` | Add firewall rule |
| GET | `/nodes/{node}/qemu/{vmid}/pending` | Pending config changes |
| GET | `/nodes/{node}/qemu/{vmid}/rrd` | RRD performance data |
| GET | `/nodes/{node}/qemu/{vmid}/rrddata` | RRD data points |

---

## LXC Containers

| Method | Path | Description |
|---|---|---|
| GET | `/nodes/{node}/lxc` | List containers |
| POST | `/nodes/{node}/lxc` | Create container |
| GET | `/nodes/{node}/lxc/{vmid}/config` | CT config |
| PUT | `/nodes/{node}/lxc/{vmid}/config` | Update CT config |
| DELETE | `/nodes/{node}/lxc/{vmid}` | Delete container |
| GET | `/nodes/{node}/lxc/{vmid}/status/current` | CT status |
| POST | `/nodes/{node}/lxc/{vmid}/status/start` | Start CT |
| POST | `/nodes/{node}/lxc/{vmid}/status/stop` | Stop CT |
| POST | `/nodes/{node}/lxc/{vmid}/status/shutdown` | Graceful shutdown |
| POST | `/nodes/{node}/lxc/{vmid}/status/reboot` | Reboot CT |
| POST | `/nodes/{node}/lxc/{vmid}/migrate` | Migrate CT |
| POST | `/nodes/{node}/lxc/{vmid}/clone` | Clone CT |
| GET | `/nodes/{node}/lxc/{vmid}/snapshot` | List snapshots |
| POST | `/nodes/{node}/lxc/{vmid}/snapshot` | Create snapshot |
| POST | `/nodes/{node}/lxc/{vmid}/snapshot/{snapname}/rollback` | Rollback |
| PUT | `/nodes/{node}/lxc/{vmid}/resize` | Resize CT disk |
| GET | `/nodes/{node}/lxc/{vmid}/interfaces` | Network interfaces |

---

## Storage

| Method | Path | Description |
|---|---|---|
| GET | `/storage` | List all storage |
| POST | `/storage` | Add storage |
| GET | `/storage/{storageid}` | Storage config |
| PUT | `/storage/{storageid}` | Update storage |
| DELETE | `/storage/{storageid}` | Remove storage |
| GET | `/nodes/{node}/storage` | Node storage list |
| POST | `/nodes/{node}/storage/{storage}/prunebackups` | Prune backups |

---

## Ceph

| Method | Path | Description |
|---|---|---|
| GET | `/nodes/{node}/ceph/status` | Ceph cluster status |
| GET | `/nodes/{node}/ceph/osd` | List OSDs |
| POST | `/nodes/{node}/ceph/osd` | Create OSD |
| DELETE | `/nodes/{node}/ceph/osd/{osdid}` | Remove OSD |
| GET | `/nodes/{node}/ceph/pools` | List pools |
| POST | `/nodes/{node}/ceph/pools` | Create pool |
| GET | `/nodes/{node}/ceph/mon` | List monitors |
| POST | `/nodes/{node}/ceph/mon/{monid}` | Create monitor |
| POST | `/nodes/{node}/ceph/init` | Initialise Ceph |
| POST | `/nodes/{node}/ceph/stop` | Stop Ceph services |
| POST | `/nodes/{node}/ceph/start` | Start Ceph services |
| POST | `/nodes/{node}/ceph/restart` | Restart Ceph service |

---

## Firewall

| Method | Path | Description |
|---|---|---|
| GET | `/cluster/firewall/rules` | Cluster rules |
| POST | `/cluster/firewall/rules` | Add cluster rule |
| GET | `/cluster/firewall/ipset` | IP sets |
| POST | `/cluster/firewall/ipset` | Create IP set |
| GET | `/nodes/{node}/firewall/rules` | Node rules |
| GET | `/nodes/{node}/qemu/{vmid}/firewall/rules` | VM rules |
| POST | `/nodes/{node}/qemu/{vmid}/firewall/rules` | Add VM rule |
| GET | `/nodes/{node}/qemu/{vmid}/firewall/log` | VM firewall log |

---

## Backup

| Method | Path | Description |
|---|---|---|
| GET | `/cluster/backup` | List backup jobs |
| POST | `/cluster/backup` | Create backup job |
| GET | `/cluster/backup/{id}` | Get backup job |
| PUT | `/cluster/backup/{id}` | Update backup job |
| DELETE | `/cluster/backup/{id}` | Delete backup job |
| GET | `/nodes/{node}/vzdump/defaults` | vzdump defaults |
| POST | `/nodes/{node}/vzdump` | Run vzdump now |
| POST | `/nodes/{node}/storage/{storage}/prunebackups` | Prune backups |

---

## pvesh Usage

```bash
# Interactive shell
pvesh

# One-off commands
pvesh get /nodes                         # list nodes
pvesh get /cluster/resources             # all resources
pvesh get /nodes/pve/qemu                # VMs on 'pve'
pvesh get /nodes/pve/qemu/200/config     # VM 200 config
pvesh create /nodes/pve/qemu/200/status/start   # start VM 200
pvesh set /nodes/pve/qemu/200/config -cores 4   # update config

# Output formats
pvesh get /nodes --output-format json-pretty
pvesh get /nodes --output-format yaml
pvesh get /cluster/resources --output-format table
```
