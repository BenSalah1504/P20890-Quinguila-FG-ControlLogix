# ==============================================================================
# QUINGUILA FIELD FIRE & GAS CONTROL PANEL (FGCP-7404-001)
# MASTER ENGINEERING COMMENTARY & SUBROUTINE EXPLANATIONS
# Aligned with EPPM Angola engineering documents, P&ID schedules, C&E matrices,
# and field operational safety procedures.
# ==============================================================================

ROUTINE_DESCRIPTIONS = {
    "AOI_AI_Channel": (
        "Add-On Instruction: AOI_AI_Channel (Analog Channel Processing Block)\n"
        "Encapsulates 4-20mA signal conditioning, NAMUR NE 43 diagnostic fault thresholds, "
        "low/high alarm setpoint comparisons, manual maintenance inhibit masking, "
        "first-out chronological trip capture, and 3000 ms debounce timers for open/short circuits."
    ),
    "MainRoutine": (
        "Main Routine: Master Cyclic Scan Dispatcher\n"
        "Orchestrates the top-level cyclic execution sequence of the Fire & Gas safety application. "
        "Executes Init on power-up / first scan (S:FS), and continuously dispatches Input, Logic, "
        "Modbus_Comm, and Output routines during normal running scans."
    ),
    "Init": (
        "Subroutine: Init (Cold / Warm Startup Initialization)\n"
        "Executes exclusively on the first program scan (S:FS). Clears pump pulse timer accumulators, "
        "resets Cause & Effect warm-up delays, unlatches acoustic alarms, and initializes internal flags "
        "to prevent spurious trips or uncommanded horn sounding during CPU boot."
    ),
    "Input": (
        "Subroutine: Input (Master Input Scan & Pre-Processing Dispatcher)\n"
        "Sequences physical I/O mapping and conditioning routines in strict deterministic order: "
        "IO_Mapping_In -> DI_1 -> DI_2 -> AI_1 -> AI_2 -> AI_3 -> Vote_1."
    ),
    "DI_1": (
        "Subroutine: DI_1 (Discrete Inputs Processing & Line Fault Monitoring - Group 1)\n"
        "Conditions field discrete switches: ESD valve limit switches (6401-ZSH/ZSL-001), "
        "foam and firewater tank level switches (7503-LS-001/002), firewater deluge flow switch "
        "(7503-FS-001), pump run feedback pulses, manual ESD pushbuttons, and maintenance inhibit key-switches."
    ),
    "DI_2": (
        "Subroutine: DI_2 (Discrete Inputs Processing - Group 2 / Spares)\n"
        "Allocated for future field discrete expansion channels and secondary area monitoring."
    ),
    "AI_1": (
        "Subroutine: AI_1 (Analog Combustible Gas Detectors 7404-DG-001 to 008)\n"
        "Processes 4-20mA combustible hydrocarbon gas detectors located in the Pump House and "
        "Fuel Gas Skid. Scales 0-100% LEL, evaluates Low Alarm (20% LEL), High Alarm (30% LEL), "
        "NAMUR NE 43 broken wire / open circuit (-10.0% / <3.6mA), and short circuit (98.0% / >21mA)."
    ),
    "AI_2": (
        "Subroutine: AI_2 (Analog Gas Detectors 009-010, Open Path 011R, Flame Detectors DF-001/002)\n"
        "Processes combustible gas detectors DG-009/010, optical flame detectors DF-001/002 (with "
        "1-hour pump active interlocks), and open-path infrared line-of-sight gas detector DG-011R "
        "including optical beam obscuration fault window (-0.78 to -0.47 LEL*m)."
    ),
    "AI_3": (
        "Subroutine: AI_3 (Process Pressure Transmitters & Foam Deluge Release Monitors)\n"
        "Monitors ESDV pneumatic air accumulator pressure PST-7002-001 (low-acting trip at 50 PSI), "
        "fuel gas header pressure PST-6401-001 (high trip at 100 PSI), deluge water pressure PST-7503-001, "
        "and foam release pressure transmitters FR-7503-001/002/003."
    ),
    "Vote_1": (
        "Subroutine: Vote_1 (Sensor Voting Logic & Supervisory Aggregation)\n"
        "Executes 1oo2, 2oo2 voting across gas detector zones. Aggregates all active channel maintenance "
        "inhibits into 'Voting_All_Inhibits' and all channel hardware wire-break / open/short circuit faults "
        "into 'Voting_All_Faults' for HMI and supervisory panel indication."
    ),
    "Logic": (
        "Subroutine: Logic (Master Cause & Effect Matrix & System Clocks)\n"
        "Generates 1.0-second flasher pulses and 1.0-minute watchdog clocks. Executes the 120-second "
        "detector warm-up delay timer (TMR_C_E_Delay), evaluates master System_Reset from panel PB E11 "
        "and HMI touch button, performs controller minor fault logging (GSV/SSV), and dispatches CE_LOG."
    ),
    "CE_LOG": (
        "Subroutine: CE_LOG (Cause & Effect Shutdown Matrix & Pump Sequencing)\n"
        "Executes the core safety interlocks: process pump shutdown (PumpShutdown), fuel gas valve isolation "
        "(EY_6401_001_002), electrical booster pump trips (P2100/P2200, P3600/P3700), and diesel pump B "
        "automatic 3-cycle cranking sequence with deluge pressure feedback and 1-hour pump run limiting."
    ),
    "Sound": (
        "Subroutine: Sound (Acoustic Siren Cadence, Strobe Flasher & Alarm Mute)\n"
        "Detects rising edge alarm events via one-shots, latches acoustic horns and visual beacons, "
        "and processes panel door Mute pushbutton E12 (Mute_Alm_PB) to allow operators to silence acoustic "
        "horns during an emergency while maintaining flashing beacons and active safety trip interlocks."
    ),
    "Output": (
        "Subroutine: Output (Master Output Execution Dispatcher)\n"
        "Dispatches final output conditioning subroutines: Shutdow (ESD trips), Protect (equipment "
        "safeguarding), Indicat (panel lamps), Loc_Al (local annunciator), FLT_1 (fault watchdogs), "
        "and IO_Mapping_Out (writes to physical Slot 8 1756-OB32 module)."
    ),
    "Shutdow": (
        "Subroutine: Shutdow (Emergency Shutdown Fail-Safe Outputs)\n"
        "Drives critical ESD outputs using Fail-Safe Active-Low (De-energize to Trip) logic: "
        "PumpShutdown, EY_6401_001_002, P2100_P2200, and P3600_P3700. In safe state, coils are energized (1); "
        "upon fire/gas confirmation or power loss, coils de-energize (0) to bring the facility to a safe stop."
    ),
    "Protect": (
        "Subroutine: Protect (Pump Safeguarding, Pulse Outputs & Disagree Diagnostics)\n"
        "Generates 1.5-second start pulses for fire pumps, enforces maintenance inhibit interlocks "
        "(INHIBIT_ALL_OUTPUTS, INHIBIT_FOAM_REL), and executes 70-second pump start disagree watchdog timers "
        "to detect pump contactor failure or open circuit wiring."
    ),
    "Indicat": (
        "Subroutine: Indicat (Panel Door LED Pilot Lamp Drivers)\n"
        "Drives status pilot lamps on the enclosure door: ESDV closed status (Tag_DO_13), ESDV open status "
        "(Tag_DO_12), and ESDV low pneumatic air pressure warning (Tag_DO_14)."
    ),
    "Loc_Al": (
        "Subroutine: Loc_Al (Local Panel Annunciator, Siren & Horn Arbitration)\n"
        "Arbitrates local panel annunciator buzzer, main acoustic horn (SA_7404_001_002), and visual strobe "
        "(Tag_DO_15), interlocked with maintenance foam inhibit."
    ),
    "FLT_1": (
        "Subroutine: FLT_1 (System Fault Annunciation & Output Watchdogs)\n"
        "Conditions pulse output commands for Electric Pump A and Diesel Pump B, ensuring deterministic "
        "signal duration to motor control center (MCC) starter relays."
    ),
    "Modbus_Comm": (
        "Subroutine: Modbus_Comm (Murphy Diesel Pump RS485 Modbus RTU Interface)\n"
        "Communicates with Clarke / Murphy diesel fire pump engine panels via ProSoft MVI56E-MCM (Slot 9). "
        "Monitors engine speed (RPM), lube oil pressure, water temperature, alarm codes, and generates common "
        "process alarm PA-001."
    ),
    "IO_Mapping_In": (
        "Subroutine: IO_Mapping_In (Physical Slot Input Buffer Table)\n"
        "Isolates physical backplane hardware from internal application logic. Buffers Slot 7 1756-IB32 "
        "discrete inputs, Slots 2-5 1756-IF16 analog inputs, and Slot 6 1756-IF8H HART input into program tags."
    ),
    "IO_Mapping_Out": (
        "Subroutine: IO_Mapping_Out (Physical Slot Output Buffer Table)\n"
        "Writes conditioned application commands to physical Slot 8 1756-OB32 24VDC sourcing output module, "
        "enforcing terminal-by-terminal alignment with EPPM wiring schedule TB-08."
    ),
}


