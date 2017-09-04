#!/usr/bin/python

import time
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import argparse
import yaml
import logging
import subprocess
import re

DEFAULT_PORT=9258
DEFAULT_LOG_LEVEL='info'

class DockerServiceReplicasCollector(object):
  def __init__(self, config):
    self._config = config

  def collect(self):
    service_replicas_lines = subprocess.check_output(['docker', 'service', 'ls', '--format', '"{{.Name}} {{.Replicas}}"']).strip().split('\n')
    cleaned_service_replicas_lines = [service_replicas_line for service_replicas_line in service_replicas_lines if service_replicas_line is not None and service_replicas_line != '']
    service_replicas_running_gauge = GaugeMetricFamily('docker_service_replicas_running', 'Number of replicas running for a service', labels=['instance'])
    service_replicas_expected_gauge = GaugeMetricFamily('docker_service_replicas_expected', 'Number of replicas expected for a service', labels=['instance'])
    service_replicas_success_gauge = GaugeMetricFamily('docker_service_replicas_success', 'Checks if number replicas running is same as expected for a service', labels=['instance'])
    logging.debug("service_replicas_lines: {}".format(service_replicas_lines))
    for service_replicas_line in cleaned_service_replicas_lines:
      logging.debug("service_replicas_line: {}".format(service_replicas_line))
      result = re.match('"(.+) (\d+)/(\d+)"', service_replicas_line)
      service_name = result.group(1)
      service_replicas_running = float(result.group(2))
      service_replicas_expected = float(result.group(3))
      service_replicas_success = (service_replicas_running == service_replicas_expected)
      service_replicas_running_gauge.add_metric([service_name], service_replicas_running)
      service_replicas_expected_gauge.add_metric([service_name], service_replicas_expected)
      service_replicas_success_gauge.add_metric([service_name], service_replicas_success)
    yield service_replicas_running_gauge
    yield service_replicas_expected_gauge
    yield service_replicas_success_gauge


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Expose metrics for docker service replicas')
  parser.add_argument('config_file_path', help='Path of the config file')
  args = parser.parse_args()
  with open(args.config_file_path) as config_file:
    config = yaml.load(config_file)
    log_level = config.get('log_level', DEFAULT_LOG_LEVEL)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(log_level.upper()))
    exporter_port = config.get('exporter_port', DEFAULT_PORT)
    logging.debug("Config %s", config)
    logging.info('Starting server on port %s', exporter_port)
    start_http_server(exporter_port)
    REGISTRY.register(DockerServiceReplicasCollector(config))
  while True: time.sleep(1)