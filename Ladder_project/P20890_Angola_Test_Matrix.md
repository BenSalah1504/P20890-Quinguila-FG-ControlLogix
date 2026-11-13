# P20890 Angola — conversion test matrix

Fire & Gas / ESD panel **P20890 (Quinguila field pump house)** — GE VersaMax → RSLogix 5000 v17.

> **Status of these test cases.** They are the *factory acceptance / site acceptance* script for the
> converted program. None of them has been executed: no controller, no simulator and no v17 licence
> were available in the conversion environment. They are written straight off the source rungs and the
> converted ladder so that a commissioning engineer can run them one by one. A pass in this matrix is a
> precondition for, and not a substitute for, a formal F&G functional test and a third-party review.

## 0. How to run this matrix

* Load `P20890_Angola_RSLogix5000_V17.L5X` into an Emulator or the real controller, alias the field I/O
  per §6 of the traceability report, and put the program in Run.
* Unless stated otherwise, start every case from the **same reference state**: system powered, no
  alarms, `INHIBIT_ALL_OUTPUTS` off, `INHIBIT_FOAM` off, all `*_INH` bits off, `System_Reset` not pressed,
  and **more than two minutes** since the first scan (so the Cause & Effect delay has expired).
* "0 → 1" means the tag turns from 0 to 1 as the stimulus is applied, and is expected to be seen **on the
  very next scan** unless a delay is quoted.
* Tag names are the controller tags in the L5X. GE addresses are given in brackets for cross-checking
  against `var.xml` and the C&E chart `DE-GN-FG-SAF-74-1001`.

## 1. Startup, first scan and the Cause & Effect delay

| # | Stimulus | Expected result | Evidence in the ladder |
|---|---|---|---|
| 1.1 | Power up / cold start, watch the first scan | `Init` executes exactly once; all `Pump_Timer1..13`, `System_C_E_Delay`, `System_HMI_Reset_Timer` registers read 0; `Tag_DO_15_INT` `%M00239` and `SA_7404_001_002_INT` `%M00226` are reset (`OTU`) | `MainRoutine` rung 0 `XIC(S:FS)JSR(Init)`; `Init` rungs 2, 4, 6 |
| 1.2 | Second and subsequent scans | `Init` no longer runs; `Input`, `Logic`, `Output` run every scan | `MainRoutine` rungs 1–3 use `XIO(S:FS)` |
| 1.3 | From power-up, measure the time before `CE_LOG` and `Sound` start executing | **120 s**. `T00002` `%T00002` goes 1 at 120 s and only then does `JSR(CE_LOG)` run; `System_Reset_Startup` `%M00702` pulses high for ~2 s just before that | `Logic` rung 11 (`TON(TMR_C_E_Delay,120000,0)`), rung 13 (`LEQ(System_Reset_HelpRegister,20)`), rung 15 |
| 1.4 | During the 120 s window, drive a gas alarm | No cause-and-effect output changes; the panel may still show the input alarm | `CE_LOG` is not called |
| 1.5 | Press and hold `System_Reset_HMI` `%M00703` (HMI button) | `System_Reset` `%M00700` goes 1; `System_Reset_HMI_Help` `%M00704` gives a single-scan pulse on the rising edge; `%M00703` is driven back to 0 after 5 s (`TMR_HMI_Reset`) even if the button is held | `Logic` rungs 3, 4, 5 |
| 1.6 | Press the physical start-up reset | `System_Reset_Startup` `%M00702` also drives `System_Reset` | `Logic` rung 3 (parallel group) |
| 1.7 | Verify the clock bits | `T_SEC_PULSE` is 0.5 s on / 0.5 s off; `T_MIN_PULSE` is 30 s on / 30 s off | `Logic` rungs 101–104 |

## 2. Digital inputs (`DI_1`), inhibit and latch

