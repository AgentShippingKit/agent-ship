#!/usr/bin/env python3
"""
Memory profiling script for AgentShip application.

This script profiles memory usage at different stages of application startup
to identify memory hotspots.

Usage:
    python scripts/profile_memory.py
    # Or with memory-profiler decorator:
    mprof run scripts/profile_memory.py
    mprof plot  # Generate visualization
"""

import os
import sys
import tracemalloc
import psutil
import gc
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def format_bytes(bytes_val):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"

def get_memory_usage():
    """Get current memory usage."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return {
        'rss': mem_info.rss,  # Resident Set Size (actual memory used)
        'vms': mem_info.vms,  # Virtual Memory Size
        'percent': process.memory_percent(),
    }

def print_memory_snapshot(label, snapshot):
    """Print memory snapshot statistics."""
    top_stats = snapshot.statistics('lineno')
    
    print(f"\n{'='*60}")
    print(f"Memory Snapshot: {label}")
    print(f"{'='*60}")
    
    print(f"\nTop 10 memory allocations:")
    for index, stat in enumerate(top_stats[:10], 1):
        print(f"{index}. {stat}")
    
    total = sum(stat.size for stat in top_stats)
    print(f"\nTotal allocated: {format_bytes(total)}")

def profile_startup():
    """Profile memory usage during application startup."""
    
    print("Starting memory profiling...")
    print(f"Initial memory: {format_bytes(get_memory_usage()['rss'])}")
    
    # Start tracing
    tracemalloc.start()
    
    snapshots = []
    memory_usage = []
    
    # Snapshot 1: Before any imports
    snapshot1 = tracemalloc.take_snapshot()
    snapshots.append(("Before imports", snapshot1))
    memory_usage.append(("Before imports", get_memory_usage()))
    
    # Snapshot 2: After basic imports
    print("\n[1/7] Importing basic modules...")
    import logging
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    snapshot2 = tracemalloc.take_snapshot()
    snapshots.append(("After basic imports", snapshot2))
    memory_usage.append(("After basic imports", get_memory_usage()))
    
    # Snapshot 3: After FastAPI
    print("[2/7] Importing FastAPI...")
    from fastapi import FastAPI
    app = FastAPI()
    
    snapshot3 = tracemalloc.take_snapshot()
    snapshots.append(("After FastAPI", snapshot3))
    memory_usage.append(("After FastAPI", get_memory_usage()))
    
    # Snapshot 4: After agent registry
    print("[3/7] Importing agent registry...")
    from src.agents.registry import AgentRegistry
    registry = AgentRegistry()
    
    snapshot4 = tracemalloc.take_snapshot()
    snapshots.append(("After registry", snapshot4))
    memory_usage.append(("After registry", get_memory_usage()))
    
    # Snapshot 5: After agent discovery
    print("[4/7] Discovering agents...")
    from src.agents.registry import discover_agents
    discover_agents()
    
    snapshot5 = tracemalloc.take_snapshot()
    snapshots.append(("After agent discovery", snapshot5))
    memory_usage.append(("After agent discovery", get_memory_usage()))
    
    # Snapshot 6: After importing Google ADK
    print("[5/7] Importing Google ADK...")
    from google.adk import Agent
    from google.adk.models.lite_llm import LiteLlm
    
    snapshot6 = tracemalloc.take_snapshot()
    snapshots.append(("After Google ADK", snapshot6))
    memory_usage.append(("After Google ADK", get_memory_usage()))
    
    # Snapshot 7: After importing Google Cloud libraries
    print("[6/7] Importing Google Cloud libraries...")
    try:
        from google.cloud import storage
        from google.cloud import secret_manager
        # Try importing unused ones to see their impact
        try:
            from google.cloud import bigtable
            print("  ⚠️  google-cloud-bigtable imported (not used in code)")
        except ImportError:
            pass
        try:
            from google.cloud import spanner
            print("  ⚠️  google-cloud-spanner imported (not used in code)")
        except ImportError:
            pass
        try:
            from google.cloud import aiplatform
            print("  ⚠️  google-cloud-aiplatform imported (not used in code)")
        except ImportError:
            pass
    except Exception as e:
        print(f"  Error importing Google Cloud: {e}")
    
    snapshot7 = tracemalloc.take_snapshot()
    snapshots.append(("After Google Cloud", snapshot7))
    memory_usage.append(("After Google Cloud", get_memory_usage()))
    
    # Snapshot 8: After full app initialization
    print("[7/7] Initializing full application...")
    from src.service.main import app as full_app
    
    snapshot8 = tracemalloc.take_snapshot()
    snapshots.append(("After full app init", snapshot8))
    memory_usage.append(("After full app init", get_memory_usage()))
    
    # Print summary
    print("\n" + "="*60)
    print("MEMORY USAGE SUMMARY")
    print("="*60)
    print(f"{'Stage':<30} {'RSS Memory':<20} {'Change':<15}")
    print("-"*60)
    
    prev_rss = memory_usage[0][1]['rss']
    for label, mem in memory_usage:
        rss = mem['rss']
        change = rss - prev_rss
        change_str = f"+{format_bytes(change)}" if change >= 0 else format_bytes(change)
        print(f"{label:<30} {format_bytes(rss):<20} {change_str:<15}")
        prev_rss = rss
    
    # Calculate differences
    print("\n" + "="*60)
    print("MEMORY INCREASES BY STAGE")
    print("="*60)
    
    for i in range(1, len(snapshots)):
        prev_label, prev_snap = snapshots[i-1]
        curr_label, curr_snap = snapshots[i]
        
        top_stats = curr_snap.compare_to(prev_snap, 'lineno')
        
        total_diff = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        if total_diff > 0:
            print(f"\n{prev_label} → {curr_label}: +{format_bytes(total_diff)}")
            print("Top 5 increases:")
            for stat in top_stats[:5]:
                if stat.size_diff > 0:
                    print(f"  {stat}")
    
    # Final memory usage
    final_mem = get_memory_usage()
    print("\n" + "="*60)
    print("FINAL MEMORY USAGE")
    print("="*60)
    print(f"RSS (Resident Set Size): {format_bytes(final_mem['rss'])}")
    print(f"VMS (Virtual Memory Size): {format_bytes(final_mem['vms'])}")
    print(f"Memory Percent: {final_mem['percent']:.2f}%")
    
    # Check against Heroku eco dyno limit
    eco_dyno_limit = 512 * 1024 * 1024  # 512MB
    if final_mem['rss'] > eco_dyno_limit:
        overage = final_mem['rss'] - eco_dyno_limit
        print(f"\n⚠️  WARNING: Exceeds eco dyno limit (512MB)")
        print(f"   Over by: {format_bytes(overage)} ({final_mem['rss'] / eco_dyno_limit * 100:.1f}%)")
    else:
        remaining = eco_dyno_limit - final_mem['rss']
        print(f"\n✅ Within eco dyno limit (512MB)")
        print(f"   Remaining: {format_bytes(remaining)}")
    
    tracemalloc.stop()
    
    return snapshots, memory_usage

if __name__ == "__main__":
    try:
        snapshots, memory_usage = profile_startup()
        print("\n✅ Profiling complete!")
        print("\nTo generate a visual plot, run:")
        print("  mprof run scripts/profile_memory.py")
        print("  mprof plot")
    except Exception as e:
        print(f"\n❌ Error during profiling: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

