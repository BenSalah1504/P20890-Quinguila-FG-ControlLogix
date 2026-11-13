# Prompt: Convert the Quinguila Fire and Gas Ladder Program to RSLogix 5000 V17

You are converting an existing GE Fanuc VersaMax Fire and Gas PLC application, authored in Proficy Machine Edition 3.00 SP6, into an importable **RSLogix 5000 / Studio 5000 version 17** `.L5X` controller export.

The goal is an exact behavioral ladder conversion, not a redesign or a simplified recreation. Reproduce every source rung's Boolean behavior, rung order, execution order, latching, output polarity, timing, arithmetic behavior, and tag intent using instructions and data types that are appropriate for RSLogix 5000 v17.

## Source folder

Review every relevant item under:

`C:\Users\yassine\Desktop\Ladder_project`

Use this source precedence when evidence differs:

1. The graphical rungs in `LAD\*.pdf` and the corresponding source blocks in `DOC\P20890_Angola.zip` -> `P20890_Angola\1\Additional Files\Program Data\BldFiles.zip`.
2. `var.xml` for source symbol names, GE addresses, data types, initial values, retentive status, and descriptions.
3. `DOC\P20890-Functional & program description.docx` and `DOC\F&G Operating Procedure.docx` for intended sequence-of-operation context.
4. `DOC\DE-GN-FG-SAF-74-1001.xlsx` (cause-and-effect matrix), `Bit_Alarm.xlsx`, `DOC\Shutdown logic diagram.pdf`, and `DOC\Terminal block connections.pdf` as cross-checks.
5. `DOL_Starter_Example_V17.L5X` as the known-good RSLogix 5000 v17 XML/RLL syntax and project-structure reference. Do not overwrite, repurpose, or copy its DOL-starter logic.

The version history in `_MAIN.pdf` records late June 2003 changes. When an older description or matrix conflicts with a source rung, retain the actual rung behavior and list the conflict in the conversion report; do not silently "correct" the legacy program.

## Required source routines

Convert every routine in the `LAD` folder, retaining the source routine structure and scan order. The source set contains:

`_MAIN`, `Init`, `Input`, `DI_1`, `DI_2`, `AI_1`, `AI_2`, `AI_3`, `Ai_AL_1`, `Ai_AL_2`, `Ai_AL_3`, `CalcVa1`, `CalcVa2`, `CalcVa3`, `Vote_1`, `Logic`, `CE_LOG`, `Sound`, `Output`, `Shutdow`/`Shutdown`, `Protect`, `Indicat`, `Loc_Al`, and `FLT_1`.

Preserve the order of routine calls and of rungs inside each routine. Preserve the source spelling consistently where `Shutdow` is the actual called routine name; do not leave a mismatched JSR target because the PDF filename uses `Shutdown`.

## Conversion requirements

- Create one complete `.L5X` controller export targeting **SoftwareRevision/MajorRev 17**. Use only instructions, XML constructs, and RLL syntax supported by RSLogix 5000 v17.
- Because the target Allen-Bradley controller model and I/O chassis are not supplied, do not invent a production I/O tree, module catalog numbers, slot addresses, or `Local:x` aliases. Follow the supplied Emulator-based V17 example for a controller-importable, hardware-neutral project. Represent field I/O as clearly named controller tags, then supply an I/O mapping table so an integrator can alias them to real modules later.
- Import all usable symbols from `var.xml`. Preserve each valid source symbol name, description, source GE address, source data type, initial value, and retentive intent. Put the GE address in the tag description or a traceability table. If a source symbol cannot be a Logix tag name or must change type, make the smallest safe change and document it explicitly.
- Do not collapse the source into a few generic arrays, a single state machine, Structured Text, or AOIs. The deliverable must be readable, conventional Logix **ladder** with source-equivalent routines and meaningful named tags.
- Preserve source comments and add concise rung comments identifying the source routine/rung and the GE address(es) involved. Exclude QuickPanel graphics/object references; preserve the associated PLC/HMI command, status, reset, inhibit, acknowledge, and manual-trip tags as controller tags.
- Model the main routine so `Init` runs only on the Logix first scan (`S:FS` or an equivalent one-scan implementation), while input, logic, and output sections execute in the same source sequence on every subsequent scan.

### Instruction and data-semantics rules

Translate the source instruction intent rather than copying GE mnemonics:

