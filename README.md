# ⛏ Ant Farm Observatory (ES/EN)

**Dwarf Fortress 24/7 + Web Observatory with IA integrated**
**Dwarf Fortress 24/7 + Observatorio web con IA integrada**

---

### [ES] Descripción (Español)

Un mundo de Dwarf Fortress corriendo de forma autónoma en tu servidor, con un observatorio web para seguir la historia de civilizaciones, héroes y artefactos — y un Oráculo IA que conoce toda la historia del mundo y responde tus preguntas como un Cronista Omnisciente.

### [EN] Description (English)

A Dwarf Fortress world running autonomously on your server, with a web observatory to follow the history of civilizations, heroes, and artifacts — and an AI Oracle that knows the entire history of the world and answers your questions like an Omniscient Chronicler.

---

## 🚀 Instalación / Installation

```bash
# [ES] Instalación rápida / [EN] Quick Install
curl -fsSL https://raw.githubusercontent.com/VaroTv7/Varo_Ant_Farm_Observatory_DF/main/install.sh | bash
```

---

## 🛠 Arquitectura / Architecture

- **Motor / Motor**: Dwarf Fortress v50.14 (Webtop)
- **Observatorio / Observatory**: Flask (Python 3.12)
- **IA**: Anthropic Claude API (Sonnet 3.5)
- **Automatización / Automation**: DFHack v50.14-r1

---

## 📂 Puertos recomendados / Recommended Ports

| Servicio / Service | Puerto / Port | Nota / Note |
|---------------------|---------------|-------------|
| Webtop (DF)         | 8080          | [ES] Acceso web al juego / [EN] Web access to game |
| Observatory         | 8090          | [ES] Crónicas e IA / [EN] Chronicles and AI |

---

## 📜 Licencia / License

MIT - See [LICENSE](LICENSE)
