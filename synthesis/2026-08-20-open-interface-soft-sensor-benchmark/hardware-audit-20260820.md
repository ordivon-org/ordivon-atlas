# Local Hardware Audit — 2026-08-20

Purpose: determine whether the owner-side physical contact/readout pilot can be executed on the currently attached workstation. This is an availability receipt, not a statement about what hardware could be acquired later.

## Linux/WSL observation

No `/dev/ttyUSB*`, `/dev/ttyACM*`, `/dev/hidraw*`, IIO devices or `/dev/video*` were exposed in the Runtime-visible Linux environment. No common instrument Python packages (`pyserial`, `pyvisa`, `pymeasure`, `nidaqmx`, `minimalmodbus`, `pymodbus`) were installed.

## Windows observation

Windows reported COM3 and COM4, both Bluetooth serial-port enumerations (`BTHENUM`), not an attached measurement/DAQ/Arduino instrument. USB enumeration showed host controllers/hubs and the integrated camera; no detected Arduino/CH340/CP210/FTDI/DAQ/Keithley/Keysight/Rigol/Siglent/Fluke/National Instruments/USB-serial measurement device.

## Standing

`PhysicalContactPilot = BLOCKED_BY_HARDWARE_ABSENCE` on the currently attached machine.

This is not a failed contact-repeatability result. No spring/pogo pad, resistance acquisition chain, motorized load axis or soft cartridge is physically present/accessible through the observed interfaces, so no physical receipt can be generated honestly.

Admissible next work while blocked: controller/firewall harness implementation and synthetic red-team validation. Physical calibration remains gated until actual hardware is attached and owner-visible.
