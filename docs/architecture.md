# Arquitetura de referência

## Papéis

| Componente | Papel | Exposição recomendada |
| --- | --- | --- |
| Proxmox VE | Ciclo de vida de VMs e LXC | Rede de administração confiável; não publicar na Internet. |
| Jellyfin | Catálogo e reprodução da biblioteca pessoal | LAN e, se necessário, tailnet; evitar exposição direta à Internet. |
| Tailscale | Acesso remoto autenticado entre dispositivos próprios | VPN privada; aplicar ACLs mínimas no tailnet. |
| Pi-hole | DNS e filtragem opcional para a LAN | Apenas redes autorizadas; não atuar como DNS público aberto. |
| Radarr / Sonarr | Organização de filmes e séries da biblioteca | Acesso administrativo restrito à LAN/tailnet. |
| Prowlarr | Gerenciamento de fontes de metadados/índices | Acesso administrativo restrito; configurar apenas fontes legais. |
| Bazarr | Legendas para mídia que o usuário pode acessar | Acesso administrativo restrito. |

O tráfego de mídia não precisa passar pelo Tailscale quando o cliente está na
rede local. Para acesso remoto, o dispositivo cliente entra na tailnet e acessa
o Jellyfin pelo endereço privado atribuído pelo Tailscale.

## Isolamento

- Coloque a administração do Proxmox em uma rede confiável e limite quem pode
  acessá-la.
- Separe os serviços em guests para limitar o impacto de uma falha, mas não
  considere LXC uma fronteira de segurança equivalente a uma VM.
- Use contas sem privilégios administrativos quando o serviço permitir.
- Não compartilhe o socket do Docker com aplicações que não precisam dele.
- Conceda aos serviços acesso somente aos diretórios de mídia necessários.
- Se houver aceleração de hardware para transcodificação, configure o dispositivo
  de forma explícita e documente permissões e dependências do host.

## Rede e DNS

- Reserve endereços no DHCP ou documente a estratégia de endereçamento.
- O Pi-hole pode ser o DNS recursivo/forwarder da rede local; configure um DNS
  alternativo para recuperação antes de torná-lo a única resolução da LAN.
- A configuração de DNS do tailnet é separada da configuração de DHCP do roteador.
  Planeje os domínios e os resolvedores antes de ativar MagicDNS ou split DNS.
- Nunca exponha portas administrativas do Proxmox, Pi-hole ou ferramentas *arr
  diretamente à Internet.

## Dados e recuperação

- Mantenha mídia e configuração de aplicação em caminhos distintos.
- Faça backup das configurações e bancos das aplicações, além do backup das VMs
  e LXC. Bind mounts do host podem ficar fora do backup padrão do guest.
- Guarde em local seguro as chaves de criptografia e segredos necessários para
  restaurar aplicações.
- Teste a restauração. Um job de backup concluído sem um teste de restore não
  demonstra que o serviço pode voltar.

## Uso responsável

As ferramentas de catálogo e automação não concedem direitos sobre obras. Use-as
somente com mídia adquirida/licenciada, criada pelo usuário ou em domínio público,
respeitando as leis e termos aplicáveis em sua região.
