variable "ubuntu_image" {
  default = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
}

variable "ssh_public_key" {
  default = "~/.ssh/nutrimetrics_ed25519.pub"
}