# ==============================================================================
# 1. AOI_AI_Channel Rung Comments (15 rungs)
# ==============================================================================
AOI_COMMENTS = {
    0: (
        "Analog Channel Input Staging: Passes scaled Process Variable (PV) from 1756-IF16/IF8H "
        "on-card scaling directly into internal engineering variable 'Val' (0-100% LEL, 0-16 bar, etc.)."
    ),
    1: (
        "Low Alarm Threshold Evaluation: Compares 'Val' against 'LoAlarmSP'. "
        "Evaluates GEQ (>=) for standard high-acting gas detectors (LoAlarmLE=0, e.g. 20% LEL), or "
        "LEQ (<=) for low-acting transmitters (LoAlarmLE=1, e.g. air accumulator pressure low trip at 50 PSI). "
        "Sets internal unlatched flag 'LoAlarmRaw'."
    ),
    2: (
        "High Alarm Threshold Evaluation: Compares 'Val' >= 'HiAlarmSP' (e.g. 30% or 60% LEL combustible gas). "
        "Sets internal unlatched flag 'HiAlarmRaw'. This signal feeds the high gas / fire trip matrix."
    ),
    3: (
        "NAMUR NE 43 Open Circuit / Signal Under-Range Detection: Compares 'Val' <= 'LoFaultSP' (typically -10.0%, "
        "corresponding to loop current < 3.6 mA / 400 counts on 12-bit ADC). Detects broken wire, disconnected sensor, "
        "or field transmitter power loss. Sets internal flag 'LoFaultRaw'."
    ),
    4: (
        "NAMUR NE 43 Short Circuit / Signal Over-Range Detection: Compares 'Val' >= 'HiFaultSP' (typically 98.0% to 102.0%, "
        "corresponding to loop current > 21.0 mA). Detects field wiring short circuit to 24VDC or transmitter failure. "
        "Sets internal flag 'HiFaultRaw'."
    ),
    5: (
        "Optical Fault Window Detection (Open Path Detector): When HasFaultWin=1, checks if 'Val' is within the optical "
        "obscuration window (FaultWinLo <= Val <= FaultWinHi, -0.78 to -0.47 LEL*m). Detects dirty optics, heavy fog, "
        "or misaligned reflector without triggering a false combustible gas alarm. Sets 'Fault1'."
    ),
    6: (
        "Low Alarm Latch Management: When channel has low alarm enabled (HasLoAlarm=1), latches 'ALL' upon rising edge "
        "of 'LoAlarmRaw'. The latch remains actively held until cleared by master 'SystemReset' after process normalizes."
    ),
    7: (
        "Low Alarm Maintenance Inhibit Masking: Passes latched alarm 'ALL' to active alarm 'ALLI' only when manual channel "
        "inhibit key/bit 'Inhibit' is OFF (0). If an engineer places this channel in inhibit, ALLI is suppressed to prevent "
        "nuisance trips during sensor calibration."
    ),
    8: (
        "High Alarm Latch Management: When channel has high alarm enabled (HasHiAlarm=1) and high latching is permitted "
        "(AllowHiLatch=1), latches 'ALH' upon rising edge of 'HiAlarmRaw'. Remains latched until master 'SystemReset'."
    ),
    9: (
        "High Alarm Maintenance Inhibit Masking: Passes latched alarm 'ALH' to trip signal 'ALHI' only when 'Inhibit' is OFF (0). "
        "Uninhibited high alarm ALHI directly initiates plant emergency shutdown (ESD) in the Cause & Effect matrix."
    ),
    10: (
        "First-Up (First-Out) Chronological Event Latch: Captures the primary initiating cause of a shutdown. If an uninhibited "
        "high alarm ALHI triggers a plant trip (AnyActions=1), latches 'FRUP' until master 'SystemReset'. Allows operators "
        "to determine which detector tripped first during an incident."
    ),
    11: (
        "Open Circuit / Broken Wire Fault Debounce Timer: 3000 ms on-delay timer (TMR_OC). Filters out transient voltage dips, "
        "electrical switching spikes, or momentary loop noise before declaring a hard wire-break fault."
    ),
    12: (
        "Open Circuit Fault Output: Driven by timer done bit TMR_OC.DN. Live, self-resetting fault bit 'OC' indicates sustained "
        "open circuit / wire-break on this analog loop. Feeds panel trouble lamp and common fault voting."
    ),
    13: (
        "Short Circuit / Loop Saturation Fault Debounce Timer: 3000 ms on-delay timer (TMR_SC). Filters out transient cable surges "
        "before confirming a hard short circuit."
    ),
    14: (
        "Short Circuit Fault Output: Driven by timer done bit TMR_SC.DN. Live fault bit 'SC' indicates sustained short circuit / "
        "over-range (>21 mA) on this analog loop."
    ),
}

# ==============================================================================
# 2. MainRoutine Rung Comments (5 rungs)
# ==============================================================================
MAIN_COMMENTS = {
    0: (
        "First-Scan Power-Up Initialization: Interlocked with system first scan bit (S:FS). "
        "Executes subroutine 'Init' exactly once upon controller transition to RUN mode to initialize "
        "watchdog timers, clear accumulators, and unlatch acoustic alarms."
    ),
    1: (
        "Cyclic Input Processing Dispatcher: Executed continuously on all normal scans (XIO S:FS). "
        "Calls subroutine 'Input' to map physical backplane I/O, apply digital de-bounce filtering, "
        "scale 4-20mA analog channels, and evaluate 1oo2/2oo3 voting."
    ),
    2: (
        "Cyclic Safety Logic & Cause-and-Effect Dispatcher: Executed continuously on all normal scans (XIO S:FS). "
        "Calls subroutine 'Logic' to evaluate master System_Reset, clock pulse generators, "
        "detector warm-up delay timers, and trigger Cause & Effect matrix subroutine CE_LOG."
    ),
    3: (
        "Cyclic Modbus Serial Engine Communications: Executed continuously on all normal scans (XIO S:FS). "
        "Calls subroutine 'Modbus_Comm' to poll ProSoft MVI56E-MCM module (Slot 9) for Clarke / Murphy "
        "diesel pump engine data (RPM, oil pressure, coolant temperature, running hours)."
    ),
    4: (
        "Cyclic Safety Output & Physical Actuation Dispatcher: Executed continuously on all normal scans (XIO S:FS). "
        "Calls subroutine 'Output' to evaluate fail-safe ESD trips, pump safeguarding, panel LED indicators, "
        "local sirens, and write final commands to Slot 8 1756-OB32 physical outputs."
    ),
}

# ==============================================================================
# 3. Init Rung Comments (3 rungs)
# ==============================================================================
INIT_COMMENTS = {
    0: (
        "Timer Accumulator Cold-Start Clear: Clears pump pulse timer accumulators (Pump_Timer1[0] = 0) and "
        "resets Cause & Effect delay timer (System_C_E_Delay[0] = 0) on CPU power-up to ensure predictable initial timing."
    ),
    1: (
        "Acoustic Alarm Internal Latches Power-Up Clear: Unlatches internal horn command (SA_7404_001_002_INT) and "
        "strobe beacon command (Tag_DO_15_INT). Prevents acoustic alarms from sounding immediately upon panel power restoration."
    ),
    2: (
        "Pump Pulse Watchdog Reset: Redundant zero-clear of electric pump A pulse timer to guarantee that no accidental "
        "start pulse is transmitted to the Motor Control Center (MCC) contactor upon CPU boot."
    ),
}

# ==============================================================================
# 4. Input Rung Comments (7 rungs)
# ==============================================================================
INPUT_COMMENTS = {
    0: (
        "Physical Input Buffer Mapping: Calls 'IO_Mapping_In' to copy raw input registers from Slot 7 1756-IB32 "
        "(Discrete Inputs), Slots 2-5 1756-IF16 (Analog Inputs), and Slot 6 1756-IF8H (HART Open Path) into internal tags."
    ),
    1: (
        "Discrete Input Conditioning - Group 1: Calls 'DI_1' to condition valve position switches (6401-ZSH/ZSL-001), "
        "deluge flow switches (7503-FS-001), tank level switches (7503-LS-001/002), and panel pushbuttons."
    ),
    2: (
        "Discrete Input Conditioning - Group 2: Calls 'DI_2' to service future discrete field expansions and spare channels."
    ),
    3: (
        "Analog Combustible Gas Detectors - Group 1: Calls 'AI_1' to execute 4-20mA signal conditioning, NAMUR NE 43 checks, "
        "and alarm threshold evaluations for gas detectors 7404-DG-001 through 008 (Pump House & Skid)."
    ),
    4: (
        "Analog Gas & Flame Detectors - Group 2: Calls 'AI_2' to process gas detectors 7404-DG-009/010, optical flame detectors "
        "7404-DF-001/002, and open-path infrared gas detector 7404-DG-011R."
    ),
    5: (
        "Process Pressures & Deluge Foam Release: Calls 'AI_3' to process ESDV air pressure PST-7002-001, fuel gas header "
        "pressure PST-6401-001, deluge line pressure PST-7503-001, and foam release sensors FR-7503-001/002/003."
    ),
    6: (
        "Sensor Voting & Common Supervisory Fault Aggregation: Calls 'Vote_1' to execute 1oo2/2oo2 voting across gas zones, "
        "and aggregate all channel maintenance inhibits and hardware faults into supervisory tags."
    ),
}