| # | Stimulus | Expected result |
|---|---|---|
| 2.1 | `ZSH_6401_001` `%I00001` 0 → 1 | `ZSH_6401_001_AL` `%M00001` 1; `ZSH_6401_001_ALI` `%M00033` 1 |
| 2.2 | Input returns to 0 | `_AL` stays 1 (latched by the seal-in branch), `_ALI` stays 1 |
| 2.3 | `System_Reset` `%M00700` pulsed while the input is normal | `_AL` and `_ALI` return to 0 |
| 2.4 | `System_Reset` pulsed **while the input is still active** | `_AL` re-seals immediately (source behaviour: reset in series with the OR of input and seal-in) — record the observed behaviour |
| 2.5 | `LS_7503_001` `%I00004` channel: set the input, then set `LS_7503_001_INH` `%M00100` | `_AL` stays 1, `_ALI` `%M00034` goes 0 (inhibit blocks the C&E bit but not the VDU alarm bit) |
| 2.6 | `ESDV_6401_001` `%I00010` (fail-safe NC field contact): open the field circuit | `ESDV_6401_001` reads 0 → `ESDV_6401_001_AL` `%M00010` 1 and the ESD button alarm appears |
| 2.7 | Repeat 2.1–2.4 for every one of the 14 wired channels | Same pattern; channels without an `_INH` symbol have no inhibit term |
| 2.8 | `DI_2` | No logic by design (empty source block). Confirm no alarm is generated from it |

## 3. Analogue inputs — scaling (`CalcVa1/2/3`)

Feed the input with a calibrated 4–20 mA source (0–32000 counts) and read the engineering value.

| # | Channel / routine | Input | Expected engineering value |
|---|---|---|---|
| 3.1 | `CalcVa1` (0–100 %LEL) e.g. `DG_7404_001` `%AI0001` | 4 mA (0) | −25.0 (`AI_ValueIn` `%R00100`) |
| 3.2 | `CalcVa1` | 12 mA (16000) | 37.5 |
| 3.3 | `CalcVa1` | 20 mA (32000) | 100.0 |
| 3.4 | `CalcVa2` (0–150 psi) e.g. `PST_6401_001` | 4 / 12 / 20 mA | −37.0 / 56.0 / 150.0 |
| 3.5 | `CalcVa3` (REAL path) e.g. `PST_7002_001` | 4 / 12 / 20 mA | −1.25 / 1.875 / 5.00 (`AI_ValueIn_Real` `%R00122`) |
| 3.6 | Intermediate values | — | `AI_TempVal` `%R00120` (`AI_TempVal_Real` `%R00124`) must pass through the same four steps: /32 → ×125 (×187, ×625) → /1000 (/100000) → move → −25 (−37, −1.25). Confirm the intermediate is *not* rounded or folded: at 12 mA `CalcVa1` must show 62500 in the temp register, not 62 or 63 |
| 3.7 | Any channel | Inject 0 mA (open circuit) | value reads the low rail and `_OC` (`AI_LoFault`) must assert — see 4.5 |
| 3.8 | Any channel | Force > 20 mA | value reads the high rail and `_SC` (`AI_HiFault`) must assert — see 4.6 |

## 4. Analogue alarms, faults, inhibit and latch (`Ai_AL_1/2/3` + `AI_1/2/3`)

Setpoints are loaded once per AI block (e.g. `AI_1` rung 4: `AI_LoAlarmSetpoint` `%R00106` = 20,
`AI_HiAlarmSetpoint` `%R00108` = 30, `AI_LoFaultSetpoint` `%R00110` = −10, `AI_HiFaultSetpoint` `%R00112` = 98).
`AI_2`/`AI_3` load their own per-channel constants — verify each channel's four values against the printed
operand before testing.

