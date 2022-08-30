# hpc-monitor

Sends notifications and alerts to Manta-Slack


## Configuration

Save configuration in `hpc.conf` or pass a config file with the `--config` parameter.

The `data_folder` is used to store a temporary file that is saved every time a notification is sent. If another event happens before `notification_limit` seconds have passed, no notification is sent.


`storage_percent_warning` and `storage_percent_critical` are disk-usage percentages thresholds: if disk usage exceeds such values, a notification is sent.

```
[channels]
CH1 = https://hooks.slack.com/services/XXXXXX
CH2 = https://hooks.slack.com/services/XXXXXX
...
CHN = https://hooks.slack.com/services/XXXXXX

notification_limit = 0

[paths]
HDD1 = PATH_TO_MOUNTPOINT_HD1
HDD2 = PATH_TO_MOUNTPOINT_HD2
...
HDDN = PATH_TO_MOUNTPOINT_HDN

data_folder = PATH_TO_DATA_FOLDER

[thr]
storage_percent_warning = 10
storage_percent_critical = 90
```