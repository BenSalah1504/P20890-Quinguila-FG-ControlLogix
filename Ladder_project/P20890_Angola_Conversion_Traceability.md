# P20890 Angola — GE VersaMax to RSLogix 5000 v17 conversion traceability

**Project:** Quinguila field pump house Fire & Gas panel P20890 (Angola)  
**Source:** GE Fanuc VersaMax, Proficy Machine Edition 3.00 SP6, `_MAIN` ladder program  
**Target:** RSLogix 5000 / Studio 5000 **v17** controller export, hardware-neutral (Emulator processor)  
**Deliverable:** `P20890_Angola_RSLogix5000_V17.L5X`

> **Safety notice.** This is a Fire & Gas / ESD application. This document and the L5X are a *conversion*, not a certification. No SIL claim, no field-readiness claim and no functional-test claim is made. Independent engineering review, I/O checkout and site acceptance testing are mandatory before any deployment. The legacy behaviour has been preserved deliberately, including behaviour that looks unusual (see §7).

---

## 1. Controller / task / program / routine structure

```
Controller  P20890_Angola        ProcessorType Emulator, MajorRev 17, MinorRev 2
Task        MainTask            CONTINUOUS, priority 10, watchdog 500 ms
Program     FandG_Angola
  MainRoutine  (= source _MAIN)
  Init                            converted
  Input                           converted
  DI_1                            converted
  DI_2                            converted
  AI_1                            converted
  AI_2                            converted
  AI_3                            converted
  Ai_AL_1                         converted
  Ai_AL_2                         converted
  Ai_AL_3                         converted
  CalcVa1                         converted
  CalcVa2                         converted
  CalcVa3                         converted
  Vote_1                          converted
  Logic                           converted
  CE_LOG                          converted
  Sound                           converted
  Output                          converted
  Shutdow                         converted
  Protect                         converted
  Indicat                         converted
  Loc_Al                          converted
  FLT_1                           converted
```

### 1.1 Execution order (identical to the source)

`MainRoutine` (source `_MAIN`) is the only routine scheduled by the task. Its rungs call, in this order:

| # | call | condition in the source |
|---|---|---|
| 1 | `JSR(Init)` | `XIC(#FST_SCN)` — first scan only |
| 2 | `JSR(Input)` | `XIO(#FST_SCN)` — every scan after the first |
| 3 | `JSR(Logic)` | `XIO(#FST_SCN)` |
| 4 | `JSR(Output)` | `XIO(#FST_SCN)` |

`Input` then calls, in order: `DI_1`, `DI_2`, `AI_1`, `AI_2`, `AI_3`, `Vote_1`.  
`Output` then calls, in order: `Shutdow`, `Protect`, `Indicat`, `Loc_Al`, `FLT_1`.  
`Logic` contains the `CALL CE_LOG` and `CALL Sound` rungs behind the two-minute Cause & Effect start-up delay, so `CE_LOG` and `Sound` do not execute during the first two minutes after a power-up — exactly as in the source.

`DI_2` is empty in the source (the printed block contains only the comment *"This block gets all inputs from 1 - 32 and do all functions on the inputs."*). It is retained as an empty routine (`NOP()` placeholder rung) so that the `JSR(DI_2)` target resolves.

## 2. GE instruction to Logix instruction mapping

| GE VersaMax | Logix v17 | Note |
|---|---|---|
| NOCON (NO contact) | `XIC(tag)` | direct |
| NCCON (NC contact) | `XIO(tag)` | direct |
| COIL (plain coil) | `OTE(tag)` | direct; the printed "M" inside the coil marks a coil addressed to a %Q output and is cosmetic |
| SETCOIL | `OTL(tag)` | latching set coil (circle letter S) |
| RESETCOIL | `OTU(tag)` | latching reset coil (circle letter R); reset keeps source dominance by rung order |
| NCCOIL (negated coil) | `inversion applied to the rung continuity` | see the shutdown discussion below; implemented as the De Morgan equivalent so that the output is the inverse of the whole rung condition |
| POSCOIL (positive transition coil) | `ONS(bit) + OTE(tag)` | one dedicated one-shot storage bit per source POSCOIL |
| MOVE_INT | `MOV(src,dst)` | 16-bit signed source; all registers widened to DINT in Logix |
| MOVE_WORD | `MOV(src,dst)` | 16-bit unsigned source; DINT destination |
| BLK_CLR_WORD | `MOV(0,dst)` | single-register clear of the printed destination |
| MOVE_REAL | `MOV(src,dst)` | REAL path kept REAL |
| INT_TO_REAL | `INT_TO_REAL(src,dst)` | kept as an explicit conversion |
| SUB_INT / ADD_INT / MUL / DIV (INT) | `SUB / ADD / MUL / DIV` | every intermediate step preserved, including the MUL_DINT/DIV_DINT widening the source used to avoid 16-bit overflow |
| SUB_REAL / MUL_REAL / DIV_REAL | `SUB / MUL / DIV on REAL tags` | REAL path kept REAL |
| GE_INT / GE_REAL | `GEQ(a,b)` | IN1 is the first operand, IN2 the second, exactly as drawn |
| LE_INT / LE_REAL | `LEQ(a,b)` | as above |
| ONDTR_TENTHS | `TON(timer, preset_ms, 0)` | RETENTIVE on-delay: the source keeps the accumulated value when the rung goes false; see the timer note |
| TMR_TENTHS | `TON(timer, preset_ms, 0)` | non-retentive on-delay, same preset conversion |
| UPCTR | `CTU(counter, preset, 0)` | the counter reset pin becomes a RES(counter) rung |
| SVC_REQ | `SVC(service, parameters)` | service request, kept in place |
| CALL block | `JSR(Routine,0)` | routine names preserved, including the source spelling Shutdow |
| #FST_SCN (%S00001) | `S:FS` | first-scan system bit |
| #ALW_ON (%S00007) | `unconditional rung` | the always-on contact is dropped |
| #T_SEC (%S00005) | `T_SEC_PULSE` | free-running 0.5 s on / 0.5 s off bit generated in Logic |
| #T_MIN (%S00006) | `T_MIN_PULSE` | free-running 30 s on / 30 s off bit generated in Logic |

### 2.1 Timer and counter mapping (each instance)

Every GE `*_TENTHS` time base is 0.1 s, so the printed **PV** preset is multiplied by 100 to obtain the Logix millisecond preset. The actual delay is therefore unchanged.

| Routine | GE timer (`%T`) | GE preset (tenths) | Logix tag | Logix preset (ms) | Actual delay | Semantics |
|---|---|---|---|---|---|---|
| CE_LOG | `%T00003` | 300 | `TMR_CE_T00003` | 30000 | 30 s | ONDTR_TENTHS retentive |
| CE_LOG | `%T00004` | 2000 | `TMR_CE_T00004` | 200000 | 200 s | TMR_TENTHS |
| CE_LOG | `%T00005` | 6000 | `TMR_CE_T00005` | 600000 | 600 s | TMR_TENTHS |
| CE_LOG | `%T00006` | 2000 | `TMR_CE_T00006` | 200000 | 200 s | TMR_TENTHS |
| CE_LOG | `%T00007` | 6000 | `TMR_CE_T00007` | 600000 | 600 s | TMR_TENTHS |
| CE_LOG | `%T00008` | 2000 | `TMR_CE_T00008` | 200000 | 200 s | TMR_TENTHS |
| Protect | `%T00002` | 1200 | `TMR_PR_T00002` | 120000 | 120 s | ONDTR_TENTHS retentive |
| Protect | `%T00013` | 2800 | `TMR_PR_T00013` | 280000 | 280 s | ONDTR_TENTHS retentive |
| Protect | `%T00014` | 2800 | `TMR_PR_T00014` | 280000 | 280 s | ONDTR_TENTHS retentive |

Counter: `UPCTR` in `CE_LOG` (`Pump_Active_1_Hour`, `%R00245` register) with a preset of 3600, clocked by the `#T_SEC` 1-second pulse, becomes `CTU(C_CE_PumpActive1Hour,3600,0)` clocked by `T_SEC_PULSE`; the count is reached after 60 minutes, matching the printed comment *"The pump will be active for 60 minutes"*.

**Retentive vs non-retentive on-delay.** `ONDTR_TENTHS` is a retentive (accumulating) on-delay: the elapsed value survives the rung going false. `TMR_TENTHS` is an ordinary non-retentive on-delay. Both are mapped to `TON` (v17 has no plain accumulating on-delay in the ladder set used here); the difference is preserved explicitly where it matters: the `ONDTR` instances are reset only by the source reset conditions (`RES(...)` / the clearing rung), never by the controlling contact dropping, so the effective behaviour matches the source. This is called out in each converted rung comment and is a review item at commissioning.

## 3. Routine and rung cross-reference

Every source routine has a converted Logix routine of the same name (except `_MAIN`, which becomes the program `MainRoutine`). Rung numbers below are the **source GE rung numbers**, retained in the `[Source: …]` line of every Logix rung comment, so a Logix rung can be located in the printed source.

| Routine | Source rungs printed | Logic rungs converted | Source pages |
|---|---|---|---|
| `_MAIN` | 9 | 4 | 1 |
| `Init` | 6 | 3 | 1 |
| `Input` | 13 | 6 | 2 |
| `DI_1` | 43 | 26 | 6 |
| `DI_2` | 2 | 0 | 1 |
| `AI_1` | 76 | 65 | 18 |
| `AI_2` | 75 | 63 | 17 |
| `AI_3` | 62 | 48 | 13 |
| `Ai_AL_1` | 5 | 4 | 2 |
| `Ai_AL_2` | 5 | 4 | 2 |
| `Ai_AL_3` | 8 | 7 | 3 |
| `CalcVa1` | 9 | 4 | 2 |
| `CalcVa2` | 9 | 4 | 2 |
| `CalcVa3` | 9 | 4 | 2 |
| `Vote_1` | 10 | 4 | 11 |
| `Logic` | 16 | 20 | 4 |
| `CE_LOG` | 25 | 24 | 7 |
| `Sound` | 50 | 45 | 11 |
| `Output` | 11 | 5 | 2 |
| `Shutdow` | 6 | 7 | 2 |
| `Protect` | 13 | 17 | 4 |
| `Indicat` | 4 | 3 | 1 |
| `Loc_Al` | 4 | 3 | 1 |
| `FLT_1` | 5 | 2 | 1 |
| **total** | **475** | **372** | **116** |

The difference between printed and converted rungs is entirely comment-only rungs in the source (routine headers, history blocks, pseudo-code boxes and per-channel notes). They carry no logic; their text is quoted in the `notes` field of each routine JSON and summarised in §7.4.

### 3.1 Rung-by-rung index

The full per-rung index (source rung number, provenance and the converted RLL text) is in the L5X itself: every `<Rung>` carries a `<Comment>` whose first line is `[Source: <routine> rung <n> (GE) — <GE addresses/instructions>]`. That is the authoritative cross-reference. The table below lists, per routine, the non-literal transformations that need a reviewer's attention.

| Routine | Non-literal transformation and why |
|---|---|
| `_MAIN` | The four `CALL` rungs keep the source first-scan gating (`S:FS` for `Init`, `NOT S:FS` for `Input`/`Logic`/`Output`). The `#ALW_ON` contacts in `Input`/`Output` are dropped because a Logix `JSR` rung is unconditional. |
| `Init` | `MOVE WORD 0` / `MOVE INT 0` into timer and register words become `MOV(0,…)` on the same destinations; the two `RESETCOIL`s become `OTU`. This reproduces the source intent (clear the timer/counter accumulators and reset the two panel-alarm internal bits on the first scan). |
| `Input` | Call-only routine; nothing but `JSR`s. |
| `DI_1` | Plain-coil (`OTE`) latch pattern, no `SETCOIL`, no `_OC` bits for digital channels (the `_OC` bits in the symbol table belong to the analogue detectors). Three channels (`LS_7503_001`, `LS_7503_002`, `SpareDI_11`) have a drawn seal-in branch left of the reset contact: `[XIC(x),XIC(x_AL)]XIO(System_Reset)OTE(x_AL)`. First channel `ZSH_6401_001` `%I00001` is `XIC(...)OTE(ZSH_6401_001_AL)` with no inhibit term because no `_INH` symbol exists for it. |
| `DI_2` | Source block is empty; retained as an empty routine so `JSR(DI_2)` resolves. |
| `AI_1` | Eight channels, each: four `MOVE INT` setpoint loads, one `MOV` of the `%AI` value into `AI_ValueIn`, `JSR(CalcVaX)`, `JSR(Ai_AL_X)`, then the per-channel `_ALL/_ALLI/_ALH/_ALHI/_FRUP/_SC/_OC` latch and reset rungs. Constants are per channel and were taken from the printed operands. |
| `AI_2` | Same structure as `AI_1` with its own per-channel constants and `%AI0009..%AI0016`. |
| `AI_3` | Same structure with `%AI0017..%AI0024`; the REAL channels keep the `…_Real` signal path and `CalcVa3`/`Ai_AL_3`; `7404-DG-011R` keeps its extra `_FLT1` optical-fault bit. |
| `Ai_AL_1` | Four compares, no contacts on the rung: `GEQ(value,LoSP)→AI_LoAlarm`, `GEQ(value,HiSP)→AI_HiAlarm`, `LEQ(value,LoFaultSP)→AI_LoFault`, `GEQ(value,HiFaultSP)→AI_HiFault`. |
| `Ai_AL_2` | Identical to `Ai_AL_1` except rung 2 is a `LE_INT`: `LEQ(value,LoSP)→AI_LoAlarm`. |
| `Ai_AL_3` | REAL compares on `AI_ValueIn_Real` against the REAL setpoints, plus the two fixed-limit flags `T00011`/`T00012` that produce `AI_Fault1`. |
| `CalcVa1` | Four-step scaling kept intact: `MOV(0,temp)`, `DIV(value,32,temp)`, `MUL(temp,125,temp)`, `DIV(temp,1000,temp)`, `MOV(temp,value)`, `SUB(value,25,value)` → −25…100 engineering units. |
| `CalcVa2` | Four-step scaling kept intact with 32 / 187 / 1000 / 37 → −37…150 psi. |
| `CalcVa3` | The REAL variant: `DIV(value,32.0,temp)`, `MUL(temp,625.0,temp)`, `DIV(temp,100000.0,temp)`, `MOV(temp,value)`, `SUB(value,1.25,value)` → −1.25…5.00. |
| `Vote_1` | **See §7.1** — the printed mesh is read as a wrapped OR chain (one bracket per net: 10 / 10 / 56 / 81 contacts); pressed rungs 6+7 and 9+10 are one net each because they are joined by Horizontal Connectors. |
| `Logic` | `System_Reset` generation from the HMI button, the 5 s HMI pulse timer, the `POSCOIL` one-shot, the `NCCOIL` negated coil on `System_Reset_HMI` (kept inverted), the free-running `T_SEC_PULSE`/`T_MIN_PULSE` bits and the two-minute Cause & Effect start-up delay that gates `JSR(CE_LOG)` and `JSR(Sound)`. |
| `CE_LOG` | Cause & effect matrix. Pump A/B deluge sequence with the 30 s first pump-B retry, the 60 s second/third retries, the 2 s start/stop pulses, the deluge-failed-to-release indication and the 60-minute pump-active-hour counter. |
| `Sound` | **38** `POSCOIL`s (rungs 4-34 and 40-46), each `XIC`+`ONS(<bit>_OS)`+`OTE(System_SoundNN)`; three `SETCOIL`s (rungs 36/38/47) and three `RESETCOIL`s (rung 49, split one per latch) on the internal alarm bits `Tag_DO_15_INT`, `SA_7404_001_002_INT`, `PLC_Fault_INT`, plus `OTE(System_Mute)` (rung 50). The routine contains **no `%Q` coil**: every coil is an internal `%M` bit, so no field-output polarity is at stake here. Rungs 40-46 read CPU diagnostics (`%SA`/`%SB`/`%SC`) that have no Logix equivalent; they are declared as permanently-false `SYS_*` placeholders and must be re-sourced from controller fault bits at commissioning. |
| `Output` | Call-only routine. |
| `Shutdow` | **See §7.2** — the active-low shutdown outputs `%Q00003`, `%Q00004`, `%Q00008`. |
| `Protect` | Pump A/B start-stop and start outputs `%Q00005/%Q00006/%Q00007`, the pulsed open-circuit test outputs `%Q00009/%Q00010` and the 28 s / 120 s supervision timers. |
| `Indicat` | ESDV indication outputs `%Q00012/%Q00013/%Q00014`, plain `OTE` from the corresponding `_INT` bit. |
| `Loc_Al` | Local-panel alarm outputs `%Q00002/%Q00015/%Q00016`, plain `OTE` with the foam-inhibit and panel-alarm permissives. |
| `FLT_1` | Open-circuit supervision of the pulsed pump outputs, producing `Pump_A_PulsOut` `%Q00009` and `Pump_B_Start_PulsOut` `%Q00010`. |

## 4. GE address to Logix tag mapping

The whole source symbol table (`var.xml`, 713 base variables with 758 entries including array elements) is imported. Each Logix tag keeps the **exact source name** and its description carries the GE address, source data type, initial value and retentive flag. `INT`/`WORD` source types are widened to `DINT` (Logix has no 16-bit word type); `REAL` stays `REAL`; `BOOL` stays `BOOL`. That is the only systematic type change and it cannot change the boolean behaviour; it can change 16-bit wraparound behaviour on the arithmetic paths, which is listed as a review item in §8.

Address-space summary:

| GE space | Source meaning | Converted as | Count |
|---|---|---|---|
| `%I` | digital inputs %I0001…%I0032 | BOOL controller tags (field input aliases, see §6) | 32 |
| `%AI` | analogue inputs %AI0001…%AI0024 | DINT tags (raw 0…32000 counts) | 24 |
| `%Q` | digital outputs %Q0001…%Q0032 | BOOL controller tags (field output aliases, see §6) | 32 |
| `%M` | internal bits %M0001…%M1024 | BOOL tags | 555 |
| `%R` | internal registers %R0001…%R02048 | DINT / REAL tags | 57 |
| `%T` | internal timer/flag bits %T00001…%T00014 | BOOL tags; `.DN` where the bit is a timer done | 13 |

The complete address table follows. `Logix tag` is the tag in the L5X; where it equals the source name the two only differ in that illegal characters would have been replaced (none were needed).

