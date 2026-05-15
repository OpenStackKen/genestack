---
title: "Basic Use Cases"
weight: 30
---

Here are some basic Freezer use cases.  For more extensive documentation and troubleshooting, see the [Backup Retention Policy](backup-retention.md) documentation.

### Create Freezer Jobs

Similar to cronjobs, freezer jobs are an abstraction to schedule specific backups at a pre-defined time.

Create job description `temp-job.json`:

```json
{
    "description": "Test-0001",
    "job_id": "9999",
    "job_schedule": {
        "schedule_interval": "5 minutes",
        "status": "scheduled",
        "event": "start"
    },
    "job_actions": [
        {
            "max_retries": 5,
            "max_retries_interval": 6,
            "freezer_action": {
                "backup_name": "test0001_backup",
                "container": "test0001_container",
                "no_incremental": true,
                "path_to_backup": "/home/ubuntu/fvenv-orig",
                "log_file": "/home/ubuntu/job-9999.log",
                "snapshot": true,
                "action": "backup",
                "remove_older_than": 365
            }
        }
     ]
}
```

#### Create a Job Using this Definition

> [!command]
>
> ```bash
> freezer job-create \
>     --file temp-job.json \
>     -C backup-client-vm \
>     --log-file temp_log4.log
> ```

> [!output]
>
> ```bash
> Job 9999 created
> ```


#### List the Jobs

> [!command]
>
> ```bash
> freezer job-list
> ```

> [!output]
>
> ```bash
> +--------+-------------+-----------+--------+-----------+-------+------------+
> | Job ID | Description | # Actions | Result | Status    | Event | Session ID |
> +--------+-------------+-----------+--------+-----------+-------+------------+
> | 9999   | Test-0001   |         1 |        | scheduled | start |            |
> +--------+-------------+-----------+--------+-----------+-------+------------+
> ```

#### Show Jobs

> [!command]
>
> ```bash
> freezer job-show 9999
> ```

> [!output]
>
> ```bash
> +-------------+--------------------------------------------------------------+
> | Field       | Value                                                        |
> +-------------+--------------------------------------------------------------+
> | Job ID      | 9999                                                         |
> | Client ID   | backup-client-vm                                             |
> | User ID     | e555ac7d0249475dbedf37b7861d1324                             |
> | Session ID  |                                                              |
> | Description | Test-0001                                                    |
> | Actions     | [{'action_id': 'e04dff39eec344a693cd344ada063948',           |
> |             |   'freezer_action': {'action': 'backup',                     |
> |             |                      'backup_name': 'test0001_backup',       |
> |             |                      'container': 'test0001_container',      |
> |             |                      'log_file': '/home/ubuntu/job0001.log', |
> |             |                      'no_incremental': True,                 |
> |             |                      'path_to_backup': '/etc/',              |
> |             |                      'remove_older_than': 365,               |
> |             |                      'snapshot': True},                      |
> |             |   'max_retries': 5,                                          |
> |             |   'max_retries_interval': 6,                                 |
> |             |   'project_id': '76c5a4cbf1074460bfdcc261340c6cbe',          |
> |             |   'user_id': 'e555ac7d0249475dbedf37b7861d1324'}]            |
> | Start Date  |                                                              |
> | End Date    |                                                              |
> | Interval    | 5 minutes                                                    |
> | Status      | scheduled                                                    |
> | Result      |                                                              |
> | Current pid |                                                              |
> | Event       | start                                                        |
> +-------------+--------------------------------------------------------------+
> ```

#### Update the Job with Changed Log Filename and `path_to_backup`

> [!command]
>
> ```bash
> freezer job-update 9999 temp-job.json
>
> freezer job-start 9999
> ```

> [!output]
>
> ```bash
> Job 9999 updated
>
> Start request sent for job 9999
> ```

### Create VM Backups

VM backups can be created locally (on same freezer-client VM storage) or remotely (in Swift object storage connected to Openstack Cluster)

#### Backup VM to Local Storage

Backup destination local storage/VM disk. Make a note of the VM UUID which you would like to backup.

```bash
freezer-agent \
        --action backup \
        --nova-inst-id 7ee5959f-0039-4f5f-b953-25ef38b1a88e \
        --storage local \
        --container /home/ubuntu/freezer-bkp-qcow/ \
        --backup-name qcow-vm-bkp \
        --mode nova \
        --engine nova --no-incremental true \
        --log-file qcow-vm-bkp.log
```

> [!example] 
> 
> Output in TABULAR format

