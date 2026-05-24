% PC Troubleshooting Knowledge Base
% This Prolog file contains facts and rules about PC hardware issues
% Used by the Python expert system for complex reasoning

% ===== PC COMPONENTS =====
component(motherboard).
component(cpu).
component(ram).
component(gpu).
component(psu).
component(hdd).
component(ssd).
component(cooling_fan).
component(case_fan).

% ===== BEEP CODE PATTERNS =====
% Different BIOS manufacturers have different beep codes
beep_code(ami_bios, 1_short, 'DRAM refresh failure').
beep_code(ami_bios, 2_short, 'Parity circuit failure').
beep_code(ami_bios, 3_short, 'Base 64K RAM failure').
beep_code(ami_bios, 4_short, 'System timer failure').
beep_code(ami_bios, 5_short, 'Processor failure').
beep_code(ami_bios, 6_short, 'Keyboard controller failure').
beep_code(ami_bios, 7_short, 'Virtual mode exception error').
beep_code(ami_bios, 8_short, 'Display memory failure').
beep_code(ami_bios, continuous, 'Memory or video problem').

beep_code(award_bios, 1_long_2_short, 'Video card error').
beep_code(award_bios, 1_long_3_short, 'Video card not detected').
beep_code(award_bios, continuous_high, 'CPU overheating').
beep_code(award_bios, repeating_high_low, 'CPU issue').

beep_code(phoenix_bios, '1-1-3', 'CMOS read/write failure').
beep_code(phoenix_bios, '1-1-4', 'ROM BIOS checksum failure').
beep_code(phoenix_bios, '1-2-1', 'Programmable interval timer failure').
beep_code(phoenix_bios, '1-2-2', 'DMA initialization failure').

% ===== COMPONENT FAILURES AND SOLUTIONS =====
component_failure(memory, 'Remove all RAM sticks and test one at a time').
component_failure(memory, 'Clean RAM contacts with isopropyl alcohol').
component_failure(memory, 'Try different RAM slots').
component_failure(memory, 'Check for incompatible RAM speeds').

component_failure(gpu, 'Reseat graphics card firmly').
component_failure(gpu, 'Check PCIe power connectors').
component_failure(gpu, 'Test in different PCIe slot').
component_failure(gpu, 'Update or rollback GPU drivers').

component_failure(psu, 'Test with paperclip method').
component_failure(psu, 'Check all power connections').
component_failure(psu, 'Verify wattage meets system requirements').
component_failure(psu, 'Look for bulging capacitors').

component_failure(motherboard, 'Check for bent CPU socket pins').
component_failure(motherboard, 'Inspect for burn marks or damage').
component_failure(motherboard, 'Reset CMOS battery').
component_failure(motherboard, 'Update BIOS to latest version').

% ===== SYMPTOM DIAGNOSIS RULES =====
% Rule: No display troubleshooting
troubleshoot_display(no_signal, 'Check monitor power cable and button').
troubleshoot_display(no_signal, 'Try different video cable (HDMI/DP/VGA)').
troubleshoot_display(no_signal, 'Connect to integrated graphics if available').
troubleshoot_display(no_signal, 'Clear CMOS to reset display settings').

% Rule: System won't POST
troubleshoot_post(failure, 'Remove all unnecessary components').
troubleshoot_post(failure, 'Test with minimum configuration (CPU, 1 RAM, PSU)').
troubleshoot_post(failure, 'Check 24-pin and CPU power connections').
troubleshoot_post(failure, 'Inspect for motherboard shorts').

% Rule: Thermal issues
thermal_issue(cpu, 'Check thermal paste application').
thermal_issue(cpu, 'Verify CPU cooler is properly mounted').
thermal_issue(cpu, 'Monitor CPU temperature in BIOS').
thermal_issue(cpu, 'Check for dust buildup in heatsink').

thermal_issue(gpu, 'Clean GPU fans and heatsink').
thermal_issue(gpu, 'Check case airflow direction').
thermal_issue(gpu, 'Consider undervolting GPU').
thermal_issue(gpu, 'Replace thermal pads if old').