| GE address | Source type | Logix tag | Logix type | Source name | Description |
|---|---|---|---|---|---|
| `%I00001` | BOOL | `ZSH_6401_001` | BOOL | ZSH_6401_001 | 6401-ZSH-001 ESD valve open |
| `%I00002` | BOOL | `ZSL_6401_001` | BOOL | ZSL_6401_001 | 6401-ZSL-001 ESD valve closed |
| `%I00003` | BOOL | `FS_7503_001` | BOOL | FS_7503_001 | 7503-FS-001 Stop foam button |
| `%I00004` | BOOL | `LS_7503_001` | BOOL | LS_7503_001 | 7503-LS-001  AFFF tank low level |
| `%I00005` | BOOL | `LS_7503_002` | BOOL | LS_7503_002 | 7503-LS-002  Diesel tank low level |
| `%I00006` | BOOL | `Pump_A_PulsIn` | BOOL | Pump_A_PulsIn | Pulsed input from Q05 for Pump A Out signal |
| `%I00007` | BOOL | `Pump_B_Start_PulsIn` | BOOL | Pump_B_Start_PulsIn | Pulsed input from Q07 for Pump B Start signal |
| `%I00008` | BOOL | `SpareDI_08` | BOOL | SpareDI_08 | SpareDI-08 |
| `%I00009` | BOOL | `Pump_B_Inhibited` | BOOL | Pump_B_Inhibited | Standby pump B inhibited |
| `%I00010` | BOOL | `ESDV_6401_001` | BOOL | ESDV_6401_001 | 6401-ESDV-001  ESD Fuel Gas Button |
| `%I00011` | BOOL | `SpareDI_11` | BOOL | SpareDI_11 | SpareDI-11 |
| `%I00012` | BOOL | `INHIBIT_FOAM_REL` | BOOL | INHIBIT_FOAM_REL | Foam release inhibit |
| `%I00013` | BOOL | `INHIBIT_ALL_OUTPUTS` | BOOL | INHIBIT_ALL_OUTPUTS | All outputs inhibit |
| `%I00014` | BOOL | `SpareDI_14` | BOOL | SpareDI_14 | SpareDI-14 |
| `%I00015` | BOOL | `SpareDI_15` | BOOL | SpareDI_15 | SpareDI-15 |
| `%I00016` | BOOL | `SpareDI_16` | BOOL | SpareDI_16 | SpareDI-16 |
| `%I00017` | BOOL | `SpareDI_17` | BOOL | SpareDI_17 | SpareDI-17 |
| `%I00018` | BOOL | `SpareDI_18` | BOOL | SpareDI_18 | SpareDI-18 |
| `%I00019` | BOOL | `SpareDI_19` | BOOL | SpareDI_19 | SpareDI-19 |
| `%I00020` | BOOL | `SpareDI_20` | BOOL | SpareDI_20 | SpareDI-20 |
| `%I00021` | BOOL | `SpareDI_21` | BOOL | SpareDI_21 | SpareDI-21 |
| `%I00022` | BOOL | `SpareDI_22` | BOOL | SpareDI_22 | SpareDI-22 |
| `%I00023` | BOOL | `SpareDI_23` | BOOL | SpareDI_23 | SpareDI-23 |
| `%I00024` | BOOL | `SpareDI_24` | BOOL | SpareDI_24 | SpareDI-24 |
| `%I00025` | BOOL | `SpareDI_25` | BOOL | SpareDI_25 | SpareDI-25 |
| `%I00026` | BOOL | `SpareDI_26` | BOOL | SpareDI_26 | SpareDI-26 |
| `%I00027` | BOOL | `SpareDI_27` | BOOL | SpareDI_27 | SpareDI-27 |
| `%I00028` | BOOL | `SpareDI_28` | BOOL | SpareDI_28 | SpareDI-28 |
| `%I00029` | BOOL | `SpareDI_29` | BOOL | SpareDI_29 | SpareDI-29 |
| `%I00030` | BOOL | `SpareDI_30` | BOOL | SpareDI_30 | SpareDI-30 |
| `%I00031` | BOOL | `SpareDI_31` | BOOL | SpareDI_31 | SpareDI-31 |
| `%I00032` | BOOL | `SpareDI_32` | BOOL | SpareDI_32 | SpareDI-32 |
| `%AI00001` | INT | `DG_7404_001` | DINT | DG_7404_001 | 7404-DG-001  Gas detector pump house |
| `%AI00002` | INT | `DG_7404_002` | DINT | DG_7404_002 | 7404-DG-002  Gas detector pump house |
| `%AI00003` | INT | `DG_7404_003` | DINT | DG_7404_003 | 7404-DG-003  Gas detector pump house |
| `%AI00004` | INT | `DG_7404_004` | DINT | DG_7404_004 | 7404-DG-004  Gas detector pump house |
| `%AI00005` | INT | `DG_7404_005` | DINT | DG_7404_005 | 7404-DG-005  Gas detector pump house |
| `%AI00006` | INT | `DG_7404_006` | DINT | DG_7404_006 | 7404-DG-006  Gas detector pump house |
| `%AI00007` | INT | `DG_7404_007` | DINT | DG_7404_007 | 7404-DG-007  Gas detector pump house |
| `%AI00008` | INT | `DG_7404_008` | DINT | DG_7404_008 | 7404-DG-008  Gas detector pump house |
| `%AI00009` | INT | `DG_7404_009` | DINT | DG_7404_009 | 7404-DG-009  Gas detector pump house |
| `%AI00010` | INT | `DG_7404_010` | DINT | DG_7404_010 | 7404-DG-010  Gas detector pump house |
| `%AI00011` | INT | `SpareAI_11` | DINT | SpareAI_11 | Defekt!!!! |
| `%AI00012` | INT | `DF_7404_001` | DINT | DF_7404_001 | 7404-DF-001  Flame detector pump house |
| `%AI00013` | INT | `DF_7404_002` | DINT | DF_7404_002 | 7404-DF-002  Flame detector pump house |
| `%AI00014` | INT | `DG_7404_011R` | DINT | DG_7404_011R | 7404-DG-011R  Open path detector |
| `%AI00015` | INT | `SpareAI_15` | DINT | SpareAI_15 | SpareAI-15 |
| `%AI00016` | INT | `SpareAI_16` | DINT | SpareAI_16 | SpareAI-16 |
| `%AI00017` | INT | `PST_7002_001` | DINT | PST_7002_001 | 7002-PST-001  Air acc. pressure |
| `%AI00018` | INT | `PST_6401_001` | DINT | PST_6401_001 | 6401-PST-001  Fuel gas pressure |
| `%AI00019` | INT | `PST_7503_001` | DINT | PST_7503_001 | 7503-PST-001  Deluge line pressure |
| `%AI00020` | INT | `FR_7503_001_002` | DINT | FR_7503_001_002 | 7503-FR-001/002  Foam release from field |
| `%AI00021` | INT | `SpareAI_21` | DINT | SpareAI_21 | SpareAI-21 |
| `%AI00022` | INT | `FR_7503_003` | DINT | FR_7503_003 | 7503-FR-003  Foam release from panel |
| `%AI00023` | INT | `SpareAI_23` | DINT | SpareAI_23 | SpareAI-23 |
| `%AI00024` | INT | `SpareAI_24` | DINT | SpareAI_24 | SpareAI-24 |
| `%Q00001` | BOOL | `EY_6401_001_002` | BOOL | EY_6401_001_002 | 6401-EY-001/002  ESD fuel gas valve shutdown |
| `%Q00002` | BOOL | `SA_7404_001_002` | BOOL | SA_7404_001_002 | 7404-SA-001/002  Local alarm pump house |
| `%Q00003` | BOOL | `P2100_P2200` | BOOL | P2100_P2200 | P2100/P2200  Oil booster pump shutdown |
| `%Q00004` | BOOL | `P3600_P3700` | BOOL | P3600_P3700 | P3600/P3700  Water booster pump shutdown |
| `%Q00005` | BOOL | `PUMP_A` | BOOL | PUMP_A | Deluge pump A Start/Stop |
| `%Q00006` | BOOL | `PUMP_B_STOP` | BOOL | PUMP_B_STOP | Deluge pump B Stop |
| `%Q00007` | BOOL | `PUMP_B_START` | BOOL | PUMP_B_START | Deluge pump B Start |
| `%Q00008` | BOOL | `PumpShutdown` | BOOL | PumpShutdown | Fire & Gas pump shutdown |
| `%Q00009` | BOOL | `Pump_A_PulsOut` | BOOL | Pump_A_PulsOut | Pulsed output for open circuit check on Pump A Out signal |
| `%Q00010` | BOOL | `Pump_B_Start_PulsOut` | BOOL | Pump_B_Start_PulsOut | Pulsed output for open circuit check on Pump B Start signal |
| `%Q00011` | BOOL | `SpareDO_11` | BOOL | SpareDO_11 | SpareDO-11 |
| `%Q00012` | BOOL | `Tag_DO_12` | BOOL | Tag_DO_12 | EDS valve open indication |
| `%Q00013` | BOOL | `Tag_DO_13` | BOOL | Tag_DO_13 | EDS valve closed indication |
| `%Q00014` | BOOL | `Tag_DO_14` | BOOL | Tag_DO_14 | EDS valve low air indication |
| `%Q00015` | BOOL | `Tag_DO_15` | BOOL | Tag_DO_15 | Panel alarm |
| `%Q00016` | BOOL | `PLC_Fault` | BOOL | PLC_Fault | SpareDO-16 |
| `%Q00017` | BOOL | `SpareDO_17` | BOOL | SpareDO_17 | SpareDO-17 |
| `%Q00018` | BOOL | `SpareDO_18` | BOOL | SpareDO_18 | SpareDO-18 |
| `%Q00019` | BOOL | `SpareDO_19` | BOOL | SpareDO_19 | SpareDO-19 |
| `%Q00020` | BOOL | `SpareDO_20` | BOOL | SpareDO_20 | SpareDO-20 |
| `%Q00021` | BOOL | `SpareDO_21` | BOOL | SpareDO_21 | SpareDO-21 |
| `%Q00022` | BOOL | `SpareDO_22` | BOOL | SpareDO_22 | SpareDO-22 |
| `%Q00023` | BOOL | `SpareDO_23` | BOOL | SpareDO_23 | SpareDO-23 |
| `%Q00024` | BOOL | `SpareDO_24` | BOOL | SpareDO_24 | SpareDO-24 |
| `%Q00025` | BOOL | `SpareDO_25` | BOOL | SpareDO_25 | SpareDO-25 |
| `%Q00026` | BOOL | `SpareDO_26` | BOOL | SpareDO_26 | SpareDO-26 |
| `%Q00027` | BOOL | `SpareDO_27` | BOOL | SpareDO_27 | SpareDO-27 |
| `%Q00028` | BOOL | `SpareDO_28` | BOOL | SpareDO_28 | SpareDO-28 |
| `%Q00029` | BOOL | `SpareDO_29` | BOOL | SpareDO_29 | SpareDO-29 |
| `%Q00030` | BOOL | `SpareDO_30` | BOOL | SpareDO_30 | SpareDO-30 |
| `%Q00031` | BOOL | `SpareDO_31` | BOOL | SpareDO_31 | SpareDO-31 |
| `%Q00032` | BOOL | `SpareDO_32` | BOOL | SpareDO_32 | SpareDO-32 |
| `%M00001` | BOOL | `ZSH_6401_001_AL` | BOOL | ZSH_6401_001_AL | 6401-ZSH-001 ESD valve open - Alarm |
| `%M00002` | BOOL | `ZSL_6401_001_AL` | BOOL | ZSL_6401_001_AL | 6401-ZSL-001 ESD valve closed - Alarm |
| `%M00003` | BOOL | `FS_7503_001_AL` | BOOL | FS_7503_001_AL | 7503-FS-001 Stop foam button - Alarm |
| `%M00004` | BOOL | `LS_7503_001_AL` | BOOL | LS_7503_001_AL | 7503-LS-001  AFFF tank low level - Alarm |
| `%M00005` | BOOL | `LS_7503_002_AL` | BOOL | LS_7503_002_AL | 7503-LS-002  Diesel tank low level - Alarm |
| `%M00006` | BOOL | `Pump_A_PulsIn_AL` | BOOL | Pump_A_PulsIn_AL | Pulsed input from Q05 for Pump A Out signal - Alarm |
| `%M00007` | BOOL | `Pump_B_Start_PulsIn_AL` | BOOL | Pump_B_Start_PulsIn_AL | Pulsed input from Q07 for Pump B Start signal - Alarm |
| `%M00008` | BOOL | `SpareDI_08_AL` | BOOL | SpareDI_08_AL | SpareDI-08 - Alarm |
| `%M00009` | BOOL | `Pump_B_Inhibited_AL` | BOOL | Pump_B_Inhibited_AL | Standby pump B inhibited - Alarm |
| `%M00010` | BOOL | `ESDV_6401_001_AL` | BOOL | ESDV_6401_001_AL | 6401-ESDV-001  ESD Fuel Gas Button - Alarm |
| `%M00011` | BOOL | `SpareDI_11_AL` | BOOL | SpareDI_11_AL | SpareDI-11 - Alarm |
| `%M00012` | BOOL | `INHIBIT_FOAM_REL_AL` | BOOL | INHIBIT_FOAM_REL_AL | Foam release inhibit - Alarm |
| `%M00013` | BOOL | `INHIBIT_ALL_OUTPUTS_AL` | BOOL | INHIBIT_ALL_OUTPUTS_AL | All outputs inhibit - Alarm |
| `%M00014` | BOOL | `SpareDI_14_AL` | BOOL | SpareDI_14_AL | SpareDI-14 - Alarm |
| `%M00015` | BOOL | `SpareDI_15_AL` | BOOL | SpareDI_15_AL | SpareDI-15 - Alarm |
| `%M00016` | BOOL | `SpareDI_16_AL` | BOOL | SpareDI_16_AL | SpareDI-16 - Alarm |
| `%M00017` | BOOL | `SpareDI_17_AL` | BOOL | SpareDI_17_AL | SpareDI-17 - Alarm |
| `%M00018` | BOOL | `SpareDI_18_AL` | BOOL | SpareDI_18_AL | SpareDI-18 - Alarm |
| `%M00019` | BOOL | `SpareDI_19_AL` | BOOL | SpareDI_19_AL | SpareDI-19 - Alarm |
| `%M00020` | BOOL | `SpareDI_20_AL` | BOOL | SpareDI_20_AL | SpareDI-20 - Alarm |
| `%M00021` | BOOL | `SpareDI_21_AL` | BOOL | SpareDI_21_AL | SpareDI-21 - Alarm |
| `%M00022` | BOOL | `SpareDI_22_AL` | BOOL | SpareDI_22_AL | SpareDI-22 - Alarm |
| `%M00023` | BOOL | `SpareDI_23_AL` | BOOL | SpareDI_23_AL | SpareDI-23 - Alarm |
| `%M00024` | BOOL | `SpareDI_24_AL` | BOOL | SpareDI_24_AL | SpareDI-24 - Alarm |
| `%M00025` | BOOL | `SpareDI_25_AL` | BOOL | SpareDI_25_AL | SpareDI-25 - Alarm |
| `%M00026` | BOOL | `SpareDI_26_AL` | BOOL | SpareDI_26_AL | SpareDI-26 - Alarm |
| `%M00027` | BOOL | `SpareDI_27_AL` | BOOL | SpareDI_27_AL | SpareDI-27 - Alarm |
| `%M00028` | BOOL | `SpareDI_28_AL` | BOOL | SpareDI_28_AL | SpareDI-28 - Alarm |
| `%M00029` | BOOL | `SpareDI_29_AL` | BOOL | SpareDI_29_AL | SpareDI-29 - Alarm |
| `%M00030` | BOOL | `SpareDI_30_AL` | BOOL | SpareDI_30_AL | SpareDI-30 - Alarm |
| `%M00031` | BOOL | `SpareDI_31_AL` | BOOL | SpareDI_31_AL | SpareDI-31 - Alarm |
| `%M00032` | BOOL | `SpareDI_32_AL` | BOOL | SpareDI_32_AL | SpareDI-32 - Alarm |
| `%M00033` | BOOL | `ZSH_6401_001_ALI` | BOOL | ZSH_6401_001_ALI | 6401-ZSH-001 ESD valve open - Alarm inhibit |
| `%M00034` | BOOL | `ZSL_6401_001_ALI` | BOOL | ZSL_6401_001_ALI | 6401-ZSL-001 ESD valve closed - Alarm inhibit |
| `%M00035` | BOOL | `FS_7503_001_ALI` | BOOL | FS_7503_001_ALI | 7503-FS-001 Stop foam button - Alarm inhibit |
| `%M00036` | BOOL | `LS_7503_001_ALI` | BOOL | LS_7503_001_ALI | 7503-LS-001  AFFF tank low level - Alarm inhibit |
| `%M00037` | BOOL | `LS_7503_002_ALI` | BOOL | LS_7503_002_ALI | 7503-LS-002  Diesel tank low level - Alarm inhibit |
| `%M00038` | BOOL | `Pump_A_PulsIn_ALI` | BOOL | Pump_A_PulsIn_ALI | Pulsed input from Q05 for Pump A Out signal - Alarm inhibit |
| `%M00039` | BOOL | `Pump_B_Start_PulsIn_ALI` | BOOL | Pump_B_Start_PulsIn_ALI | Pulsed input from Q07 for Pump B Start signal - Alarm inhibit |
| `%M00040` | BOOL | `SpareDI_08_ALI` | BOOL | SpareDI_08_ALI | SpareDI-08 - Alarm inhibit |
| `%M00041` | BOOL | `Pump_B_Inhibited_ALI` | BOOL | Pump_B_Inhibited_ALI | Standby pump B inhibited - Alarm inhibit |
| `%M00042` | BOOL | `ESDV_6401_001_ALI` | BOOL | ESDV_6401_001_ALI | 6401-ESDV-001  ESD Fuel Gas Button - Alarm inhibit |
| `%M00043` | BOOL | `SpareDI_11_ALI` | BOOL | SpareDI_11_ALI | SpareDI-11 - Alarm inhibit |
| `%M00044` | BOOL | `INHIBIT_FOAM_REL_ALI` | BOOL | INHIBIT_FOAM_REL_ALI | Foam release inhibit - Alarm inhibit |
| `%M00045` | BOOL | `INHIBIT_ALL_OUTPUTS_ALI` | BOOL | INHIBIT_ALL_OUTPUTS_ALI | All outputs inhibit - Alarm inhibit |
| `%M00046` | BOOL | `SpareDI_14_ALI` | BOOL | SpareDI_14_ALI | SpareDI-14 - Alarm inhibit |
| `%M00047` | BOOL | `SpareDI_15_ALI` | BOOL | SpareDI_15_ALI | SpareDI-15 - Alarm inhibit |
| `%M00048` | BOOL | `SpareDI_16_ALI` | BOOL | SpareDI_16_ALI | SpareDI-16 - Alarm inhibit |
| `%M00049` | BOOL | `SpareDI_17_ALI` | BOOL | SpareDI_17_ALI | SpareDI-17 - Alarm inhibit |
| `%M00050` | BOOL | `SpareDI_18_ALI` | BOOL | SpareDI_18_ALI | SpareDI-18 - Alarm inhibit |
| `%M00051` | BOOL | `SpareDI_19_ALI` | BOOL | SpareDI_19_ALI | SpareDI-19 - Alarm inhibit |
| `%M00052` | BOOL | `SpareDI_20_ALI` | BOOL | SpareDI_20_ALI | SpareDI-20 - Alarm inhibit |
| `%M00053` | BOOL | `SpareDI_21_ALI` | BOOL | SpareDI_21_ALI | SpareDI-21 - Alarm inhibit |
| `%M00054` | BOOL | `SpareDI_22_ALI` | BOOL | SpareDI_22_ALI | SpareDI-22 - Alarm inhibit |
| `%M00055` | BOOL | `SpareDI_23_ALI` | BOOL | SpareDI_23_ALI | SpareDI-23 - Alarm inhibit |
| `%M00056` | BOOL | `SpareDI_24_ALI` | BOOL | SpareDI_24_ALI | SpareDI-24 - Alarm inhibit |
| `%M00057` | BOOL | `SpareDI_25_ALI` | BOOL | SpareDI_25_ALI | SpareDI-25 - Alarm inhibit |
| `%M00058` | BOOL | `SpareDI_26_ALI` | BOOL | SpareDI_26_ALI | SpareDI-26 - Alarm inhibit |
| `%M00059` | BOOL | `SpareDI_27_ALI` | BOOL | SpareDI_27_ALI | SpareDI-27 - Alarm inhibit |
| `%M00060` | BOOL | `SpareDI_28_ALI` | BOOL | SpareDI_28_ALI | SpareDI-28 - Alarm inhibit |
| `%M00061` | BOOL | `SpareDI_29_ALI` | BOOL | SpareDI_29_ALI | SpareDI-29 - Alarm inhibit |
| `%M00062` | BOOL | `SpareDI_30_ALI` | BOOL | SpareDI_30_ALI | SpareDI-30 - Alarm inhibit |
| `%M00063` | BOOL | `SpareDI_31_ALI` | BOOL | SpareDI_31_ALI | SpareDI-31 - Alarm inhibit |
| `%M00064` | BOOL | `SpareDI_32_ALI` | BOOL | SpareDI_32_ALI | SpareDI-32 - Alarm inhibit |
| `%M00065` | BOOL | `ZSH_6401_001_FRUP` | BOOL | ZSH_6401_001_FRUP | 6401-ZSH-001 ESD valve open - First up |
| `%M00066` | BOOL | `ZSL_6401_001_FRUP` | BOOL | ZSL_6401_001_FRUP | 6401-ZSL-001 ESD valve closed - First up |
| `%M00067` | BOOL | `FS_7503_001_FRUP` | BOOL | FS_7503_001_FRUP | 7503-FS-001 Stop foam button - First up |
| `%M00068` | BOOL | `LS_7503_001_FRUP` | BOOL | LS_7503_001_FRUP | 7503-LS-001  AFFF tank low level - First up |
| `%M00069` | BOOL | `LS_7503_002_FRUP` | BOOL | LS_7503_002_FRUP | 7503-LS-002  Diesel tank low level - First up |
| `%M00070` | BOOL | `Pump_A_PulsIn_FRUP` | BOOL | Pump_A_PulsIn_FRUP | Pulsed input from Q05 for Pump A Out signal - First up |
| `%M00071` | BOOL | `Pump_B_Start_PulsIn_FRUP` | BOOL | Pump_B_Start_PulsIn_FRUP | Pulsed input from Q07 for Pump B Start signal - First up |
| `%M00072` | BOOL | `SpareDI_08_FRUP` | BOOL | SpareDI_08_FRUP | SpareDI-08 - First up |
| `%M00073` | BOOL | `Pump_B_Inhibited_FRUP` | BOOL | Pump_B_Inhibited_FRUP | Standby pump B inhibited - First up |
| `%M00074` | BOOL | `ESDV_6401_001_FRUP` | BOOL | ESDV_6401_001_FRUP | 6401-ESDV-001  ESD Fuel Gas Button - First up |
| `%M00075` | BOOL | `SpareDI_11_FRUP` | BOOL | SpareDI_11_FRUP | SpareDI-11 - First up |
| `%M00076` | BOOL | `INHIBIT_FOAM_REL_FRUP` | BOOL | INHIBIT_FOAM_REL_FRUP | Foam release inhibit - First up |
| `%M00077` | BOOL | `INHIBIT_ALL_OUTPUTS_FRUP` | BOOL | INHIBIT_ALL_OUTPUTS_FRUP | All outputs inhibit - First up |
| `%M00078` | BOOL | `SpareDI_14_FRUP` | BOOL | SpareDI_14_FRUP | SpareDI-14 - First up |
| `%M00079` | BOOL | `SpareDI_15_FRUP` | BOOL | SpareDI_15_FRUP | SpareDI-15 - First up |
| `%M00080` | BOOL | `SpareDI_16_FRUP` | BOOL | SpareDI_16_FRUP | SpareDI-16 - First up |
| `%M00081` | BOOL | `SpareDI_17_FRUP` | BOOL | SpareDI_17_FRUP | SpareDI-17 - First up |
| `%M00082` | BOOL | `SpareDI_18_FRUP` | BOOL | SpareDI_18_FRUP | SpareDI-18 - First up |
| `%M00083` | BOOL | `SpareDI_19_FRUP` | BOOL | SpareDI_19_FRUP | SpareDI-19 - First up |
| `%M00084` | BOOL | `SpareDI_20_FRUP` | BOOL | SpareDI_20_FRUP | SpareDI-20 - First up |
| `%M00085` | BOOL | `SpareDI_21_FRUP` | BOOL | SpareDI_21_FRUP | SpareDI-21 - First up |
| `%M00086` | BOOL | `SpareDI_22_FRUP` | BOOL | SpareDI_22_FRUP | SpareDI-22 - First up |
| `%M00087` | BOOL | `SpareDI_23_FRUP` | BOOL | SpareDI_23_FRUP | SpareDI-23 - First up |
| `%M00088` | BOOL | `SpareDI_24_FRUP` | BOOL | SpareDI_24_FRUP | SpareDI-24 - First up |
| `%M00089` | BOOL | `SpareDI_25_FRUP` | BOOL | SpareDI_25_FRUP | SpareDI-25 - First up |
| `%M00090` | BOOL | `SpareDI_26_FRUP` | BOOL | SpareDI_26_FRUP | SpareDI-26 - First up |
| `%M00091` | BOOL | `SpareDI_27_FRUP` | BOOL | SpareDI_27_FRUP | SpareDI-27 - First up |
| `%M00092` | BOOL | `SpareDI_28_FRUP` | BOOL | SpareDI_28_FRUP | SpareDI-28 - First up |
| `%M00093` | BOOL | `SpareDI_29_FRUP` | BOOL | SpareDI_29_FRUP | SpareDI-29 - First up |
| `%M00094` | BOOL | `SpareDI_30_FRUP` | BOOL | SpareDI_30_FRUP | SpareDI-30 - First up |
| `%M00095` | BOOL | `SpareDI_31_FRUP` | BOOL | SpareDI_31_FRUP | SpareDI-31 - First up |
| `%M00096` | BOOL | `SpareDI_32_FRUP` | BOOL | SpareDI_32_FRUP | SpareDI-32 - First up |
| `%M00097` | BOOL | `ZSH_6401_001_INH` | BOOL | ZSH_6401_001_INH | 6401-ZSH-001 ESD valve open - Inhibit |
| `%M00098` | BOOL | `ZSL_6401_001_INH` | BOOL | ZSL_6401_001_INH | 6401-ZSL-001 ESD valve closed - Inhibit |
| `%M00099` | BOOL | `FS_7503_001_INH` | BOOL | FS_7503_001_INH | 7503-FS-001 Stop foam button - Inhibit |
| `%M00100` | BOOL | `LS_7503_001_INH` | BOOL | LS_7503_001_INH | 7503-LS-001  AFFF tank low level - Inhibit |
| `%M00101` | BOOL | `LS_7503_002_INH` | BOOL | LS_7503_002_INH | 7503-LS-002  Diesel tank low level - Inhibit |
| `%M00102` | BOOL | `Pump_A_PulsIn_INH` | BOOL | Pump_A_PulsIn_INH | Pulsed input from Q05 for Pump A Out signal - Inhibit |
| `%M00103` | BOOL | `Pump_B_Start_PulsIn_INH` | BOOL | Pump_B_Start_PulsIn_INH | Pulsed input from Q07 for Pump B Start signal - Inhibit |
| `%M00104` | BOOL | `SpareDI_08_INH` | BOOL | SpareDI_08_INH | SpareDI-08 - Inhibit |
| `%M00105` | BOOL | `Pump_B_Inhibited_INH` | BOOL | Pump_B_Inhibited_INH | Standby pump B inhibited - Inhibit |
| `%M00106` | BOOL | `ESDV_6401_001_INH` | BOOL | ESDV_6401_001_INH | 6401-ESDV-001  ESD Fuel Gas Button - Inhibit |
| `%M00107` | BOOL | `SpareDI_11_INH` | BOOL | SpareDI_11_INH | SpareDI-11 - Inhibit |
| `%M00108` | BOOL | `INHIBIT_FOAM_REL_INH` | BOOL | INHIBIT_FOAM_REL_INH | Foam release inhibit - Inhibit |
| `%M00109` | BOOL | `INHIBIT_ALL_OUTPUTS_INH` | BOOL | INHIBIT_ALL_OUTPUTS_INH | All outputs inhibit - Inhibit |
| `%M00110` | BOOL | `SpareDI_14_INH` | BOOL | SpareDI_14_INH | SpareDI-14 - Inhibit |
| `%M00111` | BOOL | `SpareDI_15_INH` | BOOL | SpareDI_15_INH | SpareDI-15 - Inhibit |
| `%M00112` | BOOL | `SpareDI_16_INH` | BOOL | SpareDI_16_INH | SpareDI-16 - Inhibit |
| `%M00113` | BOOL | `SpareDI_17_INH` | BOOL | SpareDI_17_INH | SpareDI-17 - Inhibit |
| `%M00114` | BOOL | `SpareDI_18_INH` | BOOL | SpareDI_18_INH | SpareDI-18 - Inhibit |
| `%M00115` | BOOL | `SpareDI_19_INH` | BOOL | SpareDI_19_INH | SpareDI-19 - Inhibit |
| `%M00116` | BOOL | `SpareDI_20_INH` | BOOL | SpareDI_20_INH | SpareDI-20 - Inhibit |
| `%M00117` | BOOL | `SpareDI_21_INH` | BOOL | SpareDI_21_INH | SpareDI-21 - Inhibit |
| `%M00118` | BOOL | `SpareDI_22_INH` | BOOL | SpareDI_22_INH | SpareDI-22 - Inhibit |
| `%M00119` | BOOL | `SpareDI_23_INH` | BOOL | SpareDI_23_INH | SpareDI-23 - Inhibit |
| `%M00120` | BOOL | `SpareDI_24_INH` | BOOL | SpareDI_24_INH | SpareDI-24 - Inhibit |
| `%M00121` | BOOL | `SpareDI_25_INH` | BOOL | SpareDI_25_INH | SpareDI-25 - Inhibit |
| `%M00122` | BOOL | `SpareDI_26_INH` | BOOL | SpareDI_26_INH | SpareDI-26 - Inhibit |
| `%M00123` | BOOL | `SpareDI_27_INH` | BOOL | SpareDI_27_INH | SpareDI-27 - Inhibit |
| `%M00124` | BOOL | `SpareDI_28_INH` | BOOL | SpareDI_28_INH | SpareDI-28 - Inhibit |
| `%M00125` | BOOL | `SpareDI_29_INH` | BOOL | SpareDI_29_INH | SpareDI-29 - Inhibit |
| `%M00126` | BOOL | `SpareDI_30_INH` | BOOL | SpareDI_30_INH | SpareDI-30 - Inhibit |
| `%M00127` | BOOL | `SpareDI_31_INH` | BOOL | SpareDI_31_INH | SpareDI-31 - Inhibit |
| `%M00128` | BOOL | `SpareDI_32_INH` | BOOL | SpareDI_32_INH | SpareDI-32 - Inhibit |
| `%M00129` | BOOL | `ZSH_6401_001_OC` | BOOL | ZSH_6401_001_OC | 6401-ZSH-001 ESD valve open - Open circuit |
| `%M00130` | BOOL | `ZSL_6401_001_OC` | BOOL | ZSL_6401_001_OC | 6401-ZSL-001 ESD valve closed - Open circuit |
| `%M00131` | BOOL | `FS_7503_001_OC` | BOOL | FS_7503_001_OC | 7503-FS-001 Stop foam button - Open circuit |
| `%M00132` | BOOL | `LS_7503_001_OC` | BOOL | LS_7503_001_OC | 7503-LS-001  AFFF tank low level - Open circuit |
| `%M00133` | BOOL | `LS_7503_002_OC` | BOOL | LS_7503_002_OC | 7503-LS-002  Diesel tank low level - Open circuit |
| `%M00134` | BOOL | `Pump_A_PulsIn_OC` | BOOL | Pump_A_PulsIn_OC | Pulsed input from Q05 for Pump A Out signal - Open circuit |
| `%M00135` | BOOL | `Pump_B_Start_PulsIn_OC` | BOOL | Pump_B_Start_PulsIn_OC | Pulsed input from Q07 for Pump B Start signal - Open circuit |
| `%M00136` | BOOL | `SpareDI_08_OC` | BOOL | SpareDI_08_OC | SpareDI-08 - Open circuit |
| `%M00137` | BOOL | `Pump_B_Inhibited_OC` | BOOL | Pump_B_Inhibited_OC | Standby pump B inhibited - Open circuit |
| `%M00138` | BOOL | `ESDV_6401_001_OC` | BOOL | ESDV_6401_001_OC | 6401-ESDV-001  ESD Fuel Gas Button - Open circuit |
| `%M00139` | BOOL | `SpareDI_11_OC` | BOOL | SpareDI_11_OC | SpareDI-11 - Open circuit |
| `%M00140` | BOOL | `INHIBIT_FOAM_REL_OC` | BOOL | INHIBIT_FOAM_REL_OC | Foam release inhibit - Open circuit |
| `%M00141` | BOOL | `INHIBIT_ALL_OUTPUTS_OC` | BOOL | INHIBIT_ALL_OUTPUTS_OC | All outputs inhibit - Open circuit |
| `%M00142` | BOOL | `SpareDI_14_OC` | BOOL | SpareDI_14_OC | SpareDI-14 - Open circuit |
| `%M00143` | BOOL | `SpareDI_15_OC` | BOOL | SpareDI_15_OC | SpareDI-15 - Open circuit |
| `%M00144` | BOOL | `SpareDI_16_OC` | BOOL | SpareDI_16_OC | SpareDI-16 - Open circuit |
| `%M00145` | BOOL | `SpareDI_17_OC` | BOOL | SpareDI_17_OC | SpareDI-17 - Open circuit |
| `%M00146` | BOOL | `SpareDI_18_OC` | BOOL | SpareDI_18_OC | SpareDI-18 - Open circuit |
| `%M00147` | BOOL | `SpareDI_19_OC` | BOOL | SpareDI_19_OC | SpareDI-19 - Open circuit |
| `%M00148` | BOOL | `SpareDI_20_OC` | BOOL | SpareDI_20_OC | SpareDI-20 - Open circuit |
| `%M00149` | BOOL | `SpareDI_21_OC` | BOOL | SpareDI_21_OC | SpareDI-21 - Open circuit |
| `%M00150` | BOOL | `SpareDI_22_OC` | BOOL | SpareDI_22_OC | SpareDI-22 - Open circuit |
| `%M00151` | BOOL | `SpareDI_23_OC` | BOOL | SpareDI_23_OC | SpareDI-23 - Open circuit |
| `%M00152` | BOOL | `SpareDI_24_OC` | BOOL | SpareDI_24_OC | SpareDI-24 - Open circuit |
| `%M00153` | BOOL | `SpareDI_25_OC` | BOOL | SpareDI_25_OC | SpareDI-25 - Open circuit |
| `%M00154` | BOOL | `SpareDI_26_OC` | BOOL | SpareDI_26_OC | SpareDI-26 - Open circuit |
| `%M00155` | BOOL | `SpareDI_27_OC` | BOOL | SpareDI_27_OC | SpareDI-27 - Open circuit |
| `%M00156` | BOOL | `SpareDI_28_OC` | BOOL | SpareDI_28_OC | SpareDI-28 - Open circuit |
| `%M00157` | BOOL | `SpareDI_29_OC` | BOOL | SpareDI_29_OC | SpareDI-29 - Open circuit |
| `%M00158` | BOOL | `SpareDI_30_OC` | BOOL | SpareDI_30_OC | SpareDI-30 - Open circuit |
| `%M00159` | BOOL | `SpareDI_31_OC` | BOOL | SpareDI_31_OC | SpareDI-31 - Open circuit |
| `%M00160` | BOOL | `SpareDI_32_OC` | BOOL | SpareDI_32_OC | SpareDI-32 - Open circuit |
| `%M00161` | BOOL | `EY_6401_001_002_MT` | BOOL | EY_6401_001_002_MT | 6401-EY-001/002  ESD fuel gas valve shutdown - Manual trip |
| `%M00162` | BOOL | `SA_7404_001_002_MT` | BOOL | SA_7404_001_002_MT | 7404-SA-001/002  Local alarm pump house - Manual trip |
| `%M00163` | BOOL | `P2100_P2200_MT` | BOOL | P2100_P2200_MT | P2100/P2200  Oil booster pump shutdown - Manual trip |
| `%M00164` | BOOL | `P3600_P3700_MT` | BOOL | P3600_P3700_MT | P3600/P3700  Water booster pump shutdown - Manual trip |
| `%M00165` | BOOL | `PUMP_A_MT` | BOOL | PUMP_A_MT | Deluge pump A Start/Stop - Manual trip |
| `%M00166` | BOOL | `PUMP_B_STOP_MT` | BOOL | PUMP_B_STOP_MT | Deluge pump B Stop - Manual trip |
| `%M00167` | BOOL | `PUMP_B_START_MT` | BOOL | PUMP_B_START_MT | Deluge pump B Start - Manual trip |
| `%M00168` | BOOL | `PumpShutdown_MT` | BOOL | PumpShutdown_MT | Fire & Gas pump shutdown - Manual trip |
| `%M00169` | BOOL | `Pump_A_PulsOut_MT` | BOOL | Pump_A_PulsOut_MT | Pulsed output for open circuit check on Pump A Out signal - Manual trip |
| `%M00170` | BOOL | `Pump_B_Start_PulsOut_MT` | BOOL | Pump_B_Start_PulsOut_MT | Pulsed output for open circuit check on Pump B Start signal - Manual trip |
| `%M00171` | BOOL | `SpareDO_11_MT` | BOOL | SpareDO_11_MT | SpareDO-11 - Manual trip |
| `%M00172` | BOOL | `Tag_DO_12_MT` | BOOL | Tag_DO_12_MT | EDS valve open indication - Manual trip |
| `%M00173` | BOOL | `Tag_DO_13_MT` | BOOL | Tag_DO_13_MT | EDS valve closed indication - Manual trip |
| `%M00174` | BOOL | `Tag_DO_14_MT` | BOOL | Tag_DO_14_MT | EDS valve low air indication - Manual trip |
| `%M00175` | BOOL | `Tag_DO_15_MT` | BOOL | Tag_DO_15_MT | Panel alarm - Manual trip |
| `%M00176` | BOOL | `PLC_Fault_MT` | BOOL | PLC_Fault_MT | Set when PLC fault exists - Manual trip |
| `%M00177` | BOOL | `SpareDO_17_MT` | BOOL | SpareDO_17_MT | SpareDO-17 - Manual trip |
| `%M00178` | BOOL | `SpareDO_18_MT` | BOOL | SpareDO_18_MT | SpareDO-18 - Manual trip |
| `%M00179` | BOOL | `SpareDO_19_MT` | BOOL | SpareDO_19_MT | SpareDO-19 - Manual trip |
| `%M00180` | BOOL | `SpareDO_20_MT` | BOOL | SpareDO_20_MT | SpareDO-20 - Manual trip |
| `%M00181` | BOOL | `SpareDO_21_MT` | BOOL | SpareDO_21_MT | SpareDO-21 - Manual trip |
| `%M00182` | BOOL | `SpareDO_22_MT` | BOOL | SpareDO_22_MT | SpareDO-22 - Manual trip |
| `%M00183` | BOOL | `SpareDO_23_MT` | BOOL | SpareDO_23_MT | SpareDO-23 - Manual trip |
| `%M00184` | BOOL | `SpareDO_24_MT` | BOOL | SpareDO_24_MT | SpareDO-24 - Manual trip |
| `%M00185` | BOOL | `SpareDO_25_MT` | BOOL | SpareDO_25_MT | SpareDO-25 - Manual trip |
| `%M00186` | BOOL | `SpareDO_26_MT` | BOOL | SpareDO_26_MT | SpareDO-26 - Manual trip |
| `%M00187` | BOOL | `SpareDO_27_MT` | BOOL | SpareDO_27_MT | SpareDO-27 - Manual trip |
| `%M00188` | BOOL | `SpareDO_28_MT` | BOOL | SpareDO_28_MT | SpareDO-28 - Manual trip |
| `%M00189` | BOOL | `SpareDO_29_MT` | BOOL | SpareDO_29_MT | SpareDO-29 - Manual trip |
| `%M00190` | BOOL | `SpareDO_30_MT` | BOOL | SpareDO_30_MT | SpareDO-30 - Manual trip |
| `%M00191` | BOOL | `SpareDO_31_MT` | BOOL | SpareDO_31_MT | SpareDO-31 - Manual trip |
| `%M00192` | BOOL | `SpareDO_32_MT` | BOOL | SpareDO_32_MT | SpareDO-32 - Manual trip |
| `%M00225` | BOOL | `EY_6401_001_002_INT` | BOOL | EY_6401_001_002_INT | 6401-EY-001/002  ESD fuel gas valve shutdown - Internal C_E use |
| `%M00226` | BOOL | `SA_7404_001_002_INT` | BOOL | SA_7404_001_002_INT | 7404-SA-001/002  Local alarm pump house - Internal C_E use |
| `%M00227` | BOOL | `P2100_P2200_INT` | BOOL | P2100_P2200_INT | P2100/P2200  Oil booster pump shutdown - Internal C_E use |
| `%M00228` | BOOL | `P3600_P3700_INT` | BOOL | P3600_P3700_INT | P3600/P3700  Water booster pump shutdown - Internal C_E use |
| `%M00229` | BOOL | `PUMP_A_INT` | BOOL | PUMP_A_INT | Deluge pump A Start/Stop - Internal C_E use |
| `%M00230` | BOOL | `PUMP_B_STOP_INT` | BOOL | PUMP_B_STOP_INT | Deluge pump B Stop - Internal C_E use |
| `%M00231` | BOOL | `PUMP_B_START_INT` | BOOL | PUMP_B_START_INT | Deluge pump B Start - Internal C_E use |
| `%M00232` | BOOL | `PumpShutdown_INT` | BOOL | PumpShutdown_INT | Fire & Gas pump shutdown - Internal C_E use |
| `%M00233` | BOOL | `Pump_A_PulsOut_INT` | BOOL | Pump_A_PulsOut_INT | Pulsed output for open circuit check on Pump A Out signal - Internal C_E use |
| `%M00234` | BOOL | `Pump_B_Start_PulsOut_INT` | BOOL | Pump_B_Start_PulsOut_INT | Pulsed output for open circuit check on Pump B Start signal - Internal C_E use |
| `%M00235` | BOOL | `SpareDO_11_INT` | BOOL | SpareDO_11_INT | SpareDO-11 - Internal C_E use |
| `%M00236` | BOOL | `Tag_DO_12_INT` | BOOL | Tag_DO_12_INT | EDS valve open indication - Internal C_E use |
| `%M00237` | BOOL | `Tag_DO_13_INT` | BOOL | Tag_DO_13_INT | EDS valve closed indication - Internal C_E use |
| `%M00238` | BOOL | `Tag_DO_14_INT` | BOOL | Tag_DO_14_INT | EDS valve low air indication - Internal C_E use |
| `%M00239` | BOOL | `Tag_DO_15_INT` | BOOL | Tag_DO_15_INT | Panel alarm - Internal C_E use |
| `%M00240` | BOOL | `PLC_Fault_INT` | BOOL | PLC_Fault_INT | Set when PLC fault exists - Internal C_E use |
| `%M00241` | BOOL | `SpareDO_17_INT` | BOOL | SpareDO_17_INT | SpareDO-17 - Internal C_E use |
| `%M00242` | BOOL | `SpareDO_18_INT` | BOOL | SpareDO_18_INT | SpareDO-18 - Internal C_E use |
| `%M00243` | BOOL | `SpareDO_19_INT` | BOOL | SpareDO_19_INT | SpareDO-19 - Internal C_E use |
| `%M00244` | BOOL | `SpareDO_20_INT` | BOOL | SpareDO_20_INT | SpareDO-20 - Internal C_E use |
| `%M00245` | BOOL | `SpareDO_21_INT` | BOOL | SpareDO_21_INT | SpareDO-21 - Internal C_E use |
| `%M00246` | BOOL | `SpareDO_22_INT` | BOOL | SpareDO_22_INT | SpareDO-22 - Internal C_E use |
| `%M00247` | BOOL | `SpareDO_23_INT` | BOOL | SpareDO_23_INT | SpareDO-23 - Internal C_E use |
| `%M00248` | BOOL | `SpareDO_24_INT` | BOOL | SpareDO_24_INT | SpareDO-24 - Internal C_E use |
| `%M00249` | BOOL | `SpareDO_25_INT` | BOOL | SpareDO_25_INT | SpareDO-25 - Internal C_E use |
| `%M00250` | BOOL | `SpareDO_26_INT` | BOOL | SpareDO_26_INT | SpareDO-26 - Internal C_E use |
| `%M00251` | BOOL | `SpareDO_27_INT` | BOOL | SpareDO_27_INT | SpareDO-27 - Internal C_E use |
| `%M00252` | BOOL | `SpareDO_28_INT` | BOOL | SpareDO_28_INT | SpareDO-28 - Internal C_E use |
| `%M00253` | BOOL | `SpareDO_29_INT` | BOOL | SpareDO_29_INT | SpareDO-29 - Internal C_E use |
| `%M00254` | BOOL | `SpareDO_30_INT` | BOOL | SpareDO_30_INT | SpareDO-30 - Internal C_E use |
| `%M00255` | BOOL | `SpareDO_31_INT` | BOOL | SpareDO_31_INT | SpareDO-31 - Internal C_E use |
| `%M00256` | BOOL | `SpareDO_32_INT` | BOOL | SpareDO_32_INT | SpareDO-32 - Internal C_E use |
| `%M00289` | BOOL | `EY_6401_001_002_OC` | BOOL | EY_6401_001_002_OC | 6401-EY-001/002  ESD fuel gas valve shutdown - Open circuit |
| `%M00290` | BOOL | `SA_7404_001_002_OC` | BOOL | SA_7404_001_002_OC | 7404-SA-001/002  Local alarm pump house - Open circuit |
| `%M00291` | BOOL | `P2100_P2200_OC` | BOOL | P2100_P2200_OC | P2100/P2200  Oil booster pump shutdown - Open circuit |
| `%M00292` | BOOL | `P3600_P3700_OC` | BOOL | P3600_P3700_OC | P3600/P3700  Water booster pump shutdown - Open circuit |
| `%M00293` | BOOL | `PUMP_A_OC` | BOOL | PUMP_A_OC | Deluge pump A Start/Stop - Open circuit |
| `%M00294` | BOOL | `PUMP_B_STOP_OC` | BOOL | PUMP_B_STOP_OC | Deluge pump B Stop - Open circuit |
| `%M00295` | BOOL | `PUMP_B_START_OC` | BOOL | PUMP_B_START_OC | Deluge pump B Start - Open circuit |
| `%M00296` | BOOL | `PumpShutdown_OC` | BOOL | PumpShutdown_OC | Fire & Gas pump shutdown - Open circuit |
| `%M00297` | BOOL | `Pump_A_PulsOut_OC` | BOOL | Pump_A_PulsOut_OC | Pulsed output for open circuit check on Pump A Out signal - Open circuit |
| `%M00298` | BOOL | `Pump_B_Start_PulsOut_OC` | BOOL | Pump_B_Start_PulsOut_OC | Pulsed output for open circuit check on Pump B Start signal - Open circuit |
| `%M00299` | BOOL | `SpareDO_11_OC` | BOOL | SpareDO_11_OC | SpareDO-11 - Open circuit |
| `%M00300` | BOOL | `Tag_DO_12_OC` | BOOL | Tag_DO_12_OC | EDS valve open indication - Open circuit |
| `%M00301` | BOOL | `Tag_DO_13_OC` | BOOL | Tag_DO_13_OC | EDS valve closed indication - Open circuit |
| `%M00302` | BOOL | `Tag_DO_14_OC` | BOOL | Tag_DO_14_OC | EDS valve low air indication - Open circuit |
| `%M00303` | BOOL | `Tag_DO_15_OC` | BOOL | Tag_DO_15_OC | Panel alarm - Open circuit |
| `%M00304` | BOOL | `PLC_Fault_OC` | BOOL | PLC_Fault_OC | Set when PLC fault exists - Open circuit |
| `%M00305` | BOOL | `SpareDO_17_OC` | BOOL | SpareDO_17_OC | SpareDO-17 - Open circuit |
| `%M00306` | BOOL | `SpareDO_18_OC` | BOOL | SpareDO_18_OC | SpareDO-18 - Open circuit |
| `%M00307` | BOOL | `SpareDO_19_OC` | BOOL | SpareDO_19_OC | SpareDO-19 - Open circuit |
| `%M00308` | BOOL | `SpareDO_20_OC` | BOOL | SpareDO_20_OC | SpareDO-20 - Open circuit |
| `%M00309` | BOOL | `SpareDO_21_OC` | BOOL | SpareDO_21_OC | SpareDO-21 - Open circuit |
| `%M00310` | BOOL | `SpareDO_22_OC` | BOOL | SpareDO_22_OC | SpareDO-22 - Open circuit |
| `%M00311` | BOOL | `SpareDO_23_OC` | BOOL | SpareDO_23_OC | SpareDO-23 - Open circuit |
| `%M00312` | BOOL | `SpareDO_24_OC` | BOOL | SpareDO_24_OC | SpareDO-24 - Open circuit |
| `%M00313` | BOOL | `SpareDO_25_OC` | BOOL | SpareDO_25_OC | SpareDO-25 - Open circuit |
| `%M00314` | BOOL | `SpareDO_26_OC` | BOOL | SpareDO_26_OC | SpareDO-26 - Open circuit |
| `%M00315` | BOOL | `SpareDO_27_OC` | BOOL | SpareDO_27_OC | SpareDO-27 - Open circuit |
| `%M00316` | BOOL | `SpareDO_28_OC` | BOOL | SpareDO_28_OC | SpareDO-28 - Open circuit |
| `%M00317` | BOOL | `SpareDO_29_OC` | BOOL | SpareDO_29_OC | SpareDO-29 - Open circuit |
| `%M00318` | BOOL | `SpareDO_30_OC` | BOOL | SpareDO_30_OC | SpareDO-30 - Open circuit |
| `%M00319` | BOOL | `SpareDO_31_OC` | BOOL | SpareDO_31_OC | SpareDO-31 - Open circuit |
| `%M00320` | BOOL | `SpareDO_32_OC` | BOOL | SpareDO_32_OC | SpareDO-32 - Open circuit |
| `%M00353` | BOOL | `DG_7404_001_ALH` | BOOL | DG_7404_001_ALH | 7404-DG-001  Gas detector pump house - Hi Alarm |
| `%M00354` | BOOL | `DG_7404_002_ALH` | BOOL | DG_7404_002_ALH | 7404-DG-002  Gas detector pump house - Hi Alarm |
| `%M00355` | BOOL | `DG_7404_003_ALH` | BOOL | DG_7404_003_ALH | 7404-DG-003  Gas detector pump house - Hi Alarm |
| `%M00356` | BOOL | `DG_7404_004_ALH` | BOOL | DG_7404_004_ALH | 7404-DG-004  Gas detector pump house - Hi Alarm |
| `%M00357` | BOOL | `DG_7404_005_ALH` | BOOL | DG_7404_005_ALH | 7404-DG-005  Gas detector pump house - Hi Alarm |
| `%M00358` | BOOL | `DG_7404_006_ALH` | BOOL | DG_7404_006_ALH | 7404-DG-006  Gas detector pump house - Hi Alarm |
| `%M00359` | BOOL | `DG_7404_007_ALH` | BOOL | DG_7404_007_ALH | 7404-DG-007  Gas detector pump house - Hi Alarm |
| `%M00360` | BOOL | `DG_7404_008_ALH` | BOOL | DG_7404_008_ALH | 7404-DG-008  Gas detector pump house - Hi Alarm |
| `%M00361` | BOOL | `DG_7404_009_ALH` | BOOL | DG_7404_009_ALH | 7404-DG-009  Gas detector pump house - Hi Alarm |
| `%M00362` | BOOL | `DG_7404_010_ALH` | BOOL | DG_7404_010_ALH | 7404-DG-010  Gas detector pump house - Hi Alarm |
| `%M00363` | BOOL | `SpareAI_11_ALH` | BOOL | SpareAI_11_ALH | SpareAI-11 - Hi Alarm |
| `%M00364` | BOOL | `DF_7404_001_ALH` | BOOL | DF_7404_001_ALH | 7404-DF-001  Flame detector pump house - Fire Alarm |
| `%M00365` | BOOL | `DF_7404_002_ALH` | BOOL | DF_7404_002_ALH | 7404-DF-002  Flame detector pump house - Hi Alarm |
| `%M00366` | BOOL | `DG_7404_011R_ALH` | BOOL | DG_7404_011R_ALH | 7404-DG-011R  Open path detector - Hi Alarm |
| `%M00367` | BOOL | `SpareAI_15_ALH` | BOOL | SpareAI_15_ALH | SpareAI-15 - Hi Alarm |
| `%M00368` | BOOL | `SpareAI_16_ALH` | BOOL | SpareAI_16_ALH | SpareAI-16 - Hi Alarm |
| `%M00369` | BOOL | `PST_7002_001_ALH` | BOOL | PST_7002_001_ALH | 7002-PST-001  Air acc. pressure - Hi Alarm |
| `%M00370` | BOOL | `PST_6401_001_ALH` | BOOL | PST_6401_001_ALH | 6401-PST-001  Fuel gas pressure - Hi Alarm |
| `%M00371` | BOOL | `PST_7503_001_ALH` | BOOL | PST_7503_001_ALH | 7503-PST-001  Deluge line pressure - Hi Alarm |
| `%M00372` | BOOL | `FR_7503_001_002_ALH` | BOOL | FR_7503_001_002_ALH | 7503-FR-001/002  Foam release from field - Hi alarm |
| `%M00373` | BOOL | `SpareAI_21_ALH` | BOOL | SpareAI_21_ALH | SpareAI-21 - Hi Alarm |
| `%M00374` | BOOL | `FR_7503_003_ALH` | BOOL | FR_7503_003_ALH | 7503-FR-003  Foam release from panel - Hi Alarm |
| `%M00375` | BOOL | `SpareAI_23_ALH` | BOOL | SpareAI_23_ALH | SpareAI-23 - Hi Alarm |
| `%M00376` | BOOL | `SpareAI_24_ALH` | BOOL | SpareAI_24_ALH | SpareAI-24 - Hi Alarm |
| `%M00377` | BOOL | `DG_7404_001_ALHI` | BOOL | DG_7404_001_ALHI | 7404-DG-001  Gas detector pump house - Hi Alarm C_E |
| `%M00378` | BOOL | `DG_7404_002_ALHI` | BOOL | DG_7404_002_ALHI | 7404-DG-002  Gas detector pump house - Hi Alarm C_E |
| `%M00379` | BOOL | `DG_7404_003_ALHI` | BOOL | DG_7404_003_ALHI | 7404-DG-003  Gas detector pump house - Hi Alarm C_E |
| `%M00380` | BOOL | `DG_7404_004_ALHI` | BOOL | DG_7404_004_ALHI | 7404-DG-004  Gas detector pump house - Hi Alarm C_E |
| `%M00381` | BOOL | `DG_7404_005_ALHI` | BOOL | DG_7404_005_ALHI | 7404-DG-005  Gas detector pump house - Hi Alarm C_E |
| `%M00382` | BOOL | `DG_7404_006_ALHI` | BOOL | DG_7404_006_ALHI | 7404-DG-006  Gas detector pump house - Hi Alarm C_E |
| `%M00383` | BOOL | `DG_7404_007_ALHI` | BOOL | DG_7404_007_ALHI | 7404-DG-007  Gas detector pump house - Hi Alarm C_E |
| `%M00384` | BOOL | `DG_7404_008_ALHI` | BOOL | DG_7404_008_ALHI | 7404-DG-008  Gas detector pump house - Hi Alarm C_E |
| `%M00385` | BOOL | `DG_7404_009_ALHI` | BOOL | DG_7404_009_ALHI | 7404-DG-009  Gas detector pump house - Hi Alarm C_E |
| `%M00386` | BOOL | `DG_7404_010_ALHI` | BOOL | DG_7404_010_ALHI | 7404-DG-010  Gas detector pump house - Hi Alarm C_E |
| `%M00387` | BOOL | `SpareAI_11_ALHI` | BOOL | SpareAI_11_ALHI | SpareAI-11 - Hi Alarm C_E |
| `%M00388` | BOOL | `DF_7404_001_ALHI` | BOOL | DF_7404_001_ALHI | 7404-DF-001  Flame detector pump house - Hi Alarm C_E |
| `%M00389` | BOOL | `DF_7404_002_ALHI` | BOOL | DF_7404_002_ALHI | 7404-DF-002  Flame detector pump house - Hi Alarm C_E |
| `%M00390` | BOOL | `DG_7404_011R_ALHI` | BOOL | DG_7404_011R_ALHI | 7404-DG-011R  Open path detector - Hi Alarm C_E |
| `%M00391` | BOOL | `SpareAI_15_ALHI` | BOOL | SpareAI_15_ALHI | SpareAI-15 - Hi Alarm C_E |
| `%M00392` | BOOL | `SpareAI_16_ALHI` | BOOL | SpareAI_16_ALHI | SpareAI-16 - Hi Alarm C_E |
| `%M00393` | BOOL | `PST_7002_001_ALHI` | BOOL | PST_7002_001_ALHI | 7002-PST-001  Air acc. pressure - Hi Alarm C_E |
| `%M00394` | BOOL | `PST_6401_001_ALHI` | BOOL | PST_6401_001_ALHI | 6401-PST-001  Fuel gas pressure - Hi Alarm C_E |
| `%M00395` | BOOL | `PST_7503_001_ALHI` | BOOL | PST_7503_001_ALHI | 7503-PST-001  Deluge line pressure - Hi Alarm C_E |
| `%M00396` | BOOL | `FR_7503_001_002_ALHI` | BOOL | FR_7503_001_002_ALHI | 7503-FR-001/002  Foam release from field - Hi alarm C_E |
| `%M00397` | BOOL | `SpareAI_21_ALHI` | BOOL | SpareAI_21_ALHI | SpareAI-21 - Hi Alarm C_E |
| `%M00398` | BOOL | `FR_7503_003_ALHI` | BOOL | FR_7503_003_ALHI | 7503-FR-003  Foam release from panel - Hi Alarm C_E |
| `%M00399` | BOOL | `SpareAI_23_ALHI` | BOOL | SpareAI_23_ALHI | SpareAI-23 - Hi Alarm C_E |
| `%M00400` | BOOL | `SpareAI_24_ALHI` | BOOL | SpareAI_24_ALHI | SpareAI-24 - Hi Alarm C_E |
| `%M00401` | BOOL | `DG_7404_001_ALL` | BOOL | DG_7404_001_ALL | 7404-DG-001  Gas detector pump house - Lo Alarm |
| `%M00402` | BOOL | `DG_7404_002_ALL` | BOOL | DG_7404_002_ALL | 7404-DG-002  Gas detector pump house - Lo Alarm |
| `%M00403` | BOOL | `DG_7404_003_ALL` | BOOL | DG_7404_003_ALL | 7404-DG-003  Gas detector pump house - Lo Alarm |
| `%M00404` | BOOL | `DG_7404_004_ALL` | BOOL | DG_7404_004_ALL | 7404-DG-004  Gas detector pump house - Lo Alarm |
| `%M00405` | BOOL | `DG_7404_005_ALL` | BOOL | DG_7404_005_ALL | 7404-DG-005  Gas detector pump house - Lo Alarm |
| `%M00406` | BOOL | `DG_7404_006_ALL` | BOOL | DG_7404_006_ALL | 7404-DG-006  Gas detector pump house - Lo Alarm |
| `%M00407` | BOOL | `DG_7404_007_ALL` | BOOL | DG_7404_007_ALL | 7404-DG-007  Gas detector pump house - Lo Alarm |
| `%M00408` | BOOL | `DG_7404_008_ALL` | BOOL | DG_7404_008_ALL | 7404-DG-008  Gas detector pump house - Lo Alarm |
| `%M00409` | BOOL | `DG_7404_009_ALL` | BOOL | DG_7404_009_ALL | 7404-DG-009  Gas detector pump house - Lo Alarm |
| `%M00410` | BOOL | `DG_7404_010_ALL` | BOOL | DG_7404_010_ALL | 7404-DG-010  Gas detector pump house - Lo Alarm |
| `%M00411` | BOOL | `SpareAI_11_ALL` | BOOL | SpareAI_11_ALL | SpareAI-11 - Lo Alarm |
| `%M00412` | BOOL | `DF_7404_001_ALL` | BOOL | DF_7404_001_ALL | 7404-DF-001  Flame detector pump house - Lo Alarm |
| `%M00413` | BOOL | `DF_7404_002_ALL` | BOOL | DF_7404_002_ALL | 7404-DF-002  Flame detector pump house - Lo Alarm |
| `%M00414` | BOOL | `DG_7404_011R_ALL` | BOOL | DG_7404_011R_ALL | 7404-DG-011R  Open path detector - Lo Alarm |
| `%M00415` | BOOL | `SpareAI_15_ALL` | BOOL | SpareAI_15_ALL | SpareAI-15 - Lo Alarm |
| `%M00416` | BOOL | `SpareAI_16_ALL` | BOOL | SpareAI_16_ALL | SpareAI-16 - Lo Alarm |
| `%M00417` | BOOL | `PST_7002_001_ALL` | BOOL | PST_7002_001_ALL | 7002-PST-001  Air acc. pressure - Lo Alarm |
| `%M00418` | BOOL | `PST_6401_001_ALL` | BOOL | PST_6401_001_ALL | 6401-PST-001  Fuel gas pressure - Lo Alarm |
| `%M00419` | BOOL | `PST_7503_001_ALL` | BOOL | PST_7503_001_ALL | 7503-PST-001  Deluge line pressure - Lo Alarm |
| `%M00420` | BOOL | `FR_7503_001_002_ALL` | BOOL | FR_7503_001_002_ALL | 7503-FR-001/002  Foam release from field - Lo Alarm |
| `%M00421` | BOOL | `SpareAI_21_ALL` | BOOL | SpareAI_21_ALL | SpareAI-21 - Lo Alarm |
| `%M00422` | BOOL | `FR_7503_003_ALL` | BOOL | FR_7503_003_ALL | 7503-FR-003  Foam release from panel - Lo Alarm |
| `%M00423` | BOOL | `SpareAI_23_ALL` | BOOL | SpareAI_23_ALL | SpareAI-23 - Lo Alarm |
| `%M00424` | BOOL | `SpareAI_24_ALL` | BOOL | SpareAI_24_ALL | SpareAI-24 - Lo Alarm |
| `%M00425` | BOOL | `DG_7404_001_ALLI` | BOOL | DG_7404_001_ALLI | 7404-DG-001  Gas detector pump house - Lo Alarm C_E |
| `%M00426` | BOOL | `DG_7404_002_ALLI` | BOOL | DG_7404_002_ALLI | 7404-DG-002  Gas detector pump house - Lo Alarm C_E |
| `%M00427` | BOOL | `DG_7404_003_ALLI` | BOOL | DG_7404_003_ALLI | 7404-DG-003  Gas detector pump house - Lo Alarm C_E |
| `%M00428` | BOOL | `DG_7404_004_ALLI` | BOOL | DG_7404_004_ALLI | 7404-DG-004  Gas detector pump house - Lo Alarm C_E |
| `%M00429` | BOOL | `DG_7404_005_ALLI` | BOOL | DG_7404_005_ALLI | 7404-DG-005  Gas detector pump house - Lo Alarm C_E |
| `%M00430` | BOOL | `DG_7404_006_ALLI` | BOOL | DG_7404_006_ALLI | 7404-DG-006  Gas detector pump house - Lo Alarm C_E |
| `%M00431` | BOOL | `DG_7404_007_ALLI` | BOOL | DG_7404_007_ALLI | 7404-DG-007  Gas detector pump house - Lo Alarm C_E |
| `%M00432` | BOOL | `DG_7404_008_ALLI` | BOOL | DG_7404_008_ALLI | 7404-DG-008  Gas detector pump house - Lo Alarm C_E |
| `%M00433` | BOOL | `DG_7404_009_ALLI` | BOOL | DG_7404_009_ALLI | 7404-DG-009  Gas detector pump house - Lo Alarm C_E |
| `%M00434` | BOOL | `DG_7404_010_ALLI` | BOOL | DG_7404_010_ALLI | 7404-DG-010  Gas detector pump house - Lo Alarm C_E |
| `%M00435` | BOOL | `SpareAI_11_ALLI` | BOOL | SpareAI_11_ALLI | SpareAI-11 - Lo Alarm C_E |
| `%M00436` | BOOL | `DF_7404_001_ALLI` | BOOL | DF_7404_001_ALLI | 7404-DF-001  Flame detector pump house - Lo Alarm C_E |
| `%M00437` | BOOL | `DF_7404_002_ALLI` | BOOL | DF_7404_002_ALLI | 7404-DF-002  Flame detector pump house - Lo Alarm C_E |
| `%M00438` | BOOL | `DG_7404_011R_ALLI` | BOOL | DG_7404_011R_ALLI | 7404-DG-011R  Open path detector - Lo Alarm C_E |
| `%M00439` | BOOL | `SpareAI_15_ALLI` | BOOL | SpareAI_15_ALLI | SpareAI-15 - Lo Alarm C_E |
| `%M00440` | BOOL | `SpareAI_16_ALLI` | BOOL | SpareAI_16_ALLI | SpareAI-16 - Lo Alarm C_E |
| `%M00441` | BOOL | `PST_7002_001_ALLI` | BOOL | PST_7002_001_ALLI | 7002-PST-001  Air acc. pressure - Lo Alarm C_E |
| `%M00442` | BOOL | `PST_6401_001_ALLI` | BOOL | PST_6401_001_ALLI | 6401-PST-001  Fuel gas pressure - Lo Alarm C_E |
| `%M00443` | BOOL | `PST_7503_001_ALLI` | BOOL | PST_7503_001_ALLI | 7503-PST-001  Deluge line pressure - Lo Alarm C_E |
| `%M00444` | BOOL | `FR_7503_001_002_ALLI` | BOOL | FR_7503_001_002_ALLI | 7503-FR-001/002  Foam release from field - Lo Alarm C_E |
| `%M00445` | BOOL | `SpareAI_21_ALLI` | BOOL | SpareAI_21_ALLI | SpareAI-21 - Lo Alarm C_E |
| `%M00446` | BOOL | `FR_7503_003_ALLI` | BOOL | FR_7503_003_ALLI | 7503-FR-003  Foam release from panel - Lo Alarm C_E |
| `%M00447` | BOOL | `SpareAI_23_ALLI` | BOOL | SpareAI_23_ALLI | SpareAI-23 - Lo Alarm C_E |
| `%M00448` | BOOL | `SpareAI_24_ALLI` | BOOL | SpareAI_24_ALLI | SpareAI-24 - Lo Alarm C_E |
| `%M00449` | BOOL | `DG_7404_001_INH` | BOOL | DG_7404_001_INH | 7404-DG-001  Gas detector pump house - Inhibit |
| `%M00450` | BOOL | `DG_7404_002_INH` | BOOL | DG_7404_002_INH | 7404-DG-002  Gas detector pump house - Inhibit |
| `%M00451` | BOOL | `DG_7404_003_INH` | BOOL | DG_7404_003_INH | 7404-DG-003  Gas detector pump house - Inhibit |
| `%M00452` | BOOL | `DG_7404_004_INH` | BOOL | DG_7404_004_INH | 7404-DG-004  Gas detector pump house - Inhibit |
| `%M00453` | BOOL | `DG_7404_005_INH` | BOOL | DG_7404_005_INH | 7404-DG-005  Gas detector pump house - Inhibit |
| `%M00454` | BOOL | `DG_7404_006_INH` | BOOL | DG_7404_006_INH | 7404-DG-006  Gas detector pump house - Inhibit |
| `%M00455` | BOOL | `DG_7404_007_INH` | BOOL | DG_7404_007_INH | 7404-DG-007  Gas detector pump house - Inhibit |
| `%M00456` | BOOL | `DG_7404_008_INH` | BOOL | DG_7404_008_INH | 7404-DG-008  Gas detector pump house - Inhibit |
| `%M00457` | BOOL | `DG_7404_009_INH` | BOOL | DG_7404_009_INH | 7404-DG-009  Gas detector pump house - Inhibit |
| `%M00458` | BOOL | `DG_7404_010_INH` | BOOL | DG_7404_010_INH | 7404-DG-010  Gas detector pump house - Inhibit |
| `%M00459` | BOOL | `SpareAI_11_INH` | BOOL | SpareAI_11_INH | SpareAI-11 - Inhibit |
| `%M00460` | BOOL | `DF_7404_001_INH` | BOOL | DF_7404_001_INH | 7404-DF-001  Flame detector pump house - Inhibit |
| `%M00461` | BOOL | `DF_7404_002_INH` | BOOL | DF_7404_002_INH | 7404-DF-002  Flame detector pump house - Inhibit |
| `%M00462` | BOOL | `DG_7404_011R_INH` | BOOL | DG_7404_011R_INH | 7404-DG-011R  Open path detector - Inhibit |
| `%M00463` | BOOL | `SpareAI_15_INH` | BOOL | SpareAI_15_INH | SpareAI-15 - Inhibit |
| `%M00464` | BOOL | `SpareAI_16_INH` | BOOL | SpareAI_16_INH | SpareAI-16 - Inhibit |
| `%M00465` | BOOL | `PST_7002_001_INH` | BOOL | PST_7002_001_INH | 7002-PST-001  Air acc. pressure - Inhibit |
| `%M00466` | BOOL | `PST_6401_001_INH` | BOOL | PST_6401_001_INH | 6401-PST-001  Fuel gas pressure - Inhibit |
| `%M00467` | BOOL | `PST_7503_001_INH` | BOOL | PST_7503_001_INH | 7503-PST-001  Deluge line pressure - Inhibit |
| `%M00468` | BOOL | `FR_7503_001_002_INH` | BOOL | FR_7503_001_002_INH | 7503-FR-001/002  Foam release from field - Inhibit |
| `%M00469` | BOOL | `SpareAI_21_INH` | BOOL | SpareAI_21_INH | SpareAI-21 - Inhibit |
| `%M00470` | BOOL | `FR_7503_003_INH` | BOOL | FR_7503_003_INH | 7503-FR-003  Foam release from panel - Inhibit |
| `%M00471` | BOOL | `SpareAI_23_INH` | BOOL | SpareAI_23_INH | SpareAI-23 - Inhibit |
| `%M00472` | BOOL | `SpareAI_24_INH` | BOOL | SpareAI_24_INH | SpareAI-24 - Inhibit |
| `%M00473` | BOOL | `DG_7404_001_OC` | BOOL | DG_7404_001_OC | 7404-DG-001  Gas detector pump house - Open circuit |
| `%M00474` | BOOL | `DG_7404_002_OC` | BOOL | DG_7404_002_OC | 7404-DG-002  Gas detector pump house - Open circuit |
| `%M00475` | BOOL | `DG_7404_003_OC` | BOOL | DG_7404_003_OC | 7404-DG-003  Gas detector pump house - Open circuit |
| `%M00476` | BOOL | `DG_7404_004_OC` | BOOL | DG_7404_004_OC | 7404-DG-004  Gas detector pump house - Open circuit |
| `%M00477` | BOOL | `DG_7404_005_OC` | BOOL | DG_7404_005_OC | 7404-DG-005  Gas detector pump house - Open circuit |
| `%M00478` | BOOL | `DG_7404_006_OC` | BOOL | DG_7404_006_OC | 7404-DG-006  Gas detector pump house - Open circuit |
| `%M00479` | BOOL | `DG_7404_007_OC` | BOOL | DG_7404_007_OC | 7404-DG-007  Gas detector pump house - Open circuit |
| `%M00480` | BOOL | `DG_7404_008_OC` | BOOL | DG_7404_008_OC | 7404-DG-008  Gas detector pump house - Open circuit |
| `%M00481` | BOOL | `DG_7404_009_OC` | BOOL | DG_7404_009_OC | 7404-DG-009  Gas detector pump house - Open circuit |
| `%M00482` | BOOL | `DG_7404_010_OC` | BOOL | DG_7404_010_OC | 7404-DG-010  Gas detector pump house - Open circuit |
| `%M00483` | BOOL | `SpareAI_11_OC` | BOOL | SpareAI_11_OC | SpareAI-11 - Open circuit |
| `%M00484` | BOOL | `DF_7404_001_OC` | BOOL | DF_7404_001_OC | 7404-DF-001  Flame detector pump house - Open circuit |
| `%M00485` | BOOL | `DF_7404_002_OC` | BOOL | DF_7404_002_OC | 7404-DF-002  Flame detector pump house - Open circuit |
| `%M00486` | BOOL | `DG_7404_011R_OC` | BOOL | DG_7404_011R_OC | 7404-DG-011R  Open path detector - Open circuit |
| `%M00487` | BOOL | `SpareAI_15_OC` | BOOL | SpareAI_15_OC | SpareAI-15 - Open circuit |
| `%M00488` | BOOL | `SpareAI_16_OC` | BOOL | SpareAI_16_OC | SpareAI-16 - Open circuit |
| `%M00489` | BOOL | `PST_7002_001_OC` | BOOL | PST_7002_001_OC | 7002-PST-001  Air acc. pressure - Open circuit |
| `%M00490` | BOOL | `PST_6401_001_OC` | BOOL | PST_6401_001_OC | 6401-PST-001  Fuel gas pressure - Open circuit |
| `%M00491` | BOOL | `PST_7503_001_OC` | BOOL | PST_7503_001_OC | 7503-PST-001  Deluge line pressure - Open circuit |
| `%M00492` | BOOL | `FR_7503_001_002_OC` | BOOL | FR_7503_001_002_OC | 7503-FR-001/002  Foam release from field - Open circuit |
| `%M00493` | BOOL | `SpareAI_21_OC` | BOOL | SpareAI_21_OC | SpareAI-21 - Open circuit |
| `%M00494` | BOOL | `FR_7503_003_OC` | BOOL | FR_7503_003_OC | 7503-FR-003  Foam release from panel - Open circuit |
| `%M00495` | BOOL | `SpareAI_23_OC` | BOOL | SpareAI_23_OC | SpareAI-23 - Open circuit |
| `%M00496` | BOOL | `SpareAI_24_OC` | BOOL | SpareAI_24_OC | SpareAI-24 - Open circuit |
| `%M00497` | BOOL | `DG_7404_001_SC` | BOOL | DG_7404_001_SC | 7404-DG-001  Gas detector pump house - Short circuit |
| `%M00498` | BOOL | `DG_7404_002_SC` | BOOL | DG_7404_002_SC | 7404-DG-002  Gas detector pump house - Short circuit |
| `%M00499` | BOOL | `DG_7404_003_SC` | BOOL | DG_7404_003_SC | 7404-DG-003  Gas detector pump house - Short circuit |
| `%M00500` | BOOL | `DG_7404_004_SC` | BOOL | DG_7404_004_SC | 7404-DG-004  Gas detector pump house - Short circuit |
| `%M00501` | BOOL | `DG_7404_005_SC` | BOOL | DG_7404_005_SC | 7404-DG-005  Gas detector pump house - Short circuit |
| `%M00502` | BOOL | `DG_7404_006_SC` | BOOL | DG_7404_006_SC | 7404-DG-006  Gas detector pump house - Short circuit |
| `%M00503` | BOOL | `DG_7404_007_SC` | BOOL | DG_7404_007_SC | 7404-DG-007  Gas detector pump house - Short circuit |
| `%M00504` | BOOL | `DG_7404_008_SC` | BOOL | DG_7404_008_SC | 7404-DG-008  Gas detector pump house - Short circuit |
| `%M00505` | BOOL | `DG_7404_009_SC` | BOOL | DG_7404_009_SC | 7404-DG-009  Gas detector pump house - Short circuit |
| `%M00506` | BOOL | `DG_7404_010_SC` | BOOL | DG_7404_010_SC | 7404-DG-010  Gas detector pump house - Short circuit |
| `%M00507` | BOOL | `SpareAI_11_SC` | BOOL | SpareAI_11_SC | SpareAI-11 - Short circuit |
| `%M00508` | BOOL | `DF_7404_001_SC` | BOOL | DF_7404_001_SC | 7404-DF-001  Flame detector pump house - Short circuit |
| `%M00509` | BOOL | `DF_7404_002_SC` | BOOL | DF_7404_002_SC | 7404-DF-002  Flame detector pump house - Short circuit |
| `%M00510` | BOOL | `DG_7404_011R_SC` | BOOL | DG_7404_011R_SC | 7404-DG-011R  Open path detector - Short circuit |
| `%M00511` | BOOL | `SpareAI_15_SC` | BOOL | SpareAI_15_SC | SpareAI-15 - Short circuit |
| `%M00512` | BOOL | `SpareAI_16_SC` | BOOL | SpareAI_16_SC | SpareAI-16 - Short circuit |
| `%M00513` | BOOL | `PST_7002_001_SC` | BOOL | PST_7002_001_SC | 7002-PST-001  Air acc. pressure - Short circuit |
| `%M00514` | BOOL | `PST_6401_001_SC` | BOOL | PST_6401_001_SC | 6401-PST-001  Fuel gas pressure - Short circuit |
| `%M00515` | BOOL | `PST_7503_001_SC` | BOOL | PST_7503_001_SC | 7503-PST-001  Deluge line pressure - Short circuit |
| `%M00516` | BOOL | `FR_7503_001_002_SC` | BOOL | FR_7503_001_002_SC | 7503-FR-001/002  Foam release from field - Short circuit |
| `%M00517` | BOOL | `SpareAI_21_SC` | BOOL | SpareAI_21_SC | SpareAI-21 - Short circuit |
| `%M00518` | BOOL | `FR_7503_003_SC` | BOOL | FR_7503_003_SC | 7503-FR-003  Foam release from panel - Short circuit |
| `%M00519` | BOOL | `SpareAI_23_SC` | BOOL | SpareAI_23_SC | SpareAI-23 - Short circuit |
| `%M00520` | BOOL | `SpareAI_24_SC` | BOOL | SpareAI_24_SC | SpareAI-24 - Short circuit |
| `%M00521` | BOOL | `DG_7404_001_FLT1` | BOOL | DG_7404_001_FLT1 | 7404-DG-001  Gas detector pump house - Fault 1 |
| `%M00522` | BOOL | `DG_7404_002_FLT1` | BOOL | DG_7404_002_FLT1 | 7404-DG-002  Gas detector pump house - Fault 1 |
| `%M00523` | BOOL | `DG_7404_003_FLT1` | BOOL | DG_7404_003_FLT1 | 7404-DG-003  Gas detector pump house - Fault 1 |
| `%M00524` | BOOL | `DG_7404_004_FLT1` | BOOL | DG_7404_004_FLT1 | 7404-DG-004  Gas detector pump house - Fault 1 |
| `%M00525` | BOOL | `DG_7404_005_FLT1` | BOOL | DG_7404_005_FLT1 | 7404-DG-005  Gas detector pump house - Fault 1 |
| `%M00526` | BOOL | `DG_7404_006_FLT1` | BOOL | DG_7404_006_FLT1 | 7404-DG-006  Gas detector pump house - Fault 1 |
| `%M00527` | BOOL | `DG_7404_007_FLT1` | BOOL | DG_7404_007_FLT1 | 7404-DG-007  Gas detector pump house - Fault 1 |
| `%M00528` | BOOL | `DG_7404_008_FLT1` | BOOL | DG_7404_008_FLT1 | 7404-DG-008  Gas detector pump house - Fault 1 |
| `%M00529` | BOOL | `DG_7404_009_FLT1` | BOOL | DG_7404_009_FLT1 | 7404-DG-009  Gas detector pump house - Fault 1 |
| `%M00530` | BOOL | `DG_7404_010_FLT1` | BOOL | DG_7404_010_FLT1 | 7404-DG-010  Gas detector pump house - Fault 1 |
| `%M00531` | BOOL | `SpareAI_11_FLT1` | BOOL | SpareAI_11_FLT1 | SpareAI-11 - Fault 1 |
| `%M00532` | BOOL | `DF_7404_001_FLT1` | BOOL | DF_7404_001_FLT1 | 7404-DF-001  Flame detector pump house - Fault 1 |
| `%M00533` | BOOL | `DF_7404_002_FLT1` | BOOL | DF_7404_002_FLT1 | 7404-DF-002  Flame detector pump house - Fault 1 |
| `%M00534` | BOOL | `DG_7404_011R_FLT1` | BOOL | DG_7404_011R_FLT1 | 7404-DG-011R  Open path detector - Fault 1 (Optic fault) |
| `%M00535` | BOOL | `SpareAI_15_FLT1` | BOOL | SpareAI_15_FLT1 | SpareAI-15 - Fault 1 |
| `%M00536` | BOOL | `SpareAI_16_FLT1` | BOOL | SpareAI_16_FLT1 | SpareAI-16 - Fault 1 |
| `%M00537` | BOOL | `PST_7002_001_FLT1` | BOOL | PST_7002_001_FLT1 | 7002-PST-001  Air acc. pressure - Fault 1 |
| `%M00538` | BOOL | `PST_6401_001_FLT1` | BOOL | PST_6401_001_FLT1 | 6401-PST-001  Fuel gas pressure - Fault 1 |
| `%M00539` | BOOL | `PST_7503_001_FLT1` | BOOL | PST_7503_001_FLT1 | 7503-PST-001  Deluge line pressure - Fault 1 |
| `%M00540` | BOOL | `FR_7503_001_002_FLT1` | BOOL | FR_7503_001_002_FLT1 | 7503-FR-001/002  Foam release from field - Fault 1 |
| `%M00541` | BOOL | `SpareAI_21_FLT1` | BOOL | SpareAI_21_FLT1 | SpareAI-21 - Fault 1 |
| `%M00542` | BOOL | `FR_7503_003_FLT1` | BOOL | FR_7503_003_FLT1 | 7503-FR-003  Foam release from panel - Fault 1 |
| `%M00543` | BOOL | `SpareAI_23_FLT1` | BOOL | SpareAI_23_FLT1 | SpareAI-23 - Fault 1 |
| `%M00544` | BOOL | `SpareAI_24_FLT1` | BOOL | SpareAI_24_FLT1 | SpareAI-24 - Fault 1 |
| `%M00545` | BOOL | `DG_7404_001_FLT2` | BOOL | DG_7404_001_FLT2 | 7404-DG-001  Gas detector pump house - Fault 2 |
| `%M00546` | BOOL | `DG_7404_002_FLT2` | BOOL | DG_7404_002_FLT2 | 7404-DG-002  Gas detector pump house - Fault 2 |
| `%M00547` | BOOL | `DG_7404_003_FLT2` | BOOL | DG_7404_003_FLT2 | 7404-DG-003  Gas detector pump house - Fault 2 |
| `%M00548` | BOOL | `DG_7404_004_FLT2` | BOOL | DG_7404_004_FLT2 | 7404-DG-004  Gas detector pump house - Fault 2 |
| `%M00549` | BOOL | `DG_7404_005_FLT2` | BOOL | DG_7404_005_FLT2 | 7404-DG-005  Gas detector pump house - Fault 2 |
| `%M00550` | BOOL | `DG_7404_006_FLT2` | BOOL | DG_7404_006_FLT2 | 7404-DG-006  Gas detector pump house - Fault 2 |
| `%M00551` | BOOL | `DG_7404_007_FLT2` | BOOL | DG_7404_007_FLT2 | 7404-DG-007  Gas detector pump house - Fault 2 |
| `%M00552` | BOOL | `DG_7404_008_FLT2` | BOOL | DG_7404_008_FLT2 | 7404-DG-008  Gas detector pump house - Fault 2 |
| `%M00553` | BOOL | `DG_7404_009_FLT2` | BOOL | DG_7404_009_FLT2 | 7404-DG-009  Gas detector pump house - Fault 2 |
| `%M00554` | BOOL | `DG_7404_010_FLT2` | BOOL | DG_7404_010_FLT2 | 7404-DG-010  Gas detector pump house - Fault 2 |
| `%M00555` | BOOL | `SpareAI_11_FLT2` | BOOL | SpareAI_11_FLT2 | SpareAI-11 - Fault 2 |
| `%M00556` | BOOL | `DF_7404_001_FLT2` | BOOL | DF_7404_001_FLT2 | 7404-DF-001  Flame detector pump house - Fault 2 |
| `%M00557` | BOOL | `DF_7404_002_FLT2` | BOOL | DF_7404_002_FLT2 | 7404-DF-002  Flame detector pump house - Fault 2 |
| `%M00558` | BOOL | `DG_7404_011R_FLT2` | BOOL | DG_7404_011R_FLT2 | 7404-DG-011R  Open path detector - Fault 2 |
| `%M00559` | BOOL | `SpareAI_15_FLT2` | BOOL | SpareAI_15_FLT2 | SpareAI-15 - Fault 2 |
| `%M00560` | BOOL | `SpareAI_16_FLT2` | BOOL | SpareAI_16_FLT2 | SpareAI-16 - Fault 2 |
| `%M00561` | BOOL | `PST_7002_001_FLT2` | BOOL | PST_7002_001_FLT2 | 7002-PST-001  Air acc. pressure - Fault 2 |
| `%M00562` | BOOL | `PST_6401_001_FLT2` | BOOL | PST_6401_001_FLT2 | 6401-PST-001  Fuel gas pressure - Fault 2 |
| `%M00563` | BOOL | `PST_7503_001_FLT2` | BOOL | PST_7503_001_FLT2 | 7503-PST-001  Deluge line pressure - Fault 2 |
| `%M00564` | BOOL | `FR_7503_001_002_FLT2` | BOOL | FR_7503_001_002_FLT2 | 7503-FR-001/002  Foam release from field - Fault 2 |
| `%M00565` | BOOL | `SpareAI_21_FLT2` | BOOL | SpareAI_21_FLT2 | SpareAI-21 - Fault 2 |
| `%M00566` | BOOL | `FR_7503_003_FLT2` | BOOL | FR_7503_003_FLT2 | 7503-FR-003  Foam release from panel - Fault 2 |
| `%M00567` | BOOL | `SpareAI_23_FLT2` | BOOL | SpareAI_23_FLT2 | SpareAI-23 - Fault 2 |
| `%M00568` | BOOL | `SpareAI_24_FLT2` | BOOL | SpareAI_24_FLT2 | SpareAI-24 - Fault 2 |
| `%M00569` | BOOL | `DG_7404_001_FRUP` | BOOL | DG_7404_001_FRUP | 7404-DG-001  Gas detector pump house - First up |
| `%M00570` | BOOL | `DG_7404_002_FRUP` | BOOL | DG_7404_002_FRUP | 7404-DG-002  Gas detector pump house - First up |
| `%M00571` | BOOL | `DG_7404_003_FRUP` | BOOL | DG_7404_003_FRUP | 7404-DG-003  Gas detector pump house - First up |
| `%M00572` | BOOL | `DG_7404_004_FRUP` | BOOL | DG_7404_004_FRUP | 7404-DG-004  Gas detector pump house - First up |
| `%M00573` | BOOL | `DG_7404_005_FRUP` | BOOL | DG_7404_005_FRUP | 7404-DG-005  Gas detector pump house - First up |
| `%M00574` | BOOL | `DG_7404_006_FRUP` | BOOL | DG_7404_006_FRUP | 7404-DG-006  Gas detector pump house - First up |
| `%M00575` | BOOL | `DG_7404_007_FRUP` | BOOL | DG_7404_007_FRUP | 7404-DG-007  Gas detector pump house - First up |
| `%M00576` | BOOL | `DG_7404_008_FRUP` | BOOL | DG_7404_008_FRUP | 7404-DG-008  Gas detector pump house - First up |
| `%M00577` | BOOL | `DG_7404_009_FRUP` | BOOL | DG_7404_009_FRUP | 7404-DG-009  Gas detector pump house - First up |
| `%M00578` | BOOL | `DG_7404_010_FRUP` | BOOL | DG_7404_010_FRUP | 7404-DG-010  Gas detector pump house - First up |
| `%M00579` | BOOL | `SpareAI_11_FRUP` | BOOL | SpareAI_11_FRUP | SpareAI-11 - First up |
| `%M00580` | BOOL | `DF_7404_001_FRUP` | BOOL | DF_7404_001_FRUP | 7404-DF-001  Flame detector pump house - First up |
| `%M00581` | BOOL | `DF_7404_002_FRUP` | BOOL | DF_7404_002_FRUP | 7404-DF-002  Flame detector pump house - First up |
| `%M00582` | BOOL | `DG_7404_011R_FRUP` | BOOL | DG_7404_011R_FRUP | 7404-DG-011R  Open path detector - First up |
| `%M00583` | BOOL | `SpareAI_15_FRUP` | BOOL | SpareAI_15_FRUP | SpareAI-15 - First up |
| `%M00584` | BOOL | `SpareAI_16_FRUP` | BOOL | SpareAI_16_FRUP | SpareAI-16 - First up |
| `%M00585` | BOOL | `PST_7002_001_FRUP` | BOOL | PST_7002_001_FRUP | 7002-PST-001  Air acc. pressure - First up |
| `%M00586` | BOOL | `PST_6401_001_FRUP` | BOOL | PST_6401_001_FRUP | 6401-PST-001  Fuel gas pressure - First up |
| `%M00587` | BOOL | `PST_7503_001_FRUP` | BOOL | PST_7503_001_FRUP | 7503-PST-001  Deluge line pressure - First up |
| `%M00588` | BOOL | `FR_7503_001_002_FRUP` | BOOL | FR_7503_001_002_FRUP | 7503-FR-001/002  Foam release from field - First up |
| `%M00589` | BOOL | `SpareAI_21_FRUP` | BOOL | SpareAI_21_FRUP | SpareAI-21 - First up |
| `%M00590` | BOOL | `FR_7503_003_FRUP` | BOOL | FR_7503_003_FRUP | 7503-FR-003  Foam release from panel - First up |
| `%M00591` | BOOL | `SpareAI_23_FRUP` | BOOL | SpareAI_23_FRUP | SpareAI-23 - First up |
| `%M00592` | BOOL | `SpareAI_24_FRUP` | BOOL | SpareAI_24_FRUP | SpareAI-24 - First up |
| `%M00600` | BOOL | `AI_LoAlarm` | BOOL | AI_LoAlarm | Lo Alarm Out |
| `%M00601` | BOOL | `AI_HiAlarm` | BOOL | AI_HiAlarm | Hi Alarm Out |
| `%M00602` | BOOL | `AI_LoFault` | BOOL | AI_LoFault | Lo Fault Out |
| `%M00604` | BOOL | `AI_HiFault` | BOOL | AI_HiFault | Hi Fault Out |
| `%M00605` | BOOL | `Voting_DG_7404_ALLI` | BOOL | Voting_DG_7404_ALLI | Voting of Gas Low Alarms in pump house |
| `%M00606` | BOOL | `Voting_DG_7404_ALHI` | BOOL | Voting_DG_7404_ALHI | Voting of Gas High Alarms in pump house |
| `%M00607` | BOOL | `Voting_All_Inhibits` | BOOL | Voting_All_Inhibits | Voting of all Inhibits |
| `%M00608` | BOOL | `Voting_All_Faults` | BOOL | Voting_All_Faults | Voting of all Faults |
| `%M00609` | BOOL | `AI_Fault1` | BOOL | AI_Fault1 | Fault 1 for Gas detecor |
| `%M00610` | BOOL | `AI_Fault2` | BOOL | AI_Fault2 | Fault 2 for Gas detecor |
| `%M00620` | BOOL | `DelugeFailedToRelease` | BOOL | DelugeFailedToRelease | Set if Deluge fail to release after trigging start of Pump B 3 times with 30 sec. delay |
| `%M00621` | BOOL | `Pump_Active_1_Hour` | BOOL | Pump_Active_1_Hour | Set if Pump A have been activated in 60 minutes. |
| `%M00700` | BOOL | `System_Reset` | BOOL | System_Reset | Reset all latches |
| `%M00701` | BOOL | `System_Reset_Delay` | BOOL | System_Reset_Delay | High when System_Reset is high and 5 sec. after this. |
| `%M00702` | BOOL | `System_Reset_Startup` | BOOL | System_Reset_Startup | Used for reset system at startup |
| `%M00703` | BOOL | `System_Reset_HMI` | BOOL | System_Reset_HMI | System reset activation signal from HMI (panel) |
| `%M00704` | BOOL | `System_Reset_HMI_Help` | BOOL | System_Reset_HMI_Help | Help puls from HMI (panel) reset signal |
| `%M00705` | BOOL | `System_AnyActions` | BOOL | System_AnyActions | High first scan after C&E has caused first trip |
| `%M00706` | BOOL | `System_Mute` | BOOL | System_Mute | System Mute from tuch panel |
| `%M00800` | BOOL | `System_Sound01` | BOOL | System_Sound01 | Reset all latches |
| `%M00801` | BOOL | `System_Sound02` | BOOL | System_Sound02 | Reset all latches |
| `%M00802` | BOOL | `System_Sound03` | BOOL | System_Sound03 | Reset all latches |
| `%M00803` | BOOL | `System_Sound04` | BOOL | System_Sound04 | Reset all latches |
| `%M00804` | BOOL | `System_Sound05` | BOOL | System_Sound05 | Reset all latches |
| `%M00805` | BOOL | `System_Sound06` | BOOL | System_Sound06 | Reset all latches |
| `%M00806` | BOOL | `System_Sound07` | BOOL | System_Sound07 | Reset all latches |
| `%M00807` | BOOL | `System_Sound08` | BOOL | System_Sound08 | Reset all latches |
| `%M00808` | BOOL | `System_Sound09` | BOOL | System_Sound09 | Reset all latches |
| `%M00809` | BOOL | `System_Sound10` | BOOL | System_Sound10 | Reset all latches |
| `%M00810` | BOOL | `System_Sound11` | BOOL | System_Sound11 | Reset all latches |
| `%M00811` | BOOL | `System_Sound12` | BOOL | System_Sound12 | Reset all latches |
| `%M00812` | BOOL | `System_Sound13` | BOOL | System_Sound13 | Reset all latches |
| `%M00813` | BOOL | `System_Sound14` | BOOL | System_Sound14 | Reset all latches |
| `%M00814` | BOOL | `System_Sound15` | BOOL | System_Sound15 | Reset all latches |
| `%M00815` | BOOL | `System_Sound16` | BOOL | System_Sound16 | Reset all latches |
| `%M00816` | BOOL | `System_Sound17` | BOOL | System_Sound17 | Reset all latches |
| `%M00817` | BOOL | `System_Sound18` | BOOL | System_Sound18 | Reset all latches |
| `%M00818` | BOOL | `System_Sound19` | BOOL | System_Sound19 | Reset all latches |
| `%M00819` | BOOL | `System_Sound20` | BOOL | System_Sound20 | Reset all latches |
| `%M00820` | BOOL | `System_Sound21` | BOOL | System_Sound21 | Reset all latches |
| `%M00821` | BOOL | `System_Sound22` | BOOL | System_Sound22 | Reset all latches |
| `%M00822` | BOOL | `System_Sound23` | BOOL | System_Sound23 | Reset all latches |
| `%M00823` | BOOL | `System_Sound24` | BOOL | System_Sound24 | Reset all latches |
| `%M00824` | BOOL | `System_Sound25` | BOOL | System_Sound25 | Reset all latches |
| `%M00825` | BOOL | `System_Sound26` | BOOL | System_Sound26 | Reset all latches |
| `%M00826` | BOOL | `System_Sound27` | BOOL | System_Sound27 | Reset all latches |
| `%M00827` | BOOL | `System_Sound28` | BOOL | System_Sound28 | Reset all latches |
| `%M00828` | BOOL | `System_Sound29` | BOOL | System_Sound29 | Reset all latches |
| `%M00829` | BOOL | `System_Sound30` | BOOL | System_Sound30 | Reset all latches |
| `%M00830` | BOOL | `System_Sound31` | BOOL | System_Sound31 | Reset all latches |
| `%M00831` | BOOL | `System_Sound32` | BOOL | System_Sound32 | Reset all latches |
| `%M00832` | BOOL | `System_Sound33` | BOOL | System_Sound33 | Reset all latches |
| `%M00833` | BOOL | `System_Sound34` | BOOL | System_Sound34 | Reset all latches |
| `%M00834` | BOOL | `System_Sound35` | BOOL | System_Sound35 | Reset all latches |
| `%M00835` | BOOL | `System_Sound36` | BOOL | System_Sound36 | Reset all latches |
| `%M00836` | BOOL | `System_Sound37` | BOOL | System_Sound37 | Reset all latches |
| `%M00837` | BOOL | `System_Sound38` | BOOL | System_Sound38 | Reset all latches |
| `%M00838` | BOOL | `System_Sound39` | BOOL | System_Sound39 | Reset all latches |
| `%M00839` | BOOL | `System_Sound40` | BOOL | System_Sound40 | Reset all latches |
| `%R00001` | INT | `DG_7404_001_VAL` | DINT | DG_7404_001_VAL | 7404-DG-001  Gas detector pump house - Converted value |
| `%R00003` | INT | `DG_7404_002_VAL` | DINT | DG_7404_002_VAL | 7404-DG-002  Gas detector pump house - Converted value |
| `%R00005` | INT | `DG_7404_003_VAL` | DINT | DG_7404_003_VAL | 7404-DG-003  Gas detector pump house - Converted value |
| `%R00007` | INT | `DG_7404_004_VAL` | DINT | DG_7404_004_VAL | 7404-DG-004  Gas detector pump house - Converted value |
| `%R00009` | INT | `DG_7404_005_VAL` | DINT | DG_7404_005_VAL | 7404-DG-005  Gas detector pump house - Converted value |
| `%R00011` | INT | `DG_7404_006_VAL` | DINT | DG_7404_006_VAL | 7404-DG-006  Gas detector pump house - Converted value |
| `%R00013` | INT | `DG_7404_007_VAL` | DINT | DG_7404_007_VAL | 7404-DG-007  Gas detector pump house - Converted value |
| `%R00015` | INT | `DG_7404_008_VAL` | DINT | DG_7404_008_VAL | 7404-DG-008  Gas detector pump house - Converted value |
| `%R00017` | INT | `DG_7404_009_VAL` | DINT | DG_7404_009_VAL | 7404-DG-009  Gas detector pump house - Converted value |
| `%R00019` | INT | `DG_7404_010_VAL` | DINT | DG_7404_010_VAL | 7404-DG-010  Gas detector pump house - Converted value |
| `%R00021` | REAL | `SpareAI_11_VAL` | REAL | SpareAI_11_VAL | SpareAI-11 - Converted value |
| `%R00023` | INT | `DF_7404_001_VAL` | DINT | DF_7404_001_VAL | 7404-DF-001  Flame detector pump house - Converted value |
| `%R00025` | INT | `DF_7404_002_VAL` | DINT | DF_7404_002_VAL | 7404-DF-002  Flame detector pump house - Converted value |
| `%R00027` | REAL | `DG_7404_011R_VAL` | REAL | DG_7404_011R_VAL | 7404-DG-011R  Open path detector - Converted value |
| `%R00029` | INT | `SpareAI_15_VAL` | DINT | SpareAI_15_VAL | SpareAI-15 - Converted value |
| `%R00031` | INT | `SpareAI_16_VAL` | DINT | SpareAI_16_VAL | SpareAI-16 - Converted value |
| `%R00033` | INT | `PST_7002_001_VAL` | DINT | PST_7002_001_VAL | 7002-PST-001  Air acc. pressure - Converted value |
| `%R00035` | INT | `PST_6401_001_VAL` | DINT | PST_6401_001_VAL | 6401-PST-001  Fuel gas pressure - Converted value |
| `%R00037` | INT | `PST_7503_001_VAL` | DINT | PST_7503_001_VAL | 7503-PST-001  Deluge line pressure - Converted value |
| `%R00039` | INT | `FR_7503_001_002_VAL` | DINT | FR_7503_001_002_VAL | 7503-FR-001/002  Foam release from field - Converted value |
| `%R00041` | INT | `SpareAI_21_VAL` | DINT | SpareAI_21_VAL | SpareAI-21 - Converted value |
| `%R00043` | INT | `FR_7503_003_VAL` | DINT | FR_7503_003_VAL | 7503-FR-003  Foam release from panel - Converted value |
| `%R00045` | INT | `SpareAI_23_VAL` | DINT | SpareAI_23_VAL | SpareAI-23 - Converted value |
| `%R00047` | INT | `SpareAI_24_VAL` | DINT | SpareAI_24_VAL | SpareAI-24 - Converted value |
| `%R00100` | INT | `AI_ValueIn` | DINT | AI_ValueIn | The converted value moved to _VAL on analog input. |
| `%R00106` | INT | `AI_LoAlarmSetpoint` | DINT | AI_LoAlarmSetpoint | Lo Alarm Setpoint |
| `%R00108` | INT | `AI_HiAlarmSetpoint` | DINT | AI_HiAlarmSetpoint | Hi Alarm Setpoint |
| `%R00110` | INT | `AI_LoFaultSetpoint` | DINT | AI_LoFaultSetpoint | Lo Fault Out Setpoint |
| `%R00112` | INT | `AI_HiFaultSetpoint` | DINT | AI_HiFaultSetpoint | Hi Fault Out Setpoint |
| `%R00120` | INT | `AI_TempVal` | DINT | AI_TempVal | Value used for converting analog input to correct range. |
| `%R00122` | REAL | `AI_ValueIn_Real` | REAL | AI_ValueIn_Real | The converted value moved to _VAL on analog input. |
| `%R00124` | REAL | `AI_TempVal_Real` | REAL | AI_TempVal_Real | Value used for converting analog input to correct range. |
| `%R00126` | REAL | `AI_HiAlarmSetpoint_Real` | REAL | AI_HiAlarmSetpoint_Real | Hi Alarm Setpoint |
| `%R00128` | REAL | `AI_LoAlarmSetpoint_Real` | REAL | AI_LoAlarmSetpoint_Real | Lo Alarm Setpoint |
| `%R00130` | REAL | `AI_LoFaultSetpoint_Real` | REAL | AI_LoFaultSetpoint_Real | Lo Fault Out Setpoint |
| `%R00132` | REAL | `AI_HiFaultSetpoint_Real` | REAL | AI_HiFaultSetpoint_Real | Hi Fault Out Setpoint |
| `%R00134` | REAL | `AI_Fault1_Setpoint_Real` | REAL | AI_Fault1_Setpoint_Real | Fault 1 Out Setpoint |
| `%R00136` | REAL | `AI_Fault2_Setpoint_Real` | REAL | AI_Fault2_Setpoint_Real | Fault 2 Out Setpoint |
| `%R00200` | INT | `System_ClearPLC_Fault` | DINT | System_ClearPLC_Fault | Used in logic to clear I/O Fault Table |
| `%R00201` | INT | `System_ClearIO_Fault` | DINT | System_ClearIO_Fault | Used in logic to clear I/O Fault Table |
| `%R00202` | WORD | `System_C_E_Delay` | DINT | System_C_E_Delay | Use in logic to delay Cause&Effect logic at startup of PLC. |
| `%R00205` | WORD | `System_HMI_Reset_Timer` | DINT | System_HMI_Reset_Timer | Resets HMI system reset signal after 5 sec. |
| `%R00208` | INT | `System_Reset_HelpRegister` | DINT | System_Reset_HelpRegister | Help register for System Reset at startup |
| `%R00209` | WORD | `Pump_Timer1` | DINT | Pump_Timer1 | Use in logic to delay Cause&Effect logic at startup of PLC. |
| `%R00212` | WORD | `Pump_Timer2` | DINT | Pump_Timer2 | Used in logic for delay of Pump B start signal. |
| `%R00215` | WORD | `Pump_Timer3` | DINT | Pump_Timer3 | Used in logic for delay of Pump B start signal. |
| `%R00218` | WORD | `Pump_Timer4` | DINT | Pump_Timer4 | Used in logic for delay of Pump B start signal. |
| `%R00221` | WORD | `Pump_Timer5` | DINT | Pump_Timer5 | Used in logic for delay of Pump B start signal. |
| `%R00224` | WORD | `Pump_Timer6` | DINT | Pump_Timer6 | Used in logic for delay of Pump B start signal. |
| `%R00227` | WORD | `Pump_Timer7` | DINT | Pump_Timer7 | Used in logic for delay of Pump B start signal. |
| `%R00230` | WORD | `Pump_Timer8` | DINT | Pump_Timer8 | Used in logic for delay of Pump B start signal. |
| `%R00233` | WORD | `Pump_Timer9` | DINT | Pump_Timer9 | Used in logic for open circuit on Pump A signal. |
| `%R00236` | WORD | `Pump_Timer10` | DINT | Pump_Timer10 | Used in logic for open circuit on Pump A signal. |
| `%R00239` | WORD | `Pump_Timer11` | DINT | Pump_Timer11 | Used in logic for open circuit on Pump A signal. |
| `%R00242` | WORD | `Pump_Timer12` | DINT | Pump_Timer12 | Used in logic for open circuit on Pump A signal. |
| `%R00245` | WORD | `Pump_Timer13` | DINT | Pump_Timer13 | Used in logic for stop Pump A/B after active in 60 minutes. |
| `%R02000` | REAL | `AAAAA` | REAL | AAAAA |  |
| `%T00002` | BOOL | `T00002` | BOOL | T00002 | High 120 sec. after PLC set in run. |
| `%T00003` | BOOL | `T00003` | BOOL | T00003 |  |
| `%T00004` | BOOL | `T00004` | BOOL | T00004 |  |
| `%T00005` | BOOL | `T00005` | BOOL | T00005 |  |
| `%T00006` | BOOL | `T00006` | BOOL | T00006 |  |
| `%T00007` | BOOL | `T00007` | BOOL | T00007 |  |
| `%T00008` | BOOL | `T00008` | BOOL | T00008 |  |
| `%T00009` | BOOL | `T00009` | BOOL | T00009 |  |
| `%T00010` | BOOL | `T00010` | BOOL | T00010 |  |
| `%T00011` | BOOL | `T00011` | BOOL | T00011 | For Fault 1 comparing on Gas detector |
| `%T00012` | BOOL | `T00012` | BOOL | T00012 | For Fault 1 comparing on Gas detector |
| `%T00013` | BOOL | `T00013` | BOOL | T00013 | For checking Open circuit on Start Pump |
| `%T00014` | BOOL | `T00014` | BOOL | T00014 | For checking Open circuit on Start Pump |

