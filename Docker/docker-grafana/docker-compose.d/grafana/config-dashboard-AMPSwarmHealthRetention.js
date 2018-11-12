{
  "Dashboard":
  {
    "id": null,
    "title": "AMP Swarm Health Historical",
    "originalTitle": "AMP Swarm Health Historical",
    "tags": [],
    "style": "dark",
    "timezone": "browser",
    "editable": true,
    "hideControls": false,
    "sharedCrosshair": false,
    "rows": [
      {
        "collapse": false,
        "editable": true,
        "height": "",
        "panels": [],
        "showTitle": false,
        "title": "DockerLevel"
      },
      {
        "collapse": false,
        "editable": true,
        "height": "250px",
        "panels": [
          {
            "aliasColors": {},
            "bars": false,
            "datasource": null,
            "editable": true,
            "error": false,
            "fill": 1,
            "grid": {
              "threshold1": null,
              "threshold1Color": "rgba(216, 200, 27, 0.27)",
              "threshold2": null,
              "threshold2Color": "rgba(234, 112, 112, 0.22)"
            },
            "id": 1,
            "legend": {
              "avg": false,
              "current": false,
              "max": false,
              "min": false,
              "show": true,
              "total": false,
              "values": false,
              "rightSide": false,
              "sideWidth": 200,
              "alignAsTable": false
            },
            "lines": true,
            "linewidth": 2,
            "links": [],
            "nullPointMode": "connected",
            "percentage": false,
            "pointradius": 5,
            "points": false,
            "renderer": "flot",
            "seriesOverrides": [],
            "span": 12,
            "stack": false,
            "steppedLine": false,
            "targets": [
              {
                "alias": "$tag_container_name",
                "dsType": "influxdb",
                "fields": [
                  {
                    "func": "mean",
                    "name": "usage_percent"
                  }
                ],
                "groupBy": [
                  {
                    "interval": "auto",
                    "params": [
                      "auto"
                    ],
                    "type": "time"
                  },
                  {
                    "key": "datacenter",
                    "params": [
                      "datacenter"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "host",
                    "params": [
                      "host"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "container_name",
                    "params": [
                      "container_name"
                    ],
                    "type": "tag"
                  }
                ],
                "hide": false,
                "measurement": "docker_container_mem",
                "policy": "default",
                "query": "SELECT mean(mean_usage_percent)  as usage FROM $Retention.\"downsampled_docker_container_mem\" WHERE   \"container_name\" =~ /$ContainerName/ and \"datacenter\" =~ /$DataCenter/  and \"host\" =~ /$HostName/  and   $timeFilter GROUP BY time($interval), \"container_name\", \"datacenter\", \"host\"",
                "rawQuery": true,
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                  [
                    {
                      "params": [
                        "usage_percent"
                      ],
                      "type": "field"
                    },
                    {
                      "params": [],
                      "type": "mean"
                    }
                  ]
                ],
                "tags": []
              }
            ],
            "timeFrom": null,
            "timeShift": null,
            "title": "AMP Memory Utilization",
            "tooltip": {
              "msResolution": false,
              "shared": true,
              "value_type": "cumulative"
            },
            "type": "graph",
            "xaxis": {
              "show": true
            },
            "yaxes": [
              {
                "format": "short",
                "label": "Percentage",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              },
              {
                "format": "short",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              }
            ]
          },
          {
            "aliasColors": {},
            "bars": false,
            "datasource": null,
            "editable": true,
            "error": false,
            "fill": 1,
            "grid": {
              "threshold1": null,
              "threshold1Color": "rgba(216, 200, 27, 0.27)",
              "threshold2": null,
              "threshold2Color": "rgba(234, 112, 112, 0.22)"
            },
            "id": 5,
            "legend": {
              "avg": false,
              "current": false,
              "max": false,
              "min": false,
              "show": true,
              "total": false,
              "values": false
            },
            "lines": true,
            "linewidth": 2,
            "links": [],
            "nullPointMode": "connected",
            "percentage": false,
            "pointradius": 5,
            "points": false,
            "renderer": "flot",
            "seriesOverrides": [],
            "span": 12,
            "stack": false,
            "steppedLine": false,
            "targets": [
              {
                "alias": "$tag_container_name",
                "dsType": "influxdb",
                "fields": [
                  {
                    "func": "mean",
                    "name": "usage_percent"
                  }
                ],
                "groupBy": [
                  {
                    "interval": "auto",
                    "params": [
                      "auto"
                    ],
                    "type": "time"
                  },
                  {
                    "key": "datacenter",
                    "params": [
                      "datacenter"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "host",
                    "params": [
                      "host"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "container_name",
                    "params": [
                      "container_name"
                    ],
                    "type": "tag"
                  }
                ],
                "hide": false,
                "measurement": "docker_container_cpu",
                "policy": "default",
                "query": "SELECT mean(\"mean_usage_percent\") FROM $Retention.\"downsampled_docker_container_cpu\" WHERE  cpu = 'cpu-total' and  \"container_name\" =~ /$ContainerName/ and \"datacenter\" =~ /$DataCenter/  and \"host\" =~ /$HostName/ and $timeFilter GROUP BY time($interval), \"datacenter\", \"host\", \"container_name\"",
                "rawQuery": true,
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                  [
                    {
                      "params": [
                        "usage_percent"
                      ],
                      "type": "field"
                    },
                    {
                      "params": [],
                      "type": "mean"
                    }
                  ]
                ],
                "tags": []
              }
            ],
            "timeFrom": null,
            "timeShift": null,
            "title": "AMP CPU Utilization",
            "tooltip": {
              "msResolution": false,
              "shared": true,
              "value_type": "cumulative"
            },
            "type": "graph",
            "xaxis": {
              "show": true
            },
            "yaxes": [
              {
                "format": "short",
                "label": "Percentage",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              },
              {
                "format": "short",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              }
            ]
          },
          {
            "aliasColors": {},
            "bars": false,
            "datasource": null,
            "editable": true,
            "error": false,
            "fill": 1,
            "grid": {
              "threshold1": null,
              "threshold1Color": "rgba(216, 200, 27, 0.27)",
              "threshold2": null,
              "threshold2Color": "rgba(234, 112, 112, 0.22)"
            },
            "id": 6,
            "legend": {
              "avg": false,
              "current": false,
              "max": false,
              "min": false,
              "show": true,
              "total": false,
              "values": false
            },
            "lines": true,
            "linewidth": 2,
            "links": [],
            "nullPointMode": "connected",
            "percentage": false,
            "pointradius": 5,
            "points": false,
            "renderer": "flot",
            "seriesOverrides": [],
            "span": 12,
            "stack": false,
            "steppedLine": false,
            "targets": [
              {
                "alias": "$tag_container_name",
                "dsType": "influxdb",
                "fields": [
                  {
                    "func": "mean",
                    "name": "usage_percent"
                  }
                ],
                "groupBy": [
                  {
                    "interval": "auto",
                    "params": [
                      "auto"
                    ],
                    "type": "time"
                  },
                  {
                    "key": "datacenter",
                    "params": [
                      "datacenter"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "host",
                    "params": [
                      "host"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "container_name",
                    "params": [
                      "container_name"
                    ],
                    "type": "tag"
                  }
                ],
                "hide": false,
                "measurement": "docker_container_cpu",
                "policy": "default",
                "query": "SELECT non_negative_derivative(last(\"io_service_bytes_recursive_total\"))/1000 FROM \"docker_container_blkio\" WHERE  \"container_name\" =~ /$ContainerName/ and \"datacenter\" =~ /$DataCenter/  and \"host\" =~ /$HostName/ and $timeFilter GROUP BY time($interval), \"datacenter\", \"host\", \"container_name\"",
                "rawQuery": true,
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                  [
                    {
                      "params": [
                        "usage_percent"
                      ],
                      "type": "field"
                    },
                    {
                      "params": [],
                      "type": "mean"
                    }
                  ]
                ],
                "tags": []
              }
            ],
            "timeFrom": null,
            "timeShift": null,
            "title": "AMP Block I/O Utilization",
            "tooltip": {
              "msResolution": false,
              "shared": true,
              "value_type": "cumulative"
            },
            "type": "graph",
            "xaxis": {
              "show": true
            },
            "yaxes": [
              {
                "format": "short",
                "label": "Mega Bytes",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              },
              {
                "format": "short",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              }
            ]
          },
          {
            "aliasColors": {},
            "bars": false,
            "datasource": null,
            "editable": true,
            "error": false,
            "fill": 1,
            "grid": {
              "threshold1": null,
              "threshold1Color": "rgba(216, 200, 27, 0.27)",
              "threshold2": null,
              "threshold2Color": "rgba(234, 112, 112, 0.22)"
            },
            "id": 7,
            "legend": {
              "avg": false,
              "current": false,
              "max": false,
              "min": false,
              "show": true,
              "total": false,
              "values": false
            },
            "lines": true,
            "linewidth": 2,
            "links": [],
            "nullPointMode": "connected",
            "percentage": false,
            "pointradius": 5,
            "points": false,
            "renderer": "flot",
            "seriesOverrides": [],
            "span": 12,
            "stack": false,
            "steppedLine": false,
            "targets": [
              {
                "alias": "$tag_container_name:rx_bytes",
                "dsType": "influxdb",
                "fields": [
                  {
                    "func": "mean",
                    "name": "usage_percent"
                  }
                ],
                "groupBy": [
                  {
                    "interval": "auto",
                    "params": [
                      "auto"
                    ],
                    "type": "time"
                  },
                  {
                    "key": "datacenter",
                    "params": [
                      "datacenter"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "host",
                    "params": [
                      "host"
                    ],
                    "type": "tag"
                  },
                  {
                    "key": "container_name",
                    "params": [
                      "container_name"
                    ],
                    "type": "tag"
                  }
                ],
                "hide": false,
                "measurement": "docker_container_cpu",
                "policy": "default",
                "query": "SELECT non_negative_derivative(last(\"mean_rx_bytes\"))/1000 FROM $Retention.\"downsampled_docker_container_net\" WHERE \"container_name\" =~ /$ContainerName/ and \"datacenter\" =~ /$DataCenter/  and \"host\" =~ /$HostName/ and $timeFilter GROUP BY time($interval), \"datacenter\", \"host\", \"container_name\"",
                "rawQuery": true,
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                  [
                    {
                      "params": [
                        "usage_percent"
                      ],
                      "type": "field"
                    },
                    {
                      "params": [],
                      "type": "mean"
                    }
                  ]
                ],
                "tags": []
              },
              {
                "alias": "$tag_container_name:tx_bytes",
                "dsType": "influxdb",
                "groupBy": [
                  {
                    "params": [
                      "$interval"
                    ],
                    "type": "time"
                  },
                  {
                    "params": [
                      "null"
                    ],
                    "type": "fill"
                  }
                ],
                "policy": "default",
                "query": "SELECT non_negative_derivative(last(\"mean_tx_bytes\"))/1000 FROM $Retention.\"downsampled_docker_container_net\" WHERE \"container_name\" =~ /$ContainerName/ and \"datacenter\" =~ /$DataCenter/  and \"host\" =~ /$HostName/ and  $timeFilter GROUP BY time($interval), \"datacenter\", \"host\", \"container_name\"",
                "rawQuery": true,
                "refId": "B",
                "resultFormat": "time_series",
                "select": [
                  [
                    {
                      "params": [
                        "value"
                      ],
                      "type": "field"
                    },
                    {
                      "params": [],
                      "type": "mean"
                    }
                  ]
                ],
                "tags": []
              }
            ],
            "timeFrom": null,
            "timeShift": null,
            "title": "AMP Network Utilization",
            "tooltip": {
              "msResolution": false,
              "shared": true,
              "value_type": "cumulative"
            },
            "type": "graph",
            "xaxis": {
              "show": true
            },
            "yaxes": [
              {
                "format": "short",
                "label": "Mega Bytes",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              },
              {
                "format": "short",
                "logBase": 1,
                "max": null,
                "min": null,
                "show": true
              }
            ]
          }
        ],
        "title": "New row"
      }
    ],
    "time": {
      "from": "now/d",
      "to": "now/d"
    },
    "timepicker": {
      "collapse": false,
      "enable": true,
      "notice": false,
      "now": true,
      "refresh_intervals": [
        "5s",
        "10s",
        "30s",
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "1d"
      ],
      "status": "Stable",
      "time_options": [
        "5m",
        "15m",
        "1h",
        "6h",
        "12h",
        "24h",
        "2d",
        "7d",
        "30d"
      ],
      "type": "timepicker"
    },
    "templating": {
      "list": [
        {
          "current": {
            "tags": [],
            "text": "All",
            "value": [
              "$__all"
            ]
          },
          "datasource": null,
          "hide": 0,
          "includeAll": true,
          "label": "ContainerName",
          "multi": true,
          "name": "ContainerName",
          "options": [
            {
              "text": "All",
              "value": "$__all",
              "selected": true
            },
            {
              "text": "chronograf",
              "value": "chronograf",
              "selected": false
            },
            {
              "text": "consul",
              "value": "consul",
              "selected": false
            },
            {
              "text": "grafana_1",
              "value": "grafana_1",
              "selected": false
            },
            {
              "text": "influxdb",
              "value": "influxdb",
              "selected": false
            },
            {
              "text": "kapacitor",
              "value": "kapacitor",
              "selected": false
            },
            {
              "text": "registrator",
              "value": "registrator",
              "selected": false
            },
            {
              "text": "telegraf",
              "value": "telegraf",
              "selected": false
            }
          ],
          "query": "SHOW TAG VALUES FROM \"docker_container_mem\" WITH KEY = \"container_name\"",
          "refresh": 1,
          "regex": "/([^/]*$)/",
          "type": "query"
        },
        {
          "current": {
            "tags": [],
            "text": "All",
            "value": [
              "$__all"
            ]
          },
          "datasource": null,
          "hide": 0,
          "includeAll": true,
          "label": "DataCenter",
          "multi": true,
          "name": "DataCenter",
          "options": [
            {
              "text": "All",
              "value": "$__all",
              "selected": true
            },
            {
              "text": "dev",
              "value": "dev",
              "selected": false
            }
          ],
          "query": "SHOW TAG VALUES FROM \"docker_container_mem\" WITH KEY = \"datacenter\"",
          "refresh": 1,
          "regex": "/([^/]*$)/",
          "type": "query"
        },
        {
          "current": {
            "tags": [],
            "text": "All",
            "value": [
              "$__all"
            ]
          },
          "datasource": null,
          "hide": 0,
          "includeAll": true,
          "label": "HostName",
          "multi": true,
          "name": "HostName",
          "options": [
            {
              "text": "All",
              "value": "$__all",
              "selected": true
            },
            {
              "text": "069618bafb82",
              "value": "069618bafb82",
              "selected": false
            }
          ],
          "query": "SHOW TAG VALUES FROM \"docker_container_mem\" WITH KEY = \"host\"",
          "refresh": 1,
          "regex": "/([^/]*$)/",
          "type": "query"
        },
        {
          "current": {
            "text": "warm",
            "value": "warm",
            "tags": []
          },
          "datasource": null,
          "hide": 0,
          "includeAll": false,
          "label": "RetentionPolicy",
          "multi": false,
          "name": "Retention",
          "options": [
            {
              "text": "cold",
              "value": "cold",
              "selected": false
            },
            {
              "text": "warm",
              "value": "warm",
              "selected": true
            }
          ],
          "query": "cold,warm",
          "refresh": 1,
          "regex": "",
          "type": "custom"
        }
      ]
    },
    "annotations": {
      "list": []
    },
    "schemaVersion": 12,
    "version": 3,
    "links": []
  }
}
