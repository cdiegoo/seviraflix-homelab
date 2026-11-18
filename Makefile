.PHONY: help install-deps install-proxmox-serviraflix check

help:
	@printf '%s\n' \
	  'install-deps                   Instala Ansible e sshpass na máquina local' \
	  'install-proxmox-serviraflix    Cria o guest e instala o stack SeViraFlix' \
	  'check                          Valida sintaxe e inventário'

install-deps:
	@python3 scripts/install-serviraflix.py --install-deps

install-proxmox-serviraflix:
	@python3 scripts/install-serviraflix.py

check:
	@python3 -m py_compile scripts/install-serviraflix.py
	@ansible-playbook --syntax-check -i 'proxmox,seviraflix,' playbooks/install.yml
	@ansible-playbook -i 'localhost,' playbooks/check-inventory.yml
	@git diff --check
