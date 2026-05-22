# Phase 4 (optional): Linux / WSL SocketCAN & `can-utils`

Use when Pibiger devices appear as **[SocketCAN](https://wiki.archlinux.org/title/CAN)** interfaces (often `can0`). Pibiger states compatibility with **[Linux SocketCAN](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide)** alongside SavvyCAN.

## Prerequisites

- Native Linux (Ubuntu, etc.) is usually simpler than USB-CAN routing through WSL unless you vendor-specific pass-through.
- Install **can-utils** from your distro (see [linux-can/can-utils](https://github.com/linux-can/can-utils)).

Common package names:

```bash
sudo apt update
sudo apt install can-utils iproute2
```

## Bringing up the interface

After the adapter enumerates (`ip link`), typical pattern (adapt bitrates / FD flags for your vehicle):

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on
```

Consult your OEM bus nominal + FD data bitrate; wrong values obscure traffic.

Documentation:

- **`candump`**, **`canplayer`**, **`cangen`**, etc.: [can-utils README](https://github.com/linux-can/can-utils/blob/master/README.md)
- **`cansniffer`**: [Debian `cansniffer` manual](https://manpages.debian.org/unstable/can-utils/cansniffer.1.en.html) — `-f` options relate to CAN FD display/mode handling (see manual for your distro version).

## Python on Linux (`python-can`)

- **SocketCAN** backend: see [python-can SocketCAN docs](https://python-can.readthedocs.io/en/stable/interfaces/socketcan.html).
- **SLCAN** / serial path: see [python-can slcan docs](https://python-can.readthedocs.io/en/stable/interfaces/slcan.html) (limitations differ from native SocketCAN FD).
- **gs_usb / candleLight family**: see [python-can `gs_usb` documentation](https://github.com/hardbyte/python-can/blob/main/doc/interfaces/gs_usb.rst); Windows WCID/`WinUSB` vs Zadig is described there alongside [Zadig](https://zadig.akeo.ie/).

## WSL caveat

Classic WSL often **does not** expose arbitrary USB Gadgets as easily as bare Linux. Prefer **native Linux** or Windows + SavvyCAN for Pibiger if USB-CAN fails under WSL.

## Next

Proceed to Phase 5: [VALIDATION_AND_GUARDRAILS.md](VALIDATION_AND_GUARDRAILS.md).
