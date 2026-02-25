import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import random, time, threading, matplotlib.pyplot as plt, os, glob, json, datetime
from tkinter import END

SETTINGS_FILE = "settings.json"

# ----------------- Sorting Algorithms ----------------- #
def bubble_sort(arr):
    a = arr.copy()
    for i in range(len(a)):
        for j in range(len(a) - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a

def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]; j = i - 1
        while j >= 0 and key < a[j]:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key
    return a

def selection_sort(arr):
    a = arr.copy()
    for i in range(len(a)):
        min_idx = i
        for j in range(i + 1, len(a)):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr)//2
        L, R = merge_sort(arr[:mid]), merge_sort(arr[mid:])
        return merge_merge(L, R)
    return arr

def merge_merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result

def quick_sort(arr):
    a = arr.copy()
    quick_rec(a, 0, len(a)-1)
    return a

def quick_rec(arr, low, high):
    if low < high:
        pi = quick_partition(arr, low, high)
        quick_rec(arr, low, pi-1)
        quick_rec(arr, pi+1, high)

def quick_partition(arr, low, high):
    pivot = arr[high]; i = low-1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1; arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i+1

def radix_sort(arr):
    a = arr.copy(); max_num, exp = max(a), 1
    while max_num // exp > 0:
        counting_sort(a, exp); exp *= 10
    return a

def counting_sort(arr, exp):
    n, output, count = len(arr), [0]*len(arr), [0]*10
    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1
    for i in range(1, 10):
        count[i] += count[i-1]
    i = n - 1
    while i >= 0:
        index = arr[i] // exp
        output[count[index % 10]-1] = arr[i]
        count[index % 10] -= 1
        i -= 1
    for i in range(n):
        arr[i] = output[i]

SORT_FUNCTIONS = {
    "Bubble Sort": bubble_sort,
    "Insertion Sort": insertion_sort,
    "Selection Sort": selection_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Radix Sort": radix_sort
}

SORT_INFO = {
    "Bubble Sort": {
        "Advantages": "Simple to implement, good for small datasets.",
        "Disadvantages": "Very slow for large lists due to O(n²) time complexity."
    },
    "Insertion Sort": {
        "Advantages": "Simple, adaptive, efficient for nearly sorted data.",
        "Disadvantages": "O(n²) worst case, inefficient for large arrays."
    },
    "Selection Sort": {
        "Advantages": "Simple, performs well on small lists, few swaps.",
        "Disadvantages": "O(n²) time complexity regardless of input."
    },
    "Merge Sort": {
        "Advantages": "Stable, O(n log n) time, works well on large datasets.",
        "Disadvantages": "Requires extra memory, not in-place."
    },
    "Quick Sort": {
        "Advantages": "Very fast average case O(n log n), in-place sorting.",
        "Disadvantages": "Worst case O(n²), unstable sort."
    },
    "Radix Sort": {
        "Advantages": "Efficient for integers, O(nk) time complexity.",
        "Disadvantages": "Only works on integers or fixed-length keys."
    }
}

