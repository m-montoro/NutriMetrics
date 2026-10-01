terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "0.8.3"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

resource "libvirt_volume" "ubuntu" {
  name   = "nutrimetrics-ubuntu.qcow2"
  pool   = "default"
  source = var.ubuntu_image
  format = "qcow2"
}

resource "libvirt_volume" "disco" {
  name           = "nutrimetrics-disco.qcow2"
  pool           = "default"
  base_volume_id = libvirt_volume.ubuntu.id
  format         = "qcow2"
  size           = 10737418240
}

resource "libvirt_cloudinit_disk" "cloudinit" {
  name = "nutrimetrics-cloudinit.iso"
  pool = "default"

  user_data = templatefile("${path.module}/cloud_init.cfg", {
    ssh_key = trimspace(file(pathexpand(var.ssh_public_key)))
  })
}

resource "libvirt_domain" "vm" {
  name   = "nutrimetrics-vm"
  memory = 2048
  vcpu   = 2

  cloudinit = libvirt_cloudinit_disk.cloudinit.id

  disk {
    volume_id = libvirt_volume.disco.id
  }

  network_interface {
    network_name   = "default"
    wait_for_lease = true
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }
}

output "vm_ip" {
  value = libvirt_domain.vm.network_interface[0].addresses[0]
}