| # | Stimulus | Expected result |
|---|---|---|
| 4.1 | Value crosses the lo-alarm setpoint (going down for `Ai_AL_1/2`, up for the `Ai_AL_2` lo channel) | `AI_LoAlarm` `%M00600` asserts; the channel's `<CH>_ALL` `%M00401…` latches; `<CH>_ALLI` `%M00425…` follows unless `<CH>_INH` `%M00449…` is set |
| 4.2 | Value crosses the hi-alarm setpoint | `AI_HiAlarm` `%M00601`; `<CH>_ALH` `%M00353…` latches; `<CH>_ALHI` `%M00377…` follows unless inhibited |
| 4.3 | Alarm present, then `System_Reset` `%M00700` while the value is back in range | `_ALL`, `_ALH`, `_FRUP` clear |
| 4.4 | Alarm present, `System_Reset` pressed while the value is still over the limit | the latch re-seals (alarm stays) |
| 4.5 | Open circuit (0 mA) | `AI_LoFault` `%M00602` → `<CH>_OC` `%M00473…` = 1 |
| 4.6 | Short circuit (>20 mA) | `AI_HiFault` `%M00604` → `<CH>_SC` `%M00497…` = 1 |
| 4.7 | `<CH>_INH` set with an alarm standing | `<CH>_ALLI` and `<CH>_ALHI` forced to 0; `_ALL`/`_ALH` (the VDU bits) unaffected |
| 4.8 | `System_AnyActions` `%M00705` = 1 with `<CH>_ALHI` = 1 | `<CH>_FRUP` `%M00569…` latches (first-up) until reset |
| 4.9 | Repeat 4.1–4.8 on a REAL channel (`AI_3`) | same, on `…_Real` tags; `7404-DG-011R` additionally has `DG_7404_011R_FLT1` `%M00501` (optical fault) |
| 4.10 | Repeat for every analogue channel | 24 channels in total (`%AI0001…%AI0024`) |

## 5. Voting (`Vote_1`)

> These cases rest on the interpretation documented in §7.1 of the traceability report: groups of
> 4 / 3 / 3 detectors in **series parallel groups**. Re-verify against the Proficy source first.

| # | Stimulus | Expected (`Voting_DG_7404_ALLI` `%M00605`) | Expected (`Voting_DG_7404_ALHI` `%M00606`) |
|---|---|---|---|
| 5.1 | Only `DG_7404_001_ALLI` (group 1) | 0 | 0 (same for `_ALHI`) |
| 5.2 | `DG_7404_001_ALLI` + `DG_7404_005_ALLI` (groups 1+2) | 0 | 0 |
| 5.3 | One detector from **each** of the three groups | **1** | 1 on the `_ALHI` equivalents |
| 5.4 | All 10 detectors | 1 | 1 |
| 5.5 | `Voting_All_Inhibits` `%M00607` | 1 if any `_INH` is set (see the rungs 6/7 field) | — |
| 5.6 | `Voting_All_Faults` `%M00608` | 1 if any `_OC`, `_SC` or `DG_7404_011R_FLT1` is set | — |

## 6. Cause and effect — every output (`CE_LOG`, `Shutdow`, `Protect`, `Indicat`, `Loc_Al`)

Drive each initiating condition and confirm the outputs listed in the C&E chart.
`X` in the chart = the output trips.

| # | Cause (initiating device) | Outputs that must change | Tag |
|---|---|---|---|
| 6.1 | `Voting_DG_7404_ALLI` (gas low, voted) + not inhibited | fuel-gas ESD valve closes | `EY_6401_001_002` `%Q00001` |
| 6.2 | `DG_7404_011R_ALHI` (open-path gas, hi) | oil booster pumps trip | `P2100_P2200` `%Q00003` → 0 |
| 6.3 | `FR_7503_003_ALHI` (foam release from panel) | water booster pumps trip | `P3600_P3700` `%Q00004` → 0 |
| 6.4 | `DF_7404_001_ALHI` / `DF_7404_002_ALHI` (flame detectors) | F&G pump shutdown | `PumpShutdown` `%Q00008` → 0 |
| 6.5 | `PST_6401_001_ALHI` (fuel-gas pressure high-high) | ESDV closes + all pump groups | as 6.1–6.4 |
| 6.6 | `ZSL_6401_001_ALI` (ESD valve closed) | indication only | `Tag_DO_13` `%Q00013` |
| 6.7 | `ESDV_6401_001_ALI` (ESD button) | `PumpShutdown`, `P2100_P2200`, `P3600_P3700` trip (12 June 2003 change) | `%Q00008`, `%Q00003`, `%Q00004` → 0 |
| 6.8 | `FR_7503_001_002_ALHI` (foam release from field) | deluge release sequence starts (pump A) | `PUMP_A` `%Q00005` |
| 6.9 | `PST_7503_001_ALHI` (deluge line pressure) | deluge-released indication latches; pump B retries stop | `Protect`/`CE_LOG` |
| 6.10 | `FS_7503_001_ALI` (stop-foam button) | foam/deluge stop pulse | `PUMP_B_STOP` `%Q00006` |
| 6.11 | `LS_7503_001` / `LS_7503_002` (tank levels) | C&E per chart | indication |
| 6.12 | `Pump_B_Inhibited` | standby inhibited alarm; pump B start suppressed | `CE_LOG` |
| 6.13 | `PLC_Fault_INT` `%M00240` | `PLC_Fault` `%Q00016` = 1 | `Loc_Al` rung 4 |
| 6.14 | `SA_7404_001_002_INT` `%M00226` | `SA_7404_001_002` `%Q00002` = 1 | `Loc_Al` rung 2 |
| 6.15 | `Tag_DO_15_INT` `%M00239` | `Tag_DO_15` `%Q00015` = 1 | `Loc_Al` rung 3 |
| 6.16 | `Tag_DO_12_INT` / `_13_INT` / `_14_INT` | `%Q00012` / `%Q00013` / `%Q00014` | `Indicat` rungs 2–4 |

