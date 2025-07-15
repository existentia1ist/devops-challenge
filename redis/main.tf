terraform {
  required_version = ">= 1.4"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6.2"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_image" "this" {
  name = var.image
}

resource "docker_container" "this" {
  name  = var.container_name
  image = docker_image.this.latest

  command = ["redis-server", "--appendonly", "yes"]

  ports {
    internal = 6379
    external = var.port
  }

  volumes {
    host_path      = "${path.module}/data"
    container_path = "/data"
  }

  restart = "unless-stopped"
}