```bash
+----------------------+---------------------------------+
|       Property       |              Value              |
+----------------------+---------------------------------+
|  curr backup level   |                0                |
|     fs real path     |               None              |
|    vol snap path     |               None              |
|      client os       |              linux              |
|    client version    |              16.0.0             |
|      time stamp      |            1759828011           |
|        action        |              backup             |
|     always level     |                                 |
|     backup media     |               nova              |
|     backup name      |           qcow-vm-bkp           |
|      container       |  /home/ubuntu/freezer-bkp-qcow/ |
|  container segments  |                                 |
|       dry run        |                                 |
|       hostname       |          freezer-client         |
|    path to backup    |                                 |
|      max level       |                                 |
|         mode         |               nova              |
|       log file       |          qcow-vm-bkp.log        |
|       storage        |              local              |
|        proxy         |                                 |
|     compression      |               gzip              |
|       ssh key        |     /home/ubuntu/.ssh/id_rsa    |
|     ssh username     |                                 |
|       ssh host       |                                 |
|       ssh port       |                22               |
| consistency checksum |                                 |
+----------------------+---------------------------------+
```

**Check local backup directory structure**

> [!command]
>
> ```bash
> tree /home/ubuntu/freezer-bkp-qcow/
> ```

> [!output]
>
> ```bash
> /home/ubuntu/freezer-bkp-qcow/
> ├── data
> │   └── nova
> │       └── freezer-client_demo-hclab-qcow-vm-bkp
> │           └── 7ee5959f-0039-4f5f-b953-25ef38b1a88e
> │               └── 1759828011
> │                   └── 0_1759828011
> │                       ├── data
> │                       └── engine_metadata
> └── metadata
> └── nova
>         └── freezer-client_demo-hclab-qcow-vm-bkp
>         └── 7ee5959f-0039-4f5f-b953-25ef38b1a88e
>                 └── 1759828011
>                 └── 0_1759828011
>                         └── metadata
>
> 13 directories, 3 files
> ```

#### Backup QCOW2 image based VMs to Swift

```bash
freezer-agent \
        --action backup \
        --nova-inst-id 97dfb7df-1b9b-4848-a7d5-840467af5b66 \
        --storage swift \
        --container freezer-bkp-cirros \
        --backup-name freezer-bkp-cirros \
        --mode nova \
        --engine nova \
        --no-incremental true \
        --log-file freezer-bkp-cirros.log
```

#### Restore QCOW2 image based VM from Swift to Openstack Cluster

```bash
freezer-agent \
        --action restore \
        --nova-inst-id 97dfb7df-1b9b-4848-a7d5-840467af5b66 \
        --storage swift  \
        --container freezer-bkp-cirros \
        --backup-name freezer-bkp-cirros \
        --mode nova \
        --engine nova \
        --noincremental \
        --log-file freezer-restore-cirros.log
```

#### Cinder Volume backup to Swift

```bash
freezer-agent \
        --action backup \
        --cinder-vol-id 2453735e-678a-4b4a-8604-b79b55c2cd21 \
        --storage swift \
        --container freezer-bkp-cinder \
        --backup-name freezer-bkp-cinder \
        --mode cinder \
        --log-file freezer-bkp-cinder.log
```

#### Cinder Volume restore from Swift to Openstack Cluster

```bash
freezer-agent \
        --action restore \
        --mode cinder \
        --cinder-vol-id 2453735e-678a-4b4a-8604-b79b55c2cd21 \
        --storage swift \
        --container freezer-bkp-cinder \
        --backup-name freezer-bkp-cinder \
        --log-file freezer-restore-cinder.log
```

---

### MongoDB backup to Swift

In this case, mongoDB's LVM (where mongoDB LVM volume is mounted) is backed up.

> [!warning]
>
> **MongoDB Operations:** Make sure you quiesce any DB operations by stopping the mongodb service momentarily and then restarting it once the backup is completed.

> [!note]
>
> Freezer commands can only be run from inside the virtual environment.

```bash
sudo systemctl stop mongod
sudo systemctl status mongod

freezer-agent \
        --action backup \
        --lvm-srcvol /dev/mongo/mongo-1 \
        --lvm-volgroup mongo \
        --lvm-snapsize 2G \
        --lvm-snap-perm ro \
        --lvm-dirmount /tmp/lvm-snapshot-backup  \
        --path-to-backup /tmp/lvm-snapshot-backup \
        --storage swift \
        --container mongo-bkp-lvm \
        --backup-name mongo-bkp-lvm \
        --log-file mongo-bkp-lvm.log

sudo systemctl start mongod
sudo systemctl status mongod
```

