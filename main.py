import tkinter as tk
from collections import deque
import random
import math
from tkinter import scrolledtext

VARIANT = 4408
N = 10
N1, N2, N3, N4 = 4, 4, 0, 8
SEED = VARIANT

class GraphTraversalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Traversal (BFS/DFS)")
        
        self.adj_matrix = self.generate_adjacency_matrix()
        self.positions = self.calculate_positions()
        
        self.setup_ui()
        
        self.reset_traversal()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(self.root, width=40, height=20)
        self.output_text.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, pady=10)
        
        tk.Button(control_frame, text="Start BFS", command=self.start_bfs).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Start DFS", command=self.start_dfs).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Next Step", command=self.next_step).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_traversal).pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def generate_adjacency_matrix(self):
        random.seed(SEED)
        k = 1.0 - N3 * 0.01 - N4 * 0.005 - 0.15
        matrix = [[1 if random.uniform(0, 2.0) * k >= 1.0 else 0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            matrix[i][i] = 0
        return matrix

    def calculate_positions(self):
        margin = 100
        center_x, center_y = 300, 300
        positions = [(center_x, center_y)]

        if N == 1:
            return positions

        corners = [
            (margin, margin),         
            (600 - margin, margin), 
            (600 - margin, 600 - margin), 
            (margin, 600 - margin) 
        ]
        
        positions.extend(corners)
        
        sides = [
            (0, 1), 
            (1, 2), 
            (2, 3), 
            (3, 0)  
        ]
        
        remaining = N - 5  
        per_side = remaining // 4
        extra = remaining % 4
        
        for side_idx, (start_idx, end_idx) in enumerate(sides):
            count = per_side + (1 if side_idx < extra else 0)
            x1, y1 = positions[start_idx + 1] 
            x2, y2 = positions[end_idx + 1]
            
            for i in range(count):
                t = (i + 1) / (count + 1)
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                positions.append((x, y))
        
        return positions[:N]

    def reset_traversal(self):
        self.visited = []
        self.queue = deque()
        self.stack = []
        self.tree_edges = []
        self.tree_matrix = [[0]*N for _ in range(N)]
        self.new_numbering = {}
        self.next_number = 1
        self.step_counter = 0
        self.current_algorithm = None
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Матриця суміжності графа:\n")
        for row in self.adj_matrix:
            self.output_text.insert(tk.END, " ".join(map(str, row)))
            self.output_text.insert(tk.END, "\n")
        self.output_text.insert(tk.END, "\n")
        
        self.draw_graph()
        self.status_label.config(text="Ready")

    def draw_graph(self):
        self.canvas.delete("all")
        radius = 20
        
        for i in range(N):
            for j in range(N):
                if self.adj_matrix[i][j]:
                    self.draw_edge(i, j, 'gray', 2)
        
        for u, v in self.tree_edges:
            self.draw_edge(u, v, 'red', 3)
        
        for i in range(N):
            x, y = self.positions[i]
            color = self.get_vertex_color(i)
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                  fill=color, outline='black', width=2)
            
            self.canvas.create_text(x, y-10, text=str(i), font=('Arial', 10))
            if i in self.new_numbering:
                self.canvas.create_text(x, y+10, text=str(self.new_numbering[i]), 
                                      font=('Arial', 10, 'bold'), fill='red')
        

    def draw_edge(self, u, v, color, width):
        x1, y1 = self.positions[u]
        x2, y2 = self.positions[v]
        radius = 20
        
        if u == v:
            loop_radius = 25
            self.canvas.create_oval(x1+radius, y1-radius-loop_radius, 
                                   x1+radius+loop_radius, y1-radius, 
                                   outline=color, width=width, arrow=tk.LAST)
            return
        
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
            
        dx, dy = dx/dist, dy/dist
        curvature = 0.3
        
        if self.adj_matrix[v][u] and v > u:
            curvature = 0.6 * (-1 if (u + v) % 2 else 1)
        
        cx = (x1 + x2)/2 + curvature * dy * dist * 0.5
        cy = (y1 + y2)/2 - curvature * dx * dist * 0.5
        
        sx = x1 + dx * radius
        sy = y1 + dy * radius
        ex = x2 - dx * radius
        ey = y2 - dy * radius
        
        self.canvas.create_line(sx, sy, cx, cy, ex, ey,
                              smooth=True, arrow=tk.LAST,
                              fill=color, width=width, splinesteps=20)

    def get_vertex_color(self, i):
        if i in self.visited:
            return 'lightgreen' if self.current_algorithm == 'bfs' else 'lightblue'
        

    def start_bfs(self):
        self.reset_traversal()
        self.current_algorithm = 'bfs'
        start = self.find_start_vertex()
        if start is not None:
            self.queue.append(start)
            self.visit_vertex(start, None)
            self.status_label.config(text=f"BFS Started from {start}")
            self.update_output(f"Початок BFS з вершини {start}\n")
            self.draw_graph()

    def start_dfs(self):
        self.reset_traversal()
        self.current_algorithm = 'dfs'
        start = self.find_start_vertex()
        if start is not None:
            self.stack.append(start)
            self.visit_vertex(start, None)
            self.status_label.config(text=f"DFS Started from {start}")
            self.update_output(f"Початок DFS з вершини {start}\n")
            self.draw_graph()

    def find_start_vertex(self):
        for i in range(N):
            if any(self.adj_matrix[i]):
                return i
        self.update_output("Немає вершин з вихідними дугами!\n")
        return None

    def next_step(self):
        if self.current_algorithm == 'bfs':
            self.bfs_step()
        elif self.current_algorithm == 'dfs':
            self.dfs_step()
        else:
            return
            
        self.step_counter += 1
        self.status_label.config(text=f"Крок {self.step_counter} | Відвідано: {len(self.visited)}/{N}")
        self.print_matrices()
        self.draw_graph()

    def bfs_step(self):
        if not self.queue:
            self.restart_from_unvisited()
            return
        
        current = self.queue.popleft()
        for neighbor in range(N):
            if self.adj_matrix[current][neighbor] and neighbor not in self.visited:
                self.visit_vertex(neighbor, current)

    def dfs_step(self):
        if not self.stack:
            self.restart_from_unvisited()
            return
        
        current = self.stack[-1]
        found = False
        
        for neighbor in range(N):
            if self.adj_matrix[current][neighbor] and neighbor not in self.visited:
                self.visit_vertex(neighbor, current)
                found = True
                break
        
        if not found:
            self.stack.pop()

    def visit_vertex(self, vertex, parent):
        self.visited.append(vertex)
        self.new_numbering[vertex] = self.next_number
        self.next_number += 1
        
        if parent is not None:
            self.tree_edges.append((parent, vertex))
            self.tree_matrix[parent][vertex] = 1
            self.update_output(f"Відвідано {vertex} з {parent}\n")
        else:
            self.update_output(f"Початкова вершина {vertex}\n")
        
        if self.current_algorithm == 'bfs':
            self.queue.append(vertex)
        else:
            self.stack.append(vertex)

    def restart_from_unvisited(self):
        unvisited = [v for v in range(N) if v not in self.visited and any(self.adj_matrix[v])]
        if unvisited:
            start = min(unvisited)
            self.visit_vertex(start, None)
            self.update_output(f"Нова компонента - початок з {start}\n")
        else:
            self.status_label.config(text="Обхід завершено")
            self.update_output("Обхід графа завершено!\n")
            self.current_algorithm = None

    def print_matrices(self):
        self.update_output("Матриця дерева обходу:\n")
        for row in self.tree_matrix:
            self.update_output(" ".join(map(str, row)) + "\n")
        
        self.update_output("\nНова нумерація вершин:\n")
        for old_num in sorted(self.new_numbering.keys()):
            self.update_output(f"{old_num} -> {self.new_numbering[old_num]}\n")
        self.update_output("\n")

    def update_output(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphTraversalApp(root)
    root.mainloop()