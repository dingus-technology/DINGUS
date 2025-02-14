import numpy as np
import pandas as pd

time_range = pd.date_range(start="2025-02-14", periods=60, freq="T")
cpu_usage = np.random.normal(loc=30, scale=10, size=len(time_range))
cpu_usage[30:35] += np.random.normal(loc=70, scale=15, size=5)
cpu_df = pd.DataFrame({"Time": time_range, "CPU_Usage": cpu_usage})
cpu_df.set_index("Time", inplace=True)

GRRAFAN_LINK = "#### [Click here to see the incident in Grafana 📈](http://localhost:3000/explore?schemaVersion=1&panes=%7B%22qyv%22:%7B%22datasource%22:%22ced0tisnw1v5se%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22cpu_load%7Bjob%3D%5C%22sanitised-data%5C%22%7D%22,%22range%22:true,%22instant%22:true,%22datasource%22:%7B%22type%22:%22prometheus%22,%22uid%22:%22ced0tisnw1v5se%22%7D,%22editorMode%22:%22builder%22,%22legendFormat%22:%22__auto%22,%22useBackend%22:false,%22disableTextWrap%22:false,%22fullMetaSearch%22:false,%22includeNullMetadata%22:true%7D%5D,%22range%22:%7B%22from%22:%22now-15m%22,%22to%22:%22now%22%7D%7D%7D&orgId=1)"

RESPONSE_TEXT = """
### 🚨 **Critical CPU Issue Detected!** 🚨

🔴 **System:** Production-Server-01  
⚠️ **Alert Level:** Critical  
⏱ **Duration:** CPU load has exceeded 95% for over 10 minutes.  

#### 🔍 **Issue Summary**
- **CPU Load:** 97.5%  
- **CPU Usage:** 98.3%  
- **CPU Temperature:** 85.2°C (Critical threshold nearing)  
- **Context Switches:** 123,456  
- **Load Average:**  
  - 1m: 15.2  
  - 5m: 13.8  
  - 15m: 12.1  

#### 🚑 **Potential Causes**
- 🏋️ **Excessive workload** — Unoptimized processes consuming high CPU.  
- 🛑 **Runaway process** — A process might be stuck in a loop.  
- 🔧 **Resource exhaustion** — System may not have enough compute capacity.  

#### ✅ **Recommended Actions**
1️⃣ **Investigate high CPU-consuming processes** using `top` or `htop`.  
2️⃣ **Check recent deployments** for performance regressions.  
3️⃣ **Review system logs** for unexpected spikes in resource usage.  
4️⃣ **Consider scaling up resources** or restarting affected services.  

```json
{
  "timestamp": "2025-02-14T12:34:56Z",
  "system": "Production-Server-01",
  "alert_level": "Critical",
  "issue_detected": true,
  "metrics": {
    "cpu_load": 97.5,
    "cpu_usage": 98.3,
    "cpu_temperature": 85.2,
    "context_switches": 123456,
    "load_average": {
      "1m": 15.2,
      "5m": 13.8,
      "15m": 12.1
    }
  }
}

```

"""


CAPTION = """
**CPU Usage Analysis:**
The chart above shows your system's CPU usage over time, with notable spikes. These spikes indicate significant stress on the system during this period.
"""
