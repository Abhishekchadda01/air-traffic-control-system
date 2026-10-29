"""
AIR TRAFFIC CONTROL NETWORK SIMULATOR
DAA Mini Project — Prim's Minimum Spanning Tree (MST)
Python + Tkinter + Canvas. No external packages required.

Educational simulation only: an MST connects all airports using minimum total
edge weight. It is not a real flight-routing or collision-avoidance system.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math
import heapq

SAMPLE_AIRPORTS = {
    "Delhi": {"x": 125, "y": 100, "capacity": 80, "traffic": 58},
    "Jaipur": {"x": 95, "y": 235, "capacity": 35, "traffic": 24},
    "Lucknow": {"x": 270, "y": 190, "capacity": 40, "traffic": 32},
    "Mumbai": {"x": 155, "y": 405, "capacity": 75, "traffic": 69},
    "Bhopal": {"x": 310, "y": 330, "capacity": 30, "traffic": 18},
    "Kolkata": {"x": 485, "y": 230, "capacity": 65, "traffic": 52},
    "Hyderabad": {"x": 420, "y": 430, "capacity": 55, "traffic": 41},
    "Chennai": {"x": 570, "y": 470, "capacity": 60, "traffic": 45},
}
# Illustrative sample distances in km, not operational flight data.
SAMPLE_EDGES = [
    ("Delhi", "Jaipur", 235), ("Delhi", "Lucknow", 415),
    ("Delhi", "Bhopal", 590), ("Jaipur", "Bhopal", 485),
    ("Jaipur", "Mumbai", 920), ("Lucknow", "Bhopal", 510),
    ("Lucknow", "Kolkata", 810), ("Bhopal", "Mumbai", 660),
    ("Bhopal", "Hyderabad", 590), ("Bhopal", "Kolkata", 1150),
    ("Mumbai", "Hyderabad", 620), ("Mumbai", "Chennai", 1035),
    ("Hyderabad", "Chennai", 515), ("Hyderabad", "Kolkata", 1180),
    ("Kolkata", "Chennai", 1360), ("Delhi", "Kolkata", 1300),
]

def prim_mst(airports, edges, start_airport=None):
    """Prim's algorithm with a min-heap. Returns MST edges, total and steps."""
    if not airports:
        return [], 0, []
    graph = {name: [] for name in airports}
    for a, b, weight in edges:
        if a in graph and b in graph and a != b and weight > 0:
            graph[a].append((b, weight))
            graph[b].append((a, weight))
    start = start_airport if start_airport in airports else next(iter(airports))
    visited = {start}
    heap = []
    for neighbor, weight in graph[start]:
        heapq.heappush(heap, (weight, start, neighbor))
    mst, steps, total = [], [], 0
    while heap and len(visited) < len(airports):
        weight, source, target = heapq.heappop(heap)
        if target in visited:
            continue
        visited.add(target)
        mst.append((source, target, weight))
        total += weight
        steps.append({
            "source": source, "target": target, "weight": weight,
            "total": total, "visited": sorted(visited), "count": len(visited)
        })
        for neighbor, edge_weight in graph[target]:
            if neighbor not in visited:
                heapq.heappush(heap, (edge_weight, target, neighbor))
    if len(visited) != len(airports):
        missing = sorted(set(airports) - visited)
        raise ValueError("Network is disconnected. No path to: " + ", ".join(missing))
    return mst, total, steps