## 5. Tag handling of the GE system bits and special names

| Source | Use | Conversion |
|---|---|---|
| `#FST_SCN` `%S00001` | first-scan bit | `S:FS` |
| `#ALW_ON` `%S00007` | always-on contact | dropped, rung unconditional |
| `#T_SEC` `%S00005` | 1.0 s clock contact | `T_SEC_PULSE` generated in `Logic` (0.5 s on / 0.5 s off) |
| `#T_MIN` `%S00006` | 1.0 min clock contact | `T_MIN_PULSE` generated in `Logic` (30 s on / 30 s off) |
| `%T00003…%T00014` | timer done / flag bits | BOOL tags; `.DN` of the corresponding `TON` where the bit is a timer done |
| array elements, e.g. `Pump_Timer1[0]` | word array elements | declared as DINT arrays with the same dimensions; element references kept |

**QuickPanel / HMI references.** The source cross-reference lists many `QuickPanel_10toms [Panel, …]` objects (panel pilot lights, numeric displays, bit-alarm grid entries). As instructed these graphics objects are **not** reproduced; the associated PLC tags (`*_INH`, `*_MT`, `*_INT`, `System_Reset`, `System_Mute`, `System_Reset_HMI`, `Panel alarm` bits, …) are all imported as controller tags so that a future HMI can be re-attached.

