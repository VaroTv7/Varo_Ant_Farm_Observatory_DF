# ⛏ Ant Farm Observatory (v2.0.0)

**Dwarf Fortress 24/7 + Web Observatory with AI RAG integrated**
**Dwarf Fortress 24/7 + Observatorio web con IA RAG integrada**

---

### [ES] Descripción (Español)
Ant Farm Observatory v2 es un sistema de monitoreo autónomo para mundos de Dwarf Fortress. Esta versión profesional utiliza un motor de datos de alto rendimiento basado en **SQLite** e **iterparse**, permitiendo seguir la historia de mundos masivos sin colapsar la memoria del servidor. Incluye un **Oráculo IA** con "Conciencia de Datos" (RAG) capaz de consultar la base de datos en tiempo real mediante *Tool Calling* de Anthropic Claude 3.5.

### [EN] Description (English)
Ant Farm Observatory v2 is an autonomous monitoring system for Dwarf Fortress worlds. This professional version uses a high-performance data engine based on **SQLite** and **iterparse**, allowing history tracking of massive worlds without collapsing server memory. It includes an **AI Oracle** with "Data Awareness" (RAG) capable of querying the database in real-time via Anthropic's Claude 3.5 *Tool Calling*.

---

## 🚀 Instalación / Installation

```bash
# [ES] Instalación rápida / [EN] Quick Install
git clone https://github.com/VaroTv7/Varo_Ant_Farm_Observatory_DF.git
cd Varo_Ant_Farm_Observatory_DF
./install.sh
```

---

## 🔥 Novedades de la V2 / V2 New Features

- **[ES] Panel de Simulación / [EN] Simulation Dashboard**: Interfaz rediseñada con barra lateral, estadísticas densas y modo oscuro.
- **[ES] Seguimiento de Linajes / [EN] Lineage Tracking**: Navegación por árboles genealógicos y dossiers detallados de héroes.
- **[ES] Watchdog Nativo / [EN] Native Watchdog**: Sincronización automática de `legends.xml` sin necesidad de Cron en el host.
- **[ES] Búsquedas SQLite / [EN] SQLite Search**: Búsqueda instantánea y filtrado de miles de figuras históricas.
- **[ES] Oráculo Mejorado / [EN] Enhanced Oracle**: IA con acceso directo a la base de datos (Tool Calling).

---

## 📂 Puertos recomendados / Recommended Ports

| Servicio / Service | Puerto / Port | Nota / Note |
|---------------------|---------------|-------------|
| Webtop (DF)         | 8080          | [ES] Acceso web al juego / [EN] Web access to game |
| Observatory         | 8090          | [ES] Crónicas e IA / [EN] Chronicles and AI |

---

## 🛠 Tecnologías / Technologies

- **Engine / Motor**: Dwarf Fortress v50.14 (Webtop)
- **Database / Base de Datos**: SQLite 3
- **Observatory / Observatorio**: Flask (Python 3.12) + `iterparse` (XML Streaming)
- **AI / IA**: Anthropic Claude 3.5 (Sonnet) with **Tool Calling**
- **Automation / Automatización**: Python Watchdog + DFHack

---

## 📜 Licencia / License

MIT - See [LICENSE](LICENSE)
