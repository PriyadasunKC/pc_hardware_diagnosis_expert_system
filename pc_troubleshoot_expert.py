#!/usr/bin/env python3
"""
PC TROUBLESHOOTING EXPERT SYSTEM
Uses pure Python Prolog parser to load pc_knowledge.pl
No SWI-Prolog installation required
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple

try:
    from experta import KnowledgeEngine, Rule, Fact
except ImportError:
    print("ERROR: experta not installed. Install with: pip install experta")
    sys.exit(1)


class PrologParser:
    """Pure Python Prolog knowledge base parser"""
    
    def __init__(self):
        self.facts = {}  # fact_name -> [list of arguments]
        self.rules = []  # [(head, body), ...]
        self.load_kb()
    
    def load_kb(self):
        """Load and parse pc_knowledge.pl"""
        if not os.path.exists('pc_knowledge.pl'):
            print("✗ Error: pc_knowledge.pl not found in current directory")
            return False
        
        try:
            with open('pc_knowledge.pl', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.parse_prolog(content)
            print(f"✓ Knowledge base loaded: {len(self.facts)} facts parsed")
            return True
        except Exception as e:
            print(f"✗ Error loading KB: {e}")
            return False
    
    def parse_prolog(self, content):
        """Parse Prolog facts and rules"""
        # Remove comments
        content = re.sub(r'%.*?$', '', content, flags=re.MULTILINE)
        
        # Split into clauses
        clauses = content.split('.')
        
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
            
            # Check if it's a rule (contains :-)
            if ':-' in clause:
                parts = clause.split(':-')
                head = parts[0].strip()
                body = parts[1].strip()
                self.rules.append((head, body))
            else:
                # It's a fact
                self.parse_fact(clause)
    
    def parse_fact(self, clause):
        """Parse and store a fact"""
        clause = clause.strip()
        if not clause or clause.startswith('%'):
            return
        
        # Extract predicate name and arguments
        match = re.match(r'(\w+)\s*\((.*)\)', clause)
        if match:
            predicate = match.group(1)
            args_str = match.group(2)
            
            if predicate not in self.facts:
                self.facts[predicate] = []
            
            # Store the full fact for later retrieval
            self.facts[predicate].append(args_str)
    
    def query(self, predicate: str, arg1: str = None) -> List[str]:
        """Query the knowledge base"""
        results = []
        
        if predicate in self.facts:
            for fact_args in self.facts[predicate]:
                # If querying with a specific first argument
                if arg1:
                    # Parse arguments
                    args = [a.strip().strip("'\"") for a in fact_args.split(',')]
                    if args and args[0] == arg1:
                        # Return second argument if it exists
                        if len(args) > 1:
                            results.append(args[1])
                else:
                    # Return all arguments
                    args = [a.strip().strip("'\"") for a in fact_args.split(',')]
                    if len(args) > 1:
                        results.append(args[1])
        
        return results
    
    def query_all(self, predicate: str) -> List[Tuple[str, ...]]:
        """Query and return all facts for a predicate"""
        results = []
        
        if predicate in self.facts:
            for fact_args in self.facts[predicate]:
                args = tuple(a.strip().strip("'\"") for a in fact_args.split(','))
                results.append(args)
        
        return results


class PCSymptom(Fact):
    """Fact representing a PC symptom"""
    pass


class BeepCode(Fact):
    """Fact representing BIOS beep codes"""
    pass


class PCTroubleshootingExpert(KnowledgeEngine):
    """Expert System for PC Hardware Troubleshooting"""
    
    def __init__(self):
        super().__init__()
        self.diagnosis = []
        self.solutions = []
        self.confidence_level = 0
        self.prolog = PrologParser()
    
    def query_component_failure(self, component: str) -> List[str]:
        """Query Prolog for component failure solutions"""
        return self.prolog.query('component_failure', component)
    
    def query_troubleshooting(self, issue_type: str, context: str) -> List[str]:
        """Query Prolog for troubleshooting steps"""
        predicate = f'troubleshoot_{issue_type}'
        
        # Get all facts for this predicate
        all_facts = self.prolog.query_all(predicate)
        results = []
        
        for fact in all_facts:
            if len(fact) > 1 and fact[0] == context:
                results.append(fact[1])
        
        return results
    
    def query_thermal_issue(self, component: str) -> List[str]:
        """Query Prolog for thermal issue solutions"""
        return self.prolog.query('thermal_issue', component)
    
    def query_recovery_procedure(self, issue: str) -> List[str]:
        """Query Prolog for recovery procedures"""
        return self.prolog.query('recovery_procedure', issue)
    
    # ========== BEEP CODE RULES ==========
    
    @Rule(BeepCode(pattern='1_short'))
    def beep_normal_boot(self):
        """Single short beep - System OK"""
        self.diagnosis.append("✓ System POST successful - Normal boot")
        self.confidence_level = 100
        self.solutions.append("No action needed - system is working normally")
    
    @Rule(BeepCode(pattern='continuous'))
    def beep_memory_power(self):
        """Continuous beeping - Memory or power issue"""
        self.diagnosis.append("⚠ CRITICAL: Memory or Power Supply issue detected")
        self.confidence_level = 95
        
        # Query Prolog for solutions
        memory_solutions = self.query_component_failure('memory')
        psu_solutions = self.query_component_failure('psu')
        
        if memory_solutions:
            self.solutions.extend(memory_solutions)
        if psu_solutions:
            self.solutions.extend(psu_solutions)
        
        if not memory_solutions and not psu_solutions:
            self.solutions.extend([
                "1. Check RAM modules - reseat or replace",
                "2. Test power supply unit (PSU)",
                "3. Check motherboard power connections"
            ])
    
    @Rule(BeepCode(pattern='1_long_2_short'))
    def beep_video_card(self):
        """1 long, 2 short - Video card error"""
        self.diagnosis.append("⚠ Video/Graphics card error detected")
        self.confidence_level = 90
        
        gpu_solutions = self.query_component_failure('gpu')
        
        if gpu_solutions:
            self.solutions.extend(gpu_solutions)
        else:
            self.solutions.extend([
                "1. Reseat graphics card firmly",
                "2. Check monitor cable connection",
                "3. Try different PCI-E slot"
            ])
    
    @Rule(BeepCode(pattern='1_long_3_short'))
    def beep_video_memory(self):
        """1 long, 3 short - Video memory error"""
        self.diagnosis.append("⚠ Video memory (VRAM) failure")
        self.confidence_level = 85
        
        gpu_solutions = self.query_component_failure('gpu')
        self.solutions.extend(gpu_solutions or [
            "1. Graphics card may need replacement",
            "2. Try integrated graphics if available",
            "3. Check GPU slot for physical damage"
        ])
    
    @Rule(BeepCode(pattern='3_short'))
    def beep_base_memory(self):
        """3 short beeps - Base 64K RAM failure"""
        self.diagnosis.append("⚠ Base Memory (64K RAM) failure")
        self.confidence_level = 85
        
        memory_solutions = self.query_component_failure('memory')
        self.solutions.extend(memory_solutions or [
            "1. RAM is likely defective",
            "2. Test with different RAM module",
            "3. Check RAM slot for bent pins"
        ])
    
    @Rule(BeepCode(pattern='2_short'))
    def beep_parity_error(self):
        """2 short beeps - Parity error"""
        self.diagnosis.append("⚠ Memory parity circuit failure")
        self.confidence_level = 85
        
        memory_solutions = self.query_component_failure('memory')
        self.solutions.extend(memory_solutions or [
            "1. Remove all RAM sticks",
            "2. Clean RAM contacts",
            "3. Test each stick individually"
        ])
    
    # ========== SYMPTOM-BASED RULES ==========
    
    @Rule(
        PCSymptom(issue='no_display'),
        PCSymptom(issue='fans_running')
    )
    def symptom_display_issue(self):
        """No display but fans running"""
        self.diagnosis.append("Display output issue - System powered but no video")
        self.confidence_level = 75
        
        display_steps = self.query_troubleshooting('display', 'no_signal')
        self.solutions.extend(display_steps or [
            "1. Check monitor power and cable",
            "2. Try different video output",
            "3. Reset CMOS/BIOS"
        ])
    
    @Rule(
        PCSymptom(issue='no_power'),
        PCSymptom(issue='no_lights')
    )
    def symptom_power_failure(self):
        """No power at all"""
        self.diagnosis.append("⚠ Complete power failure")
        self.confidence_level = 90
        
        post_steps = self.query_troubleshooting('post', 'failure')
        self.solutions.extend(post_steps or [
            "1. Check power cable and outlet",
            "2. Test PSU paperclip method",
            "3. Check motherboard shorts"
        ])
    
    @Rule(
        PCSymptom(issue='random_shutdown'),
        PCSymptom(issue='system_hot')
    )
    def symptom_overheating(self):
        """Random shutdowns with heat"""
        self.diagnosis.append("⚠ Overheating detected - Thermal protection triggered")
        self.confidence_level = 85
        
        cpu_thermal = self.query_thermal_issue('cpu')
        self.solutions.extend(cpu_thermal or [
            "1. Clean dust from fans and heatsinks",
            "2. Replace thermal paste on CPU",
            "3. Check CPU cooler mounting"
        ])
    
    @Rule(
        PCSymptom(issue='slow_boot'),
        PCSymptom(issue='disk_noise')
    )
    def symptom_hdd_failing(self):
        """Slow boot with disk noise"""
        self.diagnosis.append("Hard drive potentially failing")
        self.confidence_level = 70
        self.solutions.extend([
            "1. Backup data immediately",
            "2. Run disk check utility (chkdsk/fsck)",
            "3. Check S.M.A.R.T. status",
            "4. Consider SSD upgrade"
        ])
    
    @Rule(
        PCSymptom(issue='blue_screen'),
        PCSymptom(issue='memory_errors')
    )
    def symptom_ram_failure(self):
        """Blue screens with memory errors"""
        self.diagnosis.append("⚠ RAM failure detected")
        self.confidence_level = 80
        
        memory_solutions = self.query_component_failure('memory')
        self.solutions.extend(memory_solutions or [
            "1. Run Windows Memory Diagnostic",
            "2. Test each RAM stick individually",
            "3. Try different RAM slots"
        ])
    
    @Rule(
        PCSymptom(issue='random_restart'),
        PCSymptom(issue='power_fluctuation')
    )
    def symptom_psu_instability(self):
        """Random restarts with power fluctuations"""
        self.diagnosis.append("⚠ Power Supply Unit (PSU) instability")
        self.confidence_level = 75
        
        psu_solutions = self.query_component_failure('psu')
        self.solutions.extend(psu_solutions or [
            "1. Test PSU with paperclip method",
            "2. Check all power connections",
            "3. Verify PSU wattage is adequate"
        ])
    
    def get_diagnosis_report(self):
        """Generate diagnosis report"""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'diagnosis': self.diagnosis,
            'confidence': self.confidence_level,
            'recommended_actions': self.solutions,
            'knowledge_base_facts': len(self.prolog.facts)
        }
        return report


class PCDiagnosticInterface:
    """User interface for PC troubleshooting"""
    
    def __init__(self):
        self.engine = PCTroubleshootingExpert()
        self.beep_patterns = {
            '1': '1_short',
            '2': 'continuous',
            '3': '1_long_2_short',
            '4': '1_long_3_short',
            '5': '3_short',
            '6': '2_short',
        }
        
        self.symptoms = {
            '1': 'no_display',
            '2': 'no_power',
            '3': 'fans_running',
            '4': 'no_lights',
            '5': 'random_shutdown',
            '6': 'system_hot',
            '7': 'slow_boot',
            '8': 'disk_noise',
            '9': 'blue_screen',
            '10': 'memory_errors',
            '11': 'random_restart',
            '12': 'power_fluctuation'
        }
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("     PC TROUBLESHOOTING EXPERT SYSTEM")
        print("     Powered by Pure Python Prolog Parser + Experta")
        print("="*60)
        print("\n1. Diagnose by Beep Codes")
        print("2. Diagnose by Symptoms")
        print("3. Quick Diagnosis (Auto)")
        print("4. View Knowledge Base")
        print("5. Exit")
        print("-"*60)
    
    def get_beep_code(self):
        """Get beep code from user"""
        print("\n--- BEEP CODE PATTERNS ---")
        print("1. Single short beep (Normal POST)")
        print("2. Continuous beeping (Memory/Power)")
        print("3. 1 long, 2 short beeps (Video card error)")
        print("4. 1 long, 3 short beeps (Video memory error)")
        print("5. 3 short beeps (Base 64K RAM failure)")
        print("6. 2 short beeps (Parity error)")
        
        choice = input("\nSelect beep pattern (1-6): ")
        if choice in self.beep_patterns:
            return self.beep_patterns[choice]
        return None
    
    def get_symptoms(self):
        """Get symptoms from user"""
        print("\n--- PC SYMPTOMS CHECKLIST ---")
        print("Select all that apply (comma-separated):")
        print()
        for key, symptom in self.symptoms.items():
            print(f"{key:>2}. {symptom.replace('_', ' ').title()}")
        
        choices = input("\nEnter symptom numbers (e.g., 1,3,5): ").split(',')
        selected_symptoms = []
        for choice in choices:
            choice = choice.strip()
            if choice in self.symptoms:
                selected_symptoms.append(self.symptoms[choice])
        return selected_symptoms
    
    def run_diagnosis(self):
        """Run the diagnostic process"""
        while True:
            self.display_menu()
            choice = input("\nSelect option: ")
            
            if choice == '1':
                beep = self.get_beep_code()
                if beep:
                    self.engine.reset()
                    self.engine.declare(BeepCode(pattern=beep))
                    self.engine.run()
                    self.display_results()
                else:
                    print("Invalid selection.")
            
            elif choice == '2':
                symptoms = self.get_symptoms()
                if symptoms:
                    self.engine.reset()
                    for symptom in symptoms:
                        self.engine.declare(PCSymptom(issue=symptom))
                    self.engine.run()
                    self.display_results()
                else:
                    print("No symptoms selected.")
            
            elif choice == '3':
                print("\nRunning automatic diagnosis...")
                self.run_auto_diagnosis()
            
            elif choice == '4':
                self.view_knowledge_base()
            
            elif choice == '5':
                print("\nExiting PC Troubleshooting Expert System...")
                break
            
            else:
                print("\n⚠ Invalid option. Please try again.")
    
    def run_auto_diagnosis(self):
        """Automatic quick diagnosis"""
        print("\nAnswer the following questions:")
        
        self.engine.reset()
        
        if input("Is the PC turning on? (y/n): ").lower() == 'n':
            self.engine.declare(PCSymptom(issue='no_power'))
            self.engine.declare(PCSymptom(issue='no_lights'))
        else:
            if input("Is there display output? (y/n): ").lower() == 'n':
                self.engine.declare(PCSymptom(issue='no_display'))
            if input("Are fans running? (y/n): ").lower() == 'y':
                self.engine.declare(PCSymptom(issue='fans_running'))
            if input("Any beep codes? (y/n): ").lower() == 'y':
                beep = self.get_beep_code()
                if beep:
                    self.engine.declare(BeepCode(pattern=beep))
        
        self.engine.run()
        self.display_results()
    
    def display_results(self):
        """Display diagnosis results"""
        report = self.engine.get_diagnosis_report()
        
        print("\n" + "="*60)
        print("           DIAGNOSIS REPORT")
        print("="*60)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Confidence Level: {report['confidence']}%")
        print(f"KB Facts Loaded: {report['knowledge_base_facts']}")
        print("-"*60)
        
        if report['diagnosis']:
            print("\n📋 DIAGNOSIS:")
            for diag in report['diagnosis']:
                print(f"  • {diag}")
        else:
            print("\n✗ No specific issue identified")
        
        if report['recommended_actions']:
            print("\n🔧 RECOMMENDED SOLUTIONS:")
            for solution in report['recommended_actions']:
                print(f"  • {solution}")
        
        print("\n" + "="*60)
        
        if input("\nSave report to file? (y/n): ").lower() == 'y':
            self.save_report(report)
    
    def save_report(self, report):
        """Save diagnosis report to file"""
        filename = f"pc_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✓ Report saved to {filename}")
    
    def view_knowledge_base(self):
        """Display knowledge base information"""
        kb = self.engine.prolog
        
        print("\n" + "="*60)
        print("         PC TROUBLESHOOTING KNOWLEDGE BASE")
        print("="*60)
        
        print(f"\n📊 Statistics:")
        print(f"  • Total predicates: {len(kb.facts)}")
        print(f"  • Total rules: {len(kb.rules)}")
        
        print("\n📚 BEEP CODE MEANINGS (AMI BIOS):")
        print("  • 1 short: System OK")
        print("  • 2 short: Parity circuit failure")
        print("  • 3 short: Base 64K RAM failure")
        print("  • Continuous: Memory or video problem")
        
        print("\n📚 BEEP CODE MEANINGS (AWARD BIOS):")
        print("  • 1 long, 2 short: Video card error")
        print("  • 1 long, 3 short: Video card not detected")
        print("  • Continuous high: CPU overheating")
        
        print("\n⚠️ COMMON ISSUES:")
        print("  • No Display: Check cables, RAM, GPU")
        print("  • No Power: Check PSU, motherboard")
        print("  • Overheating: Clean fans, replace thermal paste")
        print("  • Random Crashes: Test RAM, check PSU")
        print("  • Slow Performance: Check HDD/SSD health")
        
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    print("\n🖥️  PC TROUBLESHOOTING EXPERT SYSTEM")
    print("    Pure Python Prolog Parser + Experta")
    print("-"*40)
    
    interface = PCDiagnosticInterface()
    try:
        interface.run_diagnosis()
    except KeyboardInterrupt:
        print("\n\nSystem interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()