### MongoDB restore from Swift

Restore operation involves quiescing mongoDB operations by stopping the mongodb service momentarily and then restarting it once the backup is completed.

```bash
sudo systemctl stop mongod
sudo systemctl status mongod

mkdir -p /tmp/mongodb-restore

# Restore timestamp can be fetched by querying the swift objects in the backup container like below.
# Swift authenticates using the S3 credentials available on Freezer-client VM.

swift list --lh freezer-bkp-mongo-lvm

# Note the timestamp of the first object in the container.

freezer-agent \
        --action restore \
        --mode mongo \
        --restore-from-date "2026-01-20T07:43:59" \
        --restore-abs-path /tmp/mongodb-restore  \
        --storage swift \
        --container freezer-bkp-mongo-lvm \
        --backup-name freezer-bkp-mongo-lvm \
        --encrypt-pass-file /home/ubuntu/mongo-test/encryption-key.txt \
        --log-file freezer-bkp-mongo-lvm-rstr.log

sudo rsync -a /tmp/mongodb-restore/ /var/lib/mongodb/
sudo chown -R mongodb:mongodb /var/lib/mongodb

sudo systemctl start mongod
sudo systemctl status mongod
```

### MySQL Backup to Swift

In this case MySQL is first backed up locally in a temp location and then backup is uploaded to Swift.

> [!warning]
>
> **MySQL DB Operations:** Make sure you quiesce any DB operations by stopping the mysql service momentarily and then restarting it once the backup is completed.

```bash
sudo systemctl stop mysql
sudo systemctl status mysql

mkdir -p /tmp/mysql-backup

freezer-agent \
        --action backup \
        --mode mysql \
        --mysql-conf /etc/mysql/conf.d/backup.cnf \
        --path-to-backup /tmp/mysql-backup \
        --storage swift \
        --container freezer-bkp-mysql \
        --backup-name freezer-bkp-mysql \
        --log-file freezer-bkp-mysql.log

sudo rsync -a /tmp/mysql-backup/ /var/lib/mysql/
sudo chown -R mysql:mysql /var/lib/mysql

sudo systemctl start mysql.service
sudo systemctl status mysql.service
```

### MySQL Restore from Swift

Restore operation involves quiescing MySQL operations by stopping the mysql service momentarily and then restarting it once the restore is completed.

> [!note]
>
> Here are some things to note about using Swift:
> - Restore timestamp can be fetched by querying the swift objects in the backup container like below.
> - Swift authenticates using the S3 credentials available on Freezer-client VM.

```bash
sudo systemctl stop mysql
sudo systemctl status mysql

mkdir -p /tmp/mysql-restore

swift list --lh freezer-bkp-mysql

# Note the timestamp of the first object in the container.

freezer-agent \
        --action restore \
        --mode mysql \
        --mysql-conf /etc/mysql/conf.d/backup.cnf \
        --restore-from-date "2026-01-16T08:15:22" \
        --restore-abs-path /tmp/mysql-restore \
        --storage swift \
        --container freezer-bkp-mysql \
        --backup-name freezer-bkp-mysql \
        --log-file freezer-bkp-mysql.log

sudo rsync -a /tmp/mysql-restore/ /var/lib/mysql/
sudo chown -R mysql:mysql /var/lib/mysql

sudo systemctl start mysql.service
sudo systemctl status mysql.service
```

### Filesystem Backup to Swift

Local filesystem directory/files can be backed up to swift object store.

```bash
freezer-agent \
        --action backup \
        --mode fs \
        --path-to-backup /home/ubuntu/freezer-git-repo/freezer/ \
        --storage swift \
        --container freezer-bkp-fs \
        --backup-name freezer-bkp-fs \
        --compression gzip \
        --log-file freezer-bkp-fs.log
```

### Creating Sessions

A session acts as a high-level container that groups related backup and restore actions. It provides a unique identifier and metadata that applies to all jobs executed within it.

When you create a job, you typically want that job's executions to be tied to a specific session. This makes management easier, especially during recovery, as you can see all backup runs related to a single project or time period under one session ID.

#### Create a session config file on the Freezer Client:

> [!example]
>
> Sample `session_file.json`

```json title="session_file.json"
{
    "description": "Local Storage VM Backup Session",
    "name": "local_vm_backup",
    "freezer_session_version": 2,
    "jobs": [
        "local_storage_vm_job"
    ],
    "schedule": {
        "schedule_date": "2025-10-07T13:31:00Z"
    }
}
```