## 7. Output inhibit

| # | Stimulus | Expected result |
|---|---|---|
| 7.1 | Set `INHIBIT_ALL_OUTPUTS_ALI` `%M00045` with a trip condition active on `%Q00003`, `%Q00004`, `%Q00008` | **All three outputs go to 1 (non-tripped)** — the inhibit overrides the trip. Verify with a meter on the field terminals |
| 7.2 | Same, while no trip is present | the outputs stay at their tripped/non-tripped state unchanged |
| 7.3 | `%Q00001` (`EY_6401_001_002`) with `INHIBIT_ALL_OUTPUTS_ALI` set | `%Q00001` = 1 (non-tripped) via the parallel branch in `Shutdow` rung 3 |
| 7.4 | Set `INHIBIT_FOAM_REL_ALI` `%M00044` | `SA_7404_001_002` `%Q00002` and `Tag_DO_15` `%Q00015` are forced to 0 (`Loc_Al` rungs 2, 3); pump A start is blocked (`Protect` rung 2) |
| 7.5 | `INHIBIT_ALL_OUTPUTS` and the pump-house sound | **the pump-house sound must NOT be triggered** by the inhibit itself (28 June 2003 change) |

## 8. Deluge pump A / pump B sequence, retries and timers (`CE_LOG`, `Protect`)

| # | Stimulus | Expected result | Timing |
|---|---|---|---|
| 8.1 | Valid fire/foam-release condition | `PUMP_A` `%Q00005` = 1 (start/stop command) and `Pump_Active_1_Hour` counting starts | immediate |
| 8.2 | `PST_7503_001_ALHI` does **not** appear after pump A starts | `PUMP_B_START` `%Q00007` gives a **2 s** start pulse | 30 s after the start command (`T00003` = 300 tenths) |
| 8.3 | Still no deluge pressure | second `%Q00007` 2 s pulse | +60 s (`T00005` = 600 tenths) |
| 8.4 | Still no deluge pressure | third `%Q00007` 2 s pulse | +60 s (`T00007`) |
| 8.5 | Still no deluge pressure | "Deluge failed to release" indication latches | +60 s |
| 8.6 | Deluge pressure appears (`PST_7503_001_ALHI`) at any point | retry chain stops; "DELUGE RELEASED" status latches | immediate |
| 8.7 | After 60 minutes of pump A activity | `Pump_Active_1_Hour` reaches 3600 and the latched fire detectors / foam release buttons are reset | 60 min (`CTU` preset 3600, 1 s clock) |
| 8.8 | Fire detectors return to normal **or** "Stop foam" pressed | a **2 s** `PUMP_B_STOP` `%Q00006` pulse is generated | immediate |
| 8.9 | Measure every pulse with a scope/logger | 2 s ± 1 scan for all four pulses; 30 s / 60 s / 60 s for the retries | — |

## 9. Output line-fault supervision (`Protect`, `FLT_1`)

