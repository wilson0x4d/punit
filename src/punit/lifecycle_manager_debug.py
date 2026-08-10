# Quick debug test
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.lifecycle import LifecycleTests as lt

# Check module-level state
print("_per_run_names.names after import:", getattr(lt, '_per_run_names', 'NOT FOUND'))
