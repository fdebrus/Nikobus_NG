<p align="left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="custom_components/nikobus_ng/brand/dark_logo@2x.png">
    <img src="custom_components/nikobus_ng/brand/logo@2x.png" alt="Nikobus NG" width="420">
  </picture>
</p>

# for Home Assistant

<p align="left">
  <a href="https://www.buymeacoffee.com/fdebrus"><img src="https://img.shields.io/badge/Support-Buy%20Me%20a%20Coffee-FFDD00?style=flat&logo=buymeacoffee" alt="Buy Me a Coffee"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-Nikobus%20NG-blue?style=flat&logo=homeassistant" alt="Nikobus NG for Home Assistant">
  <a href="https://hacs.xyz"><img src="https://img.shields.io/badge/HACS-Custom-orange?style=flat" alt="HACS Custom"></a>
  <img src="https://img.shields.io/badge/Status-Experimental-red?style=flat" alt="Experimental">
  <a href="https://github.com/fdebrus/Nikobus_NG"><img src="https://img.shields.io/badge/Maintained%20by-fdebrus-green?style=flat" alt="Maintainer"></a>
  <a href="https://github.com/fdebrus/Nikobus_NG/releases"><img src="https://img.shields.io/github/v/release/fdebrus/Nikobus_NG?style=flat&label=Release" alt="Latest release"></a>
  <a href="https://github.com/fdebrus/Nikobus_NG/issues"><img src="https://img.shields.io/github/issues/fdebrus/Nikobus_NG?style=flat&label=Issues" alt="Open issues"></a>
  <a href="https://github.com/fdebrus/Nikobus_NG/stargazers"><img src="https://img.shields.io/github/stars/fdebrus/Nikobus_NG?style=flat&label=Stars" alt="GitHub stars"></a>
</p>

**Your Nikobus installation in Home Assistant, read straight from the bus.** Switches, dimmers and shutters become native entities, every key becomes an event for your automations, and the wiring itself (which key drives which output, and how) becomes data an AI assistant can read.

Modules, plates and links are found by **one discovery**. Names, rooms and scenes come from your **`.nkb` project file**.

