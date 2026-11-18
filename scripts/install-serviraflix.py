#!/usr/bin/env python3
"""Install the SeViraFlix guest on an already-installed Proxmox VE node."""

from __future__ import annotations

import argparse
import getpass
import ipaddress
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
SSH_KEY_PATH = Path.home() / ".ssh" / "seviraflix-homelab"


def ensure_dependencies() -> None:
    if shutil.which("ansible-playbook") and shutil.which("sshpass"):
        return
    if not shutil.which("brew"):
        raise RuntimeError("Homebrew is required to install Ansible and sshpass.")

    missing = []
    if not shutil.which("ansible-playbook"):
        missing.append("ansible")
    if not shutil.which("sshpass"):
        missing.append("sshpass")
    subprocess.run(["brew", "install", *missing], check=True)

    if not shutil.which("ansible-playbook") or not shutil.which("sshpass"):
        raise RuntimeError("Homebrew finished, but Ansible or sshpass is still unavailable.")


def ensure_ssh_key() -> tuple[str, str]:
    SSH_KEY_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    SSH_KEY_PATH.parent.chmod(0o700)
    public_key_path = SSH_KEY_PATH.with_suffix(".pub")

    if not SSH_KEY_PATH.exists():
        subprocess.run(
            [
                "ssh-keygen",
                "-q",
                "-t",
                "ed25519",
                "-N",
                "",
                "-C",
                "seviraflix-homelab",
                "-f",
                str(SSH_KEY_PATH),
            ],
            check=True,
        )
    SSH_KEY_PATH.chmod(0o600)
    if not public_key_path.exists():
        public_key = subprocess.run(
            ["ssh-keygen", "-y", "-f", str(SSH_KEY_PATH)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        public_key_path.write_text(public_key + "\n", encoding="utf-8")
        public_key_path.chmod(0o644)

    return str(SSH_KEY_PATH), public_key_path.read_text(encoding="utf-8").strip()


def write_private_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
    path.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install local Ansible and SSH password dependencies, then exit.",
    )
    args = parser.parse_args()

    try:
        ensure_dependencies()
        if args.install_deps:
            print("Dependências locais prontas: ansible-playbook e sshpass.")
            return 0

        pve_host = str(ipaddress.ip_address(input("IP do nó Proxmox: ").strip()))
        pve_password = getpass.getpass("Senha SSH de root do Proxmox: ")
        if not pve_password:
            raise ValueError("A senha SSH não pode ficar vazia.")

        guest_private_key, guest_public_key = ensure_ssh_key()
        pihole_password = secrets.token_urlsafe(24)
        with tempfile.TemporaryDirectory(prefix="seviraflix-install-") as temp_dir:
            temp_path = Path(temp_dir)
            inventory_path = temp_path / "inventory.json"
            variables_path = temp_path / "variables.json"
            known_hosts_path = temp_path / "known_hosts"
            known_hosts_path.touch(mode=0o600)
            ssh_common_args = (
                f"-o UserKnownHostsFile={known_hosts_path} "
                "-o StrictHostKeyChecking=accept-new "
                "-o ControlMaster=no -o ControlPath=none"
            )

            inventory = {
                "all": {
                    "hosts": {
                        "proxmox": {
                            "ansible_host": pve_host,
                            "ansible_user": "root",
                            "ansible_password": pve_password,
                            "ansible_connection": "ssh",
                            "ansible_python_interpreter": "/usr/bin/python3",
                            "ansible_ssh_common_args": ssh_common_args,
                        }
                    }
                }
            }
            variables = {
                "guest_ssh_private_key": guest_private_key,
                "guest_ssh_public_key": guest_public_key,
                "guest_ssh_common_args": ssh_common_args,
                "pihole_password": pihole_password,
            }
            write_private_json(inventory_path, inventory)
            write_private_json(variables_path, variables)

            completed = subprocess.run(
                [
                    "ansible-playbook",
                    "-i",
                    str(inventory_path),
                    "playbooks/install.yml",
                    "--extra-vars",
                    f"@{variables_path}",
                ],
                cwd=REPO_ROOT,
                check=False,
            )
            if completed.returncode != 0:
                return completed.returncode

        print("\nSeViraFlix instalado.")
        print(f"Senha inicial do Pi-hole: {pihole_password}")
        print("Guarde-a em um gerenciador de senhas; ela não está no repositório.")
        print(f"Chave SSH para o guest: {guest_private_key}")
        print("Para entrar no Tailscale, conecte ao guest e execute: tailscale up")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Instalação interrompida: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