# ----------------- Main App ----------------- #
class SortingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Sorting GUI Dashboard")
        self.root.geometry("1050x720")
        self.root.resizable(False, False)  
        self.root.configure(fg_color="#2C3E50")

        self.numbers, self.results, self.sorted_data = [], {}, []
        self.algorithms = list(SORT_FUNCTIONS.keys())
        self.generated_folder = os.path.join(os.getcwd(), "generated_files")
        self.theme, self.font_size, self.bg_color = "dark", 12, "#2C3E50"

        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("blue")

        self.load_settings()
        self.create_widgets()
        self.update_clock()

    # ----------------- GUI ----------------- #
    def create_widgets(self):
        # Top toolbar
        toolbar = ctk.CTkFrame(self.root, fg_color="#2C3E50")
        toolbar.pack(fill="x", padx=8, pady=(8, 0))

        ctk.CTkButton(toolbar, text="🎨 Change BG", command=self.change_bg_color).pack(side="left", padx=6)
        ctk.CTkButton(toolbar, text="🧹 Clear", command=self.clear_data, fg_color="#E74C3C").pack(side="left", padx=6)
        ctk.CTkButton(toolbar, text="🔄 Reset", command=self.reset_app, fg_color="#1ABC9C").pack(side="left", padx=6)

        # Tabs
        self.tabview = ctk.CTkTabview(self.root, width=980, height=560, fg_color="#34495E")
        self.tabview.pack(padx=15, pady=12, fill="both", expand=True)

        self.tabview.add("📂 Data")
        self.tabview.add("⚙️ Sorting")
        self.tabview.add("📊 Results")

        data_tab = self.tabview.tab("📂 Data")
        sort_tab = self.tabview.tab("⚙️ Sorting")
        result_tab = self.tabview.tab("📊 Results")

        # --- Data Tab ---
        ctk.CTkLabel(data_tab, text="Step 1: Input / Generate Numbers", font=("Arial", self.font_size, "bold")).pack(pady=6)

        btn_frame = ctk.CTkFrame(data_tab, fg_color="#3B5360")
        btn_frame.pack(fill="x", pady=5, padx=8)
        ctk.CTkButton(btn_frame, text="📂 Load File", fg_color="#FFD700", text_color="black", command=self.load_file).pack(side="left", padx=6, pady=6)
        ctk.CTkButton(btn_frame, text="💾 Save Input", fg_color="#EF8FCA", text_color="white", command=self.save_input_file).pack(side="left", padx=6, pady=6)

        gen_frame = ctk.CTkFrame(data_tab, fg_color="#3B5360")
        gen_frame.pack(fill="x", pady=8, padx=8)
        ctk.CTkLabel(gen_frame, text="Generate New Set (≥10000):").grid(row=0, column=0, padx=4, pady=6)
        self.num_entry = ctk.CTkEntry(gen_frame, placeholder_text="10000", width=120)
        self.num_entry.grid(row=0, column=1, padx=4)
        ctk.CTkButton(gen_frame, text="🎲 Generate", fg_color="#27AE60", text_color="white", command=self.generate_numbers).grid(row=0, column=2, padx=4)

        self.file_label = ctk.CTkLabel(data_tab, text="No file loaded")
        self.file_label.pack(anchor="w", padx=12, pady=4)

        # Bulk file generator
        ctk.CTkLabel(data_tab, text="Bulk File Generator", font=("Arial", self.font_size, "bold")).pack(pady=6)
        file_frame = ctk.CTkFrame(data_tab, fg_color="#3B5360")
        file_frame.pack(fill="x", pady=5, padx=8)
        ctk.CTkLabel(file_frame, text="Files:").grid(row=0, column=0, padx=4, pady=6)
        self.file_count_entry = ctk.CTkEntry(file_frame, placeholder_text="3", width=80)
        self.file_count_entry.grid(row=0, column=1, padx=4)
        ctk.CTkLabel(file_frame, text="Numbers per File:").grid(row=0, column=2, padx=4)
        self.numbers_per_file_entry = ctk.CTkEntry(file_frame, placeholder_text="10000", width=100)
        self.numbers_per_file_entry.grid(row=0, column=3, padx=4)
        ctk.CTkButton(file_frame, text="📁 Generate Files", fg_color="#2980B9", text_color="white", command=self.generate_files).grid(row=0, column=4, padx=6)
        ctk.CTkButton(file_frame, text="📂 Open Folder", fg_color="#8E44AD", text_color="white", command=self.open_generated_folder).grid(row=0, column=5, padx=6)

        ctk.CTkLabel(data_tab, text="Preview (first 20 numbers):").pack(anchor="w", padx=12, pady=4)
        self.preview_box = ctk.CTkTextbox(data_tab, height=80, fg_color="#2E4053")
        self.preview_box.pack(fill="x", padx=12, pady=4)

        # --- Sorting Tab ---
        ctk.CTkLabel(sort_tab, text="Step 2: Choose Algorithms", font=("Arial", self.font_size, "bold")).pack(pady=6)
        algo_frame = ctk.CTkFrame(sort_tab, fg_color="#3B5360")
        algo_frame.pack(pady=6, fill="x", padx=8)
        self.algo_vars = {alg: ctk.BooleanVar(value=True) for alg in self.algorithms}
        for i, alg in enumerate(self.algorithms):
            ctk.CTkCheckBox(algo_frame, text=alg, variable=self.algo_vars[alg]).grid(row=0, column=i, padx=5, pady=6)

        action_frame = ctk.CTkFrame(sort_tab, fg_color="#3B5360")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="⚡ Sort Now", fg_color="#7EA1BD", text_color="white", command=self.run_sorting).grid(row=0, column=0, padx=6, pady=6)
        ctk.CTkButton(action_frame, text="💾 Save Sorted Output", fg_color="#8A2BE2", text_color="white", command=self.save_sorted_output).grid(row=0, column=1, padx=6, pady=6)

        self.progress = ctk.CTkProgressBar(sort_tab, width=500)
        self.progress.pack(pady=8)
        self.progress.set(0)

        # --- Results Tab ---
        ctk.CTkLabel(result_tab, text="Step 3: Results & Analysis", font=("Arial", self.font_size, "bold")).pack(pady=6)
        self.info = ctk.CTkTextbox(result_tab, height=300, fg_color="#2E4053")
        self.info.pack(fill="both", expand=True, padx=12, pady=6)
        btn_frame2 = ctk.CTkFrame(result_tab, fg_color="#3B5360")
        btn_frame2.pack(pady=8)
        ctk.CTkButton(btn_frame2, text="📊 Show Graph", fg_color="#E67E22", text_color="white", command=self.plot_results).pack(side="left", padx=6, pady=6)
        ctk.CTkButton(btn_frame2, text="💾 Save Graph as PNG", fg_color="#16A085", text_color="white", command=self.save_graph).pack(side="left", padx=6, pady=6)

        # Status bar & clock
        bottom_frame = ctk.CTkFrame(self.root, fg_color="#1A252F")
        bottom_frame.pack(fill="x", side="bottom")
        self.status = ctk.CTkLabel(bottom_frame, text="Ready", anchor="w", fg_color="#1A252F")
        self.status.pack(side="left", fill="x", expand=True, padx=6, pady=4)
        self.clock = ctk.CTkLabel(bottom_frame, text="", anchor="e", fg_color="#1A252F")
        self.clock.pack(side="right", padx=6, pady=4)

    # ----------------- Extra Features ----------------- #
    def change_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color and color[1]:
            self.bg_color = color[1]
            self._apply_bg_color(self.root, self.bg_color)
            self.save_settings()
            self.log(f"Background color changed to {self.bg_color}")

    def _apply_bg_color(self, widget, color):
        # Try set widget fg_color or bg if possible, else pass
        try:
            if isinstance(widget, (ctk.CTkFrame, ctk.CTkTabview, ctk.CTkTextbox, ctk.CTkLabel, ctk.CTkCheckBox, ctk.CTkButton, ctk.CTkEntry)):
                widget.configure(fg_color=color)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._apply_bg_color(child, color)

        # Additionally change root window bg as fallback
        try:
            self.root.configure(bg=color)
        except Exception:
            pass

    def clear_data(self):
        self.numbers.clear()
        self.results.clear()
        self.sorted_data.clear()
        self.preview_box.delete("1.0", END)
        self.info.delete("1.0", END)
        self.file_label.configure(text="No file loaded")
        self.progress.set(0)
        self.log("🧹 Data cleared")

    def reset_app(self):
        confirm = messagebox.askyesno("Reset", "Reset app to default settings?")
        if not confirm:
            return
        self.theme, self.font_size, self.bg_color = "dark", 12, "#2C3E50"
        ctk.set_appearance_mode(self.theme)
        self._apply_bg_color(self.root, self.bg_color)
        self.clear_data()
        self.save_settings()
        self.log("🔄 App reset to defaults")

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock.configure(text=f"⏰ {now}")
        self.root.after(1000, self.update_clock)

    def save_settings(self):
        data = {"theme": self.theme, "font_size": self.font_size, "bg_color": self.bg_color}
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.theme = data.get("theme", "dark")
                    self.font_size = data.get("font_size", 12)
                    self.bg_color = data.get("bg_color", "#2C3E50")
                    self._apply_bg_color(self.root, self.bg_color)
            except Exception:
                self.theme, self.font_size, self.bg_color = "dark", 12, "#2C3E50"

    # ----------------- Core Functions ----------------- #
    def log(self, msg):
        try:
            self.info.insert(END, msg + "\n")
            self.info.see(END)
        except:
            pass
        try:
            self.status.configure(text=msg)
        except:
            pass

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "r") as f:
                    self.numbers = list(map(int, f.read().split()))
                self.file_label.configure(text=f"Loaded {len(self.numbers)} numbers from {os.path.basename(path)}")
                self.preview_box.delete("1.0", END)
                self.preview_box.insert("1.0", " ".join(map(str, self.numbers[:20])))
                self.log(f"✅ Loaded {len(self.numbers)} numbers")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_input_file(self):
        if not self.numbers:
            return messagebox.showwarning("No Data", "Nothing to save")
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            try:
                with open(path, "w") as f:
                    f.write(" ".join(map(str, self.numbers)))
                self.log(f"💾 Input saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def generate_numbers(self):
        try:
            n = int(self.num_entry.get())
            if n < 10000:
                raise ValueError
        except Exception:
            return messagebox.showerror("Error", "Enter valid number ≥10000")
        self.numbers = [random.randint(1, 10**9) for _ in range(n)]
        self.file_label.configure(text=f"Generated {n} numbers")
        self.preview_box.delete("1.0", END)
        self.preview_box.insert("1.0", " ".join(map(str, self.numbers[:20])))
        self.log(f"🎲 Generated {n} numbers")

    def generate_files(self):
        try:
            file_count = int(self.file_count_entry.get())
            base_num = int(self.numbers_per_file_entry.get())
            if file_count < 1 or base_num < 10000:
                raise ValueError
        except Exception:
            return messagebox.showerror("Error", "Enter valid integers (files ≥1, numbers ≥10000)")

        os.makedirs(self.generated_folder, exist_ok=True)
        for old in glob.glob(os.path.join(self.generated_folder, "numbers_file_*.txt")):
            try:
                os.remove(old)
            except:
                pass

        self.progress.set(0)
        def worker():
            try:
                for i in range(file_count):
                    num_this = base_num + i * 15000
                    nums = [random.randint(1, 10**9) for _ in range(num_this)]
                    filename = os.path.join(self.generated_folder, f"numbers_file_{i + 1}.txt")
                    with open(filename, "w") as f:
                        f.write(" ".join(map(str, nums)))
                    self.log(f"📁 Generated file {i+1}: {num_this} numbers")
                    self.progress.set((i + 1) / file_count)
                self.log(f"✅ All {file_count} files created in {self.generated_folder}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed during generation: {e}")
        threading.Thread(target=worker).start()

    def open_generated_folder(self):
        try:
            if os.name == "nt":
                os.startfile(self.generated_folder)
            else:
                os.system(f'open "{self.generated_folder}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

    def run_sorting(self):
        if not self.numbers:
            return messagebox.showwarning("No Data", "Load or generate numbers first")
        selected = [a for a, v in self.algo_vars.items() if v.get()]
        if not selected:
            return messagebox.showwarning("No Algorithm", "Select at least one algorithm")
        self.results.clear()
        self.progress.set(0)
        self.info.delete("1.0", END)
        def worker():
            self.log("⚡ Sorting started")
            try:
                for i, alg in enumerate(selected):
                    func = SORT_FUNCTIONS[alg]
                    start = time.time()
                    sorted_list = func(self.numbers)
                    end = time.time()
                    self.results[alg] = end - start
                    self.sorted_data = sorted_list
                    self.log(f"⚡ {alg} finished in {end - start:.3f}s")
                    self.progress.set((i + 1) / len(selected))
                self.log("✅ Sorting complete\n")
                ad_text = ""
                for alg in selected:
                    if alg in self.results:
                        ad_text += f"{alg}:\n - Advantages: {SORT_INFO[alg]['Advantages']}\n - Disadvantages: {SORT_INFO[alg]['Disadvantages']}\n\n"
                self.info.insert(END, ad_text)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        threading.Thread(target=worker).start()

    def save_sorted_output(self):
        if not self.sorted_:
            return messagebox.showwarning("No Data", "Nothing sorted yet")
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            try:
                with open(path, "w") as f:
                    f.write(" ".join(map(str, self.sorted_data)))
                self.log(f"💾 Sorted output saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def plot_results(self):
        if not self.results:
            return messagebox.showwarning("No Results", "No sorting results")
        algos = list(self.results.keys())
        times = [self.results[a] for a in algos]
        plt.figure(figsize=(8, 6))
        plt.bar(algos, times, color="skyblue")
        plt.ylabel("Time (s)")
        plt.title("Sorting Performance")
        plt.grid(axis="y")
        plt.show()

    def save_graph(self):
        if not self.results:
            return messagebox.showwarning("No Results", "No graph to save")
        algos = list(self.results.keys())
        times = [self.results[a] for a in algos]
        plt.figure(figsize=(8, 6))
        plt.bar(algos, times, color="skyblue")
        plt.ylabel("Time (s)")
        plt.title("Sorting Performance")
        plt.grid(axis="y")
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            try:
                plt.savefig(path)
                self.log(f"💾 Graph saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {e}")

# ----------------- Run App ----------------- #
if __name__ == "__main__":
    root = ctk.CTk()
    app = SortingApp(root)
    root.mainloop()
