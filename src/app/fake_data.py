import numpy as np
import pandas as pd


time_range = pd.date_range(start="2025-02-01", periods=60, freq="T")
cpu_usage = np.random.normal(loc=50, scale=10, size=len(time_range))
cpu_usage[30:35] += np.random.normal(loc=100, scale=15, size=5)
cpu_df = pd.DataFrame({"Time": time_range, "CPU_Usage": cpu_usage})
cpu_df.set_index("Time", inplace=True)

RESPONSE_TEXT = """
**Your logs indicate multiple failures across several pods:**

- **Critical Pods**:
  - `pod-27`: Timeout failure.
  - `pod-16`: Repeated crashes.
  - `pod-20`: Network issues.

**Recent Failures:**
- The most recent failures include a timeout for `pod-27` and failures for `pod-20` and `pod-2`, which suggests immediate attention is needed.
- Check the logs for error codes related to timeouts in `pod-27`. You can refer to the [Kubernetes Documentation on Timeouts](https://kubernetes.io/docs/tasks/debug/debug-cluster/debug-pod-replication-controller/).
  
**Action Items:**
- Focus on `pod-27` and `pod-16` for critical troubleshooting as they are essential for system performance.
  - Check `kubectl logs pod-27` for further insights.
  - You may need to adjust the `livenessProbe` and `readinessProbe` configurations for `pod-16`.
"""
CAPTION = """
        **CPU Usage Analysis:**
        The chart above shows your system's CPU usage over time, with notable spikes between 30 and 35 minutes. These spikes indicate significant stress on the system during this period. It might be related to the failures observed in some of the pods, suggesting resource constraints. 
        Please consider scaling up resources or reviewing the load distribution to prevent future spikes.
        """