import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import psutil
import pynvml

class CPUUsageMonitor:
    def __init__(self, root):
        self.root = root
        self.after_id = None  # Initialize a variable to store the 'after' ID

        # GPU Usage
        try:
            pynvml.nvmlInit()
            self.gpu_available = True
            self.device_count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError as error:
            print(f"Failed to initialize NVML: {error}")
            self.gpu_available = False
        
        self.gpu_memory_usage = []  # This will hold the last 10 GPU memory usage percentages

        # CPU Usage
        self.cpu_usage = []  # This will now hold the last 10 CPU usage percentages

        # Memory Usage
        self.memory_usage = []  # This will hold the last 10 memory usage percentages

        # Disk Usage
        self.diskusage = psutil.disk_usage('/')
        self.sizes = [self.diskusage.used, self.diskusage.free]
        self.labels = ['Used', 'Free']
        self.colors = ['lightcoral', 'lightblue']

        self.init_ui()

    def display_gpu_info(self):
        if not self.gpu_available:
            return

        for i in range(self.device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpu_name = pynvml.nvmlDeviceGetName(handle)
            gpu_driver = pynvml.nvmlSystemGetDriverVersion()
            gpu_memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            total_memory = gpu_memory_info.total / 1024 ** 2  # Convert bytes to MB
            
            # Displaying the information
            self.gpu_info.insert(tk.END, f"GPU {i}:\n")
            self.gpu_info.insert(tk.END, f"Name: {gpu_name}\n")
            self.gpu_info.insert(tk.END, f"Driver Version: {gpu_driver}\n")
            self.gpu_info.insert(tk.END, f"Total Memory: {total_memory:.2f} MB\n\n")
        
        self.gpu_info.config(state=tk.DISABLED)  # Make the Text widget read-only



    def init_ui(self):
        self.root.title("System Usage Monitor")
        
        # CPU Usage Diagram
        cpu_frame = tk.Frame(self.root)
        cpu_frame.grid(row=0, column=0, padx=10, pady=10)
        fig1 = Figure(figsize=(3, 2), dpi=100)
        self.cpu_plot = fig1.add_subplot(1, 1, 1)
        self.cpu_canvas = FigureCanvasTkAgg(fig1, master=cpu_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Memory Usage Diagram
        memory_frame = tk.Frame(self.root)
        memory_frame.grid(row=1, column=0, padx=10, pady=10)  # Increase pady for vertical spacing
        fig2 = Figure(figsize=(3, 2), dpi=100)
        self.memory_plot = fig2.add_subplot(1, 1, 1)
        self.memory_canvas = FigureCanvasTkAgg(fig2, master=memory_frame)
        self.memory_canvas.draw()
        self.memory_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Disk Usage Diagram
        disk_frame = tk.Frame(self.root)
        disk_frame.grid(row=1, column=1, padx=10, pady=10)
        fig3 = Figure(figsize=(3, 2), dpi=100)
        self.disk_plot = fig3.add_subplot(1, 1, 1)
        self.disk_plot.pie(self.sizes, labels=self.labels, colors=self.colors, autopct='%1.1f%%', startangle=140)
        self.disk_plot.axis('equal')  # This ensures the pie chart is drawn as a circle.
        self.disk_canvas = FigureCanvasTkAgg(fig3, master=disk_frame)  # Integrate the figure with Tkinter
        self.disk_canvas.draw()
        self.disk_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # GPU Usage Diagram (if GPU is available)
        if self.gpu_available:
            gpu_frame = tk.Frame(self.root)
            gpu_frame.grid(row=3, column=0, padx=10, pady=10)
            fig4 = Figure(figsize=(3, 2), dpi=100)
            self.gpu_plot = fig4.add_subplot(1, 1, 1)
            self.gpu_canvas = FigureCanvasTkAgg(fig4, master=gpu_frame)
            self.gpu_canvas.draw()
            self.gpu_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # GPU Info Textbox (if GPU is available)
        if self.gpu_available:
            self.gpu_info = tk.Text(self.root, height=5, width=40)
            self.gpu_info.grid(row=3, column=1, padx=10, pady=10)
            self.display_gpu_info()  # Now that gpu_info is defined, you can populate it

            

        self.update_plot()

    def read_system_usage(self):
        # Read and update CPU usage list
        cpu_percent = psutil.cpu_percent(interval=0.01)
        if len(self.cpu_usage) >= 10:  # keep last 10 readings
            self.cpu_usage.pop(0)
        self.cpu_usage.append(cpu_percent)

        # Read and update memory usage list
        vm = psutil.virtual_memory()
        memory_percent = (vm.total - vm.available) / vm.total * 100
        if len(self.memory_usage) >= 10:
            self.memory_usage.pop(0)
        self.memory_usage.append(memory_percent)

        # Read GPU memory usage (if GPU is available)
        if self.gpu_available:
            temp_gpu_usage = []  # Temporary list to store current readings
            for i in range(self.device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_percent = meminfo.used / meminfo.total * 100
                temp_gpu_usage.append(gpu_memory_percent)

            # Now, update the self.gpu_memory_usage with the latest readings
            if not self.gpu_memory_usage:  # If it's the first reading
                self.gpu_memory_usage = [[usage] for usage in temp_gpu_usage]
            else:
                for i, usage in enumerate(temp_gpu_usage):
                    if len(self.gpu_memory_usage[i]) >= 10:  # Keep last 10 readings
                        self.gpu_memory_usage[i].pop(0)
                    self.gpu_memory_usage[i].append(usage)

    def update_plot(self):
        self.read_system_usage()
        
        # Update CPU plot
        self.cpu_plot.clear()
        self.cpu_plot.plot(self.cpu_usage, '-o', color='blue')
        self.cpu_plot.set_title("CPU Usage: {:.2f}%".format(self.cpu_usage[-1]))
        self.cpu_plot.set_xlabel("Samples")
        self.cpu_plot.set_ylabel("CPU Usage (%)")
        self.cpu_plot.set_ylim(0, 100)
        self.cpu_canvas.draw_idle()

        # Update Memory plot
        self.memory_plot.clear()
        self.memory_plot.plot(self.memory_usage, '-o', color='red')
        self.memory_plot.set_title("Memory Usage: {:.2f}%".format(self.memory_usage[-1]))
        self.memory_plot.set_xlabel("Samples")
        self.memory_plot.set_ylabel("Memory Usage (%)")
        self.memory_plot.set_ylim(0, 100)
        self.memory_canvas.draw_idle()

        # Update Disk plot
        self.disk_plot.set_title("Disk Usage")
        
        # Update GPU plot if GPU is available
        if self.gpu_available:
            self.gpu_plot.clear()
            for gpu_usage in self.gpu_memory_usage:
                self.gpu_plot.plot(gpu_usage, '-o')  # You might want to differentiate GPUs by color
            self.gpu_plot.set_title("GPU Memory Usage")
            self.gpu_plot.set_xlabel("Samples")
            self.gpu_plot.set_ylabel("GPU Memory Usage (%)")
            self.gpu_plot.set_ylim(0, 100)
            self.gpu_canvas.draw_idle()

        # Cancel the existing 'after' call if it exists
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)

        # Schedule the next update and store the 'after' ID
        self.after_id = self.root.after(1000, self.update_plot)

    def on_close(self):
        # Cancel the scheduled 'update_plot' call to prevent errors
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()  # Close the application window
def main():
    root = tk.Tk()
    app = CPUUsageMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # Override the close event
    root.mainloop()

if __name__ == "__main__":
    main()