% ===== DIAGNOSTIC PATHS =====
% Complex diagnostic reasoning
diagnose_issue(Symptoms, Issue) :-
    member(no_power, Symptoms),
    member(no_lights, Symptoms),
    Issue = power_supply_failure.

diagnose_issue(Symptoms, Issue) :-
    member(power_on, Symptoms),
    member(no_display, Symptoms),
    member(beeping, Symptoms),
    Issue = ram_or_gpu_failure.

diagnose_issue(Symptoms, Issue) :-
    member(random_shutdown, Symptoms),
    member(high_temp, Symptoms),
    Issue = overheating.

diagnose_issue(Symptoms, Issue) :-
    member(slow_performance, Symptoms),
    member(disk_noise, Symptoms),
    Issue = hdd_failure.

% ===== COMPATIBILITY CHECKS =====
compatible_ram(ddr4, ddr4_slot).
compatible_ram(ddr5, ddr5_slot).
incompatible_ram(ddr4, ddr5_slot).
incompatible_ram(ddr5, ddr4_slot).

compatible_gpu(pcie_3, pcie_3_slot).
compatible_gpu(pcie_4, pcie_4_slot).
compatible_gpu(pcie_3, pcie_4_slot).  % Backward compatible
compatible_gpu(pcie_4, pcie_3_slot).  % Works but reduced speed

% ===== PSU WATTAGE REQUIREMENTS =====
min_psu_wattage(basic_office, 300).
min_psu_wattage(gaming_mid, 550).
min_psu_wattage(gaming_high, 750).
min_psu_wattage(workstation, 850).

component_power_draw(cpu_low, 65).
component_power_draw(cpu_mid, 95).
component_power_draw(cpu_high, 125).
component_power_draw(gpu_low, 75).
component_power_draw(gpu_mid, 200).
component_power_draw(gpu_high, 350).

% ===== BOOT SEQUENCE =====
boot_stage(1, 'Power supply test').
boot_stage(2, 'CPU initialization').
boot_stage(3, 'Memory detection').
boot_stage(4, 'Video initialization').
boot_stage(5, 'Keyboard detection').
boot_stage(6, 'Drive detection').
boot_stage(7, 'OS boot loader').

% ===== COMMON FIX PRIORITY =====
fix_priority(reseat_components, 1).
fix_priority(clear_cmos, 2).
fix_priority(test_minimal_config, 3).
fix_priority(swap_components, 4).
fix_priority(update_firmware, 5).

% ===== RULES FOR COMPLEX DIAGNOSTICS =====
% Rule: Determine if PSU is adequate
adequate_psu(SystemWattage, PSUWattage) :-
    Overhead is SystemWattage * 1.2,  % 20% overhead recommended
    PSUWattage >= Overhead.

% Rule: Check component compatibility
check_compatibility(Component1, Component2, Result) :-
    compatible_ram(Component1, Component2),
    Result = compatible.

check_compatibility(Component1, Component2, Result) :-
    incompatible_ram(Component1, Component2),
    Result = incompatible.

% Rule: Progressive troubleshooting
troubleshooting_sequence(Step, Action) :-
    fix_priority(Action, Step).

% Rule: Beep pattern interpretation
interpret_beeps(Pattern, Manufacturer, Meaning) :-
    beep_code(Manufacturer, Pattern, Meaning).

% ===== HELPER PREDICATES =====
% Check if component needs replacement
needs_replacement(Component) :-
    component_failure(Component, _),
    \+ fixable(Component).

fixable(ram).
fixable(gpu).
fixable(hdd).

% Emergency recovery procedures
recovery_procedure(no_boot, 'Remove CMOS battery for 5 minutes').
recovery_procedure(corrupt_bios, 'Use BIOS recovery jumper or button').
recovery_procedure(boot_loop, 'Boot to safe mode or recovery environment').

% ===== END OF KNOWLEDGE BASE =====