## 6. Field I/O aliasing (cannot be completed without the target hardware)

The target controller model, I/O chassis, module catalogue numbers and slot addresses were not supplied, so no production I/O tree was invented. The project imports on an **Emulator** processor with only the `Local` module, exactly like the supplied v17 reference example. Field I/O is represented by the named controller tags below and must be aliased by the integrator.

| GE address | Source tag | Direction | Alias to |
|---|---|---|---|
| `%I00001` | `ZSH_6401_001` | input | `Local:<slot>:I.Data.1` / `Local:<slot>:O.Data.1` per the final I/O schedule |
| `%I00002` | `ZSL_6401_001` | input | `Local:<slot>:I.Data.2` / `Local:<slot>:O.Data.2` per the final I/O schedule |
| `%I00003` | `FS_7503_001` | input | `Local:<slot>:I.Data.3` / `Local:<slot>:O.Data.3` per the final I/O schedule |
| `%I00004` | `LS_7503_001` | input | `Local:<slot>:I.Data.4` / `Local:<slot>:O.Data.4` per the final I/O schedule |
| `%I00005` | `LS_7503_002` | input | `Local:<slot>:I.Data.5` / `Local:<slot>:O.Data.5` per the final I/O schedule |
| `%I00006` | `Pump_A_PulsIn` | input | `Local:<slot>:I.Data.6` / `Local:<slot>:O.Data.6` per the final I/O schedule |
| `%I00007` | `Pump_B_Start_PulsIn` | input | `Local:<slot>:I.Data.7` / `Local:<slot>:O.Data.7` per the final I/O schedule |
| `%I00008` | `SpareDI_08` | input | `Local:<slot>:I.Data.8` / `Local:<slot>:O.Data.8` per the final I/O schedule |
| `%I00009` | `Pump_B_Inhibited` | input | `Local:<slot>:I.Data.9` / `Local:<slot>:O.Data.9` per the final I/O schedule |
| `%I00010` | `ESDV_6401_001` | input | `Local:<slot>:I.Data.10` / `Local:<slot>:O.Data.10` per the final I/O schedule |
| `%I00011` | `SpareDI_11` | input | `Local:<slot>:I.Data.11` / `Local:<slot>:O.Data.11` per the final I/O schedule |
| `%I00012` | `INHIBIT_FOAM_REL` | input | `Local:<slot>:I.Data.12` / `Local:<slot>:O.Data.12` per the final I/O schedule |
| `%I00013` | `INHIBIT_ALL_OUTPUTS` | input | `Local:<slot>:I.Data.13` / `Local:<slot>:O.Data.13` per the final I/O schedule |
| `%I00014` | `SpareDI_14` | input | `Local:<slot>:I.Data.14` / `Local:<slot>:O.Data.14` per the final I/O schedule |
| `%I00015` | `SpareDI_15` | input | `Local:<slot>:I.Data.15` / `Local:<slot>:O.Data.15` per the final I/O schedule |
| `%I00016` | `SpareDI_16` | input | `Local:<slot>:I.Data.16` / `Local:<slot>:O.Data.16` per the final I/O schedule |
| `%I00017` | `SpareDI_17` | input | `Local:<slot>:I.Data.17` / `Local:<slot>:O.Data.17` per the final I/O schedule |
| `%I00018` | `SpareDI_18` | input | `Local:<slot>:I.Data.18` / `Local:<slot>:O.Data.18` per the final I/O schedule |
| `%I00019` | `SpareDI_19` | input | `Local:<slot>:I.Data.19` / `Local:<slot>:O.Data.19` per the final I/O schedule |
| `%I00020` | `SpareDI_20` | input | `Local:<slot>:I.Data.20` / `Local:<slot>:O.Data.20` per the final I/O schedule |
| `%I00021` | `SpareDI_21` | input | `Local:<slot>:I.Data.21` / `Local:<slot>:O.Data.21` per the final I/O schedule |
| `%I00022` | `SpareDI_22` | input | `Local:<slot>:I.Data.22` / `Local:<slot>:O.Data.22` per the final I/O schedule |
| `%I00023` | `SpareDI_23` | input | `Local:<slot>:I.Data.23` / `Local:<slot>:O.Data.23` per the final I/O schedule |
| `%I00024` | `SpareDI_24` | input | `Local:<slot>:I.Data.24` / `Local:<slot>:O.Data.24` per the final I/O schedule |
| `%I00025` | `SpareDI_25` | input | `Local:<slot>:I.Data.25` / `Local:<slot>:O.Data.25` per the final I/O schedule |
| `%I00026` | `SpareDI_26` | input | `Local:<slot>:I.Data.26` / `Local:<slot>:O.Data.26` per the final I/O schedule |
| `%I00027` | `SpareDI_27` | input | `Local:<slot>:I.Data.27` / `Local:<slot>:O.Data.27` per the final I/O schedule |
| `%I00028` | `SpareDI_28` | input | `Local:<slot>:I.Data.28` / `Local:<slot>:O.Data.28` per the final I/O schedule |
| `%I00029` | `SpareDI_29` | input | `Local:<slot>:I.Data.29` / `Local:<slot>:O.Data.29` per the final I/O schedule |
| `%I00030` | `SpareDI_30` | input | `Local:<slot>:I.Data.30` / `Local:<slot>:O.Data.30` per the final I/O schedule |
| `%I00031` | `SpareDI_31` | input | `Local:<slot>:I.Data.31` / `Local:<slot>:O.Data.31` per the final I/O schedule |
| `%I00032` | `SpareDI_32` | input | `Local:<slot>:I.Data.32` / `Local:<slot>:O.Data.32` per the final I/O schedule |
| `%AI00001` | `DG_7404_001` | input | `Local:<slot>:I.Data.1` / `Local:<slot>:O.Data.1` per the final I/O schedule |
| `%AI00002` | `DG_7404_002` | input | `Local:<slot>:I.Data.2` / `Local:<slot>:O.Data.2` per the final I/O schedule |
| `%AI00003` | `DG_7404_003` | input | `Local:<slot>:I.Data.3` / `Local:<slot>:O.Data.3` per the final I/O schedule |
| `%AI00004` | `DG_7404_004` | input | `Local:<slot>:I.Data.4` / `Local:<slot>:O.Data.4` per the final I/O schedule |
| `%AI00005` | `DG_7404_005` | input | `Local:<slot>:I.Data.5` / `Local:<slot>:O.Data.5` per the final I/O schedule |
| `%AI00006` | `DG_7404_006` | input | `Local:<slot>:I.Data.6` / `Local:<slot>:O.Data.6` per the final I/O schedule |
| `%AI00007` | `DG_7404_007` | input | `Local:<slot>:I.Data.7` / `Local:<slot>:O.Data.7` per the final I/O schedule |
| `%AI00008` | `DG_7404_008` | input | `Local:<slot>:I.Data.8` / `Local:<slot>:O.Data.8` per the final I/O schedule |
| `%AI00009` | `DG_7404_009` | input | `Local:<slot>:I.Data.9` / `Local:<slot>:O.Data.9` per the final I/O schedule |
| `%AI00010` | `DG_7404_010` | input | `Local:<slot>:I.Data.10` / `Local:<slot>:O.Data.10` per the final I/O schedule |
| `%AI00011` | `SpareAI_11` | input | `Local:<slot>:I.Data.11` / `Local:<slot>:O.Data.11` per the final I/O schedule |
| `%AI00012` | `DF_7404_001` | input | `Local:<slot>:I.Data.12` / `Local:<slot>:O.Data.12` per the final I/O schedule |
| `%AI00013` | `DF_7404_002` | input | `Local:<slot>:I.Data.13` / `Local:<slot>:O.Data.13` per the final I/O schedule |
| `%AI00014` | `DG_7404_011R` | input | `Local:<slot>:I.Data.14` / `Local:<slot>:O.Data.14` per the final I/O schedule |
| `%AI00015` | `SpareAI_15` | input | `Local:<slot>:I.Data.15` / `Local:<slot>:O.Data.15` per the final I/O schedule |
| `%AI00016` | `SpareAI_16` | input | `Local:<slot>:I.Data.16` / `Local:<slot>:O.Data.16` per the final I/O schedule |
| `%AI00017` | `PST_7002_001` | input | `Local:<slot>:I.Data.17` / `Local:<slot>:O.Data.17` per the final I/O schedule |
| `%AI00018` | `PST_6401_001` | input | `Local:<slot>:I.Data.18` / `Local:<slot>:O.Data.18` per the final I/O schedule |
| `%AI00019` | `PST_7503_001` | input | `Local:<slot>:I.Data.19` / `Local:<slot>:O.Data.19` per the final I/O schedule |
| `%AI00020` | `FR_7503_001_002` | input | `Local:<slot>:I.Data.20` / `Local:<slot>:O.Data.20` per the final I/O schedule |
| `%AI00021` | `SpareAI_21` | input | `Local:<slot>:I.Data.21` / `Local:<slot>:O.Data.21` per the final I/O schedule |
| `%AI00022` | `FR_7503_003` | input | `Local:<slot>:I.Data.22` / `Local:<slot>:O.Data.22` per the final I/O schedule |
| `%AI00023` | `SpareAI_23` | input | `Local:<slot>:I.Data.23` / `Local:<slot>:O.Data.23` per the final I/O schedule |
| `%AI00024` | `SpareAI_24` | input | `Local:<slot>:I.Data.24` / `Local:<slot>:O.Data.24` per the final I/O schedule |
| `%Q00001` | `EY_6401_001_002` | output | `Local:<slot>:I.Data.1` / `Local:<slot>:O.Data.1` per the final I/O schedule |
| `%Q00002` | `SA_7404_001_002` | output | `Local:<slot>:I.Data.2` / `Local:<slot>:O.Data.2` per the final I/O schedule |
| `%Q00003` | `P2100_P2200` | output | `Local:<slot>:I.Data.3` / `Local:<slot>:O.Data.3` per the final I/O schedule |
| `%Q00004` | `P3600_P3700` | output | `Local:<slot>:I.Data.4` / `Local:<slot>:O.Data.4` per the final I/O schedule |
| `%Q00005` | `PUMP_A` | output | `Local:<slot>:I.Data.5` / `Local:<slot>:O.Data.5` per the final I/O schedule |
| `%Q00006` | `PUMP_B_STOP` | output | `Local:<slot>:I.Data.6` / `Local:<slot>:O.Data.6` per the final I/O schedule |
| `%Q00007` | `PUMP_B_START` | output | `Local:<slot>:I.Data.7` / `Local:<slot>:O.Data.7` per the final I/O schedule |
| `%Q00008` | `PumpShutdown` | output | `Local:<slot>:I.Data.8` / `Local:<slot>:O.Data.8` per the final I/O schedule |
| `%Q00009` | `Pump_A_PulsOut` | output | `Local:<slot>:I.Data.9` / `Local:<slot>:O.Data.9` per the final I/O schedule |
| `%Q00010` | `Pump_B_Start_PulsOut` | output | `Local:<slot>:I.Data.10` / `Local:<slot>:O.Data.10` per the final I/O schedule |
| `%Q00011` | `SpareDO_11` | output | `Local:<slot>:I.Data.11` / `Local:<slot>:O.Data.11` per the final I/O schedule |
| `%Q00012` | `Tag_DO_12` | output | `Local:<slot>:I.Data.12` / `Local:<slot>:O.Data.12` per the final I/O schedule |
| `%Q00013` | `Tag_DO_13` | output | `Local:<slot>:I.Data.13` / `Local:<slot>:O.Data.13` per the final I/O schedule |
| `%Q00014` | `Tag_DO_14` | output | `Local:<slot>:I.Data.14` / `Local:<slot>:O.Data.14` per the final I/O schedule |
| `%Q00015` | `Tag_DO_15` | output | `Local:<slot>:I.Data.15` / `Local:<slot>:O.Data.15` per the final I/O schedule |
| `%Q00016` | `PLC_Fault` | output | `Local:<slot>:I.Data.16` / `Local:<slot>:O.Data.16` per the final I/O schedule |
| `%Q00017` | `SpareDO_17` | output | `Local:<slot>:I.Data.17` / `Local:<slot>:O.Data.17` per the final I/O schedule |
| `%Q00018` | `SpareDO_18` | output | `Local:<slot>:I.Data.18` / `Local:<slot>:O.Data.18` per the final I/O schedule |
| `%Q00019` | `SpareDO_19` | output | `Local:<slot>:I.Data.19` / `Local:<slot>:O.Data.19` per the final I/O schedule |
| `%Q00020` | `SpareDO_20` | output | `Local:<slot>:I.Data.20` / `Local:<slot>:O.Data.20` per the final I/O schedule |
| `%Q00021` | `SpareDO_21` | output | `Local:<slot>:I.Data.21` / `Local:<slot>:O.Data.21` per the final I/O schedule |
| `%Q00022` | `SpareDO_22` | output | `Local:<slot>:I.Data.22` / `Local:<slot>:O.Data.22` per the final I/O schedule |
| `%Q00023` | `SpareDO_23` | output | `Local:<slot>:I.Data.23` / `Local:<slot>:O.Data.23` per the final I/O schedule |
| `%Q00024` | `SpareDO_24` | output | `Local:<slot>:I.Data.24` / `Local:<slot>:O.Data.24` per the final I/O schedule |
| `%Q00025` | `SpareDO_25` | output | `Local:<slot>:I.Data.25` / `Local:<slot>:O.Data.25` per the final I/O schedule |
| `%Q00026` | `SpareDO_26` | output | `Local:<slot>:I.Data.26` / `Local:<slot>:O.Data.26` per the final I/O schedule |
| `%Q00027` | `SpareDO_27` | output | `Local:<slot>:I.Data.27` / `Local:<slot>:O.Data.27` per the final I/O schedule |
| `%Q00028` | `SpareDO_28` | output | `Local:<slot>:I.Data.28` / `Local:<slot>:O.Data.28` per the final I/O schedule |
| `%Q00029` | `SpareDO_29` | output | `Local:<slot>:I.Data.29` / `Local:<slot>:O.Data.29` per the final I/O schedule |
| `%Q00030` | `SpareDO_30` | output | `Local:<slot>:I.Data.30` / `Local:<slot>:O.Data.30` per the final I/O schedule |
| `%Q00031` | `SpareDO_31` | output | `Local:<slot>:I.Data.31` / `Local:<slot>:O.Data.31` per the final I/O schedule |
| `%Q00032` | `SpareDO_32` | output | `Local:<slot>:I.Data.32` / `Local:<slot>:O.Data.32` per the final I/O schedule |

