import tkinter as tk
from tkinter import ttk
from tkinter import *
from typing import List, Dict, Any, Optional
from tkinter import messagebox
from PIL import Image, ImageTk

class BuildingIcon:

    def __init__(self, canvas: tk.Canvas, x: int, y: int, building_type: str, name: str):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.type = building_type
        self.name = name
        self._icon_size = 20
        self._icon = None
        self._label = None

        if (self.type == 'library'):
            self._icon_size = 60
        self.create_icon()

        if (self.type == "playground & gym"):
            self._icon_size = 90
        self.create_icon()
        if (self.type == "hospital"):
            self._icon_size = 40
        self.create_icon()
        if (self.type == "playground"):
            self._icon_size = 55
            self.create_icon()
        if (self.type == "square"):
            self._icon_size = 80
            self.create_icon()
        if (self.type == "basketball ground"):
            self._icon_size = 40
        self.create_icon()

    def create_icon(self):
        """Create Icon"""
        colors = {
            "teaching": "#ADD8E6",  # Teaching Building - Light Blue
            "dormitory": "#98FB98",  # Dormitory - Light Green
            "canteen": "#FFB6C1",  # Dining Hall - Pink
            "default": "#D3D3D3",  # Default - Light Gray
            "innovative2": "#FFFF00",  # McDonald's - Yellow
            "playground & gym": "#E42833",  # Playground - Red
            "hospital": "#B245F5",  # Medical Center - Purple
            "academy": "#FF7F00",  # Academy
            "playground": "#0170C5",  # Playground - Blue
            "square": "#eadfb4",  # Square - Gray-Yellow
            "service center": "#b4eab5",  # Service Center
            "basketball ground": "#f9b868"  # Basketball Court
        }

        color = colors.get(self.type, colors["default"])

        self._icon = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self._icon_size,
            self.y + self._icon_size,
            fill=color,
            tags=("building", self.name)
        )

        self._label = self.canvas.create_text(
            self.x + self._icon_size / 2,
            self.y + self._icon_size + 5,
            text=self.name,
            tags=("label", self.name)
        )

class CampusGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Campus Navigation System")  # Already in English

        self.root.geometry("1400x1000")

        # "day" and "night"
        self.current_mode = "day"

        # main frame
        self.create_main_frame()

        # control panel
        self.create_control_panel()

        # map canvas
        self.create_map_canvas()

        # info panel
        self.create_info_panel()

        self.buildings: List[BuildingIcon] = []

        # event
        self.bind_events()

        self.moving_point = None
        self.animation_id = None

        self.node_positions = {}  # dictionary for node
        self.current_path = []
        self.path_lines = []
        self.auto_movement_running = False
        self.path_infos = {}  # dictionary for path infos

        self.path_lines = []  # list for path
        self.animation_id = None
        self.moving_point = None
        self.floyd_matrix = None  # Floyd matrix

        # 8:20
        self.map_hours = 8
        self.map_minutes = 20
        self.time_text = tk.Text(self.control_frame, height=1, wrap=tk.NONE)
        self.time_text.pack(fill=tk.X, padx=5, pady=5)
        self.update_time_display()

        self.simulation_running = True

        self.status_text = tk.Text(self.control_frame, height=2, wrap=tk.WORD)
        self.status_text.pack(fill=tk.X, padx=5, pady=5)

    def show_node_maps(self):
        """show node maps"""
        map_window = tk.Toplevel(self.root)
        map_window.title("Campus Node Maps")

        # size
        screen_width = map_window.winfo_screenwidth()
        screen_height = map_window.winfo_screenheight()

        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        map_window.geometry(f"{window_width}x{window_height}")

        notebook = ttk.Notebook(map_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        def create_map_tab(tab_name, image_path):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=tab_name)

            frame = ttk.Frame(tab)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame)

            x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
            y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)

            canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

            canvas.grid(row=0, column=0, sticky="nsew")
            x_scrollbar.grid(row=1, column=0, sticky="ew")
            y_scrollbar.grid(row=0, column=1, sticky="ns")

            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            try:

                image = Image.open(image_path)

                max_width = window_width - 50
                max_height = window_height - 50

                resized_image = self.resize_image(image, max_width, max_height)
                photo = ImageTk.PhotoImage(resized_image)

                canvas.config(scrollregion=(0, 0, image.width, image.height))

                canvas_image = canvas.create_image(0, 0, image=photo, anchor="nw")

                canvas.image = photo

                def on_mousewheel(event):
                    if event.state == 4:
                        scale = 1.1 if event.delta > 0 else 0.9

                        current_width = canvas.bbox(canvas_image)[2]
                        current_height = canvas.bbox(canvas_image)[3]

                        new_width = int(current_width * scale)
                        new_height = int(current_height * scale)

                        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        photo_new = ImageTk.PhotoImage(resized)
                        canvas.delete(canvas_image)
                        canvas.create_image(0, 0, image=photo_new, anchor="nw")
                        canvas.image = photo_new  # 保持引用
                        canvas.config(scrollregion=canvas.bbox("all"))

                canvas.bind("<MouseWheel>", on_mousewheel)

            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                canvas.create_text(window_width // 2, window_height // 2,
                                   text=f"Error loading map image: {image_path}",
                                   fill="red")

        # 创建两个地图标签页
        create_map_tab("Map 1", "map1.jpg")
        create_map_tab("Map 2", "map2.png")

        # 添加关闭按钮
        close_button = ttk.Button(map_window, text="Close", command=map_window.destroy)
        close_button.pack(pady=5)

    def resize_image(self, image, max_width, max_height):

        width, height = image.size

        width_ratio = max_width / width
        height_ratio = max_height / height
        ratio = min(width_ratio, height_ratio)

        new_width = int(width * ratio)
        new_height = int(height * ratio)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    def print_student_schedule(self):
        """Print student schedules with their information"""
        student_schedules = {
            1: [
                "08:40 Depart from dormitory D5e to classroom F3b for class",
                "12:00 After class, go to cafeteria F5b for lunch",
                "12:40 Return to dormitory D5e to rest after lunch",
                "13:25 Depart from dormitory to classroom F3a for class",
                "17:05 After class, go to cafeteria D5b for dinner",
                "17:35 After dinner, go to library E3 for self-study",
                "21:30 Return to dormitory D5e from library to rest"
            ],
            2: [
                "08:30 Depart from dormitory D5f to classroom F3a for class",
                "12:10 After class, go to convenience store D5c for lunch",
                "12:50 Return to dormitory D5f to rest after lunch",
                "13:35 Depart from dormitory to library E3 for self-study",
                "17:15 After self-study, go to cafeteria F5b for dinner",
                "17:45 After dinner, return to library E3 for self-study",
                "21:40 Return to dormitory D5f from library to rest"
            ],
            3: [
                "08:50 Depart from dormitory D5g to classroom F3c for class",
                "12:20 After class, go to cafeteria F5b for lunch",
                "13:00 Return to dormitory D5g to rest after lunch",
                "13:45 Depart from dormitory to laboratory D3d for experiment",
                "17:25 After experiment, go to cafeteria D5b for dinner",
                "18:00 After dinner, go to library E3 for self-study",
                "21:55 Return to dormitory D5g from library to rest"
            ],
            4: [
                "09:00 Depart from dormitory D5f to classroom F3c for class",
                "13:00 After class, go to cafeteria D5b for lunch",
                "13:30 Return to dormitory D5f to rest after lunch",
                "14:15 Depart from dormitory to library E3 for self-study",
                "17:45 After self-study, go to cafeteria B1e for dinner",
                "18:20 After dinner, return to library E3 for self-study",
                "22:20 Return to dormitory D5f from library to rest"
            ],
            5: [
                "09:10 Depart from dormitory D5e to classroom D3a for class",
                "13:10 After class, go to Xiao Mian restaurant for lunch",
                "13:40 Return to dormitory D5e to rest after lunch",
                "14:25 Depart from dormitory to classroom F3b for class",
                "18:05 After class, go to McDonald's for dinner",
                "18:35 After dinner, go to library E3 for self-study",
                "22:20 Return to dormitory D5e from library to rest"
            ],
            6: [
                "10:30 Depart from dormitory D5f to classroom F3c for class",
                "12:10 After class, go to cafeteria B1e for lunch",
                "12:55 Return to dormitory D5f to rest after lunch",
                "13:40 Depart from dormitory to gymnasium D6 East",
                "16:00 Return to dormitory D5f after PE class",
                "17:00 Depart again to cafeteria B1e for dinner",
                "17:45 Return to dormitory D5f after dinner"
            ],
            7: [
                "09:30 Depart from dormitory D5f to classroom F3b as teaching assistant",
                "10:20 Return to dormitory D5f to review latest research papers",
                "12:00 Depart from dormitory to cafeteria B1e for lunch",
                "12:40 Return to dormitory D5f to rest after lunch",
                "17:20 Depart from dormitory to cafeteria B1e for dinner",
                "17:50 After dinner, proceed to gymnasium D6 for exercise",
                "19:25 Return to dormitory D5f for deep learning experiments"
            ]
        }
        student_info = {
            1: {
                "major": "Intelligent Manufacturing",
                "color": "red",
                "type": "point"
            },
            2: {
                "major": "Future Technology",
                "color": "green",
                "type": "point"
            },
            3: {
                "major": "Microelectronics",
                "color": "blue",
                "type": "point"
            },
            4: {
                "major": "Biomedical Engineering",
                "color": "purple",
                "type": "point"
            },
            5: {
                "major": "Integrated Circuits",
                "color": "orange",
                "type": "point"
            },
            6: {
                "major": "Professor A",
                "color": "yellow",
                "type": "square"
            },
            7: {
                "major": "Professor B",
                "color": "brown",
                "type": "square"
            }
        }

        schedule_text = "====== Student & Professor Schedule ======\n\n"

        for student_id, info in student_info.items():
            if student_id <= 5:
                schedule_text += f"Student {student_id}:\n"
                schedule_text += f"Major: {info['major']}\n"
                schedule_text += f"Represented by a {info['color']} {info['type']}\n"
            else:
                schedule_text += f"{info['major']}:\n"
                schedule_text += f"Represented by a {info['color']} {info['type']}\n"

            # 修改这部分代码，直接打印字符串
            schedule = student_schedules.get(student_id, [])
            if schedule:
                schedule_text += "Daily Schedule:\n"
                for activity in schedule:
                    schedule_text += f"{activity}\n"
            schedule_text += "\n"

        # 创建新窗口显示日程表
        schedule_window = tk.Toplevel(self.root)
        schedule_window.title("Schedule Information")
        schedule_window.geometry("600x800")

        text_widget = tk.Text(schedule_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, schedule_text)
        text_widget.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(schedule_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

    def move_all_students(self):

        # all schedules
        student_schedules = {
            1: [("08:10", 31, 73), ("12:00", 73, 50), ("12:40", 50, 31), ("13:25", 31, 72), ("17:05", 72, 33),
                ("17:35", 33, 64), ("21:30", 64, 31)],
            2: [("08:20", 26, 72), ("12:10", 72, 32), ("12:50", 32, 26), ("13:35", 26, 64), ("17:15", 64, 50),
                ("17:45", 50, 64), ("21:40", 64, 26)],
            3: [("08:30", 27, 68), ("12:20", 68, 50), ("13:00", 50, 27), ("13:45", 27, 55), ("17:25", 55, 33),
                ("18:00", 33, 64), ("21:55", 64, 27)],
            4: [("09:00", 26, 67), ("13:00", 67, 50), ("13:30", 50, 26), ("14:15", 26, 64), ("17:45", 64, 103),
                ("18:20", 103, 64), ("22:20", 64, 26)],
            5: [("09:10", 31, 59), ("13:10", 59, 76), ("13:40", 76, 31), ("14:25", 31, 73), ("18:05", 73, 39),
                ("18:35", 39, 120), ("22:35", 120, 31)],
            6: [("08:30", 26, 67), ("12:10", 67, 103), ("12:55", 103, 26), ("13:40", 26, 135), ("15:00", 135, 26),
                ("15:00", 26, 103), ("15:15", 103, 26)],
            7: [("08:30", 26, 73), ("10:20", 73, 26), ("12:00", 26, 103), ("12:40", 103, 26), ("17:20", 26, 103),
                ("17:50", 103, 133), ("19:25", 133, 26)]
        }
        if not self.simulation_running:
            return

        def move_student(student_id, schedule, schedule_index=0):
            if schedule_index >= len(schedule):
                return

            target_time_str, start_node, end_node = schedule[schedule_index]
            target_hours, target_minutes = map(int, target_time_str.split(':'))

            def check_and_move():
                current_time = self.map_hours * 60 + self.map_minutes
                target_time = target_hours * 60 + target_minutes

                if abs(current_time - target_time) <= 1:
                    if not hasattr(self, 'moving_students'):
                        self.moving_students = set()

                    if student_id in self.moving_students:
                        self.root.after(200, check_and_move)
                        return

                    self.moving_students.add(student_id)
                    start_idx = start_node - 1
                    end_idx = end_node - 1

                    def movement_complete():
                        self.moving_students.remove(student_id)
                        move_student(student_id, schedule, schedule_index + 1)

                    self.move_along_floyd_path(
                        start_idx,
                        end_idx,
                        self.floyd_matrix,
                        student_id,
                        callback=movement_complete
                    )
                else:
                    self.root.after(200, check_and_move)

            check_and_move()


        for student_id, schedule in student_schedules.items():
            self.root.after(1000 * (student_id - 1),
                            lambda sid=student_id, s=schedule: move_student(sid, s))

        self.start_time_update()

    def log_movement(self, student_id, current_time, target_time):
        print(f"Student {student_id}: Current time: {current_time // 60}:{current_time % 60:02d}, "
              f"Target time: {target_time // 60}:{target_time % 60:02d}")

    def reset_simulation(self):

        self.simulation_running = True
        self.map_hours = 7
        self.map_minutes = 0
        self.update_time_display()
        self.status_text.delete(1.0, tk.END)
        if hasattr(self, 'start_button'):
            self.start_button.configure(state=tk.NORMAL)

    def draw_path(self, path_nodes, student_id=1):
        """
        Args:
            path_nodes: node list
            student_id: student ID（1-5）
        """
        colors = {
            1: "red",
            2: "green",
            3: "blue",
            4: "purple",
            5: "orange"
        }
        path_color = colors.get(student_id, "red")

        if not hasattr(self, 'path_lines_dict'):
            self.path_lines_dict = {}

        if student_id in self.path_lines_dict:
            for line in self.path_lines_dict[student_id]:
                self.canvas.delete(line)
        self.path_lines_dict[student_id] = []

        for i in range(len(path_nodes) - 1):
            start_node = path_nodes[i] + 1
            end_node = path_nodes[i + 1] + 1

            if start_node in self.node_positions and end_node in self.node_positions:
                start_pos = self.node_positions[start_node]
                end_pos = self.node_positions[end_node]

                line = self.canvas.create_line(
                    start_pos[0], start_pos[1],
                    end_pos[0], end_pos[1],
                    fill=path_color,
                    width=2,
                    dash=(5, 2),
                    tags=(f'path_line_{student_id}',)
                )
                self.path_lines_dict[student_id].append(line)

    def floydWarshall(self, graph):

        V = len(graph)
        dist = graph.copy()
        path = [[j if graph[i][j] != float('inf') else -1 for j in range(V)] for i in range(V)]

        for k in range(V):
            for i in range(V):
                for j in range(V):
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        if dist[i][j] > dist[i][k] + dist[k][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            path[i][j] = path[i][k]
        return dist, path

    def get_path(self, path_matrix, start, end):

        if path_matrix[start][end] == -1:
            return []

        path = [start]
        while start != end:
            start = path_matrix[start][end]
            path.append(start)
        return path

    def move_along_floyd_path(self, start_node_idx, end_node_idx, floyd_matrix, student_id=1, callback=None):
        """
        Args:
            start_node_idx
            end_node_idx
            floyd_matrix
            student_id: (1-5)，默认为1保持向后兼容
        """
        # shortest path
        dist_matrix, path_matrix = self.floydWarshall(floyd_matrix)

        # complete path
        path = self.get_path(path_matrix, start_node_idx, end_node_idx)

        if not path:
            messagebox.showerror("error", "No path found")
            return

        # real node pos
        path_positions = []
        for node_idx in path:
            actual_node = node_idx + 1
            if actual_node in self.node_positions:
                path_positions.append(self.node_positions[actual_node])

        # color the path
        self.draw_path(path, student_id)

        start_pos = path_positions[0]
        if not hasattr(self, 'moving_points') or student_id not in self.moving_points:
            self.create_moving_point(*start_pos, student_id)
        else:
            point = self.moving_points[student_id]
            self.canvas.coords(point,
                               start_pos[0] - 3, start_pos[1] - 3,
                               start_pos[0] + 3, start_pos[1] + 3)

        def animate_movement(position_index=0):
            if position_index < len(path_positions) - 1:
                start = path_positions[position_index]
                end = path_positions[position_index + 1]
                self.move_point_along_path(start, end, student_id, duration=500)
                self.animation_id = self.root.after(800,
                                                    lambda: animate_movement(position_index + 1))
            elif callback:
                callback()

        animate_movement()

    def parse_path_matrix(self, matrix_str: str) -> List[List[int]]:

        lines = matrix_str.strip().split('\n')
        matrix = []
        for line in lines:
            if line.strip() and not line.startswith("shortest path matrix:"):
                row = [int(x) for x in line.split() if x.isdigit()]
                if row:
                    matrix.append(row)
        return matrix

    def parse_path(self, path_str: str) -> List[int]:

        start = path_str.find('[')
        end = path_str.find(']')
        if start != -1 and end != -1:
            path_nums = path_str[start + 1:end].split(',')
            return [int(x.strip()) for x in path_nums]
        return []

    def set_node_positions(self):
        self.node_positions = {
            1: (315, 175),  # node1
            2: (415, 175),  # node2
            3: (515, 175),  # node3
            4: (615, 175),  # node4
            5: (315, 285),  # node5
            6: (415, 285),  # node6
            7: (515, 285),  # node7
            8: (615, 285),  # node8
            9: (355, 285),  # node9
            10: (445, 285),  # node10
            11: (485, 285),  # node11
            12: (575, 285),  # node12
            13: (315, 365),  # node13
            14: (355, 365),  # node14
            15: (415, 365),  # node15
            16: (445, 365),  # node16
            17: (485, 365),  # node17
            18: (515, 365),  # node18
            19: (575, 365),  # node19
            20: (615, 365),  # node20
            21: (315, 470),  # node21
            22: (415, 470),  # node22
            23: (515, 470),  # node23
            24: (615, 470),  # node24
            25: (315, 190),  # node25
            26: (330, 190),  # node26
            27: (370, 180),  # node27
            28: (370, 175),  # node28
            29: (330, 220),  # node29
            30: (315, 220),  # node30
            31: (370, 215),  # node31
            32: (370, 245),  # node32
            33: (330, 250),  # node33
            34: (330, 285),  # node34
            35: (415, 245),  # node35
            36: (415, 215),  # node36
            37: (415, 180),  # node37
            38: (415, 180),  # node38
            39: (465, 210),  # node39
            40: (465, 285),  # node40
            41: (515, 185),  # node41
            42: (515, 215),  # node42
            43: (515, 210),  # node43
            44: (515, 245),  # node44
            45: (530, 185),  # node45
            46: (530, 215),  # node46
            47: (530, 245),  # node47
            48: (570, 175),  # node48
            49: (570, 210),  # node49
            50: (570, 240),  # node50
            51: (570, 285),  # node51
            52: (370, 365),  # node52
            53: (315, 380),  # node53
            54: (330, 380),  # node54
            55: (370, 380),  # node55
            56: (415, 380),  # node56
            57: (350, 400),  # node57
            58: (315, 420),  # node58
            59: (330, 420),  # node59
            60: (370, 420),  # node60
            61: (415, 420),  # node61
            62: (370, 470),  # node62
            63: (430, 365),  # node63
            64: (430, 380),  # node64
            65: (570, 365),  # node65
            66: (515, 380),  # node66
            67: (530, 380),  # node67
            68: (570, 380),  # node68
            69: (615, 380),  # node69
            70: (550, 400),  # node70
            71: (515, 420),  # node71
            72: (530, 420),  # node72
            73: (570, 420),  # node73
            74: (615, 420),  # node74
            75: (570, 470),  # node75
            76: (435, 180),  # node76
            77: (220, 285),  # node77
            78: (158, 365),  # node78
            79: (147, 390),  # node79
            80: (158, 390),  # node80
            81: (142, 410),  # node81
            82: (65, 370),  # node82
            83: (125, 457),  # node83
            84: (148, 470),  # node84
            85: (158, 470),  # node85
            86: (220, 470),  # node86
            87: (220, 365),  # node87
            88: (235, 275),  # node88
            89: (280, 275),  # node89
            90: (235, 315),  # node90
            91: (280, 330),  # node91
            92: (235, 345),  # node92
            93: (220, 315),  # node93
            94: (220, 345),  # node94
            95: (315, 375),  # node95
            96: (315, 430),  # node96
            97: (235, 470),  # node97
            98: (280, 470),  # node98
            99: (235, 500),  # node99
            100: (280, 520),  # node100
            101: (235, 540),  # node101
            102: (220, 540),  # node102
            103: (125, 475),  # node103
            104: (175, 520),  # node104
            105: (135, 540),  # node105
            106: (100, 510),  # node106
            107: (100, 540),  # node107
            108: (136, 463),  # node108
            109: (95, 500),  # node109
            110: (90, 510),  # node110
            111: (90, 540),  # node111
            112: (90, 600),  # node112
            113: (135, 600),  # node113
            114: (220, 600),  # node114
            115: (315, 600),  # node115
            116: (330, 500),  # node116
            117: (330, 540),  # node117
            118: (370, 520),  # node118
            119: (415, 600),  # node119
            120: (425, 500),  # node120
            121: (425, 470),  # node121
            122: (515, 500),  # node122
            123: (515, 540),  # node123
            124: (515, 600),  # node124
            125: (530, 500),  # node125
            126: (530, 540),  # node126
            127: (570, 520),  # node127
            128: (615, 600),  # node128
            129: (210, 185),  # node129
            130: (252, 250),  # node130
            131: (315, 70),  # node131
            132: (415, 70),  # node132
            133: (320, 77),  # node133
            134: (315, 77),  # node134
            135: (320, 175),  # node135
            136: (235, 365)  # node136
        }

    def move_along_path(self, path: List[int]):

        if not path or len(path) < 2:
            return

        def move_next(index=0):
            if index < len(path) - 1:
                start = self.node_positions[path[index]]
                end = self.node_positions[path[index + 1]]
                self.move_point_along_path(start, end, duration=1000)
                self.root.after(1100, lambda: move_next(index + 1))


        start_pos = self.node_positions[path[0]]
        if self.moving_point is None:
            self.create_moving_point(*start_pos)
        else:

            self.canvas.coords(self.moving_point,
                               start_pos[0] - 3, start_pos[1] - 3,
                               start_pos[0] + 3, start_pos[1] + 3)

        # start
        self.root.after(800, lambda: move_next())

    def create_main_frame(self):

        self.main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def move_through_path(self, point_index=0):

        if not self.auto_movement_running:
            return

        if point_index < len(self.path_points) - 1:
            start = self.path_points[point_index]
            end = self.path_points[point_index + 1]
            self.move_point_along_path(start, end, duration=100)
            self.animation_id = self.root.after(1100,
                                                lambda: self.move_through_path(point_index + 1))

    def create_control_panel(self):

        self.control_frame = ttk.Frame(self.main_frame, width=200)
        self.main_frame.add(self.control_frame)


        self.filter_frame = ttk.LabelFrame(self.control_frame, text="Building Type")
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)

        self.building_type_var = tk.StringVar(value="all")
        types = [("All Buildings", "all"), ("Teaching Buildings", "teaching"),
                 ("Dormitories", "dormitory"), ("Dining Halls", "canteen")]

        self.path_frame = ttk.LabelFrame(self.control_frame, text="Path input")
        self.path_frame.pack(fill=tk.X, padx=5, pady=5)

        self.path_text = tk.Text(self.path_frame, height=5)
        self.path_text.pack(fill=tk.X, padx=5, pady=5)

        self.button_frame = ttk.Frame(self.path_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)

        paths_info_button = ttk.Button(
            self.control_frame,
            text="Show All Paths Info",
            command=self.show_all_paths_info
        )
        paths_info_button.pack(padx=5, pady=5)

        self.path_input_frame = ttk.LabelFrame(self.control_frame, text="Path planning")
        self.path_input_frame.pack(fill=tk.X, padx=5, pady=5)

        # start input
        start_frame = ttk.Frame(self.path_input_frame)
        start_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(start_frame, text="Starting Node:").pack(side=tk.LEFT)
        self.start_node_entry = ttk.Entry(start_frame, width=5)
        self.start_node_entry.pack(side=tk.LEFT, padx=5)

        # end input
        end_frame = ttk.Frame(self.path_input_frame)
        end_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(end_frame, text="End Node:").pack(side=tk.LEFT)
        self.end_node_entry = ttk.Entry(end_frame, width=5)
        self.end_node_entry.pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(self.path_input_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=2)

        self.mode_button = ttk.Button(
            button_frame,
            text="Change mode",
            command=self.toggle_mode
        )
        self.mode_button.pack(side=tk.LEFT, padx=2)

        preview_button_frame = ttk.Frame(self.path_frame)
        preview_button_frame.pack(fill=tk.X, padx=5, pady=2)

        schedule_button = ttk.Button(
            self.control_frame,
            text="Show Schedule",
            command=self.print_student_schedule
        )
        schedule_button.pack(padx=5, pady=5)

        self.preview_var = tk.BooleanVar(value=True)
        self.preview_check = ttk.Checkbutton(
            preview_button_frame,
            text="Path Preview",
            variable=self.preview_var,
            command=self.toggle_path_preview
        )
        self.preview_check.pack(side=tk.LEFT, padx=2)

        self.start_button = ttk.Button(
            preview_button_frame,
            text="Start moving",
            command=self.start_movement,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, padx=2)

        map_button = ttk.Button(
            self.control_frame,
            text="Show Maps",
            command=self.show_node_maps
        )
        map_button.pack(padx=5, pady=5)

        self.navigate_button = ttk.Button(
            button_frame,
            text="Start navigation",
            command=self.start_navigation
        )
        self.navigate_button.pack(side=tk.LEFT, padx=2)

        for text, value in types:
            ttk.Radiobutton(self.filter_frame, text=text,
                            variable=self.building_type_var,
                            value=value).pack(anchor=tk.W, padx=5, pady=2)

    def start_navigation(self):

        try:
            start_node = int(self.start_node_entry.get())
            end_node = int(self.end_node_entry.get())

            # shift node
            start_idx = start_node - 1
            end_idx = end_node - 1

            self.move_along_floyd_path(start_idx, end_idx, floyd_matrix)

        except ValueError:
            messagebox.showerror("error", "Please input valid node")

    def draw_path_preview(self):

        self.clear_path_preview()

        if self.current_path and self.preview_var.get():

            for i in range(len(self.current_path) - 1):
                start = self.node_positions[self.current_path[i]]
                end = self.node_positions[self.current_path[i + 1]]

                line = self.canvas.create_line(
                    start[0], start[1],
                    end[0], end[1],
                    fill='#FF6B6B', # red
                    width=3,
                    dash=(5, 3),
                    tags=('path_preview',)
                )
                self.path_lines.append(line)

                radius = 4
                circle = self.canvas.create_oval(
                    start[0] - radius, start[1] - radius,
                    start[0] + radius, start[1] + radius,
                    fill='#FF6B6B',
                    outline='#FF6B6B',
                    tags=('path_preview',)
                )
                self.path_lines.append(circle)

        self.canvas.tag_raise('path_preview')
        if self.moving_point:
            self.canvas.tag_raise(self.moving_point)

    def clear_path_preview(self):

        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines = []

    def toggle_path_preview(self):

        if self.preview_var.get():
            self.draw_path_preview()
        else:
            self.clear_path_preview()

    def parse_path_input(self):

        input_text = self.path_text.get("1.0", tk.END)
        parts = input_text.split('\n')
        matrix_str = '\n'.join(p for p in parts if not p.startswith('从节点'))
        path_str = next((p for p in parts if p.startswith('从节点')), '')

        matrix = self.parse_path_matrix(matrix_str)
        self.current_path = self.parse_path(path_str)

        self.set_node_positions()

        if self.current_path:

            start_pos = self.node_positions[self.current_path[0]]
            if self.moving_point is None:
                self.create_moving_point(*start_pos)
            else:
                self.canvas.coords(self.moving_point,
                                   start_pos[0] - 3, start_pos[1] - 3,
                                   start_pos[0] + 3, start_pos[1] + 3)

            if self.preview_var.get():
                self.draw_path_preview()

            self.start_button.configure(state=tk.NORMAL)

            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "路径已解析，点击'开始移动'开始运动\n")
            self.info_text.insert(tk.END, f"路径: {self.current_path}")
        else:

            self.start_button.configure(state=tk.DISABLED)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "路径解析失败，请检查输入格式")

    def start_movement(self):

        # avoid been click twice
        self.start_button.configure(state=tk.DISABLED)

        def move_next(index=0):
            if index < len(self.current_path) - 1:
                start = self.node_positions[self.current_path[index]]
                end = self.node_positions[self.current_path[index + 1]]

                if self.preview_var.get():
                    self.canvas.tag_lower('path_preview')
                    self.canvas.tag_raise(self.moving_point)

                self.move_point_along_path(start, end, duration=100)
                self.root.after(1000, lambda: move_next(index + 1))
            else:

                self.start_button.configure(state=tk.NORMAL)

        move_next()

    def create_moving_point(self, x, y, student_id=1, size=6):
        """
        Args:
            x, y: node pos
            student_id: student id
            size: node size
        """
        colors = ["red", "green", "blue", "purple", "orange", "yellow", "brown"]  # brown for professor
        color = colors[student_id - 1] if 1 <= student_id <= len(colors) else "red"

        if not hasattr(self, 'moving_points'):
            self.moving_points = {}
            self.moving_point = None

        if student_id in [6, 7]:  # square for professor
            point = self.canvas.create_rectangle(
                x - size / 2, y - size / 2,
                x + size / 2, y + size / 2,
                fill=color,
                tags=f'moving_point_{student_id}'
            )
        else:
            point = self.canvas.create_oval(
                x - size / 2, y - size / 2,
                x + size / 2, y + size / 2,
                fill=color,
                tags=f'moving_point_{student_id}'
            )

        self.moving_points[student_id] = point

        if student_id == 1:
            self.moving_point = point

        return point

    def create_color_block(self, x1, y1, x2, y2, color):

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def create_map_canvas(self):

        self.canvas_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.canvas_frame)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800,
            height=600,
            bg='white'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.create_color_block(150, 300, 750, 350, 'lightblue')
        self.create_color_block(315, 175, 415, 285, '#E0F8E0')
        self.create_color_block(315, 70, 415, 175, '#E0F8E0')
        self.create_color_block(515, 175, 615, 285, '#E0F8E0')
        self.create_color_block(415, 365, 515, 470, '#F5F5F5')
        self.create_color_block(315, 365, 415, 470, '#E0F8E0')
        self.create_color_block(515, 365, 615, 470, '#E0F8E0')
        self.create_color_block(220, 365, 315, 470, '#E0F8E0')
        self.create_color_block(415, 175, 515, 285, '#F5F5F5')
        self.create_color_block(315, 285, 615, 300, '#D2691E')
        self.create_color_block(315, 350, 615, 365, '#D2691E')
        self.create_color_block(415, 470, 515, 600, '#E0F8E0')
        self.create_color_block(515, 470, 615, 600, '#E0F8E0')
        self.create_color_block(315, 470, 415, 600, '#E0F8E0')
        self.create_color_block(220, 470, 315, 600, '#E0F8E0')
        self.create_color_block(100, 175, 315, 285, '#F5F5F5')
        self.create_color_block(50, 365, 315, 600, '#F5F5F5')

        # day & night
        self.sun_image = tk.PhotoImage(file="sun.png")
        self.moon_image = tk.PhotoImage(file="moon.png")
        self.display_mode_icon()

    def display_mode_icon(self):
        if self.current_mode == "day":
            icon_image = self.sun_image
        else:
            icon_image = self.moon_image

        self.canvas.create_image(0, 0, image=icon_image, anchor=tk.NW)

    def set_day_mode(self):

        self.current_mode = "day"
        self.canvas.configure(bg='white')

        for building in self.buildings:
            if building._icon:
                original_color = self.get_original_building_color(building.type)
                self.canvas.itemconfig(building._icon, fill=original_color)
        self.display_mode_icon()

    def get_original_building_color(self, building_type):

        colors = {
            "teaching": "#ADD8E6",
            "dormitory": "#98FB98",
            "canteen": "#FFB6C1",
            "default": "#D3D3D3",
            "innovative2": "#FFFF00",
            "playground & gym": "#E42833",
            "hospital": "#B245F5",
            "academy": "#FF7F00",
            "playground": "#0170C5",
            "square": "#eadfb4",
            "service center": "#b4eab5",
            "basketball ground": "#f9b868"
        }
        return colors.get(building_type, colors["default"])

    def set_night_mode(self):

        self.current_mode = "night"
        self.canvas.configure(bg='#1a1a1a')

        for building in self.buildings:
            if building._icon:
                current_color = self.canvas.itemcget(building._icon, "fill")

                darker_color = self.darken_color(current_color)
                self.canvas.itemconfig(building._icon, fill=darker_color)
        self.display_mode_icon()

    def darken_color(self, color):

        try:
            # RGB
            rgb = self.canvas.winfo_rgb(color)

            darkened = tuple(int(c * 0.7 / 256) for c in rgb)
            return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'
        except:
            return color

    def toggle_mode(self):

        if self.current_mode == "day":
            self.set_night_mode()
        else:
            self.set_day_mode()

    def create_info_panel(self):

        self.info_frame = ttk.LabelFrame(self.control_frame, text="Building information:")
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.info_text = tk.Text(self.info_frame, height=3, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)

    def bind_events(self):

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_release(self, event):

        clicked_item = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(clicked_item)
        if "building" in tags:
            self.show_building_info(tags[1])

    def add_building(self, x: int, y: int, building_type: str, name: str):

        building = BuildingIcon(self.canvas, x, y, building_type, name)
        self.buildings.append(building)

    def show_building_info(self, building_name: str):

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Buliding name: {building_name}\n")

    def clear_map(self):

        self.canvas.delete("all")
        self.buildings.clear()

    def draw_line(self, x1, y1, x2, y2, color="black", width=2):

        start_node = None
        end_node = None
        for node_id, pos in self.node_positions.items():
            if pos == (x1, y1):
                start_node = node_id
            if pos == (x2, y2):
                end_node = node_id
            if start_node and end_node:
                break

        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        if length < 50:
            capacity = "Low (2-4 people)"
        elif length < 100:
            capacity = "Medium (5-7 people)"
        else:
            capacity = "High (8-10 people)"

        height_diff = abs(y2 - y1)
        if height_diff < 20:
            difficulty = "Easy (Flat)"
        elif height_diff < 50:
            difficulty = "Medium (Slight Slope)"
        else:
            difficulty = "Hard (Stairs/Steep Slope)"

        line = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

        self.path_infos[line] = {
            'nodes': f"Node {start_node} to Node {end_node}",
            'length': f"{length:.1f} units",
            'capacity': capacity,
            'difficulty': difficulty,
            'coords': (x1, y1, x2, y2)
        }

        self.canvas.tag_bind(line, '<Button-1>',
                             lambda e, line_id=line: self.show_path_info(e, line_id))

    def show_path_info(self, event, line_id):

        info = self.path_infos[line_id]
        info_text = f"Path Information:\n"
        info_text += f"Path: {info['nodes']}\n"
        info_text += f"Length: {info['length']}\n"
        info_text += f"Capacity: {info['capacity']}\n"
        info_text += f"Difficulty: {info['difficulty']}"

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)

    def show_all_paths_info(self):

        paths_window = tk.Toplevel(self.root)
        paths_window.title("All Paths Information")
        paths_window.geometry("400x600")

        text_widget = tk.Text(paths_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(paths_window, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_widget.insert(tk.END, "=== Campus Paths Information ===\n\n")
        for line_id, info in self.path_infos.items():
            text_widget.insert(tk.END, f"{info['nodes']}:\n")
            text_widget.insert(tk.END, f"Length: {info['length']}\n")
            text_widget.insert(tk.END, f"Capacity: {info['capacity']}\n")
            text_widget.insert(tk.END, f"Difficulty: {info['difficulty']}\n\n")

        text_widget.config(state=tk.DISABLED)
    def move_point_along_path(self, start_pos, end_pos, student_id=1, duration=200):
        """
        Args:
            start_pos
            end_pos
            student_id
            duration: the duration of time
        """
        point = self.moving_points.get(student_id) if hasattr(self, 'moving_points') else self.moving_point

        if point is not None:
            steps = 10
            dx = (end_pos[0] - start_pos[0]) / steps
            dy = (end_pos[1] - start_pos[1]) / steps
            step_duration = duration / steps

            def step_movement(step=0):
                if step < steps:
                    self.canvas.move(point, dx, dy)
                    self.animation_id = self.root.after(
                        int(step_duration),
                        lambda: step_movement(step + 1)
                    )

            step_movement()

    def create_route(self):
        self.set_node_positions()

        node1_x, node1_y = 315, 175
        node2_x, node2_y = 415, 175
        node3_x, node3_y = 515, 175
        node4_x, node4_y = 615, 175
        node5_x, node5_y = 315, 285
        node6_x, node6_y = 415, 285
        node7_x, node7_y = 515, 285
        node8_x, node8_y = 615, 285
        node9_x, node9_y = 355, 285
        node10_x, node10_y = 445, 285
        node11_x, node11_y = 485, 285
        node12_x, node12_y = 575, 285
        node13_x, node13_y = 315, 365
        node14_x, node14_y = 355, 365
        node15_x, node15_y = 415, 365
        node16_x, node16_y = 445, 365
        node17_x, node17_y = 485, 365
        node18_x, node18_y = 515, 365
        node19_x, node19_y = 575, 365
        node20_x, node20_y = 615, 365
        node21_x, node21_y = 315, 470
        node22_x, node22_y = 415, 470
        node23_x, node23_y = 515, 470
        node24_x, node24_y = 615, 470
        node25_x, node25_y = 315, 190
        node26_x, node26_y = 330, 190
        node27_x, node27_y = 370, 180
        node28_x, node28_y = 370, 175
        node29_x, node29_y = 330, 220
        node30_x, node30_y = 315, 220
        node31_x, node31_y = 370, 215
        node32_x, node32_y = 370, 245
        node33_x, node33_y = 330, 250
        node34_x, node34_y = 330, 285
        node35_x, node35_y = 415, 245
        node36_x, node36_y = 415, 215
        node37_x, node37_y = 415, 180
        node38_x, node38_y = 415, 180
        node39_x, node39_y = 465, 210
        node40_x, node40_y = 465, 285
        node41_x, node41_y = 515, 185
        node42_x, node42_y = 515, 215
        node43_x, node43_y = 515, 210
        node44_x, node44_y = 515, 245
        node45_x, node45_y = 530, 185
        node46_x, node46_y = 530, 215
        node47_x, node47_y = 530, 245
        node48_x, node48_y = 570, 175
        node49_x, node49_y = 570, 210
        node50_x, node50_y = 570, 240
        node51_x, node51_y = 570, 285
        node52_x, node52_y = 370, 365
        node53_x, node53_y = 315, 380
        node54_x, node54_y = 330, 380
        node55_x, node55_y = 370, 380
        node56_x, node56_y = 415, 380
        node57_x, node57_y = 350, 400
        node58_x, node58_y = 315, 420
        node59_x, node59_y = 330, 420
        node60_x, node60_y = 370, 420
        node61_x, node61_y = 415, 420
        node62_x, node62_y = 370, 470
        node63_x, node63_y = 430, 365
        node64_x, node64_y = 430, 380
        node65_x, node65_y = 570, 365
        node66_x, node66_y = 515, 380
        node67_x, node67_y = 530, 380
        node68_x, node68_y = 570, 380
        node69_x, node69_y = 615, 380
        node70_x, node70_y = 550, 400
        node71_x, node71_y = 515, 420
        node72_x, node72_y = 530, 420
        node73_x, node73_y = 570, 420
        node74_x, node74_y = 615, 420
        node75_x, node75_y = 570, 470
        node76_x, node76_y = 435, 180
        node77_x, node77_y = 220, 285
        node78_x, node78_y = 158, 365
        node79_x, node79_y = 147, 390
        node80_x, node80_y = 158, 390
        node81_x, node81_y = 142, 410
        node82_x, node82_y = 65, 370
        node83_x, node83_y = 125, 457
        node84_x, node84_y = 148, 470
        node85_x, node85_y = 158, 470
        node86_x, node86_y = 220, 470
        node87_x, node87_y = 220, 365
        node88_x, node88_y = 235, 375
        node89_x, node89_y = 280, 375
        node90_x, node90_y = 235, 415
        node91_x, node91_y = 280, 430
        node92_x, node92_y = 235, 445
        node93_x, node93_y = 220, 415
        node94_x, node94_y = 220, 445
        node95_x, node95_y = 315, 375
        node96_x, node96_y = 315, 430
        node97_x, node97_y = 235, 470
        node98_x, node98_y = 280, 470
        node99_x, node99_y = 235, 500
        node100_x, node100_y = 280, 520
        node101_x, node101_y = 235, 540
        node102_x, node102_y = 220, 540
        node103_x, node103_y = 125, 475
        node104_x, node104_y = 175, 520
        node105_x, node105_y = 135, 540
        node106_x, node106_y = 100, 510
        node107_x, node107_y = 100, 540
        node108_x, node108_y = 136, 463
        node109_x, node109_y = 95, 500
        node110_x, node110_y = 90, 510
        node111_x, node111_y = 90, 540
        node112_x, node112_y = 90, 600
        node113_x, node113_y = 135, 600
        node114_x, node114_y = 220, 600
        node115_x, node115_y = 315, 600
        node116_x, node116_y = 330, 500
        node117_x, node117_y = 330, 540
        node118_x, node118_y = 370, 520
        node119_x, node119_y = 415, 600
        node120_x, node120_y = 425, 500
        node121_x, node121_y = 425, 470
        node122_x, node122_y = 515, 500
        node123_x, node123_y = 515, 540
        node124_x, node124_y = 515, 600
        node125_x, node125_y = 530, 500
        node126_x, node126_y = 530, 540
        node127_x, node127_y = 570, 520
        node128_x, node128_y = 615, 600
        node129_x, node129_y = 210, 185
        node130_x, node130_y = 252, 250
        node131_x, node131_y = 315, 70
        node132_x, node132_y = 415, 70
        node133_x, node133_y = 320, 77
        node134_x, node134_y = 315, 77
        node135_x, node135_y = 320, 175
        node136_x, node136_y = 235, 365

        self.draw_line(node1_x, node1_y, node2_x, node2_y)
        self.draw_line(node2_x, node2_y, node3_x, node3_y)
        self.draw_line(node3_x, node3_y, node4_x, node4_y)
        self.draw_line(node1_x, node1_y, node5_x, node5_y)
        self.draw_line(node2_x, node2_y, node6_x, node6_y)
        self.draw_line(node3_x, node3_y, node7_x, node7_y)
        self.draw_line(node4_x, node4_y, node8_x, node8_y)
        self.draw_line(node5_x, node5_y, node9_x, node9_y)
        self.draw_line(node9_x, node9_y, node6_x, node6_y)
        self.draw_line(node6_x, node6_y, node10_x, node10_y)
        self.draw_line(node10_x, node10_y, node11_x, node11_y)
        self.draw_line(node11_x, node11_y, node7_x, node7_y)
        self.draw_line(node7_x, node7_y, node12_x, node12_y)
        self.draw_line(node12_x, node12_y, node8_x, node8_y)
        self.draw_line(node9_x, node9_y, node14_x, node14_y)
        self.draw_line(node10_x, node10_y, node16_x, node16_y)
        self.draw_line(node11_x, node11_y, node17_x, node17_y)
        self.draw_line(node12_x, node12_y, node19_x, node19_y)
        self.draw_line(node13_x, node13_y, node14_x, node14_y)
        self.draw_line(node13_x, node13_y, node21_x, node21_y)
        self.draw_line(node14_x, node14_y, node15_x, node15_y)
        self.draw_line(node15_x, node15_y, node16_x, node16_y)
        self.draw_line(node15_x, node15_y, node22_x, node22_y)
        self.draw_line(node16_x, node16_y, node17_x, node17_y)
        self.draw_line(node17_x, node17_y, node18_x, node18_y)
        self.draw_line(node18_x, node18_y, node23_x, node23_y)
        self.draw_line(node18_x, node18_y, node19_x, node19_y)
        self.draw_line(node19_x, node19_y, node20_x, node20_y)
        self.draw_line(node20_x, node20_y, node24_x, node24_y)
        self.draw_line(node21_x, node21_y, node22_x, node22_y)
        self.draw_line(node22_x, node22_y, node23_x, node23_y)
        self.draw_line(node23_x, node23_y, node24_x, node24_y)
        self.draw_line(node17_x, node17_y, node11_x, node11_y)
        self.draw_line(node19_x, node19_y, node12_x, node12_y)
        self.draw_line(node13_x, node13_y, node14_x, node14_y)
        self.draw_line(node13_x, node13_y, node53_x, node53_y)
        self.draw_line(node14_x, node14_y, node52_x, node52_y)
        self.draw_line(node15_x, node15_y, node52_x, node52_y)
        self.draw_line(node15_x, node15_y, node63_x, node63_y)
        self.draw_line(node16_x, node16_y, node63_x, node63_y)
        self.draw_line(node15_x, node15_y, node56_x, node56_y)
        self.draw_line(node16_x, node16_y, node17_x, node17_y)
        self.draw_line(node17_x, node17_y, node18_x, node18_y)
        self.draw_line(node18_x, node18_y, node66_x, node66_y)
        self.draw_line(node18_x, node18_y, node65_x, node65_y)
        self.draw_line(node19_x, node19_y, node20_x, node20_y)
        self.draw_line(node19_x, node19_y, node65_x, node65_y)
        self.draw_line(node20_x, node20_y, node69_x, node69_y)
        self.draw_line(node74_x, node74_y, node24_x, node24_y)
        self.draw_line(node75_x, node75_y, node73_x, node73_y)
        self.draw_line(node74_x, node74_y, node69_x, node69_y)
        self.draw_line(node73_x, node73_y, node74_x, node74_y)
        self.draw_line(node68_x, node68_y, node69_x, node69_y)
        self.draw_line(node68_x, node68_y, node73_x, node73_y)
        self.draw_line(node75_x, node75_y, node24_x, node24_y)
        self.draw_line(node75_x, node75_y, node23_x, node23_y)
        self.draw_line(node65_x, node65_y, node68_x, node68_y)
        self.draw_line(node67_x, node67_y, node68_x, node68_y)
        self.draw_line(node70_x, node70_y, node68_x, node68_y)
        self.draw_line(node70_x, node70_y, node67_x, node67_y)
        self.draw_line(node70_x, node70_y, node73_x, node73_y)
        self.draw_line(node70_x, node70_y, node72_x, node72_y)
        self.draw_line(node72_x, node72_y, node73_x, node73_y)
        self.draw_line(node72_x, node72_y, node67_x, node67_y)
        self.draw_line(node66_x, node66_y, node67_x, node67_y)
        self.draw_line(node66_x, node66_y, node71_x, node71_y)
        self.draw_line(node71_x, node71_y, node72_x, node72_y)
        self.draw_line(node71_x, node71_y, node23_x, node23_y)
        self.draw_line(node23_x, node23_y, node22_x, node22_y)
        self.draw_line(node63_x, node63_y, node64_x, node64_y)
        self.draw_line(node56_x, node56_y, node61_x, node61_y)
        self.draw_line(node22_x, node22_y, node61_x, node61_y)
        self.draw_line(node22_x, node22_y, node62_x, node62_y)
        self.draw_line(node60_x, node60_y, node61_x, node61_y)
        self.draw_line(node60_x, node60_y, node62_x, node62_y)
        self.draw_line(node21_x, node21_y, node62_x, node62_y)
        self.draw_line(node21_x, node21_y, node58_x, node58_y)
        self.draw_line(node59_x, node59_y, node58_x, node58_y)
        self.draw_line(node53_x, node53_y, node58_x, node58_y)
        self.draw_line(node53_x, node53_y, node54_x, node54_y)
        self.draw_line(node55_x, node55_y, node56_x, node56_y)
        self.draw_line(node55_x, node55_y, node52_x, node52_y)
        self.draw_line(node57_x, node57_y, node54_x, node54_y)
        self.draw_line(node57_x, node57_y, node55_x, node55_y)
        self.draw_line(node57_x, node57_y, node59_x, node59_y)
        self.draw_line(node57_x, node57_y, node60_x, node60_y)
        self.draw_line(node55_x, node55_y, node54_x, node54_y)
        self.draw_line(node59_x, node59_y, node60_x, node60_y)
        self.draw_line(node14_x, node14_y, node9_x, node9_y)
        self.draw_line(node16_x, node16_y, node10_x, node10_y)
        self.draw_line(node17_x, node17_y, node11_x, node11_y)
        self.draw_line(node19_x, node19_y, node12_x, node12_y)
        self.draw_line(node76_x, node76_y, node38_x, node38_y)
        self.draw_line(node1_x, node1_y, node25_x, node25_y)
        self.draw_line(node1_x, node1_y, node28_x, node28_y)
        self.draw_line(node2_x, node2_y, node28_x, node28_y)
        self.draw_line(node2_x, node2_y, node37_x, node37_y)
        self.draw_line(node2_x, node2_y, node3_x, node3_y)
        self.draw_line(node3_x, node3_y, node41_x, node41_y)
        self.draw_line(node3_x, node3_y, node48_x, node48_y)
        self.draw_line(node4_x, node4_y, node48_x, node48_y)
        self.draw_line(node4_x, node4_y, node8_x, node8_y)
        self.draw_line(node25_x, node25_y, node30_x, node30_y)
        self.draw_line(node25_x, node25_y, node26_x, node26_y)
        self.draw_line(node26_x, node26_y, node29_x, node29_y)
        self.draw_line(node26_x, node26_y, node27_x, node27_y)
        self.draw_line(node26_x, node26_y, node31_x, node31_y)
        self.draw_line(node30_x, node30_y, node29_x, node29_y)
        self.draw_line(node29_x, node29_y, node32_x, node32_y)
        self.draw_line(node29_x, node29_y, node31_x, node31_y)
        self.draw_line(node33_x, node33_y, node32_x, node32_y)
        self.draw_line(node33_x, node33_y, node34_x, node34_y)
        self.draw_line(node30_x, node30_y, node5_x, node5_y)
        self.draw_line(node5_x, node5_y, node34_x, node34_y)
        self.draw_line(node34_x, node34_y, node9_x, node9_y)
        self.draw_line(node9_x, node9_y, node6_x, node6_y)
        self.draw_line(node27_x, node27_y, node37_x, node37_y)
        self.draw_line(node27_x, node27_y, node31_x, node31_y)
        self.draw_line(node31_x, node31_y, node32_x, node32_y)
        self.draw_line(node31_x, node31_y, node36_x, node36_y)
        self.draw_line(node32_x, node32_y, node35_x, node35_y, )
        self.draw_line(node37_x, node37_y, node38_x, node38_y)
        self.draw_line(node38_x, node38_y, node36_x, node36_y)
        self.draw_line(node36_x, node36_y, node35_x, node35_y)
        self.draw_line(node35_x, node35_y, node6_x, node6_y)

        self.draw_line(node6_x, node6_y, node10_x, node10_y)
        self.draw_line(node10_x, node10_y, node40_x, node40_y)
        self.draw_line(node38_x, node38_y, node76_x, node76_y)
        self.draw_line(node76_x, node76_y, node39_x, node39_y)
        self.draw_line(node39_x, node39_y, node40_x, node40_y)
        self.draw_line(node39_x, node39_y, node43_x, node43_y)
        self.draw_line(node40_x, node40_y, node11_x, node11_y)
        self.draw_line(node11_x, node11_y, node7_x, node7_y)

        self.draw_line(node41_x, node41_y, node45_x, node45_y)
        self.draw_line(node41_x, node41_y, node42_x, node42_y)
        self.draw_line(node42_x, node42_y, node46_x, node46_y)
        self.draw_line(node42_x, node42_y, node43_x, node43_y)
        self.draw_line(node43_x, node43_y, node44_x, node44_y)
        self.draw_line(node44_x, node44_y, node7_x, node7_y)
        self.draw_line(node44_x, node44_y, node47_x, node47_y)
        self.draw_line(node45_x, node45_y, node49_x, node49_y)
        self.draw_line(node46_x, node46_y, node49_x, node49_y)
        self.draw_line(node46_x, node46_y, node50_x, node50_y)
        self.draw_line(node47_x, node47_y, node50_x, node50_y)
        self.draw_line(node48_x, node48_y, node49_x, node49_y)
        self.draw_line(node49_x, node49_y, node50_x, node50_y)
        self.draw_line(node47_x, node47_y, node50_x, node50_y)
        self.draw_line(node50_x, node50_y, node51_x, node51_y)
        self.draw_line(node7_x, node7_y, node51_x, node51_y)
        self.draw_line(node51_x, node51_y, node12_x, node12_y)
        self.draw_line(node12_x, node12_y, node8_x, node8_y)

        self.draw_line(node48_x, node48_y, node4_x, node4_y)
        self.draw_line(node4_x, node4_y, node8_x, node8_y)

        self.draw_line(node77_x, node77_y, node5_x, node5_y)
        self.draw_line(node78_x, node78_y, node77_x, node77_y)
        self.draw_line(node79_x, node79_y, node78_x, node78_y)
        self.draw_line(node80_x, node80_y, node79_x, node79_y)
        self.draw_line(node81_x, node81_y, node79_x, node79_y)
        self.draw_line(node82_x, node82_y, node81_x, node81_y)
        self.draw_line(node83_x, node83_y, node81_x, node81_y)
        self.draw_line(node84_x, node84_y, node85_x, node85_y)
        self.draw_line(node85_x, node85_y, node80_x, node80_y)
        self.draw_line(node86_x, node86_y, node85_x, node85_y)
        self.draw_line(node87_x, node87_y, node78_x, node78_y)
        self.draw_line(node87_x, node87_y, node88_x, node88_y)
        self.draw_line(node89_x, node89_y, node88_x, node88_y)
        self.draw_line(node89_x, node89_y, node91_x, node91_y)
        self.draw_line(node90_x, node90_y, node89_x, node89_y)
        self.draw_line(node91_x, node91_y, node90_x, node90_y)
        self.draw_line(node91_x, node91_y, node98_x, node98_y)
        self.draw_line(node92_x, node92_y, node91_x, node91_y)
        self.draw_line(node93_x, node93_y, node90_x, node90_y)
        self.draw_line(node93_x, node93_y, node87_x, node87_y)
        self.draw_line(node94_x, node94_y, node93_x, node93_y)
        self.draw_line(node94_x, node94_y, node92_x, node92_y)
        self.draw_line(node94_x, node94_y, node86_x, node86_y)
        self.draw_line(node95_x, node95_y, node89_x, node89_y)
        self.draw_line(node95_x, node95_y, node13_x, node13_y)
        self.draw_line(node95_x, node95_y, node53_x, node53_y)
        self.draw_line(node96_x, node96_y, node58_x, node58_y)
        self.draw_line(node96_x, node96_y, node91_x, node91_y)
        self.draw_line(node96_x, node96_y, node21_x, node21_y)
        self.draw_line(node97_x, node97_y, node86_x, node86_y)
        self.draw_line(node98_x, node98_y, node97_x, node97_y)
        self.draw_line(node98_x, node98_y, node21_x, node21_y)
        self.draw_line(node99_x, node99_y, node97_x, node97_y)
        self.draw_line(node100_x, node100_y, node99_x, node99_y)
        self.draw_line(node100_x, node100_y, node98_x, node98_y)
        self.draw_line(node100_x, node100_y, node101_x, node101_y)
        self.draw_line(node101_x, node101_y, node99_x, node99_y)
        self.draw_line(node102_x, node102_y, node101_x, node101_y)
        self.draw_line(node102_x, node102_y, node86_x, node86_y)
        self.draw_line(node100_x, node100_y, node99_x, node99_y)
        self.draw_line(node103_x, node103_y, node104_x, node104_y)
        self.draw_line(node105_x, node105_y, node104_x, node104_y)
        self.draw_line(node106_x, node106_y, node105_x, node105_y)
        self.draw_line(node107_x, node107_y, node106_x, node106_y)
        self.draw_line(node107_x, node107_y, node105_x, node105_y)

        self.draw_line(node106_x, node106_y, node109_x, node109_y)
        self.draw_line(node106_x, node106_y, node103_x, node103_y)
        self.draw_line(node106_x, node106_y, node107_x, node107_y)
        self.draw_line(node105_x, node105_y, node107_x, node107_y)
        self.draw_line(node103_x, node103_y, node108_x, node108_y)
        self.draw_line(node109_x, node109_y, node110_x, node110_y)
        self.draw_line(node107_x, node107_y, node111_x, node111_y)
        self.draw_line(node105_x, node105_y, node113_x, node113_y)
        self.draw_line(node62_x, node62_y, node118_x, node118_y)
        self.draw_line(node116_x, node116_y, node118_x, node118_y)
        self.draw_line(node116_x, node116_y, node117_x, node117_y)
        self.draw_line(node117_x, node117_y, node118_x, node118_y)
        self.draw_line(node121_x, node121_y, node120_x, node120_y)
        self.draw_line(node122_x, node122_y, node125_x, node125_y)
        self.draw_line(node123_x, node123_y, node126_x, node126_y)
        self.draw_line(node125_x, node125_y, node126_x, node126_y)
        self.draw_line(node125_x, node125_y, node127_x, node127_y)
        self.draw_line(node126_x, node126_y, node127_x, node127_y)
        self.draw_line(node21_x, node21_y, node115_x, node115_y)
        self.draw_line(node22_x, node22_y, node119_x, node119_y)
        self.draw_line(node23_x, node23_y, node124_x, node124_y)
        self.draw_line(node24_x, node24_y, node128_x, node128_y)
        self.draw_line(node114_x, node114_y, node86_x, node86_y)
        self.draw_line(node114_x, node114_y, node115_x, node115_y)
        self.draw_line(node115_x, node115_y, node119_x, node119_y)
        self.draw_line(node124_x, node124_y, node128_x, node128_y)
        self.draw_line(node129_x, node129_y, node130_x, node130_y)
        self.draw_line(node1_x, node1_y, node130_x, node130_y)
        self.draw_line(node1_x, node1_y, node135_x, node135_y)
        self.draw_line(node1_x, node1_y, node134_x, node134_y)
        self.draw_line(node130_x, node130_y, node77_x, node77_y)
        self.draw_line(node131_x, node131_y, node132_x, node132_y)
        self.draw_line(node131_x, node131_y, node134_x, node134_y)
        self.draw_line(node133_x, node133_y, node134_x, node134_y)
        self.draw_line(node133_x, node133_y, node135_x, node135_y)
        self.draw_line(node2_x, node2_y, node132_x, node132_y)
        self.draw_line(node2_x, node2_y, node28_x, node28_y)
        self.draw_line(node28_x, node28_y, node135_x, node135_y)
        self.draw_line(node87_x, node87_y, node136_x, node136_y)
        self.draw_line(node13_x, node13_y, node136_x, node136_y)
        self.draw_line(node53_x, node53_y, node58_x, node58_y)
        self.draw_line(node84_x, node84_y, node108_x, node108_y)
        self.draw_line(node83_x, node83_y, node108_x, node108_y)
        self.draw_line(node83_x, node83_y, node109_x, node109_y)
        self.draw_line(node111_x, node111_y, node110_x, node110_y)
        self.draw_line(node111_x, node111_y, node112_x, node112_y)
        self.draw_line(node113_x, node113_y, node112_x, node112_y)
        self.draw_line(node113_x, node113_y, node114_x, node114_y)
        self.draw_line(node119_x, node119_y, node124_x, node124_y)
        self.draw_line(node121_x, node121_y, node22_x, node22_y)
        self.draw_line(node121_x, node121_y, node23_x, node23_y)
        self.draw_line(node127_x, node127_y, node75_x, node75_y)

        self.path_points = [
            (node1_x, node1_y),
            (node2_x, node2_y),
            (node3_x, node3_y),
            (node4_x, node4_y),
            (node1_x, node1_y)
        ]


        initial_positions = [
            (node31_x, node31_y),  # student 1
            (node27_x, node27_y),  # student 2
            (node26_x, node26_y),  # student 3
            (node29_x, node29_y),  # student 4
            (node32_x, node32_y),  # student 5
            (node75_x, node75_y),  # student 6
            (node26_x, node26_y), # Professor 1
            (node18_x, node18_y)  # Professor 2
        ]

        if hasattr(self, 'moving_points'):
            for point in self.moving_points.values():
                self.canvas.delete(point)
            self.moving_points = {}

        for i, pos in enumerate(initial_positions, 1):
            self.create_moving_point(*pos, i)

    def update_time_display(self):
        time_str = f"{self.map_hours:02}:{self.map_minutes:02}"
        self.time_text.delete(1.0, tk.END)
        self.time_text.insert(tk.END, time_str)

    def start_time_update(self):
        """
         if not self.simulation_running:
            return

        """
        if not self.simulation_running:

            self.start_button.configure(state=tk.DISABLED)
            return

        self.map_minutes += 1
        if self.map_minutes == 60:
            self.map_minutes = 0
            self.map_hours += 1

        # reach 24:00 or not
        if self.map_hours >= 24:
            self.simulation_running = False
            self.map_hours = 24
            self.map_minutes = 0
            self.update_time_display()

            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "The day of SCUT Student has finished", "center")
            self.status_text.tag_configure("center", justify='center')

            if hasattr(self, 'start_button'):
                self.start_button.configure(state=tk.DISABLED)

            return

        if self.map_hours >= 19 and self.current_mode == "day":
            self.set_night_mode()
        elif self.map_hours < 19 and self.current_mode == "night":
            self.set_day_mode()

        self.update_time_display()
        self.root.after(1000, self.start_time_update)

def create_gui() -> CampusGUI:

    root = tk.Tk()
    return CampusGUI(root)


if __name__ == "__main__":

    import pandas as pd
    import numpy as np

    file_path = "matrix_update.xlsx"

    try:
        df = pd.read_excel(file_path, header=None)
        distance_data = df.iloc[1:, 1:].values

        # change 0 to INF
        floyd_matrix = np.where(distance_data == 0, float('inf'), distance_data)
        np.fill_diagonal(floyd_matrix, 0)

        gui = create_gui()
        gui.create_route()
        gui.floyd_matrix = floyd_matrix

        reset_button = ttk.Button(
            gui.control_frame,
            text="Reset the simulation",
            command=gui.reset_simulation
        )
        reset_button.pack(padx=5, pady=5)
        # D5
        gui.add_building(330, 250, "canteen", "D5b")
        gui.add_building(370, 245, "dormitory", "D5c")
        gui.add_building(330, 220, "dormitory", "D5d")
        gui.add_building(370, 215, "dormitory", "D5e")
        gui.add_building(330, 190, "dormitory", "D5f")
        gui.add_building(370, 180, "dormitory", "D5g")

        # F5
        gui.add_building(530, 245, "dormitory", "F5a")
        gui.add_building(530, 215, "dormitory", "F5c")
        gui.add_building(570, 240, "canteen", "F5b")
        gui.add_building(570, 210, "dormitory", "F5d")
        gui.add_building(530, 185, "dormitory", "F5e")

        # F3
        gui.add_building(570, 380, "teaching", "F3d")
        gui.add_building(530, 380, "teaching", "F3c")
        gui.add_building(530, 420, "teaching", "F3a")
        gui.add_building(570, 420, "teaching", "F3b")

        # D3
        gui.add_building(330, 380, "teaching", "D3c")
        gui.add_building(370, 380, "teaching", "D3d")
        gui.add_building(330, 420, "teaching", "D3a")
        gui.add_building(370, 420, "teaching", "D3b")

        # D1(new)
        gui.add_building(330, 500, "academy", "D1c")
        gui.add_building(370, 520, "academy", "D1b")
        gui.add_building(330, 540, "academy", "D1a")

        # F1(new)
        gui.add_building(530, 500, "service center", "F1c")
        gui.add_building(530, 540, "service center", "F1b")
        gui.add_building(570, 520, "service center", "F1a")

        # C1(new)
        gui.add_building(235, 500, "academy", "C1c")
        gui.add_building(280, 520, "academy", "C1b")
        gui.add_building(235, 540, "academy", "C1a")

        # B1(new)
        gui.add_building(100, 510, "academy", "B1d")
        gui.add_building(175, 520, "academy", "B1c")
        gui.add_building(100, 540, "academy", "B1a")
        gui.add_building(135, 540, "academy", "B1b")
        gui.add_building(125, 475, "canteen", "B1e")

        # B2(new)
        gui.add_building(158, 390, "playground", "B2")

        # E1(new)
        gui.add_building(425, 500, "square", "E1")

        # C3&2(new)
        gui.add_building(235, 375, "service center", "C3c")
        gui.add_building(280, 375, "service center", "C3b")
        gui.add_building(235, 415, "service center", "C3a")
        gui.add_building(235, 445, "academy", "C2a")
        gui.add_building(280, 430, "academy", "C2b")

        # E3
        gui.add_building(430, 380, "library", "E3")

        # D6
        gui.add_building(320, 77, "playground & gym", "D6")  # 4新增

        # A2b
        gui.add_building(210, 185, "hospital", "A2b")  # 8新增

        # A3
        gui.add_building(65, 370, "basketball ground", "A3")  # 8新增

        # E5
        gui.add_building(435, 180, "innovative2", "Noodles")
        gui.add_building(465, 210, "innovative2", "McDonald")


        start_movement_button = ttk.Button(
            gui.control_frame,
            text="Start the movement of student",
            command=gui.move_all_students
        )
        start_movement_button.pack(padx=5, pady=5)
        gui.root.mainloop()

    except Exception as e:
        print(f"Error: {e}")







