# Phase 1: Windows driver + SavvyCAN

Complete these steps on the **same PC** where you will capture (your Windows 10/11 machine).

## 1. Install Pibiger driver

Per [Pibiger Quick Start — How to Use On Windows](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide):

1. Download **Driver** from the quick-start page (ZIP link in section 1-2).
2. Extract and run the installer / follow vendor instructions inside the ZIP.
3. Plug in **USB** to the PC (adapter not connected to CAN yet).
4. Open **Device Manager** (`Win + X` → Device Manager).
5. Confirm a CAN-related USB device appears without errors (name varies by driver).

If the device shows as unknown or the wrong USB class:

- Refer to vendor docs for “change product ID” if you dual-boot Linux/macOS ([Pibiger quick start § 1-7](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide)).
- As a fallback for WinUSB-compatible adapters, see [Zadig](https://zadig.akeo.ie/)—**only** if vendor docs say WinUSB/Zadig is appropriate for your SKU.

## 2. SavvyCAN builds

Official builds: **[SavvyCAN Releases](https://github.com/collin80/SavvyCAN/releases)**.

Recommended order:

1. Install latest **stable** tagged release (`SavvyCAN-Windows_x64_CIBuild.zip` or equivalent for that tag).
2. If the GUI does not connect to your adapter, try the **development / continuous** build from the releases page—but expect rough edges.

Pibiger also hosts **SavvyCAN FD** package—see ZIP link **SavvyCAN FD Software** on the same [quick start](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide)—use whichever works best with your cable.

Steps:

1. Download ZIP → extract to e.g. `C:\Tools\SavvyCAN\`.
2. Run `SavvyCAN.exe`.
3. **Connection Window**: add your device via the vendor-supported method (SerialBus plugin / driver-specific entries per [SavvyCAN connection docs](https://savvycan.com/docs/connectionwindow.html)).

## 3. Verification (before touching the vehicle bus)

- [ ] Driver installed, no Device Manager warnings.
- [ ] SavvyCAN launches.
- [ ] Connection can be opened (even with **no CAN** attached you may see no frames—that is OK).
- [ ] Note your **planned** nominal bitrate and CAN FD data rate from service docs or OEM bus info—set them **before** first real capture once you attach to CAN.

## 4. Next

Continue to [PASSIVE_CAPTURE_CHECKLIST.md](PASSIVE_CAPTURE_CHECKLIST.md).
