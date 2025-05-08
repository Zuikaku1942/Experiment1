import tkinter as tk
from tkinter import ttk
import random
import datetime
import time
import threading
import sys  # 添加这行导入语句

class TurboEncoder:
    """Implementation of a simplified Turbo encoder for satellite communications"""
    
    def __init__(self):
        pass
        
    def interleave(self, bits):
        """Interleave the input bits according to a predefined pattern"""
        length = len(bits)
        result = [0] * length
        
        # Simple interleaving pattern (more complex in real systems)
        for i in range(length):
            new_pos = (3 * i + 7) % length
            result[new_pos] = bits[i]
            
        return result
    
    def rsc_encode(self, bits, initial_state=0):
        """Recursive Systematic Convolutional (RSC) encoder"""
        output = []
        state = initial_state  # Initial state of the encoder
        
        # For each input bit
        for bit in bits:
            # Calculate parity bit based on current state and input
            # This is a simplified model - real RSC encoders have more complex polynomials
            parity_bit = (bit + ((state >> 1) & 1) + (state & 1)) % 2
            
            # Update state (shift register)
            state = ((state << 1) | bit) & 0x3  # 2-bit state
            
            # Add parity bit to output
            output.append(parity_bit)
            
        return output
    
    def encode(self, input_bits):
        """Encode input bits using Turbo coding principles"""
        # Original data stream (systematic bits)
        systematic_bits = input_bits.copy()
        
        # First encoder - original sequence
        parity1 = self.rsc_encode(input_bits)
        
        # Interleave input bits
        interleaved_bits = self.interleave(input_bits)
        
        # Second encoder - interleaved sequence
        parity2 = self.rsc_encode(interleaved_bits)
        
        # Combine all bits to form the complete Turbo code
        # In a real system, puncturing might be applied here to reduce redundancy
        encoded = systematic_bits + parity1 + parity2
        
        return {
            'encoded': encoded,
            'components': {
                'systematic': systematic_bits,
                'parity1': parity1,
                'parity2': parity2
            }
        }

def monitor(tag, data):
    """Monitoring function to log system activity"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return {
        'tag': tag,
        'data': data,
        'timestamp': timestamp
    }

class SatelliteEncodingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Satellite Mobile Terminal Digital Signal Encoding Subsystem")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")
        
        self.encoder = TurboEncoder()
        self.input_data = []
        self.encoded_data = {
            'encoded': [],
            'components': {
                'systematic': [],
                'parity1': [],
                'parity2': []
            }
        }
        self.monitoring_enabled = False
        self.monitoring_logs = []
        
        self.setup_ui()
        self.generate_and_process_data()
        
        # Start automatic data generation thread
        self.auto_update = True
        self.update_thread = threading.Thread(target=self.auto_update_data)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Satellite Mobile Terminal Digital Signal Encoding Subsystem",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # Data flow frame
        data_frame = tk.LabelFrame(main_frame, text="Data Flow", padx=10, pady=10, bg="white")
        data_frame.pack(fill="x", pady=(0, 10))
        
        # Input data
        tk.Label(data_frame, text="Input Data Stream (16 bits):", anchor="w", bg="white").pack(fill="x")
        self.input_display = tk.Label(
            data_frame, 
            text="", 
            bg="#f8f9fa", 
            font=("Courier", 12),
            padx=5, 
            pady=5,
            relief="sunken",
            width=50,
            anchor="w"
        )
        self.input_display.pack(fill="x", pady=(0, 10))
        
        # Encoded output
        tk.Label(data_frame, text="Turbo Encoded Output:", anchor="w", bg="white").pack(fill="x")
        self.output_display = tk.Label(
            data_frame, 
            text="", 
            bg="#f8f9fa", 
            font=("Courier", 12),
            padx=5, 
            pady=5,
            relief="sunken",
            width=50,
            anchor="w"
        )
        self.output_display.pack(fill="x", pady=(0, 10))
        
        # Generate button
        self.generate_button = tk.Button(
            data_frame,
            text="Generate New Data",
            command=self.generate_and_process_data,
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5
        )
        self.generate_button.pack(pady=(0, 5))
        
        # Monitoring toggle
        monitor_frame = tk.Frame(main_frame, bg="#f0f0f0")
        monitor_frame.pack(fill="x", pady=5)
        
        self.monitor_var = tk.BooleanVar(value=False)
        self.monitor_checkbox = tk.Checkbutton(
            monitor_frame,
            text="❌ Monitoring Disabled",
            variable=self.monitor_var,
            command=self.toggle_monitoring,
            bg="#f0f0f0",
            font=("Arial", 11)
        )
        self.monitor_checkbox.pack(anchor="w")
        
        # Monitoring area
        self.monitoring_frame = tk.LabelFrame(main_frame, text="Monitoring Points", padx=10, pady=10, bg="white")
        self.monitoring_frame.pack(fill="both", expand=True, pady=5)
        self.monitoring_frame.pack_forget()  # Hidden initially
        
        # Create a canvas with scrollbar for the monitoring logs
        self.canvas = tk.Canvas(self.monitoring_frame, bg="white")
        self.scrollbar = ttk.Scrollbar(self.monitoring_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Frame inside canvas for logs
        self.logs_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.logs_frame, anchor="nw")
        
        self.logs_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Module information
        info_frame = tk.LabelFrame(main_frame, text="Module Information", padx=10, pady=10, bg="white")
        info_frame.pack(fill="x", pady=5)
        
        info_text = """This module implements a simplified Turbo encoder for a satellite mobile terminal communication system. It includes:
- Random 16-bit data generation
- Turbo encoding with interleaving and dual RSC encoders
- Monitoring capabilities with timestamp tracking
- Clear input/output interfaces for integration with other subsystems"""
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            justify="left",
            bg="white",
            padx=5,
            pady=5,
            anchor="w",
            wraplength=750
        )
        info_label.pack(fill="x")
    
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """When the canvas changes size, resize the inner frame"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def generate_random_data(self):
        """Generate random 16-bit data"""
        self.input_data = [random.randint(0, 1) for _ in range(16)]
        self.input_display.config(text=self.format_binary(self.input_data))
        return self.input_data
    
    def process_data(self, data):
        """Process data through the encoder"""
        result = self.encoder.encode(data)
        self.encoded_data = result
        self.output_display.config(text=self.format_binary(result['encoded']))
        
        # Add to monitoring logs if enabled
        if self.monitoring_enabled:
            log_data = {
                'input': ''.join(map(str, data)),
                'output': ''.join(map(str, result['encoded'])),
                'systematic': ''.join(map(str, result['components']['systematic'])),
                'parity1': ''.join(map(str, result['components']['parity1'])),
                'parity2': ''.join(map(str, result['components']['parity2']))
            }
            
            new_log = monitor("Turbo Encoding", log_data)
            self.monitoring_logs.insert(0, new_log)
            
            # Keep only last 10 logs
            if len(self.monitoring_logs) > 10:
                self.monitoring_logs = self.monitoring_logs[:10]
            
            self.update_monitoring_display()
        
        return result
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        self.monitoring_enabled = self.monitor_var.get()
        
        if self.monitoring_enabled:
            self.monitor_checkbox.config(text="✅ Monitoring Enabled")
            self.monitoring_frame.pack(fill="both", expand=True, pady=5)
            # Add initial log if none exists
            if not self.monitoring_logs and self.input_data:
                self.process_data(self.input_data)
        else:
            self.monitor_checkbox.config(text="❌ Monitoring Disabled")
            self.monitoring_frame.pack_forget()
            self.monitoring_logs = []  # Clear logs when disabling
    
    def update_monitoring_display(self):
        """Update the monitoring display area with current logs"""
        # Clear existing logs display
        for widget in self.logs_frame.winfo_children():
            widget.destroy()
        
        # No logs message
        if not self.monitoring_logs:
            no_logs_label = tk.Label(
                self.logs_frame,
                text="No monitoring data available yet.",
                font=("Arial", 10, "italic"),
                fg="#666666",
                bg="white"
            )
            no_logs_label.pack(anchor="w", pady=5)
            return
        
        # Add each log entry
        for log in self.monitoring_logs:
            log_frame = tk.Frame(
                self.logs_frame,
                bg="#f8f9fa",
                highlightbackground="#3498db",
                highlightthickness=2,
                padx=8,
                pady=8
            )
            log_frame.pack(fill="x", pady=5, padx=5)
            
            # Log header
            header = tk.Label(
                log_frame,
                text=f"{log['tag']} - {log['timestamp']}",
                font=("Arial", 10, "bold"),
                bg="#f8f9fa",
                anchor="w"
            )
            header.pack(fill="x")
            
            # Log data
            data_frame = tk.Frame(log_frame, bg="#f8f9fa")
            data_frame.pack(fill="x", pady=(5, 0))
            
            for key, value in log['data'].items():
                data_item = tk.Label(
                    data_frame,
                    text=f"{key}: {value}",
                    font=("Courier", 9),
                    bg="#f8f9fa",
                    anchor="w"
                )
                data_item.pack(fill="x")
    
    def generate_and_process_data(self):
        """Generate and process new data"""
        data = self.generate_random_data()
        self.process_data(data)
    
    def auto_update_data(self):
        """Background thread for automatic data updates"""
        while self.auto_update:
            time.sleep(5)  # Update every 5 seconds
            # Use after to update UI from the main thread
            self.root.after(0, self.generate_and_process_data)
    
    def format_binary(self, arr):
        """Format binary array as string"""
        if not arr or len(arr) == 0:
            return ""
        return ''.join(map(str, arr))

def main():
    try:
        root = tk.Tk()
        app = SatelliteEncodingApp(root)
        root.protocol("WM_DELETE_WINDOW", lambda: (setattr(app, 'auto_update', False), root.destroy()))
        root.mainloop()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()