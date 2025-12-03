# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# Inlined AutomataHanoiMatricial so the project is a single-file script
class AutomataHanoiMatricial:
    """Minimal automaton implementation for Towers of Hanoi.
    """

    def __init__(self, n_disks: int):
        if n_disks < 1:
            raise ValueError("n_disks must be >= 1")
        self.n = n_disks
        self.states = []
        self.sequence = []
        # build states and sequence
        self._build()

    def _build(self):
        # pegs as lists; top is at the end
        pegs = [list(range(self.n, 0, -1)), [], []]
        # record initial state
        self.states = [self._snapshot(pegs)]
        self.sequence = []

        def move(k, src, dst, aux):
            if k == 0:
                return
            if k == 1:
                disk = pegs[src].pop()
                pegs[dst].append(disk)
                self.sequence.append(f"{chr(65+src)}->{chr(65+dst)}")
                self.states.append(self._snapshot(pegs))
                return
            move(k-1, src, aux, dst)
            move(1, src, dst, aux)
            move(k-1, aux, dst, src)

        move(self.n, 0, 2, 1)

    def _snapshot(self, pegs):
        # store peg contents as tuples (bottom...top)
        return (tuple(pegs[0]), tuple(pegs[1]), tuple(pegs[2]))

    def export_csv(self, path: str):
        """Export states to a simple CSV: index, pegA, pegB, pegC"""
        import csv
        rows = []
        for i, st in enumerate(self.states):
            rows.append((i, "-".join(map(str, st[0])), "-".join(map(str, st[1])), "-".join(map(str, st[2]))))
        with open(path, "w", newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["index", "pegA", "pegB", "pegC"])
            for r in rows:
                w.writerow(r)

    def export_jflap(self, path: str):
        """Export the automaton as a JFLAP-compatible .jff file.

        The output matches the requested compact format with a <structure>
        element, <type>fa</type>, and an <automaton> containing <state>
        elements with <x>/<y> coordinates and <transition> entries.
        """
        import html

        total = len(self.states)
        # layout parameters (mirror example): start x=150, spacing=120, y=200
        x_start = 150
        x_spacing = 120
        y_coord = 200

        parts = []
        parts.append("<?xml version='1.0' encoding='utf-8'?>\n")
        parts.append("<structure>")
        parts.append("<type>fa</type>")
        parts.append("<automaton>")

        # states
        for i in range(total):
            name = f"S{i}"
            x = x_start + i * x_spacing
            parts.append(f"<state id=\"{i}\" name=\"{name}\">")
            parts.append(f"<x>{x}</x>")
            parts.append(f"<y>{y_coord}</y>")
            if i == 0:
                parts.append("<initial />")
            if i == total - 1:
                parts.append("<final />")
            parts.append("</state>")

        # transitions: assume linear transitions matching self.sequence
        for i, mv in enumerate(self.sequence):
            # escape for XML (convert '>' to &gt; etc.)
            read = html.escape(mv)
            parts.append("<transition>")
            parts.append(f"<from>{i}</from>")
            parts.append(f"<to>{i+1}</to>")
            parts.append(f"<read>{read}</read>")
            parts.append("</transition>")

        parts.append("</automaton>")
        parts.append("</structure>\n")

        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(parts))

    def simulate_manual(self, moves_list):
        """Simulate a list of moves like ['A->C', 'A->B'].

        Returns: (ok: bool, message: str, trace: list[(state_str, move_str)])
        """
        # copy initial pegs
        pegs = [list(range(self.n, 0, -1)), [], []]
        trace = [(self._state_str(pegs), "start")]
        for mv in moves_list:
            mv = mv.strip()
            if not mv or '->' not in mv:
                return False, f"Movimiento inválido: '{mv}'", trace
            src_c, dst_c = mv.split('->')
            try:
                src = ord(src_c.strip().upper()) - 65
                dst = ord(dst_c.strip().upper()) - 65
            except Exception:
                return False, f"Movimiento inválido: '{mv}'", trace
            if src not in (0,1,2) or dst not in (0,1,2):
                return False, f"Pilon desconocido en movimiento: '{mv}'", trace
            if not pegs[src]:
                return False, f"Pilon {src_c} está vacío: {mv}", trace
            disk = pegs[src][-1]
            if pegs[dst] and pegs[dst][-1] < disk:
                return False, f"Movimiento ilegal: no se puede poner disco {disk} sobre disco {pegs[dst][-1]}", trace
            pegs[src].pop()
            pegs[dst].append(disk)
            trace.append((self._state_str(pegs), mv))
        return True, "Simulación completada", trace

    def _state_str(self, pegs):
        return f"A:{pegs[0]} B:{pegs[1]} C:{pegs[2]}"

class HanoiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Autómata Torre de Hanoi")

        # TOP FRAME: OPtions
        frame_top = ttk.Frame(root, padding=10)
        frame_top.pack(fill="x")

        ttk.Label(frame_top, text="Número de discos:").pack(side="left")
        self.spin_disks = ttk.Spinbox(frame_top, from_=1, to=10, width=5)
        self.spin_disks.pack(side="left")
        self.spin_disks.set(3)

        ttk.Button(frame_top, text="Generar autómata", command=self.generar).pack(side="left", padx=10)
        ttk.Button(frame_top, text="Exportar CSV", command=self.export_csv).pack(side="left")
        ttk.Button(frame_top, text="Exportar JFLAP", command=self.export_jflap).pack(side="left")

        # 
        frame_controls = ttk.Frame(root, padding=8)
        frame_controls.pack(fill="x")
        self.btn_play = ttk.Button(frame_controls, text="Play", command=self.play)
        self.btn_play.pack(side="left", padx=4)
        self.btn_pause = ttk.Button(frame_controls, text="Pause", command=self.pause)
        self.btn_pause.pack(side="left", padx=4)
        self.btn_prev = ttk.Button(frame_controls, text="Prev", command=self.prev_step)
        self.btn_prev.pack(side="left", padx=4)
        self.btn_next = ttk.Button(frame_controls, text="Next", command=self.next_step)
        self.btn_next.pack(side="left", padx=4)
        # Manual interaction controls
        self.btn_manual = ttk.Button(frame_controls, text="Modo Manual", command=self.toggle_manual)
        self.btn_manual.pack(side="left", padx=(12,4))
        ttk.Button(frame_controls, text="Reset Manual", command=self.reset_manual).pack(side="left", padx=4)
        ttk.Label(frame_controls, text="Velocidad:").pack(side="left", padx=(10,2))
        self.speed = tk.DoubleVar(value=1.0)
        ttk.Scale(frame_controls, from_=0.2, to=2.0, variable=self.speed, orient="horizontal", length=150).pack(side="left")

        # FRAME CENTRAL: Canvas visual
        frame_center = ttk.Frame(root, padding=10)
        frame_center.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(frame_center, width=640, height=360, bg="#f7f7f7")
        self.canvas.pack(side="left", expand=True, fill="both")

        # panel derecho: estado / logs
        panel_right = ttk.Frame(frame_center, width=260)
        panel_right.pack(side="right", fill="y")
        # textual state / transition removed — diagram will show current node/transition

        ttk.Label(panel_right, text="Diagrama del autómata:").pack(anchor="nw", padx=6, pady=(6,0))
        self.canvas_diag = tk.Canvas(panel_right, width=240, height=120, bg="#ffffff", highlightthickness=1, highlightbackground="#ddd")
        self.canvas_diag.pack(padx=6, pady=4)

        ttk.Label(panel_right, text="Registro / Secuencia:").pack(anchor="nw", padx=6, pady=(6,0))
        self.text_output = tk.Text(panel_right, width=30, height=8)
        self.text_output.pack(padx=6, pady=4)

        self.moves = []
        self.automata = None

        # manual interaction state
        self.manual_mode = False
        self.manual_state = None  # list of lists representing current manual pegs
        self.manual_selected = None  # selected peg index or None
        # dynamic diagram built from manual moves: list of states and edges
        self.manual_diagram_nodes = []  # each node is a tuple-of-tuples state
        self.manual_diagram_edges = []  # list of (from_idx, to_idx, move_str)

        # visualization state
        self.current_index = 0
        self.playing = False

        # canvas drawing params
        self.peg_x = [120, 320, 520]
        self.base_y = 300
        self.peg_height = 200
        self.disk_height = 20
        self.disk_min_w = 40
        self.disk_max_w = 200

        self._draw_pegs()

    def _draw_pegs(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 640
        h = self.canvas.winfo_height() or 360
        # background nice
        self.canvas.create_rectangle(0, 0, w, h, fill="#f2f6f9", outline="")
        floor_y = self.base_y + 10
        self.canvas.create_rectangle(0, floor_y, w, h, fill="#e8e8e8", outline="")
        for x in self.peg_x:
            self.canvas.create_rectangle(x-5, self.base_y - self.peg_height, x+5, self.base_y, fill="#8b6b4f")
            # label
            idx = self.peg_x.index(x)
            # if in manual mode, visually mark peg C (idx==2) as the goal
            if getattr(self, 'manual_mode', False) and idx == 2:
                # draw a colored halo and place a large star and 'META' label above the top of peg C
                top_y = self.base_y - self.peg_height
                # halo slightly above the peg top
                self.canvas.create_oval(x-40, top_y-44, x+40, top_y+8, outline="#e76f51", width=3)
                # big star above the halo
                self.canvas.create_text(x, top_y-24, text="★", font=("Arial", 20), fill="#f4a261")
                # label 'META' directly above the star
                self.canvas.create_text(x, top_y-48, text=f"{chr(65+idx)}  (META)", font=("Arial", 12, "bold"), fill="#e76f51")
            else:
                self.canvas.create_text(x, self.base_y + 30, text=chr(65+idx), font=("Arial", 12, "bold"))

    def generar(self):
        try:
            n = int(self.spin_disks.get())
        except Exception:
            messagebox.showwarning("Error", "Número de discos inválido")
            return
        self.automata = AutomataHanoiMatricial(n)
        self.moves = []
        self.current_index = 0
        self.playing = False
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, f"Autómata generado para {n} discos.\n")
        self.text_output.insert(tk.END, f"Estados: {len(self.automata.states)}\n")
        self.text_output.insert(tk.END, f"Movimientos esperados: {len(self.automata.sequence)}\n")
        self.text_output.insert(tk.END, "Secuencia automática:\n")
        self.text_output.insert(tk.END, " → ".join(self.automata.sequence) + "\n")
        # draw initial state
        self._draw_pegs()
        self.draw_state(self.automata.states[0])
        # initialize manual state to current state
        self.manual_state = [list(peg) for peg in self.automata.states[0]]
        self._update_info()

    def export_csv(self):
        if not self.automata:
            messagebox.showwarning("Error", "Primero genera un autómata.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".csv")
        if f:
            self.automata.export_csv(f)
            messagebox.showinfo("Éxito", "CSV exportado correctamente.")

    def export_jflap(self):
        if not self.automata:
            messagebox.showwarning("Error", "Primero genera un autómata.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".jff")
        if f:
            self.automata.export_jflap(f)
            messagebox.showinfo("Éxito", "Archivo JFLAP exportado.")

    def draw_state(self, state, exclude=None):
        # state is tuple of three tuples (pegA, pegB, pegC) (bottom..top)
        # exclude: optional tuple (peg_idx, disk_size) to skip drawing that disk (used during animation)
        self.canvas.delete("disk")
        n = self.automata.n if self.automata else 1
        for peg_idx, peg in enumerate(state):
            # peg is tuple bottom..top; draw from bottom->top so larger disks appear below smaller ones
            for depth, disk in enumerate(peg):
                if exclude and exclude[0] == peg_idx and exclude[1] == disk:
                    continue
                # compute size and width
                size = disk
                if n > 1:
                    w = self.disk_min_w + (size-1) * (self.disk_max_w - self.disk_min_w) / (n-1)
                else:
                    w = self.disk_max_w
                x = self.peg_x[peg_idx]
                # position from bottom: index in peg (0 bottom)
                stack_pos = depth
                y = self.base_y - (stack_pos + 1) * self.disk_height
                color = self._color_for_disk(size)
                # draw rectangle (bottom ones first, top ones later will appear above)
                self.canvas.create_rectangle(x - w/2, y - self.disk_height + 2, x + w/2, y + 2, fill=color, outline="#333", tags=("disk",))
                self.canvas.create_text(x, y - self.disk_height/2 + 2, text=str(size), tags=("disk",), fill="#fff")

    def _color_for_disk(self, size):
        # deterministic color palette based on size
        palette = ["#e63946", "#f3722c", "#f9c74f", "#90be6d", "#43aa8b", "#577590", "#6a4c93", "#2a9d8f", "#264653", "#ffb703"]
        return palette[(size-1) % len(palette)]

    def _update_info(self):
        if not self.automata:
            # nothing to update in diagram when no automaton
            return
        st = self.automata.states[self.current_index]
        # textual labels removed — keep diagram updated
        # draw automaton diagram centered on current index
        self.draw_automaton_diagram()

    def add_move(self):
        # keep simple: allow manual adding to log only
        mv = self.entry_move.get().strip()
        if mv:
            self.moves.append(mv)
            self.text_output.insert(tk.END, f"\nMovimiento agregado: {mv}")
            self.entry_move.delete(0, tk.END)

    def simular_manual(self):
        if not self.automata:
            messagebox.showwarning("Error", "Primero genera un autómata.")
            return
        ok, msg, trace = self.automata.simulate_manual(self.moves)
        self.text_output.insert(tk.END, "\n\n--- Simulación manual ---\n")
        for state, move in trace:
            self.text_output.insert(tk.END, f"{state} <- {move}\n")
        self.text_output.insert(tk.END, f"\nResultado: {msg}\n")

    # playback controls
    def play(self):
        if not self.automata:
            messagebox.showwarning("Error", "Primero genera un autómata.")
            return
        if self.playing:
            return
        self.playing = True
        self._play_step()

    def _play_step(self):
        if not self.playing:
            return
        if self.current_index < len(self.automata.states) - 1:
            # advance after delay (diagram shows transition)
            delay = int(800 / self.speed.get())
            self.root.after(delay, self._advance_and_draw)
        else:
            self.playing = False

    def _advance_and_draw(self):
        # animate move from current_index -> next
        if not self.automata or self.current_index >= len(self.automata.states) - 1:
            self.playing = False
            return
        if getattr(self, 'animating', False):
            return
        start = self.automata.states[self.current_index]
        end = self.automata.states[self.current_index+1]
        # determine move from sequence string
        mv = self.automata.sequence[self.current_index]
        try:
            src = ord(mv.split('->')[0].strip().upper()) - 65
            dst = ord(mv.split('->')[1].strip().upper()) - 65
        except Exception:
            src = dst = None
        # find disk moved by set difference
        disk = None
        if src is not None:
            diff = set(start[src]) - set(end[src])
            if diff:
                disk = diff.pop()

        if disk is None or src is None or dst is None:
            # fallback: just advance without animation
            self.current_index += 1
            self.draw_state(self.automata.states[self.current_index])
            self._update_info()
            if self.playing:
                self._play_step()
            return

        # perform animated move
        self.animating = True
        self.animate_move(src, dst, disk, start, end, lambda: self._on_animation_done())

    def draw_automaton_diagram(self):
        """Draw a compact linear diagram of states centered on the current index.
        """
        # If manual mode is active, show only the manual diagram
        if getattr(self, 'manual_mode', False):
            self.canvas_diag.delete("all")
            # draw only user's manual path
            m_nodes = getattr(self, 'manual_diagram_nodes', []) or []
            m_edges = getattr(self, 'manual_diagram_edges', []) or []
            # If no manual nodes, show a hint
            w = int(self.canvas_diag.winfo_width() or 240)
            h = int(self.canvas_diag.winfo_height() or 120)
            if not m_nodes:
                self.canvas_diag.create_text(w//2, h//2, text="Aún no has hecho movimientos.", fill="#666")
                # show goal indicator
                
                return
            # draw a focused manual diagram centered
            # reuse compact drawer
            self.draw_compact_diagram(self.canvas_diag, m_nodes, m_edges, highlight_idx=len(m_nodes)-1, title="Tu diagrama (manual)")
            # visual goal indicator for peg C
            self.canvas_diag.create_text(w-48, 14, text="", fill="#e76f51", font=("Arial", 9, "bold"))
            return
        if not self.automata:
            self.canvas_diag.delete("all")
            return
        total = len(self.automata.states)
        max_nodes = 11
        # determine window centered at current_index
        center = self.current_index
        half = max_nodes // 2
        start = max(0, center - half)
        end = min(total, start + max_nodes)
        if end - start < max_nodes:
            start = max(0, end - max_nodes)

        self.canvas_diag.delete("all")
        w = int(self.canvas_diag.winfo_width() or 240)
        h = int(self.canvas_diag.winfo_height() or 120)
        pad = 16
        count = end - start
        if count <= 0:
            return
        spacing = (w - 2*pad) / max(1, count-1)
        r = 12
        y = h//2
        for idx in range(start, end):
            x = int(pad + (idx - start) * spacing)
            is_current = (idx == self.current_index)
            fill = "#2a9d8f" if is_current else "#ffffff"
            outline = "#0b3d2e" if is_current else "#666"
            self.canvas_diag.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=outline, width=2)
            # small label
            label = f"q{idx}"
            self.canvas_diag.create_text(x, y, text=label, fill="#fff" if is_current else "#000")
            # draw arrow to next
            if idx < end-1:
                x2 = int(pad + (idx+1 - start) * spacing)
                # highlight arrow if this is the current transition
                arrow_color = "#e76f51" if idx == self.current_index else "#aaa"
                self.canvas_diag.create_line(x+r, y, x2-r, y, arrow=tk.LAST, fill=arrow_color, width=2)
        # legend: current transition text
        if self.current_index < total-1:
            mv = self.automata.sequence[self.current_index]
            self.canvas_diag.create_text(w//2, h-14, text=f"Transición: {mv}", fill="#222", font=("Arial", 9))

        # ---- Draw manual path (if any) below the main diagram ----
        if getattr(self, 'manual_diagram_nodes', None):
            m_nodes = self.manual_diagram_nodes
            m_edges = self.manual_diagram_edges
            if m_nodes:
                # draw manual nodes in lower third
                y_manual = int(h * 0.75)
                # compute layout: spread across width
                pad_m = 12
                count = max(1, len(m_nodes))
                spacing_m = (w - 2*pad_m) / max(1, count-1)
                r_m = 8
                # title
                self.canvas_diag.create_text(w//2, int(h*0.57), text="Ruta manual:", fill="#333", font=("Arial", 8, "italic"))
                for i, node in enumerate(m_nodes):
                    x = int(pad_m + i * spacing_m)
                    is_last = (i == len(m_nodes)-1)
                    fill = "#264653" if is_last else "#ffffff"
                    outline = "#264653" if is_last else "#888"
                    self.canvas_diag.create_oval(x-r_m, y_manual-r_m, x+r_m, y_manual+r_m, fill=fill, outline=outline, width=2)
                    # tiny label with index
                    self.canvas_diag.create_text(x, y_manual, text=str(i), fill="#fff" if is_last else "#000", font=("Arial", 8))
                # edges
                for e in m_edges:
                    fx, tx, mv = e
                    x1 = int(pad_m + fx * spacing_m)
                    x2 = int(pad_m + tx * spacing_m)
                    self.canvas_diag.create_line(x1+r_m, y_manual, x2-r_m, y_manual, arrow=tk.LAST, fill="#e9c46a", width=2)
                    # label midway
                    xm = (x1 + x2)//2
                    self.canvas_diag.create_text(xm, y_manual-12, text=mv, fill="#b35f00", font=("Arial", 7))

    def animate_diagram_move(self, old_idx, new_idx):
        # animate a highlight moving from old_idx to new_idx within the current window
        if not self.automata:
            return
        total = len(self.automata.states)
        max_nodes = 11
        center = self.current_index
        half = max_nodes // 2
        start = max(0, center - half)
        end = min(total, start + max_nodes)
        if end - start < max_nodes:
            start = max(0, end - max_nodes)

        w = int(self.canvas_diag.winfo_width() or 240)
        h = int(self.canvas_diag.winfo_height() or 120)
        pad = 16
        count = end - start
        if count <= 0:
            return
        spacing = (w - 2*pad) / max(1, count-1)

        # compute positions; if new_idx outside window, just set current_index and redraw
        if not (start <= old_idx < end) or not (start <= new_idx < end):
            self.current_index = new_idx
            self.draw_automaton_diagram()
            return

        x_old = int(pad + (old_idx - start) * spacing)
        x_new = int(pad + (new_idx - start) * spacing)
        y = h//2
        r = 14

        overlay = self.canvas_diag.create_oval(x_old-r, y-r, x_old+r, y+r, fill="#264653", outline="#000", width=2, tags=("overlay",))
        steps = max(4, int(abs(x_new - x_old) / 6))
        dx = (x_new - x_old) / steps

        def step(i=0):
            if i < steps:
                self.canvas_diag.move(overlay, dx, 0)
                self.root.after(30, lambda: step(i+1))
            else:
                self.canvas_diag.delete(overlay)
                self.current_index = new_idx
                self.draw_automaton_diagram()

        step()

    # --- Manual interaction helpers ---
    def toggle_manual(self):
        if not self.automata:
            messagebox.showwarning("Error", "Primero genera un autómata.")
            return
        self.manual_mode = not self.manual_mode
        if self.manual_mode:
            # enable manual: pause playback, bind clicks, copy current displayed state
            self.pause()
            self.btn_manual.config(text="Salir Manual")
            self.manual_state = [list(peg) for peg in self.automata.states[self.current_index]]
            # initialize manual diagram path with current configuration as first node
            self.manual_diagram_nodes = [tuple(tuple(peg) for peg in self.manual_state)]
            self.manual_diagram_edges = []
            self.manual_selected = None
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.text_output.insert(tk.END, "\nModo manual activado. Clic en un poste para seleccionar, luego clic en destino para mover.\n")
            # disable playback controls while manual active
            self.disable_playback_controls(True)
            # start pulsing goal marker above peg C
            # start pulsing goal marker above peg C
            try:
                self.start_goal_pulse()
            except Exception:
                pass
        else:
            # disable manual
            self.btn_manual.config(text="Modo Manual")
            self.manual_selected = None
            self.canvas.unbind("<Button-1>")
            self.canvas.delete("selection")
            self.text_output.insert(tk.END, "\nModo manual desactivado.\n")
            # re-enable playback controls
            self.disable_playback_controls(False)
        pass
        # update diagram to reflect manual diagram presence
        self.draw_automaton_diagram()
        # stop pulsing when exiting manual mode
        if not self.manual_mode:
            try:
                self.stop_goal_pulse()
            except Exception:
                pass

    def reset_manual(self):
        if not self.automata:
            return
        self.manual_state = [list(peg) for peg in self.automata.states[0]]
        self.draw_state(tuple(tuple(peg) for peg in self.manual_state))
        self.manual_selected = None
        self.canvas.delete("selection")
        self.text_output.insert(tk.END, "\nEstado manual reseteado a la configuración inicial.\n")
        # reset manual diagram as well
        self.manual_diagram_nodes = [tuple(tuple(peg) for peg in self.manual_state)]
        self.manual_diagram_edges = []
        self.draw_automaton_diagram()

    def on_canvas_click(self, event):
        if not self.manual_mode or getattr(self, 'animating', False):
            return
        x = event.x
        # find nearest peg
        distances = [abs(x - px) for px in self.peg_x]
        peg_idx = distances.index(min(distances))
        if min(distances) > 120:
            return
        # selection flow
        if self.manual_selected is None:
            # select source if it has disks
            if not self.manual_state[peg_idx]:
                self.text_output.insert(tk.END, f"\nEl poste {chr(65+peg_idx)} está vacío. Selecciona otro poste.\n")
                return
            self.manual_selected = peg_idx
            self._draw_selection(peg_idx)
            self.text_output.insert(tk.END, f"\nSeleccionado poste {chr(65+peg_idx)}\n")
        else:
            src = self.manual_selected
            dst = peg_idx
            if src == dst:
                # deselect
                self.manual_selected = None
                self.canvas.delete("selection")
                return
            # validate move
            if not self.manual_state[src]:
                self.text_output.insert(tk.END, "\nSeleccion inválida (vacío).\n")
                self.manual_selected = None
                self.canvas.delete("selection")
                return
            disk = self.manual_state[src][-1]
            if self.manual_state[dst] and self.manual_state[dst][-1] < disk:
                # illegal
                self._indicate_invalid_move(dst, disk)
                self.manual_selected = None
                self.canvas.delete("selection")
                return
            # legal: animate move from manual_state
            start_state = tuple(tuple(peg) for peg in self.manual_state)
            # create end_state
            end_state_list = [list(peg) for peg in self.manual_state]
            end_state_list[src].pop()
            end_state_list[dst].append(disk)
            end_state = tuple(tuple(peg) for peg in end_state_list)
            self.animating = True
            # animate_move will draw end_state at the end; on_done update manual_state
            def on_done():
                self.animating = False
                self.manual_state = end_state_list
                self.manual_selected = None
                self.canvas.delete("selection")
                self.text_output.insert(tk.END, f"\nMovimiento: {chr(65+src)}->{chr(65+dst)}\n")

            # after manual move completes, check if manual_state matches an automaton state
            def on_done_with_sync():
                on_done()
                # append to manual diagram path
                new_node = tuple(tuple(peg) for peg in self.manual_state)
                from_idx = len(self.manual_diagram_nodes) - 1
                to_idx = from_idx + 1
                mv_str = f"{chr(65+src)}->{chr(65+dst)}"
                self.manual_diagram_nodes.append(new_node)
                self.manual_diagram_edges.append((from_idx, to_idx, mv_str))
                # redraw to show updated manual path
                self.draw_automaton_diagram()
                # if the manual configuration matches an automaton state, animate main diagram
                target = new_node
                try:
                    idx = self.automata.states.index(target)
                except ValueError:
                    idx = None
                if idx is not None:
                    old = self.current_index
                    self.animate_diagram_move(old, idx)
                    # if we reached the final automaton state, show congratulations and both diagrams
                    try:
                        final_state = self.automata.states[-1]
                    except Exception:
                        final_state = None
                    if final_state is not None and tuple(tuple(peg) for peg in self.manual_state) == final_state:
                        # show completion dialog
                        self.show_completion_dialog()

            self.animate_move(src, dst, disk, start_state, end_state, on_done_with_sync)

    def _draw_selection(self, peg_idx):
        # draw a highlight rectangle around top disk of peg
        self.canvas.delete("selection")
        peg = self.manual_state[peg_idx]
        if not peg:
            return
        n = self.automata.n if self.automata else 1
        disk = peg[-1]
        if n > 1:
            w = self.disk_min_w + (disk-1) * (self.disk_max_w - self.disk_min_w) / (n-1)
        else:
            w = self.disk_max_w
        x = self.peg_x[peg_idx]
        stack_pos = len(peg)-1
        y = self.base_y - (stack_pos + 1) * self.disk_height
        self.canvas.create_rectangle(x - w/2 - 4, y - self.disk_height + 2 - 4, x + w/2 + 4, y + 2 + 4, outline="#ffdd57", width=3, tags=("selection",))

    def _indicate_invalid_move(self, dst, disk):
        # shake left canvas to indicate invalid move and log error
        self.text_output.insert(tk.END, f"\nMovimiento inválido: no se puede colocar disco {disk} sobre uno más pequeño en {chr(65+dst)}\n")
        pattern = [-10, 20, -16, 12, -6, 0]
        def do_shake(i=0):
            if i >= len(pattern):
                return
            dx = pattern[i]
            self.canvas.move("all", dx, 0)
            self.root.after(40, lambda: do_shake(i+1))
        do_shake()

    def pause(self):
        self.playing = False

    def _on_animation_done(self):
        self.animating = False
        # after animation, advance index and update
        self.current_index += 1
        self.draw_state(self.automata.states[self.current_index])
        self._update_info()
        if self.playing:
            self._play_step()

    def _on_animation_prev_done(self):
        self.animating = False
        # after reverse animation, decrement index and update
        self.current_index -= 1
        self.draw_state(self.automata.states[self.current_index])
        self._update_info()

    def disable_playback_controls(self, disable=True):
        state = 'disabled' if disable else 'normal'
        try:
            self.btn_play.config(state=state)
            self.btn_pause.config(state=state)
            self.btn_prev.config(state=state)
            self.btn_next.config(state=state)
        except Exception:
            pass

    def next_step(self):
        if not self.automata or getattr(self, 'animating', False):
            return
        if self.current_index < len(self.automata.states) - 1:
            # animate single step similar to play
            start = self.automata.states[self.current_index]
            end = self.automata.states[self.current_index+1]
            mv = self.automata.sequence[self.current_index]
            try:
                src = ord(mv.split('->')[0].strip().upper()) - 65
                dst = ord(mv.split('->')[1].strip().upper()) - 65
            except Exception:
                src = dst = None
            disk = None
            if src is not None:
                diff = set(start[src]) - set(end[src])
                if diff:
                    disk = diff.pop()
            if disk is None or src is None or dst is None:
                self.current_index += 1
                self.draw_state(self.automata.states[self.current_index])
                self._update_info()
            else:
                self.animating = True
                self.animate_move(src, dst, disk, start, end, lambda: self._on_animation_done())

    def prev_step(self):
        if not self.automata or getattr(self, 'animating', False):
            return
        if self.current_index > 0:
            # animate reverse move: determine forward move at index-1, then animate dst->src
            start = self.automata.states[self.current_index]
            end = self.automata.states[self.current_index-1]
            mv_forward = self.automata.sequence[self.current_index-1]
            try:
                src_f = ord(mv_forward.split('->')[0].strip().upper()) - 65
                dst_f = ord(mv_forward.split('->')[1].strip().upper()) - 65
            except Exception:
                src_f = dst_f = None
            disk = None
            if dst_f is not None:
                diff = set(start[dst_f]) - set(end[dst_f])
                if diff:
                    disk = diff.pop()
            if disk is None or src_f is None or dst_f is None:
                # fallback: just move index back
                self.current_index -= 1
                self.draw_state(self.automata.states[self.current_index])
                self._update_info()
            else:
                # animate from dst_f -> src_f (reverse of forward move)
                self.animating = True
                self.animate_move(dst_f, src_f, disk, start, end, lambda: self._on_animation_prev_done())

    def animate_move(self, src, dst, disk, start_state, end_state, on_done=None):
        """Animate a single disk moving from peg `src` to peg `dst`.

        Animation path: lift -> horizontal -> drop. Uses `self.speed` to scale duration.
        on_done: callback called after animation ends.
        """
        # compute start coords
        try:
            start_stack_pos = list(start_state[src]).index(disk)
        except ValueError:
            start_stack_pos = 0
        try:
            end_stack_pos = list(end_state[dst]).index(disk)
        except ValueError:
            end_stack_pos = 0

        start_x = self.peg_x[src]
        end_x = self.peg_x[dst]
        start_y = self.base_y - (start_stack_pos + 1) * self.disk_height
        end_y = self.base_y - (end_stack_pos + 1) * self.disk_height

        n = self.automata.n if self.automata else 1
        size = disk
        if n > 1:
            w = self.disk_min_w + (size-1) * (self.disk_max_w - self.disk_min_w) / (n-1)
        else:
            w = self.disk_max_w
        color = self._color_for_disk(size)

        # prepare static drawing without the moving disk
        self.draw_state(start_state, exclude=(src, disk))

        # create moving disk
        rect = self.canvas.create_rectangle(start_x - w/2, start_y - self.disk_height + 2, start_x + w/2, start_y + 2, fill=color, outline="#333", tags=("moving",))
        text = self.canvas.create_text(start_x, start_y - self.disk_height/2 + 2, text=str(size), fill="#fff", tags=("moving",))

        # animation timing
        total_ms = max(200, int(700 / max(0.2, min(self.speed.get(), 2.0))))
        lift_ms = int(total_ms * 0.25)
        horiz_ms = int(total_ms * 0.5)
        drop_ms = int(total_ms * 0.25)

        # compute lift to a safe y above pegs
        top_y = self.base_y - self.peg_height - 20

        steps_lift = max(3, int(lift_ms / 30))
        steps_horiz = max(3, int(horiz_ms / 30))
        steps_drop = max(3, int(drop_ms / 30))

        dx_lift = 0
        dy_lift = (top_y - start_y) / steps_lift

        dx_horiz = (end_x - start_x) / steps_horiz
        dy_horiz = 0

        dx_drop = 0
        dy_drop = (end_y - top_y) / steps_drop

        # step counters
        state = {"phase": "lift", "i": 0}

        def step():
            if state["phase"] == "lift":
                if state["i"] < steps_lift:
                    self.canvas.move(rect, dx_lift, dy_lift)
                    self.canvas.move(text, dx_lift, dy_lift)
                    state["i"] += 1
                    self.root.after(30, step)
                else:
                    state["phase"] = "horiz"
                    state["i"] = 0
                    step()
            elif state["phase"] == "horiz":
                if state["i"] < steps_horiz:
                    self.canvas.move(rect, dx_horiz, dy_horiz)
                    self.canvas.move(text, dx_horiz, dy_horiz)
                    state["i"] += 1
                    self.root.after(30, step)
                else:
                    state["phase"] = "drop"
                    state["i"] = 0
                    step()
            elif state["phase"] == "drop":
                if state["i"] < steps_drop:
                    self.canvas.move(rect, dx_drop, dy_drop)
                    self.canvas.move(text, dx_drop, dy_drop)
                    state["i"] += 1
                    self.root.after(30, step)
                else:
                    # end animation: remove moving items and draw end state
                    self.canvas.delete("moving")
                    self.draw_state(end_state)
                    if on_done:
                        on_done()

        # start animation
        step()

    def draw_compact_diagram(self, canvas_obj, nodes, edges, highlight_idx=None, title=None):
        """Draw a simple horizontal diagram on `canvas_obj` from `nodes` and `edges`.

        - `nodes`: list of state objects (can be any printable identifier)
        - `edges`: list of (from_idx, to_idx, label)
        - `highlight_idx`: index to emphasize
        """
        canvas_obj.delete("all")
        w = int(canvas_obj.winfo_width() or 360)
        h = int(canvas_obj.winfo_height() or 200)
        pad = 16
        count = max(1, len(nodes))
        spacing = (w - 2*pad) / max(1, count-1)
        r = 14
        y = h//2
        # optional title
        if title:
            canvas_obj.create_text(w//2, 12, text=title, fill="#222", font=("Arial", 10, "bold"))
        for i in range(len(nodes)):
            x = int(pad + i * spacing)
            is_current = (i == highlight_idx)
            fill = "#2a9d8f" if is_current else "#fff"
            outline = "#0b3d2e" if is_current else "#666"
            canvas_obj.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=outline, width=2)
            canvas_obj.create_text(x, y, text=f"{i}", fill="#fff" if is_current else "#000")
        # draw edges with labels
        for e in edges:
            fx, tx, mv = e
            if fx < 0 or tx < 0 or fx >= len(nodes) or tx >= len(nodes):
                continue
            x1 = int(pad + fx * spacing)
            x2 = int(pad + tx * spacing)
            canvas_obj.create_line(x1+r, y, x2-r, y, arrow=tk.LAST, fill="#888", width=2)
            xm = (x1 + x2)//2
            canvas_obj.create_text(xm, y-12, text=mv, fill="#333", font=("Arial", 8))

    def show_completion_dialog(self):
        """Show a popup congratulating the user and displaying both diagrams.

        Left: optimal automaton (full sequence). Right: user's manual path.
        """
        # disable manual interactions while dialog is open
        self.manual_mode = False
        self.canvas.unbind("<Button-1>")
        self.btn_manual.config(text="Modo Manual")
        self.disable_playback_controls(False)

        top = tk.Toplevel(self.root)
        top.title("¡Felicidades!")
        top.geometry("760x360")
        ttk.Label(top, text="¡Felicidades! Has completado la torre.", font=("Arial", 12, "bold")).pack(pady=8)
        frame = ttk.Frame(top)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        left = tk.Canvas(frame, width=360, height=260, bg="#fff", highlightthickness=1, highlightbackground="#ccc")
        left.pack(side="left", padx=6, pady=6)
        right = tk.Canvas(frame, width=360, height=260, bg="#fff", highlightthickness=1, highlightbackground="#ccc")
        right.pack(side="right", padx=6, pady=6)

        # prepare automaton edges (consecutive transitions)
        auto_edges = []
        for i, mv in enumerate(self.automata.sequence):
            auto_edges.append((i, i+1, mv))

        # manual edges are already stored
        manual_edges = list(self.manual_diagram_edges)

        # draw diagrams (if canvases haven't been rendered size yet, after_idle helps)
        def draw_both():
            self.draw_compact_diagram(left, self.automata.states, auto_edges, highlight_idx=len(self.automata.states)-1, title="Solución óptima")
            self.draw_compact_diagram(right, self.manual_diagram_nodes, manual_edges, highlight_idx=len(self.manual_diagram_nodes)-1, title="Tu solución (manual)")

        top.after(100, draw_both)
        ttk.Button(top, text="Cerrar", command=top.destroy).pack(pady=6)

    def show_hint(self):
        # hint feature removed; no-op
        return

    def start_goal_pulse(self):
        """Start a pulsing animation above peg C. Idempotent."""
        try:
            self.stop_goal_pulse()
        except Exception:
            pass
        x = self.peg_x[2]
        top_y = self.base_y - self.peg_height
        halo = self.canvas.create_oval(x-40, top_y-44, x+40, top_y+8, outline="#e76f51", width=3, tags=("goal_pulse",))
        star = self.canvas.create_text(x, top_y-24, text="★", font=("Arial", 20), fill="#f4a261", tags=("goal_pulse",))
        label = self.canvas.create_text(x, top_y-48, text=f"C  (META)", font=("Arial", 12, "bold"), fill="#e76f51", tags=("goal_pulse",))
        self._goal_pulse = {"x": x, "top_y": top_y, "phase": 0, "dir": 1, "job": None, "steps": 8}

        def pulse_step():
            st = self._goal_pulse
            steps = st["steps"]
            i = st["phase"]
            t = (i / (steps-1))
            scale = 1.0 + 0.18 * (0.5 - 0.5 * (__import__("math").cos(t * 2 * __import__("math").pi)))
            x = st["x"]
            top_y = st["top_y"]
            r = int(40 * scale)
            try:
                self.canvas.coords(halo, x-r, top_y-(r+4), x+r, top_y+(r/2))
                self.canvas.itemconfig(halo, width=max(2, int(3 * scale)))
                star_size = int(18 * scale)
                self.canvas.itemconfig(star, font=("Arial", star_size))
            except Exception:
                pass
            st["phase"] += st["dir"]
            if st["phase"] >= steps - 1 or st["phase"] <= 0:
                st["dir"] *= -1
            st["job"] = self.root.after(100, pulse_step)

        self._goal_pulse["job"] = self.root.after(150, pulse_step)

    def stop_goal_pulse(self):
        """Stop and remove pulse overlay items."""
        st = getattr(self, '_goal_pulse', None)
        if st:
            job = st.get('job')
            if job:
                try:
                    self.root.after_cancel(job)
                except Exception:
                    pass
        try:
            self.canvas.delete("goal_pulse")
        except Exception:
            pass
        self._goal_pulse = None


if __name__ == "__main__":
    root = tk.Tk()
    app = HanoiGUI(root)
    root.mainloop()
