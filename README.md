# docker-service-replicas-exporter

Prometheus metrics exporter for docker service replication counts

### Metrics

Metrics will available in http://localhost:9258

```sh
$ curl -s localhost:9258
# HELP docker_service_replicas_running Number of replicas running for a service
# TYPE docker_service_replicas_running gauge
docker_service_replicas_running{service_name="service1"} 2.0
docker_service_replicas_running{service_name="service2"} 1.0
# HELP docker_service_replicas_expected Number of replicas expected for a service
# TYPE docker_service_replicas_expected gauge
docker_service_replicas_expected{service_name="service1"} 1.0
docker_service_replicas_expected{service_name="service2"} 1.0
```

### Alert Example

```
ALERT service_replication_failure
  IF ((docker_service_replicas_running / docker_service_replicas_expected) * 100) < 100
  FOR 5m
  ANNOTATIONS {
      summary = "Service replication failed",
      description = "Service replication is {{$value}}% for {{ $labels.service_name }}",
  }
```

### Config

```yml
exporter_port: 9258 # Port on which Prometheus can call this exporter to get metrics
log_level: info
```

### Run

#### Using code (local)

```
# Ensure python 2.x and pip installed
pip install -r app/requirements.txt
python app/exporter.py example/config.yml
```

#### Using docker

> This must be run on a docker swarm master node

```
docker run -p 9258:9258 -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/example/config.yml:/etc/docker-service-replicas-exporter/config.yml sunbird/docker-service-replicas-exporter /etc/docker-service-replicas-exporter/config.yml
```