# ==============================================================================
# 5. DI_1 Rung Comments (26 rungs)
# ==============================================================================
DI1_COMMENTS = {
    0: (
        "Fuel Gas Shut-Off Valve Open Position (6401-ZSH-001): Reads limit switch High (TB-01: 01-02). "
        "XIC evaluates TRUE when the ESD valve is fully open, driving live status bit ZSH_6401_001_AL."
    ),
    1: (
        "Fuel Gas Valve Open Uninhibited Alarm: Passes valve open status to uninhibited alarm bit ZSH_6401_001_ALI "
        "for display on panel indicator lamp Tag_DO_12."
    ),
    2: (
        "Fuel Gas Shut-Off Valve Closed Position (6401-ZSL-001): Reads limit switch Low (TB-01: 03-04). "
        "XIC evaluates TRUE when the ESD valve is fully closed, driving live status bit ZSL_6401_001_AL."
    ),
    3: (
        "Fuel Gas Valve Closed Uninhibited Alarm: Passes valve closed status to uninhibited alarm bit ZSL_6401_001_ALI. "
        "Feeds panel door LED indicator Tag_DO_13."
    ),
    4: (
        "Deluge Firewater Flow Switch (7503-FS-001): Reads flow switch contact (TB-01: 09-10). When firewater flows through "
        "the deluge valve, contact closes. Latches alarm FS_7503_001_AL until cleared by master System_Reset."
    ),
    5: (
        "Deluge Firewater Flow Maintenance Inhibit: Passes latched flow alarm to active trip bit FS_7503_001_ALI "
        "unless suppressed by maintenance inhibit switch FS_7503_001_INH (e.g. during periodic deluge flow testing)."
    ),
    6: (
        "Firewater Storage Tank Low Level Switch (7503-LS-001): Reads low level float switch (TB-01: 11-12). "
        "Self-latches alarm LS_7503_001_AL upon low water level. Latched until water is replenished and System_Reset is pressed."
    ),
    7: (
        "Firewater Tank Low Level Maintenance Inhibit: Passes latched low level alarm to active bit LS_7503_001_ALI "
        "unless masked by channel maintenance inhibit LS_7503_001_INH."
    ),
    8: (
        "Foam Concentrate Tank Low Level Switch (7503-LS-002): Reads foam tank level switch (TB-01: 07-08). "
        "Self-latches alarm LS_7503_002_AL when AFFF foam concentrate falls below safety operating threshold."
    ),
    9: (
        "Foam Tank Low Level Maintenance Inhibit: Passes latched foam low level alarm to active bit LS_7503_002_ALI "
        "unless masked by channel maintenance inhibit LS_7503_002_INH."
    ),
    10: (
        "Electric Fire Pump A Running Feedback Pulse: Reads auxiliary run feedback pulse from Pump A contactor (TB-01: 13-14). "
        "Drives internal run status bit Pump_A_PulsIn_AL."
    ),
    11: (
        "Electric Fire Pump A Run Uninhibited Status: Passes pump A run feedback to internal safety bit Pump_A_PulsIn_ALI. "
        "Resets the 70-second start failure watchdog timer in routine Protect."
    ),
    12: (
        "Diesel Fire Pump B Start Command Feedback Pulse: Reads start confirmation pulse from Diesel Pump B Murphy controller "
        "(TB-01: 15-16). Drives internal status bit Pump_B_Start_PulsIn_AL."
    ),
    13: (
        "Diesel Fire Pump B Start Feedback Uninhibited: Passes start feedback to internal bit Pump_B_Start_PulsIn_ALI. "
        "Resets the 70-second cranking failure watchdog timer in routine Protect."
    ),
    14: (
        "Spare Digital Input Channel 08: Reads field contact (TB-01: 17-18). Reserved for expansion; drives SpareDI_08_AL."
    ),
    15: (
        "Spare Digital Input Channel 08 Uninhibited: Passes SpareDI_08_AL to SpareDI_08_ALI."
    ),
    16: (
        "Diesel Fire Pump B Maintenance Inhibit Key-Switch: Reads panel door inhibit switch (TB-01: 17-18). "
        "When active, indicates standby diesel pump B is locked out for engine maintenance. Drives Pump_B_Inhibited_AL."
    ),
    17: (
        "Diesel Fire Pump B Inhibit Uninhibited Flag: Passes Pump_B_Inhibited_AL to active safety tag Pump_B_Inhibited_ALI. "
        "Prevents automatic cranking of Pump B during maintenance."
    ),
    18: (
        "Field Emergency Shutdown Pushbutton (6401-ESDV-001): Physically wired NORMALLY CLOSED (NC) for fail-safe integrity "
        "(TB-01: 25-26). In healthy normal state, 24VDC is present and contact is closed (1). When pressed or wire broken, "
        "contact opens (0). XIO evaluates TRUE on open contact, instantly latching emergency shutdown alarm ESDV_6401_001_AL."
    ),
    19: (
        "Field ESD Pushbutton Uninhibited Trip: Passes emergency pushbutton alarm to active trip bit ESDV_6401_001_ALI. "
        "Directly initiates immediate plant shutdown in Cause & Effect routine CE_LOG."
    ),
    20: (
        "Spare Digital Input Channel 11: Reads field contact (TB-01: 21-22). Self-latches until System_Reset."
    ),
    21: (
        "Spare Digital Input Channel 11 Inhibit: Masks SpareDI_11_AL with channel inhibit SpareDI_11_INH."
    ),
    22: (
        "Foam Deluge Release Master Inhibit Key-Switch: Reads panel front key-switch (TB-01: 27-28). "
        "When engaged by authorized personnel, latches INHIBIT_FOAM_REL_AL until System_Reset."
    ),
    23: (
        "Foam Deluge Inhibit Active Flag: Passes INHIBIT_FOAM_REL_AL to active inhibit tag INHIBIT_FOAM_REL_ALI. "
        "Interlocks deluge pump starting and solenoid discharge to prevent accidental foam release during dry testing."
    ),
    24: (
        "System Master Output Inhibit Key-Switch: Reads master key-switch (TB-01: 29-30). "
        "Used during panel commissioning to isolate all physical outputs. Latches INHIBIT_ALL_OUTPUTS_AL."
    ),
    25: (
        "System Master Output Inhibit Active Flag: Passes to INHIBIT_ALL_OUTPUTS_ALI. Interlocks all 32 physical outputs "
        "to prevent accidental field trips while technicians perform live testing."
    ),
}

# ==============================================================================
# 6. DI_2 Rung Comments (1 rung)
# ==============================================================================
DI2_COMMENTS = {
    0: (
        "Digital Inputs Expansion Group 2: Empty placeholder routine preserved from original GE Fanuc program structure. "
        "Reserved for future discrete I/O expansion."
    ),
}


