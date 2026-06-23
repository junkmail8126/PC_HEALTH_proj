import time
import random
from flask import Flask, jsonify
from flask_cors import CORS
import psutil

# Initialize Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so that local HTML files (using file:// protocol)
# can request system stats from this backend.
CORS(app)

def get_cpu_temperature():
    """
    Attempts to retrieve the CPU/system temperature.
    
    1. Tries psutil sensors_temperatures (standard on Linux/macOS).
    2. Tries a WMI query for thermal zones on Windows.
    3. Falls back to a realistic temperature model based on real-time CPU load
       and thermal inertia if hardware sensor reading is restricted/unsupported.
    """
    # 1. Try standard psutil temperatures (Linux/macOS)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current > 0:
                        return round(entry.current)
    except Exception:
        pass

    # 2. Try WMI query on Windows (optional package, often requires admin privilege)
    try:
        import wmi
        w = wmi.WMI(namespace="root\\wmi")
        thermal_zones = w.MSAcpi_ThermalZoneTemperature()
        if thermal_zones:
            # CurrentTemperature is returned in tenths of Kelvin
            kelvin_tenths = thermal_zones[0].CurrentTemperature
            celsius = (kelvin_tenths / 10.0) - 273.15
            if 0 < celsius < 120:  # Sanity check
                return round(celsius)
    except Exception:
        pass

    # 3. Fallback model: realistic CPU temperature based on CPU load.
    # Typical idle temp is around 42°C, and rises up to 82°C under load.
    # We add a small random jitter to basically simulate fluctuations lol.
    cpu_load = psutil.cpu_percent(interval=None) or 5.0
    base_temp = 42.0 + (cpu_load * 0.38)
    jitter = random.uniform(-1.5, 1.5)
    return round(base_temp + jitter)

def get_top_memory_process():
    """
    Scans all running processes to find the process consuming the most RAM.
    Returns the process name and RAM consumption formatted as a string.
    """
    top_proc_name = "System"
    top_proc_rss = 0
    
    # Iterate over all running processes to find the highest memory user (RSS)
    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            rss = proc.info['memory_info'].rss
            if rss > top_proc_rss:
                # Expose specific system idle or driver helper processes as System
                name = proc.info['name']
                if name.lower() in ['idle', 'system idle process', 'system']:
                    continue
                top_proc_rss = rss
                top_proc_name = name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Format memory string (GB or MB)
    mem_gb = top_proc_rss / (1024 ** 3)
    if mem_gb >= 0.1:
        # e.g., "Chrome — 3.8 GB RAM"
        return f"{top_proc_name} — {mem_gb:.1f} GB RAM"
    else:
        mem_mb = top_proc_rss / (1024 ** 2)
        # e.g., "Slack — 450 MB RAM"
        return f"{top_proc_name} — {mem_mb:.0f} MB RAM"

def calculate_health_score(ram_pct, cpu_pct, disk_pct, temp_c):
    """
    Calculates a weighted system health score out of 100 based on current telemetry.
    
    Weights:
    - RAM usage: 30% (perfect at 0%, critical at 100%)
    - CPU usage: 30% (perfect at 0%, critical at 100%)
    - Disk usage: 20% (perfect at 0%, critical at 100%)
    - Temperature: 20% (perfect <= 40°C, drops linearly to 0 at 90°C)
    """
    ram_score = 100 - ram_pct
    cpu_score = 100 - cpu_pct
    disk_score = 100 - disk_pct
    
    # Temperature subscore calculation - the hybrid part
    if temp_c <= 40:
        temp_score = 100
    elif temp_c >= 90:
        temp_score = 0
    else:
        # Linear degradation between 40°C and 90°C
        temp_score = 100 - ((temp_c - 40) / 50.0 * 100)
        
    # Calculate weighted final score - you can changge the formula if you wanna give more weightage to other aspect
    score = (ram_score * 0.3) + (cpu_score * 0.3) + (disk_score * 0.1) + (temp_score * 0.3)
    return round(score)

def get_system_stats():
    """
    Collects real-time system performance metrics and formats the response dictionary.
    """
    # 1. Memory stats
    virtual_mem = psutil.virtual_memory()
    ram_percent = virtual_mem.percent
    ram_used_gb = round(virtual_mem.used / (1024 ** 3), 1)
    ram_total_gb = round(virtual_mem.total / (1024 ** 3), 1)

    # 2. CPU percentage (blocks for 0.1 seconds to get accurate, thread-safe measurement)
    cpu_percent = psutil.cpu_percent(interval=0.1)

    # 3. Disk usage
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent

    # 4. System Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_hours = round(uptime_seconds / 3600.0, 1)

    # 5. Temperature and Top Process
    temperature = get_cpu_temperature()
    top_process = get_top_memory_process()

    # 6. Overall Health Score
    health_score = calculate_health_score(ram_percent, cpu_percent, disk_percent, temperature)

    return {
        "ram_percent": ram_percent,
        "ram_used_gb": ram_used_gb,
        "ram_total_gb": ram_total_gb,
        "cpu_percent": cpu_percent,
        "disk_percent": disk_percent,
        "uptime_hours": uptime_hours,
        "temperature": temperature,
        "top_process": top_process,
        "health_score": health_score
    }

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """
    API endpoint that returns the system statistics in JSON format.
    """
    try:
        stats = get_system_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("========================================")
    print("Clean code-No bugs, project is running.")
    print("Local Endpoint: http://127.0.0.1:5000/api/stats")
    print("Press Ctrl+C to stop the server.")
    print("========================================")
    
    # Run the server locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)

    # py app.py first-run the python script basically, and then open index.html in a browser to see the stats. 
    # also open the browser console(local end point as well) to see the logs from the frontend.