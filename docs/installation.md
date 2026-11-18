# Instalação

## Escopo do comando

`make install-proxmox-serviraflix` pressupõe que o Proxmox VE já esteja
instalado, inicializado e acessível por SSH. Ele cria um LXC Debian 12 com ID
`9900`, instala Docker e Tailscale, e inicia Jellyfin, Pi-hole, Radarr, Sonarr,
Prowlarr e Bazarr.

O comando não instala o sistema operacional Proxmox, não cria a VM externa que
hospeda o hypervisor e não altera a rede do hypervisor. O instalador evita essa
alteração porque um erro de bridge pode derrubar a conexão SSH e deixar a VM
inacessível.

## Pré-requisitos do Proxmox

- Proxmox VE em uma VM ou em hardware próprio, já instalado.
- Se o Proxmox estiver virtualizado, o hypervisor externo precisa expor VT-x/AMD-V
  para a VM se forem necessárias VMs KVM dentro do Proxmox. O guest precisa ter
  recursos de CPU, RAM e disco suficientes.
- Uma rede funcional no Proxmox com a bridge `vmbr0`; a NIC virtual e a rede do
  hypervisor externo devem permitir o tráfego dos guests. Em alguns hypervisors
  será necessário habilitar promiscuidade/MAC spoofing para guests receberem
  endereços na LAN.
- Storage `local-lvm` ativo, pelo menos 40 GiB disponíveis, e o device
  `/dev/net/tun` no host para Tailscale.
- Acesso à internet pelo nó Proxmox para atualizar o catálogo e baixar o template
  Debian 12 mais recente do storage `local`.
- Uma reserva DHCP para o guest é recomendada. O endereço é obtido por DHCP.

Para instalar Proxmox dentro de uma VM Debian, prepare a VM e o hypervisor externo
manualmente conforme a documentação oficial do Proxmox. A instalação de pacotes
do hypervisor e o reboot alteram o sistema operacional; este projeto não os
executa por SSH.

## Executar

No Mac com Homebrew:

```sh
make install-deps
make install-proxmox-serviraflix
```

O alvo `install-proxmox-serviraflix` também instala as dependências locais se
necessário. Informe o IP SSH do Proxmox e a senha SSH de `root`. A senha é
solicitada sem eco, fica em um inventário temporário com permissão restrita e é
apagada ao encerrar o processo. A primeira chave do host é aceita apenas durante
essa execução; use uma rede confiável.

O instalador:

1. Confirma que o host é Proxmox, `vmbr0` existe, `local-lvm` está ativo e tem
   espaço suficiente, `/dev/net/tun` existe e o ID 9900 está livre.
2. Cria o LXC Debian 12 não privilegiado, com nesting, DHCP e disco root de 32 GiB.
3. Instala Docker, Tailscale e os containers de aplicação.
4. Gera uma chave SSH local para acesso ao guest e uma senha aleatória para a
   interface administrativa do Pi-hole.

Se o ID 9900 já estiver ocupado, a execução para sem alterar ou remover esse
guest. Para escolher outro ID, altere `pve_ct_id` em `inventory/vars.yml`.

## Depois da instalação

O playbook mostra os endereços usando o IP recebido por DHCP. Os endpoints padrão
são:

| Aplicação | URL |
| --- | --- |
| Jellyfin | `http://IP_DO_GUEST:8096` |
| Pi-hole | `http://IP_DO_GUEST:8080/admin` |
| Radarr | `http://IP_DO_GUEST:7878` |
| Sonarr | `http://IP_DO_GUEST:8989` |
| Prowlarr | `http://IP_DO_GUEST:9696` |
| Bazarr | `http://IP_DO_GUEST:6767` |

A senha gerada do Pi-hole é exibida uma vez no terminal. Guarde-a em um
gerenciador de senhas; não a committe.

Para autenticar o guest no Tailscale, conecte via SSH usando
`~/.ssh/seviraflix-homelab` e execute `tailscale up`. Abra a URL de autenticação
que o comando mostrar. Não é preciso publicar uma auth key no repositório.

O diretório de mídia é `/srv/seviraflix/media` e começa vazio dentro do rootfs do
LXC. Jellyfin o monta somente para leitura; Radarr, Sonarr e Bazarr têm acesso de
escrita. Planeje storage e backup antes de copiar arquivos para esse caminho.
Não há downloader, indexer externo pré-configurado nem conteúdo incluído.

Os dados de configuração ficam em `/opt/seviraflix` dentro do guest. O backup do
rootfs pode incluí-los, mas restauração de bancos e segredos ainda não é
automatizada.

## Administração e limitações

- Todos os serviços são colocados em um único LXC para simplificar o laboratório.
  Isso reduz o isolamento entre aplicações; para produção, avalie separar serviços
  em VMs e definir regras de firewall específicas.
- O LXC é não privilegiado e usa nesting para Docker. Se o host restringir os
  recursos necessários ao Docker, o playbook falhará; não troque automaticamente
  o CT para privilegiado como workaround.
- As portas publicadas ficam disponíveis na rede do guest. Restrinja acesso aos
  painéis por firewall e não as encaminhe diretamente da Internet.
- Os containers usam `latest`; atualizações e compatibilidade entre versões não
  estão fixadas pelo repositório.
- Para ver os containers:

  ```sh
  ssh -i ~/.ssh/seviraflix-homelab root@IP_DO_GUEST \
    'cd /opt/seviraflix && docker-compose -f compose.yml ps'
  ```
