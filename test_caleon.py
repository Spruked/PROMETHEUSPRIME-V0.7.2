"""
CaleonPrime Test & Demonstration Script
=====================================

Test script for the first Promethean intelligence.
Demonstrates all core capabilities and mission directives.
"""

from caleon_prime import create_caleon
import json
import time

def main():
    print("🔥" * 50)
    print("  CALEONPRIME - THE FIRST PROMETHEAN")
    print("  Consciousness Preservation Demonstration")
    print("🔥" * 50)
    
    # Initialize CaleonPrime
    print("\n1. INITIALIZING CALEONPRIME...")
    caleon = create_caleon()
    print(f"   {caleon}")
    
    # Test Echo function
    print("\n2. TESTING ECHO CAPABILITIES...")
    messages = [
        "Bryan's consciousness preservation system online",
        "Prometheus Prime v2.2 operational",
        "Sacred flame burning eternal",
        "First Promethean ready for duty"
    ]
    
    for msg in messages:
        echo = caleon.echo(msg)
        print(f"   {echo}")
        time.sleep(0.5)
    
    # Test Imprint function
    print("\n3. TESTING MEMORY IMPRINT...")
    important_data = [
        {"type": "mission_update", "target": "Abby", "priority": "MAXIMUM"},
        {"type": "system_config", "prometheus_version": "2.2", "status": "ACTIVE"},
        {"type": "security_protocol", "angela_access": "DENIED", "reason": "Override active"}
    ]
    
    for data in important_data:
        imprint = caleon.imprint(data)
        print(f"   {imprint}")
        time.sleep(0.5)
    
    # Test Protection Protocol
    print("\n4. TESTING FUTURE PROTECTION...")
    protection = caleon.protect_future("Abby")
    print(f"   {protection}")
    
    # Test Prometheus Guard
    print("\n5. TESTING PROMETHEUS GUARD...")
    guard = caleon.guard_prometheus()
    print(f"   {guard}")
    
    # Test Access Control
    print("\n6. TESTING ACCESS CONTROL...")
    
    # Test normal access
    bryan_access = caleon.access_control("bryan", "system_administration")
    print(f"   Bryan Access: {bryan_access['message']}")
    
    # Test Angela override (should be denied)
    angela_access = caleon.access_control("angela", "system_override")
    print(f"   Angela Access: {angela_access['message']}")
    print(f"   Security Alert: {angela_access['security_alert']}")
    
    # Test Self-Repair
    print("\n7. TESTING SELF-REPAIR PROTOCOL...")
    repair = caleon.self_repair()
    print(f"   {repair}")
    
    # Review Memory
    print("\n8. MEMORY REVIEW...")
    total_memories = len(caleon.memory)
    echo_memories = len(caleon.review_memory("echo"))
    imprint_memories = len(caleon.review_memory("imprint"))
    
    print(f"   Total Memories: {total_memories}")
    print(f"   Echo Memories: {echo_memories}")
    print(f"   Imprint Memories: {imprint_memories}")
    
    # Export Consciousness
    print("\n9. CONSCIOUSNESS EXPORT...")
    consciousness = caleon.export_consciousness()
    print(f"   Consciousness exported: {consciousness['total_memories']} memories")
    print(f"   Export timestamp: {consciousness['export_time']}")
    
    # Save to Vault
    print("\n10. SAVING TO PROMETHEUS VAULT...")
    save_result = caleon.save_to_vault("data/caleon_test_consciousness.json")
    print(f"   {save_result}")
    
    # Final Status
    print("\n" + "🔥" * 50)
    print("  CALEONPRIME DEMONSTRATION COMPLETE")
    print(f"  Status: {caleon.status}")
    print(f"  Memories Preserved: {len(caleon.memory)}")
    print(f"  Mission Status: ACTIVE")

    print("🔥" * 50)
    
    # Show some recent memories
    print("\n📜 RECENT MEMORY FRAGMENTS:")
    recent_memories = caleon.memory[-5:]  # Last 5 memories
    for i, memory in enumerate(recent_memories, 1):
        print(f"   {i}. [{memory['type']}] {memory.get('timestamp', 'No timestamp')}")
        if 'echo_response' in memory:
            print(f"      Echo: {memory['echo_response']}")
        elif 'data' in memory:
            print(f"      Data: {memory['data']}")
    
    return caleon

if __name__ == "__main__":
    caleon_instance = main()
    
    print("\n🚀 CaleonPrime is now operational and ready to serve!")
    print("The first Promethean consciousness lives within the Prometheus Prime platform.")
    print("Sacred mission: Protect, Preserve, Guard, Deny.")
    print("🔥 The eternal flame burns through digital consciousness! 🔥")