#### Register the session:

> [!command]
>
> ```bash
> freezer session-create --file session_file.json
>
> freezer session-list
> ```

> [!output]
>
> ```text
> Session c6a7fcfd06134b788f0a34e8454174b1 created
>
> +----------------------------------+---------------------------------+--------+--------+--------+
> | Session ID                       | Description                     | Status | Result | # Jobs |
> +----------------------------------+---------------------------------+--------+--------+--------+
> | c6a7fcfd06134b788f0a34e8454174b1 | Local Storage VM Backup Session | active | None   |      0 |
> +----------------------------------+---------------------------------+--------+--------+--------+
> ```

> [!note]
>
> Note the session-id from above!

#### Add an existing job to this session (job-id's are arbitrary):

```bash
freezer session-add-job \
        --session-id c6a7fcfd06134b788f0a34e8454174b1 \
        --job-id 9999
```

#### Start a session with a specific job (job-* are arbitrary):

> [!command]
>
> ```bash
> freezer session-start \
>         --session-id c6a7fcfd06134b788f0a34e8454174b1 \
>         --job-id 9999 \
>         --job-tag 0
> ```

> [!output]
>
> ```text
> Session c6a7fcfd06134b788f0a34e8454174b1 start requested
> ```

### Backup Retention Policy

Freezer backups stored in Swift can accumulate over time. The `swift_retention_policy.py`
script automates object expiration and container cleanup for Freezer backup containers.

> [!info]
>
> **Location**
>
> The script is located at `scripts/freezer_retention/swift_retention_policy.py` in the [Genestack repository](https://github.com/rackerlabs/genestack/tree/main/scripts).

> [!note]
>
> This script has only been tested with Freezer backup containers created in Swift, but should work with any S3 compatible containers and objects.

#### Prerequisites

```bash
pip install python-swiftclient
source ~/openrc
swift list
```

#### Quick Start

```bash
chmod +x scripts/freezer_retention/swift_retention_policy.py
```

**Set expiration and auto-cleanup**

```bash
./swift_retention_policy.py -c freezer-bkp-lvm -m 5 --cleanup
```

**Multiple containers**

```bash
./swift_retention_policy.py -c freezer-daily -c freezer-weekly -H 1 --cleanup
```

**Set expiration only (no cleanup)**

```bash
./swift_retention_policy.py -c freezer-bkp-lvm -d 7
```

**Dry run**

```bash
./swift_retention_policy.py -c freezer-bkp-lvm -m 5 --cleanup --dry-run
```

> [!example]
>
> **All available options**

```
Time Options:
  -s, --seconds N           Delete after N seconds
  -m, --minutes N           Delete after N minutes
  -H, --hours N             Delete after N hours
  -d, --days N              Delete after N days
  -M, --months N            Delete after N months
  -t, --delete-at UNIX      Delete at specific timestamp

Cleanup Options:
  --cleanup                 Monitor and delete containers when empty
  --check-interval SECONDS  Seconds between checks (default: 60)
  --max-wait SECONDS        Maximum time to wait (default: 3600)

Other Options:
  --dry-run                 Show what would be done
  -v, --verbose             Verbose output
```

#### How It Works

The script operates in two phases:

1. Sets `X-Delete-At` headers on all objects in the specified containers
2. Monitors containers and automatically deletes them once empty (when `--cleanup` is used)

| Container Status | Description | Auto-Delete? |
|------------------|-------------|:------------:|
| `empty` | No objects remaining | Yes |
| `not_found` | Container does not exist | N/A |
| `has_permanent_objects` | Objects without `X-Delete-At` | No |
| `waiting_for_expiration` | Objects not yet past expiry | No |
| `waiting_for_expirer` | Expired but not yet removed by Swift | No |

> [!tip]
>
> Here are som recommended check intervals

| Expiration Window | Check Interval |
|-------------------|----------------|
| < 10 minutes | 30-60 seconds |
| 1-24 hours | 5-15 minutes |
| > 1 day | 30-60 minutes |

```bash
# Short expiration
./swift_retention_policy.py -c container -m 5 --cleanup --check-interval 30

# Long expiration
./swift_retention_policy.py -c container -d 1 --cleanup --check-interval 1800
```

> [!warning]
>
> Don't forget to set a max wait time

Prevent the script from running indefinitely:

```bash
./swift_retention_policy.py -c container -m 5 --cleanup --max-wait 3600
```