class AirTrafficApp:
    NODE_RADIUS = 24

    def __init__(self, root):
        self.root = root
        self.root.title("Air Traffic Control Network Simulator — Prim's Algorithm")
        self.root.geometry("1180x790")
        self.root.minsize(980, 680)
        self.airports = {k: v.copy() for k, v in SAMPLE_AIRPORTS.items()}
        self.edges = list(SAMPLE_EDGES)
        self.mst_edges, self.steps, self.current_step = [], [], 0
        self.total_distance = 0
        self.start_var = tk.StringVar(value="Delhi")
        self._style()
        self._build_ui()
        self.draw_network()
        self.update_summary()

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", rowheight=24)

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(14, 10))
        header.pack(fill="x")
        ttk.Label(header, text="✈ Air Traffic Control Network Simulator",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="DAA Mini Project | Prim's Minimum Spanning Tree | Educational Simulation").pack(anchor="w")

        body = ttk.Frame(self.root, padding=(10, 0, 10, 8))
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(body, width=340)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        canvas_box = ttk.LabelFrame(left, text="Airport Network Visualization", padding=6)
        canvas_box.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_box, bg="#f5f8fc", width=700, height=540, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        ttk.Label(left, text="Legend:  Blue = airport   Grey dashed = connection   Green = selected MST edge").pack(anchor="w", pady=5)

        controls = ttk.LabelFrame(right, text="Prim's Algorithm Controls", padding=9)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Label(controls, text="Starting airport:").pack(anchor="w")
        self.start_combo = ttk.Combobox(controls, textvariable=self.start_var,
                                        state="readonly", values=list(self.airports))
        self.start_combo.pack(fill="x", pady=(3, 8))
        ttk.Button(controls, text="Build Minimum Spanning Tree", command=self.run_prim).pack(fill="x", pady=3)
        row = ttk.Frame(controls)
        row.pack(fill="x", pady=3)
        ttk.Button(row, text="◀ Previous Step", command=self.previous_step).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(row, text="Next Step ▶", command=self.next_step).pack(side="left", expand=True, fill="x", padx=(3, 0))
        ttk.Button(controls, text="Show Full MST", command=self.show_full_mst).pack(fill="x", pady=3)
        ttk.Button(controls, text="Reset Sample Network", command=self.reset_network).pack(fill="x", pady=3)

        summary = ttk.LabelFrame(right, text="Network Summary", padding=9)
        summary.pack(fill="x", pady=(0, 8))
        self.airport_count_label = ttk.Label(summary)
        self.airport_count_label.pack(anchor="w", pady=2)
        self.connection_count_label = ttk.Label(summary)
        self.connection_count_label.pack(anchor="w", pady=2)
        self.mst_count_label = ttk.Label(summary)
        self.mst_count_label.pack(anchor="w", pady=2)
        self.distance_label = ttk.Label(summary)
        self.distance_label.pack(anchor="w", pady=2)
        self.capacity_label = ttk.Label(summary)
        self.capacity_label.pack(anchor="w", pady=2)

        progress = ttk.LabelFrame(right, text="Algorithm Progress", padding=8)
        progress.pack(fill="both", expand=True, pady=(0, 8))
        self.status_label = ttk.Label(progress, text="Click Build Minimum Spanning Tree to run Prim's algorithm.",
                                      wraplength=300, justify="left")
        self.status_label.pack(anchor="w", fill="x", pady=(0, 6))
        self.step_list = tk.Listbox(progress, height=7)
        self.step_list.pack(fill="both", expand=True)
        self.step_list.bind("<<ListboxSelect>>", self.on_step_select)

        edit = ttk.LabelFrame(right, text="Edit Network", padding=8)
        edit.pack(fill="x")
        ttk.Label(edit, text="Add airport: name / capacity").pack(anchor="w")
        r1 = ttk.Frame(edit)
        r1.pack(fill="x", pady=3)
        self.new_name = ttk.Entry(r1, width=17)
        self.new_name.insert(0, "Amritsar")
        self.new_name.pack(side="left", fill="x", expand=True)
        self.new_capacity = ttk.Entry(r1, width=8)
        self.new_capacity.insert(0, "30")
        self.new_capacity.pack(side="left", padx=(4, 0))
        ttk.Button(edit, text="Add Airport", command=self.add_airport).pack(fill="x", pady=(0, 5))
        ttk.Label(edit, text="Connection: airport A, airport B, distance km").pack(anchor="w")
        self.edge_entry = ttk.Entry(edit)
        self.edge_entry.insert(0, "Delhi, Amritsar, 450")
        self.edge_entry.pack(fill="x", pady=3)
        ttk.Button(edit, text="Add Connection", command=self.add_connection).pack(fill="x")

        ttk.Label(self.root, text="Educational simulation only — not for real-world flight operations.",
                  foreground="#8a3b12", padding=(12, 3)).pack(fill="x")

    def _positions(self):
        self.canvas.update_idletasks()
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 540)
        xs = [d["x"] for d in self.airports.values()]
        ys = [d["y"] for d in self.airports.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x, span_y = max(max_x - min_x, 1), max(max_y - min_y, 1)
        return {
            name: (40 + (d["x"] - min_x) / span_x * (width - 80),
                   40 + (d["y"] - min_y) / span_y * (height - 80))
            for name, d in self.airports.items()
        }

    def draw_network(self):
        self.canvas.delete("all")
        positions = self._positions()
        revealed = {
            frozenset((s["source"], s["target"]))
            for s in self.steps[:self.current_step]
        }
        all_mst = {frozenset((a, b)) for a, b, _ in self.mst_edges}
        for a, b, weight in self.edges:
            if a not in positions or b not in positions:
                continue
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            key = frozenset((a, b))
            green = key in all_mst and (self.current_step == len(self.steps) or key in revealed)
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill="#13834b" if green else "#a9b6c6",
                                    width=4 if green else 1, dash=None if green else (5, 4))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_rectangle(mx - 19, my - 10, mx + 19, my + 10,
                                         fill="white", outline="")
            self.canvas.create_text(mx, my, text=str(weight), fill="#344054", font=("Segoe UI", 8))
        for name, data in self.airports.items():
            x, y = positions[name]
            use = data["traffic"] / data["capacity"] if data["capacity"] else 0
            fill = "#f7b6b2" if use >= .85 else "#ffe0a3" if use >= .65 else "#b8d8ff"
            self.canvas.create_oval(x-self.NODE_RADIUS, y-self.NODE_RADIUS,
                                    x+self.NODE_RADIUS, y+self.NODE_RADIUS,
                                    fill=fill, outline="#24476b", width=2)
            self.canvas.create_text(x, y, text=name, font=("Segoe UI", 8, "bold"), width=68)
            self.canvas.create_text(x, y+self.NODE_RADIUS+12,
                                    text=f"Load {data['traffic']}/{data['capacity']}",
                                    font=("Segoe UI", 7), fill="#344054")
        self.canvas.create_text(10, 10, anchor="nw",
                                text="Illustrative network • edge labels = distance (km)",
                                fill="#475467", font=("Segoe UI", 9, "italic"))

    def run_prim(self):
        try:
            self.mst_edges, self.total_distance, self.steps = prim_mst(
                self.airports, self.edges, self.start_var.get())
        except ValueError as exc:
            messagebox.showerror("Network error", str(exc))
            return
        self.current_step = 0
        self.step_list.delete(0, "end")
        self.step_list.insert("end", "Start: " + self.start_var.get())
        for i, step in enumerate(self.steps, 1):
            self.step_list.insert("end",
                                  f"{i}. {step['source']} → {step['target']} ({step['weight']} km)")
        self.status_label.config(text=f"Prim's algorithm starts at {self.start_var.get()}.\nClick Next Step to reveal each chosen MST edge.")
        self.draw_network()
        self.update_summary()

    def next_step(self):
        if not self.steps:
            self.run_prim()
            if not self.steps:
                return
        if self.current_step < len(self.steps):
            self.current_step += 1
            s = self.steps[self.current_step - 1]
            self.status_label.config(text=(
                f"Step {self.current_step}/{len(self.steps)}\n"
                f"Selected edge: {s['source']} — {s['target']}\n"
                f"Distance: {s['weight']} km\nRunning total: {s['total']} km\n"
                f"Airports connected: {s['count']}/{len(self.airports)}"))
            self.step_list.selection_clear(0, "end")
            self.step_list.selection_set(self.current_step)
            self.step_list.see(self.current_step)
            self.draw_network()
        else:
            self.status_label.config(text=f"Complete! MST total = {self.total_distance} km.")

    def previous_step(self):
        if not self.steps or self.current_step == 0:
            return
        self.current_step -= 1
        self.draw_network()
        if self.current_step == 0:
            self.status_label.config(text="Start node selected; no MST edges revealed yet.")
        else:
            s = self.steps[self.current_step - 1]
            self.status_label.config(text=f"Step {self.current_step}: {s['source']} — {s['target']}\nRunning total: {s['total']} km")
        self.step_list.selection_clear(0, "end")
        self.step_list.selection_set(self.current_step)
        self.step_list.see(self.current_step)

    def show_full_mst(self):
        if not self.steps:
            self.run_prim()
            if not self.steps and len(self.airports) > 1:
                return
        self.current_step = len(self.steps)
        self.draw_network()
        self.status_label.config(text=f"MST complete: {len(self.mst_edges)} connections connect {len(self.airports)} airports.\nTotal distance: {self.total_distance} km.")
        self.update_summary()

    def on_step_select(self, _event):
        sel = self.step_list.curselection()
        if not sel or not self.steps:
            return
        idx = sel[0]
        self.current_step = min(idx, len(self.steps))
        if idx == 0:
            self.status_label.config(text="Start airport selected.")
        else:
            s = self.steps[self.current_step - 1]
            self.status_label.config(text=f"Step {self.current_step}: {s['source']} — {s['target']}\nEdge: {s['weight']} km | Total: {s['total']} km")
        self.draw_network()

    def add_airport(self):
        name = self.new_name.get().strip()
        try:
            capacity = int(self.new_capacity.get())
            if not name or capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid airport", "Enter a name and positive integer capacity.")
            return
        if name in self.airports:
            messagebox.showerror("Duplicate airport", "This airport already exists.")
            return
        count = len(self.airports)
        angle = 2 * math.pi * count / (count + 1)
        self.airports[name] = {
            "x": int(350 + 280 * math.cos(angle)),
            "y": int(280 + 210 * math.sin(angle)),
            "capacity": capacity,
            "traffic": int(capacity * .55)
        }
        self.start_combo["values"] = list(self.airports)
        self.draw_network()
        self.update_summary()
        self.status_label.config(text=f"Added {name}. Add a connection to connect it, then rerun Prim's algorithm.")

    def add_connection(self):
        try:
            parts = [p.strip() for p in self.edge_entry.get().split(",")]
            if len(parts) != 3:
                raise ValueError("Use: Airport A, Airport B, distance")
            a, b, distance_text = parts
            distance = int(distance_text)
            if a not in self.airports or b not in self.airports:
                raise ValueError("Both airports must exist first.")
            if a == b or distance <= 0:
                raise ValueError("Choose two different airports and a positive distance.")
            if any({x, y} == {a, b} for x, y, _ in self.edges):
                raise ValueError("This connection already exists.")
        except ValueError as exc:
            messagebox.showerror("Invalid connection", str(exc))
            return
        self.edges.append((a, b, distance))
        self.draw_network()
        self.update_summary()
        self.status_label.config(text=f"Added {a} — {b} ({distance} km). Rerun Prim's algorithm.")

    def reset_network(self):
        self.airports = {k: v.copy() for k, v in SAMPLE_AIRPORTS.items()}
        self.edges = list(SAMPLE_EDGES)
        self.mst_edges, self.steps, self.current_step = [], [], 0
        self.total_distance = 0
        self.start_var.set("Delhi")
        self.start_combo["values"] = list(self.airports)
        self.step_list.delete(0, "end")
        self.status_label.config(text="Sample network restored. Run Prim's algorithm.")
        self.draw_network()
        self.update_summary()

    def update_summary(self):
        self.airport_count_label.config(text=f"Airports: {len(self.airports)}")
        self.connection_count_label.config(text=f"Connections: {len(self.edges)}")
        if self.mst_edges or len(self.airports) == 1:
            self.mst_count_label.config(text=f"MST connections: {len(self.mst_edges)}")
            self.distance_label.config(text=f"Total MST distance: {self.total_distance:,} km")
        else:
            self.mst_count_label.config(text="MST connections: not calculated")
            self.distance_label.config(text="Total MST distance: —")
        uses = [d["traffic"] / d["capacity"] for d in self.airports.values() if d["capacity"] > 0]
        avg = sum(uses) / len(uses) * 100 if uses else 0
        self.capacity_label.config(text=f"Average capacity use: {avg:.1f}%")

def main():
    root = tk.Tk()
    AirTrafficApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
