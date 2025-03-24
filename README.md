# Integração dos Aquecedores Rinnai para Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]

[![Buy me a coffee!](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)][buymecoffee]

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mukaschultze&repository=ha-aquecedor-rinnai&category=integration)

<!-- [![Discord][discord-shield]][discord] -->
<!-- [![Community Forum][forum-shield]][forum] -->

Integração para conectar aquecedores de água a gás Rinnai ao Home Assistant. Com esta integração, você pode monitorar e
controlar diversos aspectos do seu aquecedor, como temperatura da água, consumo de gás e água, e acessar dados em tempo
real, tudo diretamente do seu painel do Home Assistant.

## Funcionalidades

- **Monitoramento de Temperatura**: Visualize e ajuste a temperatura do aquecedor.
- **Sensores de Consumo**: Monitore o consumo de água e gás em tempo real e obtenha relatórios históricos.
- **Status do Dispositivo**: Receba alertas de status, como falhas no dispositivo e necessidade de manutenção.
- **Automatizações**: Integre o controle do aquecedor com outras automatizações e dispositivos no Home Assistant.

| ![image](https://github.com/user-attachments/assets/3764a17f-a613-4627-89e1-3a4b64a07c44) | ![image](https://github.com/user-attachments/assets/d7581e4e-ed77-44cd-9efd-30d36108aa98) |
| :---------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------: |

## Dispositivos Suportados

Testado em um aquecedor REU-E211 FEH e controlador WIFI ROU-004, porém deve funcionar normalmente em modelos similares.

## Disclaimer

Este projeto é uma integração de código aberto e não é afiliado ou endossado pela Rinnai. O uso desta integração pode
anular a garantia do seu dispositivo; utilize-a por sua conta e risco.

A integração opera exclusivamente em rede local (LAN) e não utiliza recursos online (cloud), garantindo que todos os
dados permaneçam dentro da sua rede doméstica.

## Instalação

### HACS (Home Assistant Community Store)

Se você possui o HACS instalado, basta procurar por `Rinnai Water Heater` e instalar a integração diretamente por lá. Ou
alternativamente, [clicar
aqui](https://my.home-assistant.io/redirect/hacs_repository/?owner=mukaschultze&repository=ha-aquecedor-rinnai&category=integration).

### Instalação manual

1. Baixe a [última versão](https://github.com/mukaschultze/ha-aquecedor-rinnai/releases/latest) da integração.
2. Extraia o arquivo baixado.
3. Copie o diretório `custom_components/rinnai` para o diretório de configurações do seu Home Assistant.
4. Reinicie o Home Assistant.

Após a instalação seu diretório de configurações deve ficar deste jeito:

```text
    └── ...
    └── configuration.yaml
    └── secrets.yaml
    └── custom_components
        └── rinnai
            └── __init__.py
            └── config_flow.py
            └── const.py
            └── ...
```

## Uso

1. Abra o Home Assistant.
2. Navegue para "Configuração" -> "Dispositivos e integrações."
3. Clique no botão de "Adicionar Integração" para adicionar uma nova integração.
4. Pesquise por `Aquecedor Rinnai` ou `Rinnai Heater`.
5. Escolha um nome e insira o IP do seu aquecedor no campo `host`, ou alternativamente use `WIFI-RINNAI`.

![image](https://github.com/user-attachments/assets/e7889628-f046-4fca-91b2-64131481e08f)

### Card

![image](https://github.com/user-attachments/assets/1125684e-54db-4784-b77d-66c64d16b3f3)

É possivel gerenciar o aquecedor em um dashboard como na imagem acima através do card `tile` usando o yaml abaixo:

```yaml
features:
  - type: target-temperature
  - type: water-heater-operation-modes
type: tile
entity: water_heater.e21_heater
grid_options:
  rows: auto
  columns: full
state_content:
  - state
  - current_temperature
features_position: bottom
vertical: false
```

## Suporte e Contribuições

Para relatar bugs, solicitar novos recursos ou fazer perguntas gerais, crie uma issue no repositório GitHub.

Contribuições são bem-vindas! Sinta-se à vontade para fazer um fork do repositório, realizar alterações e enviar um pull request.

## Agradecimentos

Este plugin não teria sido possível sem as valiosas contribuições e engenharia reversa feitas pela comunidade, em especial a este repositório:

- https://github.com/ale-jr/rinnai_br_homeassistant

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](./LICENSE) para mais detalhes.

---

[integration_blueprint]: https://github.com/mukaschultze/ha-aquecedor-rinnai
[buymecoffee]: https://www.buymeacoffee.com/mukaschultze
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/mukaschultze/ha-aquecedor-rinnai.svg?style=for-the-badge
[commits]: https://github.com/mukaschultze/ha-aquecedor-rinnai/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/mukaschultze/ha-aquecedor-rinnai.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40mukaschultze-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mukaschultze/ha-aquecedor-rinnai.svg?style=for-the-badge
[releases]: https://github.com/mukaschultze/ha-aquecedor-rinnai/releases
