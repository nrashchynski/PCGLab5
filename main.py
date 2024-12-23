import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time

convex_polygon = [
    (-5, -5),
    (5, -5),
    (7, 2),
    (3, 7),
    (-3, 6),
    (-7, 2)
]


class LineClippingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы отсечения отрезков")
        self.grid_step = 15
        self.grid_range = 15
        self.segments = []
        self.clip_window = []
        self.create_interface()
        self.canvas_size = 400
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=12, padx=10, pady=10)
        self.draw_grid()

    def create_interface(self):
        ttk.Label(self.root, text="Выберите алгоритм:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.algorithm = tk.StringVar(value="liang_barsky")
        ttk.Combobox(
            self.root,
            textvariable=self.algorithm,
            values=["liang_barsky", "polygon_clipping"],
            state="readonly",
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.root, text="Загрузить данные", command=self.load_data).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(self.root, text="Запустить", command=self.run_algorithm).grid(row=0, column=3, padx=10, pady=5)

        self.time_label = ttk.Label(self.root, text="Время выполнения: ---")
        self.time_label.grid(row=2, column=0, columnspan=12, padx=10, pady=5, sticky="w")

        ttk.Label(self.root, text="Масштаб сетки:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.grid_scale = tk.Scale(self.root, from_=15, to_=80, orient="horizontal", command=self.update_grid_step)
        self.grid_scale.set(self.grid_step)
        self.grid_scale.grid(row=3, column=1, padx=5, pady=5)

    def draw_grid(self):
        self.canvas.delete("all")
        step = self.grid_step
        grid_range = self.grid_range
        canvas_mid = self.canvas_size // 2

        for i in range(-grid_range, grid_range + 1):
            coord = canvas_mid + i * step
            self.canvas.create_line(coord, 0, coord, self.canvas_size, fill="#ddd")
            self.canvas.create_line(0, coord, self.canvas_size, coord, fill="#ddd")

            if i != 0:
                self.canvas.create_text(coord, canvas_mid + 15, text=str(i), fill="black")
                self.canvas.create_text(canvas_mid - 15, coord, text=str(-i), fill="black")

        self.canvas.create_line(canvas_mid, 0, canvas_mid, self.canvas_size, width=2, arrow=tk.LAST)
        self.canvas.create_line(0, canvas_mid, self.canvas_size, canvas_mid, width=2, arrow=tk.LAST)
        self.canvas.create_text(canvas_mid + 20, canvas_mid - 10, text="0", fill="black")

    def to_canvas_coordinates(self, x, y):
        step = self.grid_step
        canvas_mid = self.canvas_size // 2
        canvas_x = canvas_mid + x * step
        canvas_y = canvas_mid - y * step
        return canvas_x, canvas_y

    def draw_pixel(self, x, y, color="black"):
        canvas_x, canvas_y = self.to_canvas_coordinates(x, y)
        self.canvas.create_oval(canvas_x - 2, canvas_y - 2, canvas_x + 2, canvas_y + 2, fill=color, outline=color)

    def draw_polygon(self, polygon, color="red"):
        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % len(polygon)]
            self.draw_segment(x1, y1, x2, y2, color=color, tag="polygon")

    def draw_segment(self, x1, y1, x2, y2, color="black", tag=None):
        canvas_x1, canvas_y1 = self.to_canvas_coordinates(x1, y1)
        canvas_x2, canvas_y2 = self.to_canvas_coordinates(x2, y2)
        self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill=color, width=2, tags=tag)

    def liang_barsky(self, x1, y1, x2, y2, clip_window):
        dx, dy = x2 - x1, y2 - y1
        p = [-dx, dx, -dy, dy]
        q = [x1 - clip_window[0], clip_window[2] - x1, y1 - clip_window[1], clip_window[3] - y1]

        t_min, t_max = 0, 1
        for i in range(4):
            if p[i] == 0 and q[i] < 0:
                return None
            if p[i] != 0:
                t = q[i] / p[i]
                if p[i] < 0:
                    t_min = max(t_min, t)
                else:
                    t_max = min(t_max, t)

        if t_min > t_max:
            return None

        nx1, ny1 = x1 + t_min * dx, y1 + t_min * dy
        nx2, ny2 = x1 + t_max * dx, y1 + t_max * dy
        return nx1, ny1, nx2, ny2

    def polygon_clipping(self, x1, y1, x2, y2, polygon):
        def compute_normal(p1, p2):
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            return -dy, dx

        def dot_product(v1, v2):
            return v1[0] * v2[0] + v1[1] * v2[1]

        t_min, t_max = 0, 1
        dx, dy = x2 - x1, y2 - y1
        for i in range(len(polygon)):
            p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]
            normal = compute_normal(p1, p2)
            edge_vector = (dx, dy)
            w = (x1 - p1[0], y1 - p1[1])

            numerator = -dot_product(normal, w)
            denominator = dot_product(normal, edge_vector)

            if denominator == 0 and numerator < 0:
                return None

            if denominator != 0:
                t = numerator / denominator
                if denominator > 0:
                    t_min = max(t_min, t)
                else:
                    t_max = min(t_max, t)

        if t_min > t_max:
            return None
        return x1 + t_min * dx, y1 + t_min * dy, x1 + t_max * dx, y1 + t_max * dy

    def load_data(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        with open(file_path, "r") as f:
            lines = f.readlines()

        n = int(lines[0])
        self.segments = [tuple(map(int, line.split())) for line in lines[1:n + 1]]

        if self.algorithm.get() == "liang_barsky":
            if len(lines) > n + 1:
                self.clip_window = tuple(map(int, lines[n + 1].split()))
            else:
                messagebox.showerror("Ошибка", "В файле отсутствует окно отсечения для Liang-Barsky!")
                return
        elif self.algorithm.get() == "polygon_clipping":
            self.clip_window = []

        self.draw_grid()
        for x1, y1, x2, y2 in self.segments:
            self.draw_segment(x1, y1, x2, y2, color="blue")

        if self.algorithm.get() == "liang_barsky" and len(self.clip_window) == 4:
            x_min, y_min, x_max, y_max = self.clip_window
            self.draw_segment(x_min, y_min, x_max, y_min, color="red")
            self.draw_segment(x_max, y_min, x_max, y_max, color="red")
            self.draw_segment(x_max, y_max, x_min, y_max, color="red")
            self.draw_segment(x_min, y_max, x_min, y_min, color="red")

        elif self.algorithm.get() == "polygon_clipping":
            self.draw_polygon(convex_polygon, color="red")


    def run_algorithm(self):
        self.draw_grid()
        self.canvas.delete("polygon")
        start_time = time.time()

        if self.algorithm.get() == "liang_barsky":
            if not self.clip_window or len(self.clip_window) != 4:
                messagebox.showerror("Ошибка", "Окно отсечения не задано или задано некорректно для Liang-Barsky!")
            else:
                for x1, y1, x2, y2 in self.segments:
                    result = self.liang_barsky(x1, y1, x2, y2, self.clip_window)
                    if result:
                        nx1, ny1, nx2, ny2 = result
                        # Отрисовка части отрезка внутри окна
                        self.draw_segment(nx1, ny1, nx2, ny2, color="green")
                        # Отрисовка части отрезка вне окна
                        self.draw_segment(x1, y1, nx1, ny1, color="blue")
                        self.draw_segment(nx2, ny2, x2, y2, color="blue")

        elif self.algorithm.get() == "polygon_clipping":
            for x1, y1, x2, y2 in self.segments:
                result = self.polygon_clipping(x1, y1, x2, y2, convex_polygon)
                if result:
                    nx1, ny1, nx2, ny2 = result
                    # Отрисовка части отрезка внутри многоугольника
                    self.draw_segment(nx1, ny1, nx2, ny2, color="green")
                    # Отрисовка части отрезка вне многоугольника
                    self.draw_segment(x1, y1, nx1, ny1, color="blue")
                    self.draw_segment(nx2, ny2, x2, y2, color="blue")

        # Обновляем время выполнения
        elapsed_time = time.time() - start_time
        self.time_label.config(text=f"Время выполнения: {elapsed_time:.6f} секунд")

    def update_grid_step(self, val):
        self.grid_step = int(val)
        self.draw_grid()
        self.run_algorithm()


if __name__ == "__main__":
    root = tk.Tk()
    app = LineClippingApp(root)
    root.mainloop()