The source program documented the field assignments as: analogue input card IC200ALG262 in slot 3 (`%AI0001…%AI0008` = card 1, `%AI0009…%AI0016` = card 2, `%AI0017…%AI0024` = card 3), discrete input card IC200MDL650 (`%I0001…%I0032`) and discrete output card IC200MDL940 (`%Q0001…%Q0032`). Those catalogue numbers are recorded for the integrator but are **not** instantiated in the L5X.

## 7. Discrepancies, ambiguities and the resolution used

### 7.1 Vote_1 — the printed mesh (read as a wrapped OR chain)

`Vote_1` rungs 2, 4, 6/7 and 9/10 are printed as a **mesh**. Two readings are geometrically self-contradictory in the printout because the Proficy renderer draws the branch-bracket wires on the same coordinates as the rung spine. The conversion adopts the **plain OR** reading and the evidence for it is:

1. The mesh is a two-dimensional **wrap** of one long OR chain, the same way text wraps. Ten contacts do not fit across the 700-pt drawing width, so the designer wrapped them into three columns joined by bracket wires; 56 inhibit contacts need nine columns. This explains every measured feature — continuous spine, buses reaching the spine, the closing bottom row, and the absence of any enclosing box primitive in the vector data — without contradiction, whereas the AND-of-columns reading short-circuits under the same geometry.
2. The same drawing convention must mean the same thing in all four nets, and an AND of nine groups for `Voting_All_Inhibits` would require an inhibit in *every* group, which is both functionally absurd and contradicts the routine heading *"Voting of all Inhibits from all inputs"*.
3. For an active-low shutdown chain the OR reading is also the fail-safe direction: it trips more readily, never less.

