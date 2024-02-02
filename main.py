import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil

class CPUUsageMonitor:
    def __init__(self, root):
        self.root = root
        self.cpu_usage = []  # CPU usage data
        self.memory_usage = []  # Memory usage data
        self.init_ui()

    def init_ui(self):
        self.root.title("System Monitor")
        self.fig = Figure(figsize=(10, 8), dpi=100)

        # CPU Usage plot
        self.cpu_plot = self.fig.add_subplot(2, 1, 1)
        # Memory Usage plot
        self.memory_plot = self.fig.add_subplot(2, 1, 2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.update_plot()

    def read_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        if len(self.cpu_usage) >= 10:  # keep last 10 readings
            self.cpu_usage.pop(0)
        self.cpu_usage.append(cpu_usage)

    def read_memory_usage(self):
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        if len(self.memory_usage) >= 10:  # keep last 10 readings
            self.memory_usage.pop(0)
        self.memory_usage.append(memory_usage)

    def update_plot(self):
        self.read_cpu_usage()
        self.read_memory_usage()
        
        # Update CPU Usage plot
        self.cpu_plot.clear()
        self.cpu_plot.plot(self.cpu_usage, '-o', color='blue')
        self.cpu_plot.set_title("CPU Usage Over Time")
        self.cpu_plot.set_xlabel("Samples")
        self.cpu_plot.set_ylabel("CPU Usage (%)")
        self.cpu_plot.set_ylim(0, 100)

        # Update Memory Usage plot
        self.memory_plot.clear()
        self.memory_plot.plot(self.memory_usage, '-o', color='red')
        self.memory_plot.set_title("Memory Usage Over Time")
        self.memory_plot.set_xlabel("Samples")
        self.memory_plot.set_ylabel("Memory Usage (%)")
        self.memory_plot.set_ylim(0, 100)

        self.canvas.draw_idle()
        self.root.after(1000, self.update_plot)

def main():
    root = tk.Tk()
    app = CPUUsageMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
