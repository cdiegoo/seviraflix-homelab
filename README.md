# SeViraFlix Homelab

Um guia para montar um servidor pessoal de mídia com **Proxmox VE**, **Jellyfin**
e acesso remoto privado via **Tailscale**. Pi-hole pode fornecer DNS e bloqueio
de domínios na rede local. Radarr, Sonarr, Prowlarr e Bazarr ajudam a organizar
uma biblioteca pessoal.

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

O desenho é conceitual: a escolha entre VM, LXC e containers depende do hardware,
das permissões necessárias e da familiaridade de quem administra. Veja
[`docs/architecture.md`](docs/architecture.md) para detalhes e decisões de rede.

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

## Antes de começar

1. Instale e atualize o Proxmox VE em hardware que você controla.
2. Planeje endereços IP reservados no roteador e capacidade de armazenamento.
3. Separe as credenciais e tokens em um gerenciador de segredos; nunca os coloque
   em arquivos versionados.
4. Configure backups em outro equipamento ou local. Um segundo disco no mesmo
   host não protege contra perda do host.
5. Restrinja painéis administrativos à rede local ou à tailnet.

Este repositório não contém inventário de uma rede real, playbooks prontos para
provisionar hosts, credenciais, mídia nem configuração privada. Preencha os
valores e valide a segurança antes de adaptar qualquer exemplo ao seu ambiente.

## Publicação

O repositório é intencionalmente genérico. Antes de compartilhar configurações
reais, remova IPs públicos ou privados, nomes de host, MACs, UUIDs, tokens,
chaves, domínios pessoais, URLs de acesso e qualquer dado identificável.

## Licenças

Consulte as licenças de cada componente no respectivo projeto. O conteúdo deste
guia é disponibilizado sob a licença MIT; veja [`LICENSE`](LICENSE).