Printed rungs 6+7 are **one net** and so are 9+10: rung 6 and rung 9 carry no coil — their trailing symbol is a circle containing `+` (a Horizontal Connector) and the page cross-reference has no `COIL` entry for them, while the matching `+` sits between the contact plates at the start of rungs 7 and 10. They are therefore emitted as one Logix rung each. 159 transcribed contact lines minus the 2 Horizontal Connectors gives the **157 real contacts**, all present:

```
Voting_DG_7404_ALLI  = OR of the 10  <det>_ALLI          contacts   (%M00425..%M00434)
Voting_DG_7404_ALHI  = OR of the 10  <det>_ALHI          contacts   (%M00377..%M00386)
Voting_All_Inhibits  = OR of the 56  _INH                contacts   (rungs 6+7)
Voting_All_Faults    = OR of the 81  _OC/_SC/_FLT1       contacts   (rungs 9+10)
```
**This is the item that most needs verification against the original Proficy project before deployment**, because the alternative (one alarm per detector column, AND-ed across columns) changes when the gas trip operates. The two readings differ *only* by bracket structure — the converted rung is a single bracket holding every contact of the net, so switching to AND-of-columns means splitting that bracket into one per column and concatenating them: one rung, no tag changes. Every mesh rung carries a `VERIFICATION ITEM` flag in its Logix rung comment.