> **Experimental.** Nikobus NG runs on one real installation so far, and most of it has only been tested against a simulated PC-Link. [What is verified](#what-is-verified) says exactly what has and has not been seen on hardware. Testers are welcome, especially with hardware listed there as not seen.

<p align="left">
  <a href="#quick-start"><b>Quick start</b></a> ·
  <a href="#what-you-get">What you get</a> ·
  <a href="#key-presses-in-automations">Key presses</a> ·
  <a href="#for-ai-assistants">AI assistants</a> ·
  <a href="#coming-from-nikobus">Coming from Nikobus</a> ·
  <a href="#supported-hardware">Hardware</a> ·
  <a href="#what-is-verified">What is verified</a> ·
  <a href="#known-limitations">Limitations</a>
</p>

### What "NG" means

Nikobus NG ("Next Generation") is a second integration, written from scratch next to the [Nikobus integration](https://github.com/fdebrus/Nikobus-HA) on the same protocol library, [nikobus-connect](https://github.com/fdebrus/nikobus-connect). It is a fresh design of the same thing, not its successor yet: Nikobus stays, and stays maintained. The two use different domains and can be installed side by side, one enabled at a time.

---

## Highlights

**Finds your installation**

- 🔌 **One discovery** — one button reads the PC-Link inventory and every module's links, and it starts by itself on first setup. One module can be read again on its own.
- 📥 **Names from your `.nkb`** — modules, plates (numbered as in the Nikobus software), outputs, rooms as areas, and light scenes.

**Shows it as Home Assistant expects**

- 💡 **Native entities** — a relay is a `switch` or a `light`, a dimmer output a `light` with brightness or a `fan` with speed, a shutter a `cover` with an estimated position.
- 🎛️ **Keys are event entities** — one per key, with `pressed`, `hold`, `short_release` and `long_release`, named with where the key sits on its plate.
- 🎬 **Scenes and shutter groups** — light scenes are activated by their own telegram; a function that only moves shutters is a `cover` for the group.
- 🚥 **LED keys** — an output can be switched by pressing its key, so the plate's LED follows what Home Assistant does.
- 🔊 **Audio zones and RGB controller** — a `media_player` per zone, a `light` for a colour controller.

**Explains itself**

- 🧭 **Every output names what drives it** — the keys and PC-Link calendar channels are in its `controlled_by` attribute, each link said in plain words.
- 🤖 **Made for AI assistants** — an action and a set of tools return the wiring, so an assistant can answer "which button switches the kitchen light?".
- 🩺 **Repairs that say what to do** — a module that stopped answering or was reprogrammed, a wrong port, a module of the wrong type; several come with a fix button.

**Stays safe**

- 🛡️ **Read-only maintenance** — check every module's programming, back up its memory, see the PC-Link's clock. Setting that clock is the only thing ever written.
- 🔁 **A take-over from Nikobus that can be undone** — entity IDs, names, areas, labels, voice exposure, LED keys and shutter run times move across.

---

## Quick start

**You need**

- **Home Assistant 2026.10 or later.**
- **A PC-Link (05-200)** on a USB/serial adapter (`/dev/ttyUSB0`) or behind a TCP-to-serial bridge (`192.168.2.50:9999`). It holds the inventory the discovery reads. Without one, your `.nkb` or two hand-written files can stand in for it.
- **The bus to yourself.** Only one program may talk to it: stop the Nikobus PC software, and disable the Nikobus integration if you have it.
- *(Optional)* **Your `.nkb` project file**, the only place your names, rooms and scene names live.

**Steps**

1. **Install** through HACS:

   [![Add to HACS](https://img.shields.io/badge/HACS-Add%20Custom%20Repository-blue.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fdebrus&repository=Nikobus_NG&category=integration)

   Then restart Home Assistant.
2. **Add the integration**: *Settings → Devices & services → Add integration → Nikobus NG*. Enter the serial port or `host:port`; the connection is tested at once.
3. **Tick *A Feedback Module is installed*** if you have a Feedback Module (05-207) and Home Assistant is on the PC-Link's port. Its own reads are then picked up, and Home Assistant reads only what it leaves out.
4. **Wait for the discovery.** It starts by itself; follow it on the *Discovery* sensor of the **Nikobus Bridge** device. Entities appear when it ends. A large installation takes a few minutes.
5. *(Optional)* **Import your names**: *Configure → Import names (.nkb)*.
6. *(Optional)* Press **Back up programming** once and keep the folder somewhere safe.

<details>
<summary>Installing without the button, or without HACS</summary>

- **HACS, by hand:** *HACS → ⋮ → Custom repositories*, add `https://github.com/fdebrus/Nikobus_NG` as an *Integration*, then install *Nikobus NG*.
- **Without HACS:** copy `custom_components/nikobus_ng` into `config/custom_components`, under that exact name, and restart.

</details>

Coming from the Nikobus integration? Follow **[Moving from Nikobus to Nikobus NG](docs/migrating-from-nikobus.md)** instead.

---

## Settings

Everything is optional and lives under **Configure** on the integration's entry. To change the connection itself, use **Reconfigure**.

| Menu | What it is for |
|---|---|
| **Import names (.nkb)** | Upload the project file: names, rooms as areas, scene names. |
| **Lights and fans** | Say which relays switch a lamp and which dimmer outputs drive a fan; label entities by kind. |
| **Shutter run times** | How long a shutter takes each way and its end margin; or show a roller output as a switch or light. |
| **Keep button LEDs in sync** | The keys pressed to switch an output on and off, so the plate's LED follows. |
| **Gateway** | Feedback Module, a PC-Link older than generation 3, telegrams per press. |
| **Correct a module's type** | For a module the inventory lists as another type. Rarely needed. |
| **Import inventory files** | For an installation with neither a PC-Link nor a `.nkb`. |
| **Take over from Nikobus** | See [Coming from Nikobus](#coming-from-nikobus). |

---

## What you get

| In your installation | In Home Assistant |
|---|---|
| Switch module output | `switch`, or `light` when ticked as switching a lamp |
| Dimmer output | `light` with brightness, or `fan` with speed |
| Roller output | `cover` with a position estimated from its run times |
| Light scene (central function) | `scene`, activated by its own telegram |
| Function that only moves shutters | `cover` for the group |
| Each key of a plate, remote or interface | `event` entity, and a press `button` (created disabled) |
| PC-Logic or Modular Interface input | `switch` that follows and sends its two frames |
| Motion detector | occupancy and light-level `binary_sensor` |
| Audio distribution zone | `media_player`: on, off, volume steps, source |
| RGB controller | `light`: on or off and its colour, switched by its linked keys |
| The gateway | connection, discovery, programming and clock sensors; four buttons |

**How it is organised**

- **Devices are filed by kind** under the **Nikobus Bridge**: *Output modules*, *System modules*, *Wall buttons*, *Remotes*, *Interfaces*, *Scenes* and *Shutter groups*.
- **Names follow the Nikobus software.** A plate the project file names is shown as `11: Boudoir (Hall)`, a module as `Dimcontroller (Cellar)`.
- **A key says where it sits**, in its name: an arrow for its row and its column counted from the left. "Key 1C ↑2" is the upper key of the second column, on a plate with two, four or eight keys. Its `position` attribute says the same in words (`upper_right`). The layouts are the vendor manual's drawings of the plates. Names you gave are kept, and entity IDs do not change.
- **An output no key drives is created disabled.** Enable it if you use it from Home Assistant only. An output with a name from the project file, or on a module whose links could not all be read, is enabled.
- **Deleting the device of a module or a plate** leaves it out from then on, through later discoveries too.

**What an entity tells you**

Open an entity's details to see what it is on the bus, with every link as the module holds it (`mode`, `t1`, `t2`, the record itself) next to what the link does:

| Entity | Its attributes |
|---|---|
| An output | its module and channel, and the keys that drive it |
| A shutter | its run times and end margin, and who moved it last |
| A key, and its press button | its plate and position, the outputs it drives (`drives` in one line, `linked_outputs` in full) |
| A scene | its outputs, and the keys that trigger it |

---

## Key presses in automations

One press gives up to four kinds of event:

| When | `type` | Comes with |
|---|---|---|
| At the first telegram | `pressed` | |
| While the key stays down, each second | `hold` | `seconds`: 1, 2, 3 |
| Released within a second | `short_release` | `duration`, `seconds` |
| Released later | `long_release` | `duration`, `seconds` (3 for three or more) |

Trigger on the key's **event entity**, or on the bus event **`nikobus_ng_press`**, which also fires for an address the inventory does not know:

```yaml
triggers:
  - trigger: event
    event_type: nikobus_ng_press
    event_data:
      address: "9A93EE"
      type: hold
      seconds: 2
```

Two things to get right:

- **Always give a `type`.** Without it the automation fires on the press, on each second it is held, and on the release.
- **Quote the address.** An all-digit address with an `E` in it is otherwise read as a number.

A blueprint, [`nikobus_ng_key_controls_entity.yaml`](blueprints/automation/fdebrus/nikobus_ng_key_controls_entity.yaml), lets a key toggle, switch, open or close an entity of any integration.

---

## For AI assistants

Home Assistant shows an entity and its state. It cannot show the wiring: which key drives which output, in which mode, for how long. Nikobus NG returns it as data, in two ways.

| | What it gives | For |
|---|---|---|
| **The `nikobus_ng.describe` action** | The whole installation at once: every output with the keys that drive it, every key with what it drives, the scenes, the logical inputs, the health of the bus. | scripts, and pasting into a chat |
| **The "Nikobus NG" tools** | The same in pieces: `nikobus_overview`, `nikobus_output`, `nikobus_key`, `nikobus_scenes`, `nikobus_health`, which only read, and `nikobus_press_key`. | Home Assistant's conversation agents and its MCP server |

> **An assistant given these tools sees the whole installation**: every output, key and scene of Nikobus NG with its name, area and state, and it can press any known key. The tools do not follow the per-assistant *Expose* setting, since a key's links cross the house and a partial view could not explain them. Enabling the Nikobus NG tools for an assistant is the one switch that grants this.

A link is said in words, with its values under what they are instead of the vendor's T1 and T2:

```json
{
  "mode": "M12 (Preset on)",
  "does": "Sets the output to 40 % (4,0 V), whatever its last level. Dimming takes 4 s.",
  "level": "40 % (4,0 V)",
  "dim_time": "4 s"
}
```

The wording is the library's, taken from the vendor's manuals. A mode on two or four keys is said for the key the link is on: "This key switches the output on; the lower key of the pair switches it off."

---

## Coming from Nikobus

Nikobus NG can be tried without losing anything: it has its own domain and its own store, and re-enabling the Nikobus entry takes you back.

**The step-by-step guide is [Moving from Nikobus to Nikobus NG](docs/migrating-from-nikobus.md)**: what to prepare, what moves by itself, what you change by hand, and the way back.

In short:

- **Take over** (*Configure → Take over from Nikobus*, with the Nikobus entry disabled) moves entity IDs, names, areas, aliases, labels, icons and voice exposure onto Nikobus NG's entities, so dashboards, automations on entities and history keep working. LED keys and shutter run times come along.
- **The form says what it would do before anything moves**, the Nikobus entities are parked under `<id>_nikobus`, and **Give back** undoes it. Removing the Nikobus NG entry gives everything back too.
- **By hand:** automations on Nikobus bus events (`nikobus_button_pressed` and the others) and calls to `nikobus.*` actions. The guide has the mapping.

How the two differ:

| | Nikobus | Nikobus NG |
|---|---|---|
| Discovery | two buttons, in order | one action, automatic on first setup |
| Keys | binary sensors and up to seven kinds of bus event | `event` entities, one bus event |
| Relay as light, dimmer as fan | module customisation | two tick lists |
| Outputs without a name | no entity | an entity, disabled when no key drives it |
| Gone modules and plates | detect, then purge | a repair for a module; delete the device of either |
| Scenes made in the options | yes | no: use Home Assistant's own scenes |
| Refresh interval | adjustable | fixed |
| Tests | against a stub of Home Assistant | against the real core and a simulated bus |

---

## Supported hardware

What the PC-Link inventory and the link scan recognise comes from the library and is the same as for the [Nikobus integration](https://github.com/fdebrus/Nikobus-HA#supported-hardware). The last column says what Nikobus NG itself has met on a real installation.

| Hardware | Ref | Seen on real hardware |
|---|---|---|
| Switch module, compact switch module | `05-000-02`, `05-002-02` | yes |
| Dim controller | `05-007-02` | yes |
| Compact dim controller | `05-008-02` | no |
| Roller shutter module | `05-001-02` | yes |
| PC-Link | `05-200` | yes, generation 3 or later |
| PC-Logic, its logical inputs | `05-201` | yes |
| Feedback Module | `05-207` | yes, its reads picked up; LED keys not yet |
| Modular Interface | `05-206` | no |
| Audio distribution module | `05-205` | no |
| RGB controller | `340-00112` | no |
| Bus push buttons, 2, 4 and 8 keys | `05-060`, `05-064`, `4*-078` | yes |
| Push button with IR receiver | `05-09x` | yes |
| Push buttons with feedback LEDs | `05-061`, `05-060-02`, `05-064-02`, `05-078-02` | no |
| RF-bus push buttons, mini RF transmitter | `05-302`, `05-304`, `05-311` | yes |
| Universal interface | `05-058` | yes |
| Motion detector | `05-7*5` | no |
| No PC-Link: `.nkb` or two files as inventory | | no |

"Yes" means discovered, its links read and its state shown.

---

## What is verified

Nikobus NG runs on **one real installation**: a serial PC-Link, six output modules, a Feedback Module and 44 plates, on Home Assistant 2026.11. Everything else is tested against the real Home Assistant and `nikobus-simulator`, the simulated PC-Link shipped with the library.

<details>
<summary><b>Seen on the real installation</b></summary>

- Setup, both passes of the discovery, and the read of every output group.
- Names, rooms and the three light scenes from its `.nkb`; six logical inputs.
- A light scene activated from Home Assistant: its key went on the bus and the dimmer it holds went to its preset (4,0 V in the link, `0x66` of `0xFF` read back).
- The PC-Link's clock read, and set: from 47 minutes ahead to one second.
- The description: 52 outputs, 154 keys, 4 scenes, 6 logical inputs.
- A module the PC-Link lists but that is not on the bus: reported, and kept out once its device was deleted.
- A take-over of 45 outputs, 3 scenes, 6 input switches and 152 keys with their press buttons, with the shutter run times set in Nikobus.
- A key pressed and held at the wall: pressed, held, and released after a short and a long press, as events of its entity (2026-11-13).
- Devices filed by kind under the bridge.

</details>

<details>
<summary><b>Not yet seen on real hardware</b></summary>

- Switching an output and moving a shutter from Home Assistant, observed end to end.
- LED keys with a Feedback Module.
- An audio module, an RGB controller, a motion detector, a Modular Interface.
- An installation without a PC-Link, and a PC-Link older than generation 3.
- A module's checksum check and memory backup.
- The AI tools used by a real conversation agent.
- The take-over's import of LED keys from a real Nikobus store (that installation had none).

</details>

<details>
<summary><b>Limits of the tests themselves</b></summary>

- The connection, the bus and the modules are never faked. What the simulator lacks (the PC-Link's inventory, a module's checksum, the clock, a colour controller) is answered by the test, which says so, and a few timing constants are shortened.
- The test harness runs Home Assistant 2026.10. Entity naming changed in 2026.11; that rule is checked against the 2026.11 source, not on a running 2026.11.

</details>

---

## Known limitations

**By design**

- **Read-only.** A module's programming is never written: no restore from a backup. Setting the PC-Link clock is the only write.
- **One client per bus, one config entry.** Stop any other Nikobus software; two buses cannot share one Home Assistant.
- **Names come from the `.nkb`.** The bus carries wiring, not labels.
- **The gateway is not auto-discovered.** The serial path or `host:port` is entered by hand.
- **The refresh interval is fixed**: every two minutes, or every five for what a Feedback Module does not report.

**What the bus does not offer**

- **A shutter's position.** A module says which way the motor runs, never where the shutter is. The position is estimated, and unknown until the shutter has run to an end once: until then *open* and *close* run the whole travel, and a position cannot be asked for. It is kept across restarts.
- **The RGB controller's colour and brightness cannot be set**, and an audio zone's volume level cannot be read.
- **A press sent by Home Assistant is not echoed.** No event fires for it; the modules it drives are read instead.

**Good to know**

- **Calendar programs stay in the PC-Link.** A calendar channel that drives an output is named in `controlled_by`; its program is neither read nor fired.
- **A dimmer switched on without a level takes the last one seen since Home Assistant started**, and full after a restart.

---

## Development

```bash
pip install -r requirements_test.txt   # Python 3.14; Home Assistant and nikobus-simulator
python -m pytest -q                    # about 180 tests, 9 to 10 minutes
ruff check .
```

The code is in `custom_components/nikobus_ng/`: `hub.py` (connection, state, commands), `inventory.py` (the one store), `discovery.py`, `config_flow.py`, one file per platform, `maintenance.py`, `describe.py` and `llm_api.py` (the wiring as data), `takeover.py`. [`CLAUDE.md`](CLAUDE.md) holds the rules the project is developed under.

The design started from a [review of the Nikobus integration](https://github.com/fdebrus/Nikobus-HA/blob/main/documentation/nikobus-ng-review.md). Nikobus NG is about 6 300 lines of Python against 15 000 there.

---

## Issues, discussion & legal

**Bugs and requests:** [GitHub issues](https://github.com/fdebrus/Nikobus_NG/issues). The integration's *Download diagnostics* and a short description are what help most; the diagnostics hold addresses and counts, no names.

**Questions:** the [Home Assistant community thread](https://community.home-assistant.io/t/custom-component-nikobus/732832) of the Nikobus integration.

**Trademark:** Nikobus is a trademark of Niko NV. This project is an independent community effort, not affiliated with, endorsed by, or sponsored by Niko NV.

**License:** [PolyForm Noncommercial License 1.0.0](LICENSE) — you may use, copy, modify and share the software for any **noncommercial** purpose. **Any commercial use requires a separate license from the maintainer.** Provided "as is", without warranties of any kind.
