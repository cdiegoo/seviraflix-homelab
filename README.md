# SeViraFlix Homelab

Um guia e instalador de laboratório para **Proxmox VE**, **Jellyfin**, **Tailscale**,
Pi-hole e ferramentas de organização de uma biblioteca pessoal.

> Projeto independente, sem afiliação com Netflix ou com os projetos citados.
> Use apenas mídia que você tenha direito de armazenar e reproduzir. Este guia
> não ensina a obter conteúdo protegido por direitos autorais.

## Ideia da arquitetura

```text
Dispositivos pessoais
  ├── Jellyfin (rede local ou tailnet)
  ├── Tailscale (acesso remoto privado)
  └── Pi-hole (DNS da rede local, opcional)
             │
        Proxmox VE
  ├── VM/CT para Jellyfin
  ├── CT para Pi-hole
  ├── CT para Tailscale
  └── CTs opcionais para ferramentas de organização
             │
     Armazenamento de mídia
```

O instalador cria um LXC Debian dedicado no Proxmox e executa Jellyfin, Pi-hole,
Radarr, Sonarr, Prowlarr e Bazarr com Docker Compose. Tailscale é instalado no
guest, mas precisa de autenticação manual na tailnet. Veja
[`docs/architecture.md`](docs/architecture.md) para detalhes e decisões de rede.

## Instalação automatizada

O Proxmox VE precisa estar **instalado e acessível por SSH** antes de iniciar. Em
um Mac com Homebrew:

```sh
make install-deps
make install-proxmox-serviraflix
```

O segundo comando pede o IP do nó Proxmox e a senha SSH de `root`. Ele verifica
bridge, storage, espaço livre e ID de guest; cria o CT `9900` sem substituir
guests existentes; prepara Docker Compose e os serviços. A senha SSH usa apenas
um inventário temporário protegido e é removida ao terminar. Um par de chaves
Ed25519 local é criado em `~/.ssh/seviraflix-homelab`; o instalador também gera
uma senha inicial para Pi-hole e a exibe ao concluir.

Pré-requisitos, URLs, próximos passos e limitações estão em
[`docs/installation.md`](docs/installation.md).

## Componentes

- **Proxmox VE**: hypervisor para separar serviços em guests.
- **Jellyfin**: servidor de mídia para uma biblioteca própria.
- **Tailscale**: acesso remoto privado, sem publicar o painel do Jellyfin na
  Internet.
- **Pi-hole (opcional)**: DNS e filtragem na rede local. Ele não é VPN nem
  substitui o Tailscale.
- **Radarr / Sonarr / Prowlarr / Bazarr (opcionais)**: gerenciamento de catálogo,
  metadados e organização da biblioteca. Configure fontes compatíveis com seus
  direitos de uso.

## Limites e segurança

- O alvo não instala Proxmox VE, não cria a VM externa que o hospeda e não muda
  automaticamente a bridge do hypervisor. Veja os requisitos de virtualização
  aninhada em [`docs/installation.md`](docs/installation.md).
- O CT, o disco e os serviços usam valores genéricos, configuráveis em
  [`inventory/vars.yml`](inventory/vars.yml). O diretório de mídia começa vazio
  dentro do disco do CT; aumente/monte armazenamento antes de adicionar mídia.
- Os painéis são publicados nas portas do guest para a rede local. Não crie
  port-forward público; limite o acesso administrativo por firewall e use
  Tailscale para acesso remoto privado.
- Os containers usam tags `latest`; esta é uma instalação de laboratório, não
  uma stack com versões imutáveis ou SLA.
- O playbook não importa configurações, bancos, mídia ou segredos de outra
  instalação. Não há rotina de backup neste repositório ainda.
- Use apenas mídia que você tenha direito de armazenar e reproduzir. Configure
  fontes compatíveis com seus direitos de uso.

Valide localmente sem se conectar ao Proxmox:

```sh
make check
```

## Publicação

O repositório é intencionalmente genérico. Antes de compartilhar configurações
reais, remova IPs públicos ou privados, nomes de host, MACs, UUIDs, tokens,
chaves, domínios pessoais, URLs de acesso e qualquer dado identificável.

## Licenças

Consulte as licenças de cada componente no respectivo projeto. O conteúdo deste
guia é disponibilizado sob a licença MIT; veja [`LICENSE`](LICENSE).