# ==============================================================================
# 7. AI_1 Rung Comments (16 rungs) - Combustible Gas Detectors 001 to 008
# ==============================================================================
AI1_COMMENTS = {
    0: (
        "Combustible Gas Detector 7404-DG-001 Parameter Setup & AOI Call: "
        "Located at Pump House North (TB-02: 1-3). Passes live 4-20mA signal DG_7404_001 (0-100% LEL). "
        "Configures setpoints: Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "NAMUR NE 43 Broken Wire / Open Circuit = -10.0% (<3.6mA / 400 counts), Short Circuit = 98.0% (>21mA). "
        "Enables low and high alarms with latching; passes channel inhibit DG_7404_001_INH and master System_Reset. "
        "Executes Add-On Instruction AOI_AI_Channel(AI_Inst_DG_7404_001)."
    ),
    1: (
        "7404-DG-001 Output Unpacking: Maps AOI instance outputs to global tags: "
        "Val -> DG_7404_001_VAL (0-100% LEL for HMI display), ALL -> DG_7404_001_ALL (Latched 20% Low Alarm), "
        "ALLI -> DG_7404_001_ALLI (Uninhibited Low Alarm for amber flashing beacon), "
        "ALH -> DG_7404_001_ALH (Latched 30% High Alarm), ALHI -> DG_7404_001_ALHI (Uninhibited High Alarm for C&E ESD trip), "
        "FRUP -> DG_7404_001_FRUP (First-Out chronological trap), OC -> DG_7404_001_OC (3s debounced Open Circuit fault), "
        "SC -> DG_7404_001_SC (3s debounced Short Circuit fault)."
    ),
    2: (
        "Combustible Gas Detector 7404-DG-002 Parameter Setup & AOI Call: "
        "Located at Pump House South (TB-02: 4-6). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_002)."
    ),
    3: (
        "7404-DG-002 Output Unpacking: Maps outputs to global tags DG_7404_002_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    4: (
        "Combustible Gas Detector 7404-DG-003 Parameter Setup & AOI Call: "
        "Located at Pump House East (TB-02: 7-9). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_003)."
    ),
    5: (
        "7404-DG-003 Output Unpacking: Maps outputs to global tags DG_7404_003_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    6: (
        "Combustible Gas Detector 7404-DG-004 Parameter Setup & AOI Call: "
        "Located at Pump House West (TB-02: 10-12). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_004)."
    ),
    7: (
        "7404-DG-004 Output Unpacking: Maps outputs to global tags DG_7404_004_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    8: (
        "Combustible Gas Detector 7404-DG-005 Parameter Setup & AOI Call: "
        "Located at Fuel Gas Skid Inlet (TB-02: 13-15). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_005)."
    ),
    9: (
        "7404-DG-005 Output Unpacking: Maps outputs to global tags DG_7404_005_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    10: (
        "Combustible Gas Detector 7404-DG-006 Parameter Setup & AOI Call: "
        "Located at Fuel Gas Skid Outlet (TB-02: 16-18). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_006)."
    ),
    11: (
        "7404-DG-006 Output Unpacking: Maps outputs to global tags DG_7404_006_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    12: (
        "Combustible Gas Detector 7404-DG-007 Parameter Setup & AOI Call: "
        "Located at Manifold Area North (TB-02: 19-21). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_007)."
    ),
    13: (
        "7404-DG-007 Output Unpacking: Maps outputs to global tags DG_7404_007_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    14: (
        "Combustible Gas Detector 7404-DG-008 Parameter Setup & AOI Call: "
        "Located at Manifold Area South (TB-02: 22-24). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_008)."
    ),
    15: (
        "7404-DG-008 Output Unpacking: Maps outputs to global tags DG_7404_008_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
}

# ==============================================================================
# 8. AI_2 Rung Comments (16 rungs) - DG-009/010, Flame Detectors, Open Path DG-011R
# ==============================================================================
AI2_COMMENTS = {
    0: (
        "Combustible Gas Detector 7404-DG-009 Parameter Setup & AOI Call: "
        "Located at Gas Compressor Shelter (TB-02: 25-27). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_009)."
    ),
    1: (
        "7404-DG-009 Output Unpacking: Maps outputs to global tags DG_7404_009_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    2: (
        "Combustible Gas Detector 7404-DG-010 Parameter Setup & AOI Call: "
        "Located at Storage Tank Battery (TB-02: 28-30). Scaled 0-100% LEL. Sets Low Alarm = 20.0% LEL, High Alarm = 30.0% LEL, "
        "Open Circuit = -10.0%, Short Circuit = 98.0%. Calls AOI_AI_Channel(AI_Inst_DG_7404_010)."
    ),
    3: (
        "7404-DG-010 Output Unpacking: Maps outputs to global tags DG_7404_010_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    4: (
        "Spare Analog Input Channel 11 Parameter Setup & AOI Call: "
        "Reserved expansion channel. Calls AOI_AI_Channel(AI_Inst_SpareAI_11)."
    ),
    5: (
        "Spare Analog Input Channel 11 Output Unpacking: Maps outputs to global tags SpareAI_11_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    6: (
        "Optical Flame Detector 7404-DF-001 (Zone 1 Fire): "
        "Located at Pump House Area (TB-03: 01-03). Optical multi-spectrum IR flame detector. "
        "High Alarm setpoint = 30.0% (Fire Confirmed). Low Alarm is disabled (HasLoAlarm=0) by setting LoAlarmSP = 400.0 "
        "(inactive high threshold). High alarm latch AllowHiLatch is interlocked with firewater flow FS_7503_001_ALI and "
        "1-hour pump active timer Pump_Active_1_Hour. Calls AOI_AI_Channel(AI_Inst_DF_7404_001)."
    ),
    7: (
        "7404-DF-001 Output Unpacking: Maps outputs to global tags DF_7404_001_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC. "
        "ALHI triggers immediate deluge valve release and main plant shutdown."
    ),
    8: (
        "Optical Flame Detector 7404-DF-002 (Zone 2 Fire): "
        "Located at Fuel Gas Skid Area (TB-03: 04-06). High Alarm = 30.0%. Low Alarm disabled (LoAlarmSP = 400.0). "
        "Interlocked with deluge flow and 1-hour pump run limiting. Calls AOI_AI_Channel(AI_Inst_DF_7404_002)."
    ),
    9: (
        "7404-DF-002 Output Unpacking: Maps outputs to global tags DF_7404_002_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    10: (
        "Open Path Infrared Flammable Gas Detector 7404-DG-011R (Line-of-Sight): "
        "Monitors perimeter gas migration. Scaled in LEL-meters (0 to 5.0 LEL*m). "
        "Low Alarm = 1.0 LEL*m, High Alarm = 3.0 LEL*m. "
        "Configures optical fault window: FaultWinLo = -0.78125 LEL*m, FaultWinHi = -0.46875 LEL*m (HasFaultWin=1). "
        "Detects beam blockage, fog, or dirty lenses without false gas alarm. Calls AOI_AI_Channel(AI_Inst_DG_7404_011R)."
    ),
    11: (
        "7404-DG-011R Output Unpacking: Maps outputs to global tags DG_7404_011R_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC. "
        "Fault1 maps to DG_7404_011R_FLT1 (Optical Obscuration Trouble Alarm)."
    ),
    12: (
        "Spare Analog Input Channel 15 Setup: Calls AOI_AI_Channel(AI_Inst_SpareAI_15)."
    ),
    13: (
        "Spare Analog Input Channel 15 Output Unpacking: Maps outputs to SpareAI_15_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    14: (
        "Spare Analog Input Channel 16 Setup: Calls AOI_AI_Channel(AI_Inst_SpareAI_16)."
    ),
    15: (
        "Spare Analog Input Channel 16 Output Unpacking: Maps outputs to SpareAI_16_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
}

# ==============================================================================
# 9. AI_3 Rung Comments (12 rungs) - Process Pressures & Foam Deluge Sensors
# ==============================================================================
AI3_COMMENTS = {
    0: (
        "ESDV Pneumatic Air Accumulator Pressure (7002-PST-001): "
        "Located at ESD Valve Skid (TB-03: 13-14). Scaled 0-100 PSI (0-7 bar). "
        "Configured LOW-ACTING (LoAlarmLE = 1): trips when air pressure falls below LoAlarmSP = 50.0 PSI. "
        "If air pressure drops, the emergency shut-off valve cannot actuate. High alarm disabled (HasHiAlarm=0). "
        "Calls AOI_AI_Channel(AI_Inst_PST_7002_001)."
    ),
    1: (
        "7002-PST-001 Output Unpacking: Maps outputs to PST_7002_001_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC. "
        "ALLI drives panel door low air warning lamp Tag_DO_14."
    ),
    2: (
        "Fuel Gas Header Pressure Transmitter (6401-PST-001): "
        "Located at Fuel Gas Line (TB-03: 16-17). Scaled 0-150 PSI. High Alarm setpoint = 100.0 PSI. "
        "Low Alarm disabled (LoAlarmSP = 400.0). Calls AOI_AI_Channel(AI_Inst_PST_6401_001)."
    ),
    3: (
        "6401-PST-001 Output Unpacking: Maps outputs to PST_6401_001_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC. "
        "ALHI initiates fuel gas valve isolation EY_6401_001_002."
    ),
    4: (
        "Deluge Firewater Line Pressure Transmitter (7503-PST-001): "
        "Located at Deluge Distribution Line (TB-03: 10-11). Scaled 0-16 bar (0-230 PSI). "
        "High Alarm setpoint = 50.0 PSI (confirms active deluge water discharge). "
        "Calls AOI_AI_Channel(AI_Inst_PST_7503_001)."
    ),
    5: (
        "7503-PST-001 Output Unpacking: Maps outputs to PST_7503_001_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC. "
        "ALHI confirms successful deluge release and resets the 30-second diesel pump standby start timer."
    ),
    6: (
        "Foam Deluge Release Outside Local CP (7503-FR-001/002): "
        "Discharge pressure sensor outside control room (TB-03: 20). High Alarm = 30.0 PSI. "
        "Low Alarm disabled (LoAlarmSP = 400.0). Interlocked with deluge flow and pump run timer. "
        "Calls AOI_AI_Channel(AI_Inst_FR_7503_001_002)."
    ),
    7: (
        "7503-FR-001/002 Output Unpacking: Maps outputs to FR_7503_001_002_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    8: (
        "Spare Analog Input Channel 21 Setup: Calls AOI_AI_Channel(AI_Inst_SpareAI_21)."
    ),
    9: (
        "Spare Analog Input Channel 21 Output Unpacking: Maps outputs to SpareAI_21_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC."
    ),
    10: (
        "Foam Deluge Release Inside Local CP (7503-FR-003): "
        "Discharge pressure sensor inside local control panel (TB-03: 19). High Alarm = 30.0 PSI. "
        "Low Alarm disabled (LoAlarmSP = 400.0). Interlocked with deluge flow and pump run timer. "
        "Calls AOI_AI_Channel(AI_Inst_FR_7503_003)."
    ),
    11: (
        "7503-FR-003 Output Unpacking: Maps outputs to FR_7503_003_VAL, _ALL, _ALLI, _ALH, _ALHI, _FRUP, _OC, _SC. "
        "ALHI triggers emergency shutdown and booster pump trips."
    ),
}

# ==============================================================================
# 10. Vote_1 Rung Comments (4 rungs)
# ==============================================================================
VOTE1_COMMENTS = {
    0: (
        "Common Low Combustible Gas Voting (1oo10 OR Matrix): "
        "Evaluates uninhibited low alarm bits DG_7404_001_ALLI through DG_7404_010_ALLI in an OR configuration. "
        "If ANY single gas detector reaches 20% LEL, Voting_DG_7404_ALLI turns ON to activate local warning beacons."
    ),
    1: (
        "Common High Combustible Gas Voting (1oo10 OR Matrix): "
        "Evaluates uninhibited high alarm bits DG_7404_001_ALHI through DG_7404_010_ALHI in an OR configuration. "
        "If ANY single gas detector reaches 30% LEL, Voting_DG_7404_ALHI turns ON to initiate ESD trips in CE_LOG."
    ),
    2: (
        "Master Channel Maintenance Inhibit Aggregation (Supervisory Inhibit Bus): "
        "Evaluates every individual channel manual inhibit switch (_INH) across all 32 discrete inputs and 24 analog channels. "
        "If ANY channel is bypassed for calibration or maintenance, Voting_All_Inhibits turns ON. "
        "Drives the white panel door inhibit LED (LAMP_CR6) and alerts control room operators via HMI."
    ),
    3: (
        "Master Hardware Fault & Wire-Break Aggregation (Supervisory Trouble Bus): "
        "Evaluates all open-circuit (_OC), short-circuit (_SC), and optical beam fault (_FLT1) flags across all channels. "
        "If ANY loop experiences wire-break (<3.6mA), short circuit (>21mA), or beam misalignment, Voting_All_Faults turns ON. "
        "Drives the amber panel door fault LED (LAMP_CR5) and PLC trouble annunciator."
    ),
}

# ==============================================================================
# 11. Logic Rung Comments (17 rungs)
# ==============================================================================
LOGIC_COMMENTS = {
    0: (
        "1.0-Second Free-Running Clock Generator: 1000 ms self-resetting on-delay timer (TMR_T_SEC). "
        "Provides master timebase for alarm flasher frequencies and pulsed outputs."
    ),
    1: (
        "1.0-Second Square Wave Pulse Generator: Compares timer accumulator TMR_T_SEC.ACC < 500 ms. "
        "Produces clean 50% duty cycle square wave (500 ms ON / 500 ms OFF) in tag 'T_SEC_PULSE' to flash panel lamps."
    ),
    2: (
        "1.0-Minute Free-Running Clock Generator: 60,000 ms self-resetting timer (TMR_T_MIN). "
        "Provides master timebase for hourly accumulation and long-term watchdogs."
    ),
    3: (
        "1.0-Minute Square Wave Pulse Generator: Compares TMR_T_MIN.ACC < 30,000 ms. "
        "Produces 30 seconds ON / 30 seconds OFF pulse in tag 'T_MIN_PULSE'."
    ),
    4: (
        "Master System Reset Consolidation: Single deterministic rung driving 'System_Reset'. "
        "Activated by: (1) Physical panel door pushbutton E11 System_Reset_PB (TB-01: 21-22), "
        "(2) PanelView HMI touch reset button System_Reset_HMI, (3) Automatic power-up startup pulse System_Reset_Startup, "
        "or (4) First program scan S:FS. Resets all latched alarm registers and clears fault tables."
    ),
    5: (
        "HMI Touch Reset Pulse-Stretching Timer: 5000 ms on-delay timer (TMR_HMI_Reset). "
        "When an operator presses Reset on the HMI screen, holds the reset state active for a guaranteed 5.0 seconds "
        "so all remote network racks, voting blocks, and debounce timers process the reset transition reliably."
    ),
    6: (
        "HMI Reset Self-Clearing Logic: When the 5.0-second HMI timer completes (TMR_HMI_Reset.DN), "
        "automatically unlatches System_Reset_HMI and resets the timer, preventing operators from leaving the system in perpetual reset."
    ),
    7: (
        "ControlLogix Minor Fault Table Read (GSV): Reads controller minor fault bitmask from System Object 'FaultLog' "
        "into tag 'Sys_MinorFaultBits'. Replaces legacy GE Fanuc system status bits #LOW_BAT, #LOS_IOM, and #HRD_FLT."
    ),
    8: (
        "Battery / Energy Storage Status Monitoring: Evaluates MinorFaultBits.10 to detect real-time clock "
        "energy storage / battery low voltage. Drives tag 'SYS_LOW_BAT'."
    ),
    9: (
        "I/O Backplane Communication Fault Monitoring: Evaluates MinorFaultBits.3 to detect lost connection "
        "to any 1756 I/O chassis module. Drives tag 'SYS_LOS_IOM'."
    ),
    10: (
        "Controller Processor / Watchdog Fault Monitoring: Evaluates MinorFaultBits.4 (program execution fault) and "
        "MinorFaultBits.6 (watchdog timer expiration). Drives tag 'SYS_HRD_FLT'."
    ),
    11: (
        "Controller Fault Table Clear (SSV): Upon master System_Reset, writes zero (Sys_FaultClearZero) into "
        "FaultLog MinorFaultBits using SSV instruction. Replaces legacy GE Fanuc SVC_REQ function 14 (Clear I/O Fault Table)."
    ),
    12: (
        "Detector Power-Up Burn-In Warm-Up Timer: 120,000 ms (120 seconds / 2 minutes) on-delay timer (TMR_C_E_Delay). "
        "Prevents false trips: combustible catalytic bead gas detectors and optical flame detectors require up to 2 minutes "
        "to thermally stabilize after power restoration. Inhibits Cause & Effect trips during this stabilization window."
    ),
    13: (
        "Detector Warm-Up Complete Interlock Flag: When 120-second timer completes (TMR_C_E_Delay.DN), "
        "energizes tag 'T00002', unlocking the Cause & Effect shutdown matrix for active safety protection."
    ),
    14: (
        "Pre-Arming Auto-Reset Pulse: At 118 seconds (2.0 seconds before the 120s warm-up completes), generates a 2-second pulse "
        "on 'System_Reset_Startup' to clear any spurious alarm latches that occurred during detector boot-up."
    ),
    15: (
        "Cause & Effect Matrix Routine Execution Dispatcher: When detector warm-up is complete (XIC T00002), "
        "calls subroutine 'CE_LOG' to evaluate plant shutdown interlocks."
    ),
    16: (
        "Acoustic Alarm & Siren Routine Dispatcher: Calls subroutine 'Sound' on all scans except first scan (XIO S:FS) "
        "to evaluate alarm edge triggers and siren cadences."
    ),
}


# ==============================================================================
# 12. CE_LOG Rung Comments (23 rungs) - Cause & Effect Matrix & Pump Sequencing
# ==============================================================================
CELOG_COMMENTS = {
    0: (
        "Main Process Pumps & Booster Feeders Emergency Shutdown Matrix: "
        "Evaluates confirmed fire and gas shutdown causes: (1) High combustible gas voting Voting_DG_7404_ALHI, "
        "(2) Perimeter open-path high gas DG_7404_011R_ALHI, (3) Foam release in control room FR_7503_003_ALHI, "
        "(4) Optical flame detector Zone 1 DF_7404_001_ALHI, (5) Fuel gas overpressure PST_6401_001_ALHI, "
        "(6) Optical flame detector Zone 2 DF_7404_002_ALHI, (7) ESD valve closed limit ZSL_6401_001_ALI, "
        "(8) Foam release outside FR_7503_001_002_ALHI, or (9) Manual field ESD pushbutton ESDV_6401_001_ALI. "
        "Simultaneously drives trip internal coils: P2100_P2200_INT (Oil Booster Feeder), P3600_P3700_INT "
        "(Water Booster Feeder), and PumpShutdown_INT (Process Pumps Trip)."
    ),
    1: (
        "Fuel Gas Emergency Shut-Off Valve Isolation Matrix: "
        "Trips internal isolation command EY_6401_001_002_INT upon: high combustible gas, open path gas trip, "
        "foam discharge, flame detection in Zone 1/2, or fuel gas line overpressure. De-energizes fuel gas solenoids."
    ),
    2: (
        "Electric Fire Pump A Automatic Start Command: "
        "Initiates Electric Pump A (PUMP_A_INT) upon confirmed fire alarm (Zone 1 flame DF_7404_001, Zone 2 flame DF_7404_002, "
        "or foam discharge). Interlocked with deluge flow switch FS_7503_001_ALI, unlatched by master System_Reset, "
        "and automatically inhibited if the 1-hour pump active limit (Pump_Active_1_Hour) has been reached."
    ),
    3: (
        "Electric Pump A Hourly Operation Counter: Increments counter CTR_Pump_A_Hour on every 1-second pulse (T_SEC_PULSE) "
        "while Pump A is actively running (PUMP_A_INT). Preset = 3600 counts (3600 seconds = 1.0 hour)."
    ),
    4: (
        "Electric Pump A 1-Hour Run Limit Reached Flag: Driven by counter done bit CTR_Pump_A_Hour.DN. "
        "Sets tag 'Pump_Active_1_Hour' to prevent pump motor burn-out and prevent total depletion of the firewater storage tank."
    ),
    5: (
        "Pump Operation Counter Reset Logic: Resets counter CTR_Pump_A_Hour when deluge flow stops (XIO FS_7503_001_ALI), "
        "when master System_Reset is pressed, or when the 1-hour run limit is acknowledged."
    ),
    6: (
        "Standby Diesel Pump B Auto-Start 30-Second Evaluation Timer: When Electric Pump A is commanded to start (PUMP_A_INT), "
        "timer TMR_T00003 runs for 30,000 ms (30 seconds). If deluge line pressure (PST_7503_001_ALHI) is NOT established "
        "within 30 seconds, this timer completes to automatically trigger standby Diesel Pump B!"
    ),
    7: (
        "Standby Evaluation Timer Reset: Resets timer TMR_T00003 once deluge line pressure is verified healthy "
        "(PST_7503_001_ALHI = 1) or when Electric Pump A is stopped."
    ),
    8: (
        "Diesel Pump B Cranking Cycle 1 - Crank Pulse: 2000 ms (2.0 seconds) timer TMR_T00004. "
        "Provides the first 2-second starter motor crank pulse to the Clarke / Murphy diesel engine."
    ),
    9: (
        "Diesel Pump B Cranking Cycle 1 - Rest Interval: 60,000 ms (60 seconds) timer TMR_T00005. "
        "Allows starter motor and battery bank to cool down after Crank 1 before attempting Crank 2."
    ),
    10: (
        "Diesel Pump B Cranking Cycle 2 - Crank Pulse: 2000 ms (2.0 seconds) timer TMR_T00006. "
        "Provides the second 2-second starter motor crank pulse."
    ),
    11: (
        "Diesel Pump B Cranking Cycle 2 - Rest Interval: 60,000 ms (60 seconds) timer TMR_T00007. "
        "Second 60-second starter rest interval."
    ),
    12: (
        "Diesel Pump B Cranking Cycle 3 - Crank Pulse: 2000 ms (2.0 seconds) timer TMR_T00008. "
        "Provides the third and final 2-second starter motor crank pulse."
    ),
    13: (
        "Diesel Pump B Master Starter Solenoid Command: Drives PUMP_B_START_INT during active crank windows: "
        "Crank 1 (T00003.DN and NOT T00004.DN), Crank 2 (T00005.DN and NOT T00006.DN), or Crank 3 (T00007.DN and NOT T00008.DN)."
    ),
    14: (
        "Deluge Failure to Release Watchdog Timer: 60,000 ms (60 seconds) timer TMR_DelugeFail. "
        "Starts after Diesel Pump B has exhausted all 3 crank attempts (TMR_T00008.DN)."
    ),
    15: (
        "Deluge System Failed to Release Critical Alarm: Driven by timer done bit TMR_DelugeFail.DN. "
        "Asserts tag 'DelugeFailedToRelease' if deluge line pressure is still not achieved after all crank cycles."
    ),
    16: (
        "Deluge Failure Timer Reset: Resets timer TMR_DelugeFail once deluge pressure is verified (PST_7503_001_ALHI)."
    ),
    17: (
        "Diesel Pump B Auto-Stop 2-Second Confirmation Timer: 2000 ms timer TMR_T00009. "
        "Confirms that all fire flame alarms and foam release commands have cleared before stopping the diesel pump."
    ),
    18: (
        "Diesel Fire Pump B Stop Solenoid Command: Drives PUMP_B_STOP_INT to energize the engine fuel rack stop solenoid "
        "when deluge flow switch opens (no firewater demand) and all fire alarms have cleared."
    ),
    19: (
        "ESDV Closed Panel LED Logic: When fuel gas shut-off valve is closed (ZSL_6401_001_ALI), "
        "drives internal indicator bit Tag_DO_13_INT to illuminate panel LED L14."
    ),
    20: (
        "ESDV Open Panel LED Logic: When fuel gas shut-off valve is open (ZSH_6401_001_ALI), "
        "drives internal indicator bit Tag_DO_12_INT to illuminate panel LED L15."
    ),
    21: (
        "ESDV Low Air Pressure Panel LED Logic: When pneumatic air accumulator pressure drops below 50 PSI "
        "(PST_7002_001_ALLI), drives internal indicator bit Tag_DO_14_INT to illuminate low air warning LED."
    ),
    22: (
        "System First-Up Action One-Shot Pulse: One-shot rising edge instruction ONS(OS_AnyActions) produces a 1-scan pulse "
        "on 'System_AnyActions' whenever an ESD trip, pump start, or valve closure is initiated. Triggers First-Out event traps."
    ),
}

# ==============================================================================
# 13. Sound Rung Comments (45 rungs) - Acoustic Siren, Flasher & Mute Logic
# ==============================================================================
SOUND_COMMENTS = {
    0: "Rising Edge Detection: Gas Detector 7404-DG-001 High Alarm (ALH) -> One-shot System_Sound01.",
    1: "Rising Edge Detection: Gas Detector 7404-DG-001 Low Alarm (ALL) -> One-shot System_Sound02.",
    2: "Rising Edge Detection: Gas Detector 7404-DG-002 High Alarm (ALH) -> One-shot System_Sound03.",
    3: "Rising Edge Detection: Gas Detector 7404-DG-002 Low Alarm (ALL) -> One-shot System_Sound04.",
    4: "Rising Edge Detection: Gas Detector 7404-DG-003 High Alarm (ALH) -> One-shot System_Sound05.",
    5: "Rising Edge Detection: Gas Detector 7404-DG-003 Low Alarm (ALL) -> One-shot System_Sound06.",
    6: "Rising Edge Detection: Gas Detector 7404-DG-004 High Alarm (ALH) -> One-shot System_Sound07.",
    7: "Rising Edge Detection: Gas Detector 7404-DG-004 Low Alarm (ALL) -> One-shot System_Sound08.",
    8: "Rising Edge Detection: Gas Detector 7404-DG-005 High Alarm (ALH) -> One-shot System_Sound09.",
    9: "Rising Edge Detection: Gas Detector 7404-DG-005 Low Alarm (ALL) -> One-shot System_Sound10.",
    10: "Rising Edge Detection: Gas Detector 7404-DG-006 High Alarm (ALH) -> One-shot System_Sound11.",
    11: "Rising Edge Detection: Gas Detector 7404-DG-006 Low Alarm (ALL) -> One-shot System_Sound12.",
    12: "Rising Edge Detection: Gas Detector 7404-DG-007 High Alarm (ALH) -> One-shot System_Sound13.",
    13: "Rising Edge Detection: Gas Detector 7404-DG-007 Low Alarm (ALL) -> One-shot System_Sound14.",
    14: "Rising Edge Detection: Gas Detector 7404-DG-008 High Alarm (ALH) -> One-shot System_Sound15.",
    15: "Rising Edge Detection: Gas Detector 7404-DG-008 Low Alarm (ALL) -> One-shot System_Sound16.",
    16: "Rising Edge Detection: Gas Detector 7404-DG-009 High Alarm (ALH) -> One-shot System_Sound17.",
    17: "Rising Edge Detection: Gas Detector 7404-DG-009 Low Alarm (ALL) -> One-shot System_Sound18.",
    18: "Rising Edge Detection: Gas Detector 7404-DG-010 High Alarm (ALH) -> One-shot System_Sound19.",
    19: "Rising Edge Detection: Gas Detector 7404-DG-010 Low Alarm (ALL) -> One-shot System_Sound20.",
    20: "Rising Edge Detection: Open Path Gas Detector 7404-DG-011R High Alarm (ALH) -> One-shot System_Sound21.",
    21: "Rising Edge Detection: Open Path Gas Detector 7404-DG-011R Low Alarm (ALL) -> One-shot System_Sound22.",
    22: "Rising Edge Detection: Optical Flame Detector 7404-DF-001 Fire High Alarm -> One-shot System_Sound23.",
    23: "Rising Edge Detection: Optical Flame Detector 7404-DF-002 Fire High Alarm -> One-shot System_Sound24.",
    24: "Rising Edge Detection: Deluge Foam Release Outside FR-7503-001/002 High Alarm -> One-shot System_Sound25.",
    25: "Rising Edge Detection: Deluge Foam Release Inside Local CP FR-7503-003 High Alarm -> One-shot System_Sound26.",
    26: "Rising Edge Detection: Master Output Inhibit Key-Switch Engaged -> One-shot System_Sound27.",
    27: "Rising Edge Detection: Firewater Tank Low Level Switch LS-7503-001 Alarm -> One-shot System_Sound28.",
    28: "Rising Edge Detection: Foam Tank Low Level Switch LS-7503-002 Alarm -> One-shot System_Sound29.",
    29: "Rising Edge Detection: Air Accumulator Low Pressure PST-7002-001 Trip -> One-shot System_Sound30.",
    30: "Rising Edge Detection: ESD Valve Closed Limit Switch ZSL-6401-001 -> One-shot System_Sound31.",
    31: (
        "Optical Flasher Strobe Master Latch: 31-input OR gate evaluating one-shots System_Sound01 through 31. "
        "Upon rising edge of ANY process alarm, fire alarm, gas alarm, or level fault, latches optical strobe Tag_DO_15_INT."
    ),
    32: (
        "Acoustic Siren Master Latch: 26-input OR gate evaluating fire and gas alarm one-shots. "
        "Upon rising edge of ANY confirmed fire or gas hazard, latches main plant acoustic siren SA_7404_001_002_INT."
    ),
    33: "Rising Edge Detection: CPU Battery / Memory Failure (SYS_BAD_RAM) -> One-shot System_Sound32.",
    34: "Rising Edge Detection: Controller Hardware CPU Failure (SYS_HRD_CPU) -> One-shot System_Sound33.",
    35: "Rising Edge Detection: Controller Minor/Major Fault (SYS_HRD_FLT) -> One-shot System_Sound34.",
    36: "Rising Edge Detection: Lost Connection to I/O Module (SYS_LOS_IOM) -> One-shot System_Sound35.",
    37: "Rising Edge Detection: Lost Communication to Expansion Rack (SYS_LOS_RCK) -> One-shot System_Sound36.",
    38: "Rising Edge Detection: RTC Battery Low Voltage (SYS_LOW_BAT) -> One-shot System_Sound37.",
    39: "Rising Edge Detection: Diesel Pump B Maintenance Inhibit Engaged -> One-shot System_Sound40.",
    40: (
        "Common PLC Fault Annunciator Latch: Latches PLC_Fault_INT upon any CPU, memory, battery, or I/O module fault."
    ),
    41: (
        "Optical Strobe Flasher Silence / Unlatch: Unlatches Tag_DO_15_INT when master System_Reset is pressed "
        "or when Alarm Mute (System_Mute) is activated."
    ),
    42: (
        "Acoustic Siren Silence / Unlatch: Unlatches main plant siren SA_7404_001_002_INT when master System_Reset is pressed "
        "or when Alarm Mute (System_Mute) is activated by operator."
    ),
    43: (
        "PLC Fault Annunciator Silence / Unlatch: Unlatches PLC_Fault_INT upon System_Reset or System_Mute."
    ),
    44: (
        "Alarm Mute Pushbutton Processing: Reads physical push button E12 on panel door Mute_Alm_PB (TB-01: 23-24). "
        "Drives 'System_Mute' to silence acoustic sirens without resetting visual beacons or emergency trip interlocks, "
        "enabling personnel communication during an active field incident."
    ),
}

# ==============================================================================
# 14. Output Rung Comments (6 rungs)
# ==============================================================================
OUTPUT_COMMENTS = {
    0: "Emergency Shutdown Outputs Dispatcher: Calls 'Shutdow' to drive fail-safe de-energize to trip outputs.",
    1: "Equipment Safeguarding Outputs Dispatcher: Calls 'Protect' to condition pump run pulses and interlocks.",
    2: "Panel LED Pilot Lamps Dispatcher: Calls 'Indicat' to drive door-mounted status lamps.",
    3: "Local Panel Alarm Dispatcher: Calls 'Loc_Al' to drive local panel horn and strobe beacons.",
    4: "System Diagnostic Watchdog Dispatcher: Calls 'FLT_1' to update pump pulse output commands.",
    5: "Physical Backplane Output Write: Calls 'IO_Mapping_Out' to transfer all commands to Slot 8 1756-OB32 module.",
}

# ==============================================================================
# 15. Shutdow Rung Comments (4 rungs) - Fail-Safe Active-Low (De-energize to Trip)
# ==============================================================================
SHUTDOW_COMMENTS = {
    0: (
        "Fuel Gas Emergency Shut-Off Valves (6401-EY-001/002) - Fail-Safe Active-Low: "
        "In normal healthy operating state, internal trip coil EY_6401_001_002_INT is OFF (0), so XIO evaluates TRUE "
        "and physical output EY_6401_001_002 is ENERGIZED (1), holding fuel gas valves open. "
        "Upon fire/gas emergency trip, internal coil energizes (1), XIO opens, and the output DE-ENERGIZES (0) to "
        "spring-close the fuel gas valves. Held energized if master maintenance inhibit INHIBIT_ALL_OUTPUTS_ALI is active."
    ),
    1: (
        "Main Process Pumps Emergency Shutdown (PumpShutdown) - Fail-Safe Active-Low: "
        "Normal state: output is ENERGIZED (1) holding pump MCC permissive contact closed. "
        "Trip state: output DE-ENERGIZES (0) to instantly trip all main process pump motors (TB-08: 01-02). "
        "Loss of control power causes immediate safe shutdown."
    ),
    2: (
        "Oil Booster Pumps Feeder EDB1 Trip (P2100_P2200) - Fail-Safe Active-Low: "
        "Normal state: output is ENERGIZED (1). Trip state: output DE-ENERGIZES (0) to shunt-trip booster pump breakers (TB-08: 17-18)."
    ),
    3: (
        "Water Booster Pumps Feeder EDB2 Trip (P3600_P3700) - Fail-Safe Active-Low: "
        "Normal state: output is ENERGIZED (1). Trip state: output DE-ENERGIZES (0) to shunt-trip booster pump breakers (TB-08: 19-20)."
    ),
}

# ==============================================================================
# 16. Protect Rung Comments (17 rungs) - Pump Interlocks & Disagree Watchdogs
# ==============================================================================
PROTECT_COMMENTS = {
    0: (
        "Electric Fire Pump A Continuous Run Command: Interlocked with foam release inhibit INHIBIT_FOAM_REL_ALI "
        "and master output inhibit INHIBIT_ALL_OUTPUTS_ALI. Drives physical output PUMP_A (TB-08: 09-10)."
    ),
    1: (
        "Diesel Fire Pump B Start Pilot Command: Interlocked with foam inhibit and master inhibit. "
        "Drives physical output PUMP_B_START (TB-08: 13-14)."
    ),
    2: (
        "Diesel Fire Pump B Stop Command: Drives physical output PUMP_B_STOP (TB-08: 15-16) to energize the fuel rack stop solenoid."
    ),
    3: "Pump A Pulse Reset: Resets timer TMR_Pump_Timer11 when 1-minute pulse clock T_MIN_PULSE is low.",
    4: "Pump A Pulse On-Delay Timer: 28,000 ms timer generating the pulse duration for Pump A remote start.",
    5: "Pump A Pulse Timer Output Flag: Sets T00013 when timer completes.",
    6: (
        "Electric Pump A Momentary Start Pulse Generator: Drives internal pulse command Pump_A_PulsOut_INT "
        "to deliver a 1.5-second pulse to the MCC starter relay."
    ),
    7: "Pump A Disagree Watchdog Reset: Resets 70-second timer TMR_Pump_Timer9 when pump run feedback Pump_A_PulsIn_ALI is received.",
    8: "Pump A Start Disagree Timer: 70,000 ms (70 seconds) watchdog timer TMR_Pump_Timer9.",
    9: (
        "Electric Pump A Start Failure / Disagree Alarm: If Pump A was commanded to start but feedback is NOT received "
        "within 70 seconds, sets PUMP_A_OC (Pump A Contactor Open Circuit / Run Disagree Fault)."
    ),
    10: "Pump B Pulse Reset: Resets timer TMR_Pump_Timer12 on 1-minute clock low.",
    11: "Pump B Pulse On-Delay Timer: 28,000 ms timer for Diesel Pump B start pulse.",
    12: "Pump B Pulse Timer Output Flag: Sets T00014 when timer completes.",
    13: (
        "Diesel Pump B Momentary Start Pulse Generator: Drives internal pulse command Pump_B_Start_PulsOut_INT "
        "to deliver a start crank pulse to the Murphy engine panel."
    ),
    14: "Pump B Disagree Watchdog Reset: Resets 70-second timer TMR_Pump_Timer10 when start feedback Pump_B_Start_PulsIn_ALI is received.",
    15: "Pump B Start Disagree Timer: 70,000 ms (70 seconds) watchdog timer TMR_Pump_Timer10.",
    16: (
        "Diesel Pump B Start Failure / Disagree Alarm: If Pump B was cranked but engine run feedback is NOT received "
        "within 70 seconds, sets PUMP_B_START_OC (Diesel Engine Crank Disagree Fault)."
    ),
}

# ==============================================================================
# 17. Indicat Rung Comments (3 rungs) - Panel Door Pilot Lamps
# ==============================================================================
INDICAT_COMMENTS = {
    0: "ESDV Closed Panel LED Driver: Passes Tag_DO_13_INT to physical output Tag_DO_13 to light LED L14 (TB-08: 23-24).",
    1: "ESDV Open Panel LED Driver: Passes Tag_DO_12_INT to physical output Tag_DO_12 to light LED L15 (TB-08: 25-26).",
    2: "ESDV Low Air Pressure LED Driver: Passes Tag_DO_14_INT to physical output Tag_DO_14 to light LED L16 (TB-08: 27-28).",
}

# ==============================================================================
# 18. Loc_Al Rung Comments (3 rungs) - Local Alarm Annunciators
# ==============================================================================
LOCAL_COMMENTS = {
    0: (
        "Acoustic Alarm Siren Output: Passes internal horn command SA_7404_001_002_INT to physical output SA_7404_001_002 "
        "(TB-08: 05-06), suppressed when maintenance foam inhibit INHIBIT_FOAM_REL_ALI is active."
    ),
    1: (
        "Optical Strobe Flasher Output: Passes internal beacon command Tag_DO_15_INT to physical output Tag_DO_15 "
        "(TB-08: 45-46), suppressed when foam inhibit is active."
    ),
    2: (
        "PLC System Health Watchdog Output (Fail-Safe): Drives physical output PLC_Fault (TB-08: 21-22). "
        "Normally ENERGIZED (1) when system is healthy; de-energizes (0) upon fatal hardware failure, rack fault, or power loss."
    ),
}

# ==============================================================================
# 19. FLT_1 Rung Comments (2 rungs) - Pulse Output Conditioning
# ==============================================================================
FLT1_COMMENTS = {
    0: "Pump A Pulse Output Interlock: Passes Pump_A_PulsOut_INT to physical output Pump_A_PulsOut (TB-08: 07-08).",
    1: "Pump B Start Pulse Output Interlock: Passes Pump_B_Start_PulsOut_INT to physical output Pump_B_Start_PulsOut (TB-08: 11-12).",
}


# ==============================================================================
# 20. Modbus_Comm Rung Comments (26 rungs) - Murphy Engine Controller Interface
# ==============================================================================
MODBUS_COMMENTS = {
    0: (
        "Subroutine Header: Modbus RTU serial interface via ProSoft MVI56E-MCM module (Slot 9). "
        "Communicates over RS485 with Clarke / Murphy diesel fire pump engine panels and process pumps. "
        "MCM_IN array receives holding registers via module backplane M-file transfer."
    ),
    1: "Power Oil Pump P2300: Copies Modbus register MCM_IN[1] to alarm / shutdown code register MB_P2300_ALMCODE.",
    2: "Power Oil Pump P2300: Copies Modbus register MCM_IN[2] to engine running speed register MB_P2300_RPM.",
    3: "Power Oil Pump P2300 Fault Evaluation: If alarm code NEQ 0, asserts P2300_SHUTDOWN.",
    4: "Power Oil Pump P2400: Copies Modbus register MCM_IN[11] to alarm / shutdown code register MB_P2400_ALMCODE.",
    5: "Power Oil Pump P2400: Copies Modbus register MCM_IN[12] to engine running speed register MB_P2400_RPM.",
    6: "Power Oil Pump P2400 Fault Evaluation: If alarm code NEQ 0, asserts P2400_SHUTDOWN.",
    7: "Power Oil Pump P2500: Copies Modbus register MCM_IN[21] to alarm / shutdown code register MB_P2500_ALMCODE.",
    8: "Power Oil Pump P2500: Copies Modbus register MCM_IN[22] to engine running speed register MB_P2500_RPM.",
    9: "Power Oil Pump P2500 Fault Evaluation: If alarm code NEQ 0, asserts P2500_SHUTDOWN.",
    10: "Power Oil Pump P2600: Copies Modbus register MCM_IN[31] to alarm / shutdown code register MB_P2600_ALMCODE.",
    11: "Power Oil Pump P2600: Copies Modbus register MCM_IN[32] to engine running speed register MB_P2600_RPM.",
    12: "Power Oil Pump P2600 Fault Evaluation: If alarm code NEQ 0, asserts P2600_SHUTDOWN.",
    13: "Water Injection Pump P3800: Copies Modbus register MCM_IN[41] to alarm code register MB_P3800_ALMCODE.",
    14: "Water Injection Pump P3800: Copies Modbus register MCM_IN[42] to engine speed register MB_P3800_RPM.",
    15: "Water Injection Pump P3800 Fault Evaluation: If alarm code NEQ 0, asserts P3800_SHUTDOWN.",
    16: "Water Injection Pump P3900: Copies Modbus register MCM_IN[51] to alarm code register MB_P3900_ALMCODE.",
    17: "Water Injection Pump P3900: Copies Modbus register MCM_IN[52] to engine speed register MB_P3900_RPM.",
    18: "Water Injection Pump P3900 Fault Evaluation: If alarm code NEQ 0, asserts P3900_SHUTDOWN.",
    19: "Treater V-710 (Phase 2): Copies Modbus register MCM_IN[61] to alarm code register MB_V710_ALMCODE.",
    20: "Treater V-710 (Phase 2): Copies Modbus register MCM_IN[62] to engine speed register MB_V710_RPM.",
    21: "Treater V-810 (Phase 2): Copies Modbus register MCM_IN[71] to alarm code register MB_V810_ALMCODE.",
    22: "Treater V-810 (Phase 2): Copies Modbus register MCM_IN[72] to engine speed register MB_V810_RPM.",
    23: "Oil Expedition Flowmeter 6401-FT-005: Copies Modbus register MCM_IN[81] to alarm code register MB_FT6401_ALMCODE.",
    24: "Oil Expedition Flowmeter 6401-FT-005: Copies Modbus register MCM_IN[82] to flow rate register MB_FT6401_RPM (0-500 bbl/h).",
    25: (
        "Common Process Alarm PA-001 Generation: Evaluates shutdown flags from pump annunciators "
        "(P2300, P2400, P2500, P2600, P3800, P3900). If ANY process pump is in shutdown, drives PA_001_Process (TB-08: 47-48)."
    ),
}

# ==============================================================================
# 21. IO_Mapping_In Rung Comments (48 rungs)
# ==============================================================================
IOMAP_IN_COMMENTS = {
    0: "DI Slot 7 Point 0 -> ZSH_6401_001 : 6401-ZSH-001 Fuel Gas Valve Open Limit Switch (TB-01: 01-02).",
    1: "DI Slot 7 Point 1 -> ZSL_6401_001 : 6401-ZSL-001 Fuel Gas Valve Closed Limit Switch (TB-01: 03-04).",
    2: "DI Slot 7 Point 2 -> SpareDI_02 : Spare Digital Input Channel 02 (TB-01: 05-06).",
    3: "DI Slot 7 Point 3 -> LS_7503_002 : 7503-LS-002 Foam Concentrate Day Tank Low Level Switch (TB-01: 07-08).",
    4: "DI Slot 7 Point 4 -> FS_7503_001 : 7503-FS-001 Deluge Firewater Flow Switch (TB-01: 09-10).",
    5: "DI Slot 7 Point 5 -> LS_7503_001 : 7503-LS-001 Firewater Storage Tank Low Level Switch (TB-01: 11-12).",
    6: "DI Slot 7 Point 6 -> Pump_A_PulsIn : Electric Deluge Pump A Run Feedback Pulse from MCC Contactor (TB-01: 13-14).",
    7: "DI Slot 7 Point 7 -> Pump_B_Start_PulsIn : Diesel Deluge Pump B Start Feedback Pulse from Engine Panel (TB-01: 15-16).",
    8: "DI Slot 7 Point 8 -> Pump_B_Inhibited : Diesel Pump B Maintenance Inhibit Key-Switch (TB-01: 17-18).",
    9: "DI Slot 7 Point 9 -> SpareDI_09 : Spare Digital Input Channel 09 (TB-01: 19-20).",
    10: "DI Slot 7 Point 10 -> System_Reset_PB : Panel Door Pushbutton E11 - Master System Reset (TB-01: 21-22).",
    11: "DI Slot 7 Point 11 -> Mute_Alm_PB : Panel Door Pushbutton E12 - Acoustic Alarm Silence / Mute (TB-01: 23-24).",
    12: "DI Slot 7 Point 12 -> ESDV_6401_001 : Field Emergency Shutdown Station (NC Fail-Safe Contact) (TB-01: 25-26).",
    13: "DI Slot 7 Point 13 -> INHIBIT_FOAM_REL : Panel Front Key-Switch - Inhibit Foam Deluge Release (TB-01: 27-28).",
    14: "DI Slot 7 Point 14 -> INHIBIT_ALL_OUTPUTS : Panel Front Key-Switch - Inhibit All Physical Outputs (TB-01: 29-30).",
    15: "DI Slot 7 Point 15 -> SpareDI_15 : Spare Digital Input Channel 15 (TB-01: 31-32).",
    16: "DI Slot 7 Point 16 -> SpareDI_16 : Spare Digital Input Channel 16 (TB-01: 33-34).",
    17: "DI Slot 7 Point 17 -> SpareDI_17 : Spare Digital Input Channel 17 (TB-01: 35-36).",
    18: "DI Slot 7 Point 18 -> SpareDI_18 : Spare Digital Input Channel 18 (TB-01: 37-38).",
    19: "DI Slot 7 Point 19 -> SpareDI_19 : Spare Digital Input Channel 19 (TB-01: 39-40).",
    20: "DI Slot 7 Point 20 -> SpareDI_20 : Spare Digital Input Channel 20 (TB-01: 41-42).",
    21: "DI Slot 7 Point 21 -> SpareDI_21 : Spare Digital Input Channel 21 (TB-01: 43-44).",
    22: "DI Slot 7 Point 22 -> SpareDI_22 : Spare Digital Input Channel 22 (TB-01: 45-46).",
    23: "DI Slot 7 Point 23 -> SpareDI_23 : Spare Digital Input Channel 23 (TB-01: 47-48).",
    24: "DI Slot 7 Point 24 -> SpareDI_24 : Spare Digital Input Channel 24 (TB-01: 49-50).",
    25: "DI Slot 7 Point 25 -> SpareDI_25 : Spare Digital Input Channel 25 (TB-01: 51-52).",
    26: "DI Slot 7 Point 26 -> SpareDI_26 : Spare Digital Input Channel 26 (TB-01: 53-54).",
    27: "DI Slot 7 Point 27 -> SpareDI_27 : Spare Digital Input Channel 27 (TB-01: 55-56).",
    28: "DI Slot 7 Point 28 -> SpareDI_28 : Spare Digital Input Channel 28 (TB-01: 57-58).",
    29: "DI Slot 7 Point 29 -> SpareDI_29 : Spare Digital Input Channel 29 (TB-01: 59-60).",
    30: "DI Slot 7 Point 30 -> SpareDI_30 : Spare Digital Input Channel 30 (TB-01: 61-62).",
    31: "DI Slot 7 Point 31 -> SpareDI_31 : Spare Digital Input Channel 31 (TB-01: 63-64).",
    32: "AI Slot 2 Ch0 -> DG_7404_001 : 7404-DG-001 Gas Detector Pump House North (0-100% LEL, TB-02: 1-3).",
    33: "AI Slot 2 Ch1 -> DG_7404_002 : 7404-DG-002 Gas Detector Pump House South (0-100% LEL, TB-02: 4-6).",
    34: "AI Slot 2 Ch2 -> DG_7404_003 : 7404-DG-003 Gas Detector Pump House East (0-100% LEL, TB-02: 7-9).",
    35: "AI Slot 2 Ch3 -> DG_7404_004 : 7404-DG-004 Gas Detector Pump House West (0-100% LEL, TB-02: 10-12).",
    36: "AI Slot 2 Ch4 -> DG_7404_005 : 7404-DG-005 Gas Detector Fuel Gas Skid Inlet (0-100% LEL, TB-02: 13-15).",
    37: "AI Slot 2 Ch5 -> DG_7404_006 : 7404-DG-006 Gas Detector Fuel Gas Skid Outlet (0-100% LEL, TB-02: 16-18).",
    38: "AI Slot 2 Ch6 -> DG_7404_007 : 7404-DG-007 Gas Detector Manifold Area North (0-100% LEL, TB-02: 19-21).",
    39: "AI Slot 2 Ch7 -> DG_7404_008 : 7404-DG-008 Gas Detector Manifold Area South (0-100% LEL, TB-02: 22-24).",
    40: "AI Slot 2 Ch8 -> DG_7404_009 : 7404-DG-009 Gas Detector Gas Compressor Shelter (0-100% LEL, TB-02: 25-27).",
    41: "AI Slot 2 Ch9 -> DG_7404_010 : 7404-DG-010 Gas Detector Storage Tank Battery (0-100% LEL, TB-02: 28-30).",
    42: "AI Slot 3 Ch3 -> PST_7503_001 : 7503-PST-001 Deluge Firewater Line Pressure (0-16 bar, TB-03: 10-11).",
    43: "AI Slot 3 Ch4 -> PST_7002_001 : 7002-PST-001 ESDV Air Accumulator Pressure (0-100 PSI, TB-03: 13-14).",
    44: "AI Slot 3 Ch5 -> PST_6401_001 : 6401-PST-001 Fuel Gas Header Pressure (0-150 PSI, TB-03: 16-17).",
    45: "AI Slot 3 Ch6 -> FR_7503_003 : 7503-FR-003 Foam Release Pressure Inside Local CP (TB-03: 19).",
    46: "AI Slot 3 Ch7 -> FR_7503_001_002 : 7503-FR-001/002 Foam Release Pressure Outside (TB-03: 20).",
    47: (
        "Open Path Gas Detector 7404-DG-011R Input Multiplexer: If HART communication is enabled (HART_DG011R_Enable=1), "
        "reads digital HART process variable from Slot 6 1756-IF8H Ch0 (Local:6:I.Ch0Data). If HART is disabled, "
        "falls back to conventional 4-20mA analog channel on Slot 2 1756-IF16 Ch12 (Local:2:I.Ch12Data)."
    ),
}

# ==============================================================================
# 22. IO_Mapping_Out Rung Comments (32 rungs)
# ==============================================================================
IOMAP_OUT_COMMENTS = {
    0: (
        "DO Slot 8 Point 0 <- PumpShutdown (Fail-Safe Active-Low): Main Process Pumps Emergency Trip Relay (TB-08: 01-02). "
        "Held HIGH (1) in healthy operation; drops LOW (0) on emergency shutdown or control power failure."
    ),
    1: (
        "DO Slot 8 Point 1 <- EY_6401_001_002 (Fail-Safe Active-Low): Fuel Gas Emergency Shut-Off Valve Solenoids (TB-08: 03-04). "
        "Held HIGH (1) to keep fuel gas valves open; de-energizes LOW (0) on confirmed fire/gas trip."
    ),
    2: (
        "DO Slot 8 Point 2 <- SA_7404_001_002: Main Plant Acoustic Alarm Horn / Siren 7404-001/002 (TB-08: 05-06). "
        "Energized on confirmed fire, gas high, or process emergency. Silenced by panel Mute PB."
    ),
    3: (
        "DO Slot 8 Point 3 <- Pump_A_PulsOut: Electric Fire Pump A Remote Start Momentary Pulse Output (TB-08: 07-08). "
        "Delivers 1.5-second pulse to MCC motor starter contactor."
    ),
    4: (
        "DO Slot 8 Point 4 <- PUMP_A: Electric Fire Pump A Continuous Run Permissive Interlock (TB-08: 09-10).",
    ),
    5: (
        "DO Slot 8 Point 5 <- Pump_B_Start_PulsOut: Diesel Fire Pump B Remote Start Momentary Pulse Output (TB-08: 11-12). "
        "Delivers 1.5-second crank pulse to Murphy engine control panel."
    ),
    6: (
        "DO Slot 8 Point 6 <- PUMP_B_START: Diesel Fire Pump B Continuous Start Command Relay (TB-08: 13-14).",
    ),
    7: (
        "DO Slot 8 Point 7 <- PUMP_B_STOP: Diesel Fire Pump B Fuel Rack Stop Solenoid Command (TB-08: 15-16). "
        "Energize to stop diesel engine when firewater demand clears."
    ),
    8: (
        "DO Slot 8 Point 8 <- P2100_P2200 (Fail-Safe Active-Low): Oil Booster Pumps Feeder EDB1 Shunt Trip (TB-08: 17-18). "
        "Normally energized (1); de-energizes (0) on emergency shutdown."
    ),
    9: (
        "DO Slot 8 Point 9 <- P3600_P3700 (Fail-Safe Active-Low): Water Booster Pumps Feeder EDB2 Shunt Trip (TB-08: 19-20). "
        "Normally energized (1); de-energizes (0) on emergency shutdown."
    ),
    10: (
        "DO Slot 8 Point 10 <- PLC_Fault (Fail-Safe Active-Low): ControlLogix System Health Watchdog (TB-08: 21-22). "
        "Held energized (1) when CPU and all I/O modules are healthy; de-energizes on fatal hardware fault or power loss."
    ),
    11: "DO Slot 8 Point 11 <- Tag_DO_13: Panel Door Red LED L14 - ESD Valve Closed Status (TB-08: 23-24).",
    12: "DO Slot 8 Point 12 <- Tag_DO_12: Panel Door Green LED L15 - ESD Valve Open Status (TB-08: 25-26).",
    13: "DO Slot 8 Point 13 <- Tag_DO_14: Panel Door Amber LED L16 - ESDV Low Pneumatic Air Pressure Warning (TB-08: 27-28).",
    14: "DO Slot 8 Point 14 <- Tag_DO_11: Panel Door Amber LED - Fuel Gas Skid Low Header Pressure Warning (TB-08: 29-30).",
    15: "DO Slot 8 Point 15 <- LAMP_CR1: Panel Door Relay CR1 / Red LED L2 & L8 - Zone 1 Fire Confirmed Alarm (TB-08: 31-32).",
    16: "DO Slot 8 Point 16 <- LAMP_CR2: Panel Door Relay CR2 / Red LED L3 & L9 - Zone 2 Fire Confirmed Alarm (TB-08: 33-34).",
    17: "DO Slot 8 Point 17 <- LAMP_CR3: Panel Door Relay CR3 / Red LED L4 & L10 - Combustible Gas High Warning (TB-08: 35-36).",
    18: "DO Slot 8 Point 18 <- LAMP_CR4: Panel Door Relay CR4 / Red LED L5 & L11 - Combustible Gas High-High Trip (TB-08: 37-38).",
    19: "DO Slot 8 Point 19 <- LAMP_CR5: Panel Door Relay CR5 / Amber LED L6 & L12 - Hardware Wire-Break / System Trouble (TB-08: 39-40).",
    20: "DO Slot 8 Point 20 <- LAMP_CR6: Panel Door Relay CR6 / White LED L7 & L13 - Maintenance Inhibit Active (TB-08: 41-42).",
    21: (
        "DO Slot 8 Point 21 <- SD_GAS_GENERATORS (Fail-Safe Active-Low): Main Power Gas Turbine Generators Trip Relay (TB-08: 43-44). "
        "Normally energized (1); de-energizes (0) upon confirmed combustible gas migration or major plant fire."
    ),
    22: "DO Slot 8 Point 22 <- Tag_DO_15: Optical Xenon Flashing Strobe Beacon 24VDC - General Area Alarm (TB-08: 45-46).",
    23: "DO Slot 8 Point 23 <- PA_001_Process: Plant Public Address / Common Process Annunciator Alarm Relay (TB-08: 47-48).",
    24: "DO Slot 8 Point 24 <- SpareDO_24: Spare Digital Output Channel 24 (TB-08: 49-50).",
    25: "DO Slot 8 Point 25 <- SpareDO_25: Spare Digital Output Channel 25 (TB-08: 51-52).",
    26: "DO Slot 8 Point 26 <- SpareDO_26: Spare Digital Output Channel 26 (TB-08: 53-54).",
    27: "DO Slot 8 Point 27 <- SpareDO_27: Spare Digital Output Channel 27 (TB-08: 55-56).",
    28: "DO Slot 8 Point 28 <- SpareDO_28: Spare Digital Output Channel 28 (TB-08: 57-58).",
    29: "DO Slot 8 Point 29 <- SpareDO_29: Spare Digital Output Channel 29 (TB-08: 59-60).",
    30: "DO Slot 8 Point 30 <- ALM_H2S: Toxic Gas H2S High Concentration Warning Flasher (TB-08: 61-62).",
    31: "DO Slot 8 Point 31 <- ALM_SMOKE: Optical Smoke Detection Confirmed Siren / Strobe Beacon (TB-08: 63-64).",
}