- GE normally-open and normally-closed contacts -> `XIC` and `XIO` respectively.
- GE ordinary coils -> `OTE`; set/reset coils -> `OTL`/`OTU`, while preserving source reset dominance and rung ordering.
- GE positive-edge/pulse coils -> an explicit RSLogix v17-safe one-shot design (`ONS` with a dedicated storage bit, plus the correct output instruction) that has the same scan behavior.
- GE moves, clear operations, integer/real conversion, comparisons, and arithmetic -> the appropriate Logix `MOV`, `CLR`, conversion, compare, and math instructions. Keep every intermediate calculation where it affects truncation, rounding, overflow, sign, or timing behavior. In particular, do not replace the `CalcVa1`, `CalcVa2`, or `CalcVa3` multi-step scaling rungs with a rounded engineering-units shortcut.
- Determine the exact semantics of each source `ONDTR_TENTHS`, `TMR_TENTHS`, `UPCTR`, and related timer/counter instruction before mapping it. Do not assume they are all ordinary `TON`s. Preserve enable/reset/retentive behavior and convert the source 0.1-second preset basis to Logix milliseconds without changing the actual delay.
- Preserve `INT` versus `REAL` signal paths and setpoints. The analog routines contain both integer and real paths; do not convert the whole application to `REAL`.
- Preserve all latch/reset/inhibit logic, including alarm and cause-and-effect variants such as `_AL`, `_ALI`, `_ALH`, `_ALHI`, `_ALL`, `_ALLI`, `_INH`, `_OC`, `_SC`, `_FLT1`, `_FLT2`, `_FRUP`, `_INT`, and `_MT`.
- Preserve source output electrical polarity. This is especially important for the source's inverted/active-low shutdown behavior, including `PumpShutdown` `%Q00008`; a visually similar `OTE` is not acceptable if it reverses the field result.
- Preserve the 2-second pump-B start/stop pulses, 30-second and later 60-second pump-delay sequence, the three start attempts, the deluge-failed-to-release indication, sound/mute/reset behavior, and all voting paths exactly as evidenced by the final source rungs.

## Deliverables

Create these files in the project root:

1. `P20890_Angola_RSLogix5000_V17.L5X` - the complete importable v17 controller export.
2. `P20890_Angola_Conversion_Traceability.md` - a compact but complete conversion report containing:
   - the controller/task/program/routine structure and execution order;
   - a GE-to-Logix instruction mapping, including each timer/counter choice;
   - a source-routine/rung-to-Logix-routine/rung cross-reference, with an explanation for every non-literal transformation;
   - a GE `%I`/`%AI`/`%Q`/`%M`/`%R`/`%T` address to Logix tag mapping;
   - discrepancies among the latest source rungs and older supporting documents, and the resolution used;
   - required field I/O aliasing and commissioning items that cannot be completed without target hardware details.
3. `P20890_Angola_Test_Matrix.md` - test cases and expected outcomes for startup/first-scan reset, each analog scaling and alarm/fault path, input inhibits, latches and reset, voting, every cause-and-effect output, pump A/B sequence and retry timers, sound/mute, output line-fault checks, and active-low shutdown outputs.

## Mandatory validation before delivery

- Confirm all 24 source routines exist in the L5X and every source rung has a traceable corresponding Logix rung or documented semantic equivalent.
- Confirm that every referenced tag exists, has an appropriate compatible type, and has no unresolved aliases or external references.
- Validate the `.L5X` as well-formed XML and check it against the V17-style structure/syntax demonstrated by `DOL_Starter_Example_V17.L5X`.
- If RSLogix 5000/Studio 5000 v17 is available, import the L5X and resolve every import/verify error. If it is unavailable, state that limitation plainly and do not claim the file was imported successfully.
- Walk through the test matrix against the ladder logic and inspect the safety-critical sequences twice: gas/fire shutdown, output inhibit, ESD valve behavior, deluge pump start/retry/stop, and output polarity.

## Safety and reporting constraints

This is a Fire and Gas / emergency-shutdown application. Do not claim safety certification, SIL compliance, field readiness, or functional-test completion based solely on the conversion. Preserve the legacy behavior exactly, call out ambiguities or source conflicts, and require independent engineering review, I/O checkout, and site acceptance testing before any deployment.

Do not produce a partial skeleton, pseudocode, screenshots, placeholder rungs, or a generic demo. Deliver the complete rung-for-rung RSLogix 5000 V17 ladder conversion and its traceability/test documentation.