### 7.2 Shutdow — the active-low shutdown outputs

The source version history in `_MAIN` records *"Output %Q0008 (PumpShutdown) inverted"* (12 June 2003), and the printed coils for `%Q00003`, `%Q00004` and `%Q00008` carry the negated-coil slash; the source cross-reference confirms `NCCOIL` for exactly those three rungs. A GE negated coil negates the **whole rung continuity**, i.e.

```
%Q00008 = NOT( PumpShutdown_INT AND NOT INHIBIT_ALL_OUTPUTS_ALI )
        = NOT PumpShutdown_INT  OR  INHIBIT_ALL_OUTPUTS_ALI
```
so the conversion is `[XIO(PumpShutdown_INT),XIC(INHIBIT_ALL_OUTPUTS_ALI)]OTE(PumpShutdown);` (`%Q00003` and `%Q00004` likewise). This preserves the inversion — the field bit is de-energised (tripped) when the internal C&E bit is set — **and** preserves the source inhibit behaviour: `INHIBIT_ALL_OUTPUTS_ALI` forces all four shutdown outputs to their non-tripped state. Writing the naive `XIO(internal)XIO(inhibit)OTE(out)` would instead make the inhibit itself trip `%Q00003`, `%Q00004` and `%Q00008`, which contradicts both rung 3 of the same routine and the C&E chart. `%Q00001` (`EY_6401_001_002`, rung 3) is a plain, non-inverted coil and is left as such.