| # | Stimulus | Expected result |
|---|---|---|
| 9.1 | After the 120 s power-up block `T00002` `%T00002` | the pulsed outputs `%Q00009` (`PUMP_A_PulsOut`) and `%Q00010` (`Pump_B_Start_PulsOut`) start pulsing every **30 s** |
| 9.2 | Feedback pulse missing for 28 s (`T00013` / `T00014`, preset 2800 = 280 s in the source printout — verify the printed PV again on site) | `PUMP_A_OC` `%M00293` / `PUMP_B_START_OC` `%M00295` latch |
| 9.3 | Feedback present | no open-circuit bit; the timers reset |
| 9.4 | `Pump_A_PulsIn_ALI` `%M00038` (feedback input) held at 1 | no fault |

## 10. Sound, mute and reset (`Sound`)

| # | Stimulus | Expected result |
|---|---|---|
| 10.1 | Any new alarm (`System_Sound01…` one-shot) | the panel sound and the pump-house sound start |
| 10.2 | Press `System_Mute` `%M00706` | sound stops; latched sound bits reset |
| 10.3 | A **new** alarm arrives while muted | sound re-triggers (the mute is not a permanent inhibit) |
| 10.4 | `System_Reset` `%M00700` | all sound latches reset |
| 10.5 | `INHIBIT_ALL_OUTPUTS_ALI` | pump-house sound **not** triggered |

## 11. Output polarity — active-low shutdown outputs (safety critical)

Measure the **field terminals**, not only the tag.

| # | Condition | `%Q00008` `PumpShutdown` | `%Q00003` `P2100_P2200` | `%Q00004` `P3600_P3700` | `%Q00001` `EY_6401_001_002` |
|---|---|---|---|---|---|
| 11.1 | Healthy system | **1** (energised, not tripped) | 1 | 1 | 1 |
| 11.2 | Trip present | **0** (de-energised) | 0 | 0 | 0 |
| 11.3 | Trip present + `INHIBIT_ALL_OUTPUTS` | **1** | 1 | 1 | 1 |
| 11.4 | Trip removed | 1 | 1 | 1 | 1 |

`%Q00003`, `%Q00004` and `%Q00008` are **negated** in the source; `%Q00001` is not. Confirm the field
solenoid/relay is wired to be **de-energised to trip** on all three negated outputs, and that the
"inhibit overrides trip" behaviour of case 11.3 is the one the plant wants. This is the single most
consequential behaviour in the conversion and must be signed off by the process safety authority.

## 12. Documentation and import checks

| # | Check | Pass criterion |
|---|---|---|
| 12.1 | Import the L5X into RSLogix 5000 / Studio 5000 v17 | no import error, no unresolved tag, no unresolved JSR |
| 12.2 | Controller Properties → Verify | no verify error |
| 12.3 | Routine list | all 24 source routines present with the source names (`Shutdow`, `Loc_Al` spellings kept) |
| 12.4 | Every rung comment starts with `[Source: <routine> rung <n> (GE) …]` | traceability to the printed rung |
| 12.5 | Cross-check the tag list against `var.xml` | every source symbol present with its GE address in the description |
| 12.6 | Confirm the conversion report items §7.1 (Vote_1 mesh) and §7.2 (shutdown polarity) are signed off | required before energising field outputs |
| 12.7 | Confirm all field I/O is aliased to real modules (§6 of the report) and point-to-point checked against `DOC\Terminal block connections.pdf` | required before field commissioning |

## 13. Review gates (must be closed before deployment)

1. **Vote_1 mesh interpretation** — independent review against the original Proficy project.
2. **Shutdown output polarity and inhibit override** — process safety sign-off (cases 11.1–11.4).
3. **`ONDTR_TENTHS` retentive behaviour** — the conversion uses `TON`; confirm each timer's reset
   condition at commissioning (report §2.1, §8 item 3).
4. **Analogue scaling re-proof** on every channel with a calibrated source (cases 3.1–3.8).
5. **Import/verify in RSLogix 5000 v17** — not performed during the conversion (report §8 item 2).
6. **Complete functional test of every C&E row** against `DE-GN-FG-SAF-74-1001` (cases 6.1–6.16).