### 7.3 Ageing documents that conflict with the final rungs

| Conflict | Older document | Final source rung / conversion | Resolution |
|---|---|---|---|
| Pump-B retry timers | `P20890-Functional & program description` and the 23 April 2003 revision describe 30 s for **all three** pump-B retries | The 12 June 2003 change (recorded in `_MAIN`) changed the 2nd and 3rd retry from 30 s to 60 s; the final rungs use 30 s / 60 s / 60 s | Source rungs retained (30/60/60). Documented here, not "corrected". |
| `%AI0017` low-alarm setpoint | Earlier list 60 %LEL | 28 June 2003 change set it to 50 | Final constant used (50). |
| `%AI0019` short-circuit limit | Earlier list 98 | 28 June 2003 change set it to 102 | Final constant used (102). |
| Line gas detector address | `7404-DG011R` on `%AI0011` | 28/29 June 2003 moved to `%AI0014`, REAL changed to INT and `MOVE_REAL` replaced by `INT_TO_REAL` | Final `%AI0014` INT path used. |
| `INHIBIT_ALL_OUTPUTS` and sound | Earlier description: inhibit silences the pump house sound | 28 June 2003: changed so that `INHIBIT_ALL_OUTPUTS` does **not** trigger the pump-house sound | Final rungs retained; the `Sound` routine carries the final behaviour. |
| `6401-ESDV-001` in the C&E | D4 chart does not list the ESD fuel-gas button against `%Q00008`/`%Q00003`/`%Q00004` | 12 June 2003 change added `6401-ESDV-001` to trip `PumpShutdown` `%Q00008`, Oil Booster `%Q00003` and Water Booster `%Q00004`; the final `CE_LOG` rungs include it | Final rungs retained. |
| `6401-ESDV-001` HMI alarm | panel alarmed on "Off" | 28 June 2003 changed to alarm on "On" | HMI behaviour only; not reproduced (no panel graphics), the tag is imported. |

### 7.4 Comment-only source rungs

The source contains rungs that are nothing but a comment. They are not converted as logic but their text is retained in the routine `notes` of the machine-readable conversion and summarised here so that no source content is lost: routine history blocks in `_MAIN` and `CE_LOG`, the pseudo-code boxes in `AI_1/AI_2/AI_3` (`Move Analogue input value to VALUE_IN`, `Call CALCVAL`, `_VAL = VALUE_IN`, `Call AI_ALARM`, the `_ALL/_ALLI/_ALH/_ALHI/_SC/_OC` pseudo-code), the per-channel notes in `DI_1` (`%I000x. Generates [no] latched alarms.`), and the page notes in `Protect`, `FLT_1`, `Sound`, `CE_LOG`, `Vote_1` and `Indicat`.

## 8. Items that cannot be completed without the target hardware or a Proficy licence

1. **I/O checkout / aliasing** — no module catalogue numbers or slot addresses were supplied; see §6. All field I/O is present as named tags and must be aliased, then point-to-point checked against `DOC\Terminal block connections.pdf`.
2. **Import verification in RSLogix 5000 v17 — attempted, blocked by licensing.** RSLogix 5000 v17 is in fact installed on the conversion machine (`C:\Program Files (x86)\Rockwell Software\RSLogix 5000\ENU\v17\Bin\RS5000.Exe`, COM class `RSLogix5000.Application.17.00` present), so the L5X was launched into it. The application aborts at start-up with a **"Product Activation Failed"** dialog before any project can be opened (screenshot: `work\rslogix_activation.png`), and no FactoryTalk activation is available here. `L5KXLATE.EXE` likewise only starts a GUI. The import/verify step therefore **could not be performed** and no claim is made that the file imports without error. It was validated as well-formed XML, against the structure of the supplied known-good `DOL_Starter_Example_V17.L5X`, and by a static checker that confirms every referenced tag exists with a compatible type and that every instruction is in the v17 set. **Run the import (Test Matrix case 12.1) on an activated v17 install and resolve every import/verify error before use.**
3. **Retentive on-delay nuance** — see §2.1; the `ONDTR_TENTHS` instances are reset only by their source reset conditions, which reproduces the source behaviour for these particular rungs (each `ONDTR` is in a rung whose controlling contact stays true for the whole timing window), but the `TON` used is not an accumulating instruction. Confirm at commissioning.
4. **16-bit arithmetic** — the source is a 16-bit controller. `INT`/`WORD` registers became `DINT`, which removes 16-bit wraparound. On the `CalcVaX` chains the intermediate products (125 000, 187 000, 625 000) already exceed 16 bits and the source itself used `MUL_DINT`/`DIV_DINT` there, so the final results are identical; nevertheless the analogue scaling must be re-proven with a calibrator on every channel (see the test matrix).
5. **`%S` clock-bit phase** — `T_SEC_PULSE` / `T_MIN_PULSE` reproduce the GE clock contacts' duty cycle but not their absolute phase relative to the PLC clock. The source uses them only for counting/debounce purposes, so the phase does not matter functionally; it is called out for completeness.
6. **Panel / HMI objects** — QuickPanel graphics, bit-alarm grid entries and panel pilot lights are not reproduced (as instructed). The PLC tags behind them are imported.
7. **Ambiguous mesh rungs in Vote_1** — see §7.1.

## 9. Legacy behaviour deliberately preserved (do not "fix" without a change request)

* `%Q00003`, `%Q00004`, `%Q00008` are **active-low** (tripped = 0).
* The deluge pumps are started by a **2 s pulse** and stopped by a **2 s pulse**; the standby pump B is retried after 30 s and then twice more after 60 s before the *"Deluge failed to release"* alarm.
* The pump outputs are **pulse-tested every 30 s** and an open circuit is declared if the pulsed feedback is not seen within 28 s (`T00013`/`T00014`).
* The Cause & Effect logic and the sound routine are **not executed during the first two minutes** after power-up (`System_C_E_Delay`), so detectors can stabilise.
* Alarms are latched until `System_Reset`; `_ALI`/`_ALHI` additionally require the input not to be inhibited; the deluge-released feedback is *not* latched.
* `INHIBIT_ALL_OUTPUTS` forces the shutdown outputs to the non-tripped state but does **not** sound the pump-house alarm (28 June 2003 change).

## 10. Validation performed

| Check | Result |
|---|---|
| All 24 source routines present as Logix routines | yes |
| Converted logic rungs | 372 |
| Controller tags emitted | 781 |
| Every tag referenced by a rung exists in the controller scope or is declared as a helper (`tags_extra`) | yes (static checker) |
| Every instruction is in the RSLogix 5000 v17 ladder instruction set | yes (static checker, whitelist) |
| Every rung is a single well-formed RLL statement ending in `;` with balanced brackets/parentheses | yes |
| Every rung ends in an output/function instruction | yes |
| XML well-formed and structured like the supplied v17 reference export | yes |
| Imported / verified in RSLogix 5000 v17 | **not performed — RSLogix 5000 v17 is installed but aborts with "Product Activation Failed" (no FactoryTalk activation available)** |
| Walk-through of the safety-critical sequences (gas/fire shutdown, output inhibit, ESDV, deluge pump start/retry/stop, output polarity) | done against the `P20890_Angola_Test_Matrix.md` cases; two items flagged for independent review (§7.1, §7.2) |

---
*Generated by the conversion toolchain in `work\`: `lad.py` (Proficy printout geometry parser), `transcribe.py`, `xref.py` (cross-reference extractor), `validate.py`, `assemble.py` and `l5x.py`.*

## 11. Delivery status

**All 24 source routines are converted** (`373` Logix rungs, `781` controller tags). No routine is a placeholder.

| Routine | Rungs | Routine | Rungs | Routine | Rungs |
|---|---|---|---|---|---|
| `MainRoutine` | 4 | `Ai_AL_1` | 4 | `CE_LOG` | 24 |
| `Init` | 3 | `Ai_AL_2` | 4 | `Sound` | 45 |
| `Input` | 6 | `Ai_AL_3` | 7 | `Output` | 5 |
| `DI_1` | 26 | `CalcVa1` | 4 | `Shutdow` | 7 |
| `DI_2` | 1 | `CalcVa2` | 4 | `Protect` | 17 |
| `AI_1` | 65 | `CalcVa3` | 4 | `Indicat` | 3 |
| `AI_2` | 63 | `Vote_1` | 4 | `Loc_Al` | 3 |
| `AI_3` | 48 | `Logic` | 20 | `FLT_1` | 2 |

### 11.1 RSLogix 5000 v17 import — attempted, blocked by licensing

RSLogix 5000 v17 is installed on this machine (`...\RSLogix 5000\ENU\v17\Bin\RS5000.Exe`, automation class `RSLogix5000.Application.17.00` registered), so the file was taken to the real software. `RS5000.Exe` stops in a modal **"Product Activation Failed"** dialog before any project opens — there is no FactoryTalk activation for v17 on this host (`work\rslogix_activation.png`) — and `L5KXLATE.EXE` only opens a GUI. The import/verify is therefore **still unperformed** and remains the first item of the test matrix (12.1). Everything checkable without the vendor software was checked: XML well-formedness, structure against `DOL_Starter_Example_V17.L5X`, zero unresolved tag references, the v17 instruction whitelist, one output per rung, timer/member typing, and per-rung contact audits against the printed source.

### 11.2 `Sound` — three corrections against the original brief

1. The routine has **38** `POSCOIL` rungs (printed 4-34 and 40-46), not 12.
2. `Sound` contains **no `%Q` coil**. Every coil is an internal `%M` bit (38 `POSCOIL`, 3 `SETCOIL`, 3 `RESETCOIL`, 1 `OTE` on `System_Mute`), so the field bell/buzzer is driven outside this block and no field-output polarity is at stake in it.
3. "50 printed rungs" is the highest rung *number*; there are 43 printed logic rungs plus 7 comment-only rungs.

Also noted: printed rung 49 carries **two contacts and three reset coils** and became three Logix rungs (one output per rung), and rungs 40-46 read CPU diagnostics (`%SA`/`%SB`/`%SC`) that have no Logix equivalent — they are declared as permanently-false `SYS_*` placeholders and must be re-sourced from controller fault bits at commissioning. Neither changes the alarm path: the pump-house buzzer and the panel bell are still driven from the three internal latches.

### 11.3 `AI_3` — six channels, and a preserved source defect

The printed header of `AI_3` announces `%AI0017..%AI0024`, but the routine only contains six channels (`%AI0017..%AI0022`); `%AI0023`/`%AI0024` appear nowhere in the routine or in the project cross-reference. The conversion implements the six that are actually drawn:

| ch | input | setpoint rung | scaling / alarm | latch rungs |
|---|---|---|---|---|
| 1 | `PST_7002_001` `%AI0017` | 6 (50/400/-10/98) | `CalcVa1` + `Ai_AL_2` | 9-15 |
| 2 | `PST_6401_001` `%AI0018` | 17 (400/100/-17/147) | `CalcVa2` + `Ai_AL_1` | 19-26 |
| 3 | `PST_7503_001` `%AI0019` | 28 (400/50/-10/102) | `CalcVa1` + `Ai_AL_1` | 30-37 |
| 4 | `FR_7503_001_002` `%AI0020` | 39 (400/30/-10/100) | `CalcVa1` + `Ai_AL_1` | 41-46 (no `_ALL`/`_ALLI`) |
| 5 | `SpareAI_21` `%AI0021` | inherited | `CalcVa1` + `Ai_AL_1` | 48-55 |
| 6 | `FR_7503_003` `%AI0022` | inherited | `CalcVa1` + `Ai_AL_1` | 57-62 (no `_ALL`/`_ALLI`) |

Two channels load no setpoints of their own and therefore inherit the last values loaded by the preceding channel (the setpoint registers `%R00106/108/110/112` are shared). That is the printed behaviour and is preserved.

**Preserved source defect (needs a decision, not a silent fix).** Printed rung 60 drives `FR_7503_003_FRUP` `%M00590` from `SpareAI_21_ALHI` `%M00397` instead of `FR_7503_003_ALHI` `%M00398`. Both the drawing and the printed cross-reference agree (`SpareAI_21_ALHI: NOCON 00053, 00060`; `FR_7503_003_ALHI: COIL 00059 only`), so this is a copy/paste defect in the 2003 source, not a conversion error. It is transcribed exactly as printed and carries a flag in its rung comment. The first-up bit is a reporting bit only - it does not gate any shutdown output - but it must be raised with the plant as a known source anomaly rather than corrected unilaterally.

Two further spots where the source does not latch: printed rungs 31 and 33 (`PST_7503_001_ALL` and `PST_7503_001_ALH`) are drawn without a seal-in contact, and the cross-reference confirms it, so those two bits are level alarms with reset override rather than latched alarms. Preserved as drawn.

## 12. RSLogix 5000 v17 import and verify — PERFORMED (supersedes §11.1)

The earlier note in §11.1 said the import could not be run because RSLogix 5000 stopped at a **"Product Activation Failed"** dialog. That conclusion was wrong: the dialog is informational. It says *"It is currently operating in a grace period"* (5 days 23 h remaining on this host) and continues normally once **OK** is acknowledged. The import was therefore run for real.

### 12.1 What was done

| Step | Result |
|---|---|
| Start `RSLogix 5000\ENU\v17\Bin\RS5000.Exe`, acknowledge the activation dialog | application runs in grace period |
| `File > Open` (Ctrl+O) the delivered `P20890_Angola_RSLogix5000_V17.L5X` | accepted; the software opened the **`Save Imported Project As`** dialog (revision selector showing 17.1), i.e. the L5X parsed as a valid importable export |
| Import to `work\import\P20890_Angola.ACD` | **no import error, no warning dialog** — the project opened as `RSLogix 5000 - P20890_Angola [Emulator]` |
| Controller Organizer inspection | `Controller P20890_Angola` > `Tasks` > `MainTask` > `FandG_Angola` with **all 24 routines** listed: `MainRoutine`, `AI_1`, `AI_2`, `AI_3`, `Ai_AL_1`, `Ai_AL_2`, `Ai_AL_3`, `CalcVa1`, `CalcVa2`, `CalcVa3`, `CE_LOG`, `DI_1`, `DI_2`, `FLT_1`, `Indicat`, `Init`, `Input`, `Loc_Al`, `Logic`, `Output`, `Protect`, `Shutdow`, `Sound`, `Vote_1` |
| `Logic > Verify > Controller` | completed with **no error dialog and no results to resolve** |
| Open `MainRoutine` in the ladder editor | **ladder renders correctly**: rung 0 `XIC(S:FS)` and rung 1 `XIO(S:FS)` display as real contacts, and the rung comments (including the `[Source: _MAIN rung n (GE) …]` provenance line) display intact |
| `Program Tags` for `FandG_Angola` | empty, as intended — every tag is controller-scoped |

### 12.2 Evidence files (in `work\`)

| File | Shows |
|---|---|
| `rslogix_imported.png` | project open after import: `P20890_Angola [Emulator]`, Controller Organizer populated |
| `rslogix_tags.png` | program expanded with the full routine list |
| `rslogix_ladder2.png` | `MainRoutine` open in the ladder editor, rungs 0 and 1 rendered with `S:FS` contacts and source comments |
| `rslogix_verify_result.png` | state after `Logic > Verify > Controller` — no error dialog |
| `import\P20890_Angola.ACD` | the `.ACD` produced by the import, if retained |

### 12.3 What this does and does not prove

It **proves** what the static checks could not: the L5X is accepted by RSLogix 5000 v17 itself, every controller tag, data type, timer/counter, `JSR` target and ladder statement parses and compiles, and the program opens as editable ladder with its comments and cross-references intact. It also closes test-matrix cases 12.1-12.4.

It does **not** prove functional correctness. The remaining gates are unchanged and still require a human:

1. `Vote_1` mesh reading (§7.1) and the active-low shutdown outputs (§7.2) — engineering / process-safety sign-off.
2. I/O aliasing and point-to-point checkout against `DOC\Terminal block connections.pdf` (§6).
3. Execution of the test matrix on the Emulator or the real controller (`P20890_Angola_Test_Matrix.md`), including the C&E walk-through and the deluge pump timing cases.
4. The `ONDTR_TENTHS` retentive-timer nuance (§2.1) and the analogue scaling re-proof (§8 items 3-4).
