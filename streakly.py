import tkinter as tk
from tkinter import ttk, messagebox
import json, os, sys, calendar
from datetime import date, datetime, timedelta
from pathlib import Path

APP_NAME = "Streakly Planner"
LOCAL_ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
DATA_DIR = LOCAL_ROOT / "Streakly"
DATA_FILE = DATA_DIR / "planner_data.json"
# One-time migration from earlier Dayframe-branded builds; this copies only local data.
LEGACY_DATA_FILE = LOCAL_ROOT / "Dayframe" / "planner_data.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)
if not DATA_FILE.exists() and LEGACY_DATA_FILE.exists():
    try:
        import shutil
        shutil.copy2(LEGACY_DATA_FILE, DATA_FILE)
    except OSError:
        pass

LANG = {
"en": {"app":"Streakly Planner","calendar":"Your calendar","choose":"Choose any day to plan it.","today":"Today","back":"← Calendar","prev":"‹","next":"›","daily":"Daily timeline","add":"＋ Add task","quick":"Task details","title":"Task title","start":"Start","end":"End","category":"Category","notes":"Notes","save":"Save task","clear":"Clear","delete":"Delete","daynotes":"Daily notes","savenotes":"Save notes","empty":"No tasks yet. Add one to start planning.","invalid":"End time must be after start time.","saved":"Saved","privacy":"Offline by design · Your plans stay on this computer","categories":["Study","Work","Personal","Break","Errand","Health"],"hint":"Select a date to open its daily timeline.","taskcount":"tasks","notehint":"What matters most today?","language":"Language","edit":"Edit selected task","reminder":"Plans are saved automatically on this computer."},
"sw": {"app":"Streakly Planner","calendar":"Kalenda yako","choose":"Chagua siku yoyote kupanga ratiba.","today":"Leo","back":"← Kalenda","prev":"‹","next":"›","daily":"Ratiba ya siku","add":"＋ Ongeza kazi","quick":"Maelezo ya kazi","title":"Jina la kazi","start":"Mwanzo","end":"Mwisho","category":"Aina","notes":"Maelezo","save":"Hifadhi kazi","clear":"Futa sehemu","delete":"Futa","daynotes":"Maelezo ya siku","savenotes":"Hifadhi maelezo","empty":"Hakuna kazi bado. Ongeza moja kuanza kupanga.","invalid":"Muda wa mwisho lazima uwe baada ya muda wa mwanzo.","saved":"Imehifadhiwa","privacy":"Hufanya kazi bila intaneti · Mipango yako hubaki kwenye kompyuta hii","categories":["Masomo","Kazi","Binafsi","Mapumziko","Safari","Afya"],"hint":"Chagua tarehe ili kufungua ratiba ya siku.","taskcount":"kazi","notehint":"Ni jambo gani muhimu leo?","language":"Lugha","edit":"Hariri kazi iliyochaguliwa","reminder":"Mipango huhifadhiwa kiotomatiki kwenye kompyuta hii."},
"fr": {"app":"Streakly Planner","calendar":"Votre calendrier","choose":"Choisissez un jour à organiser.","today":"Aujourd’hui","back":"← Calendrier","prev":"‹","next":"›","daily":"Planning du jour","add":"＋ Ajouter une tâche","quick":"Détails de la tâche","title":"Titre de la tâche","start":"Début","end":"Fin","category":"Catégorie","notes":"Notes","save":"Enregistrer","clear":"Effacer","delete":"Supprimer","daynotes":"Notes du jour","savenotes":"Enregistrer les notes","empty":"Aucune tâche. Ajoutez-en une pour commencer.","invalid":"L’heure de fin doit être après l’heure de début.","saved":"Enregistré","privacy":"Hors ligne par conception · Vos données restent sur cet ordinateur","categories":["Études","Travail","Personnel","Pause","Courses","Santé"],"hint":"Sélectionnez une date pour ouvrir son planning.","taskcount":"tâches","notehint":"Quelle est la priorité du jour ?","language":"Langue","edit":"Modifier la tâche sélectionnée","reminder":"Vos plans sont enregistrés automatiquement sur cet ordinateur."},
"es": {"app":"Streakly Planner","calendar":"Tu calendario","choose":"Elige un día para organizarlo.","today":"Hoy","back":"← Calendario","prev":"‹","next":"›","daily":"Agenda diaria","add":"＋ Añadir tarea","quick":"Detalles de la tarea","title":"Título de la tarea","start":"Inicio","end":"Fin","category":"Categoría","notes":"Notas","save":"Guardar tarea","clear":"Limpiar","delete":"Eliminar","daynotes":"Notas del día","savenotes":"Guardar notas","empty":"Todavía no hay tareas. Añade una para empezar.","invalid":"La hora de fin debe ser posterior a la de inicio.","saved":"Guardado","privacy":"Sin conexión por diseño · Tus planes quedan en este ordenador","categories":["Estudio","Trabajo","Personal","Descanso","Recados","Salud"],"hint":"Selecciona una fecha para abrir su agenda.","taskcount":"tareas","notehint":"¿Qué es lo más importante hoy?","language":"Idioma","edit":"Editar tarea seleccionada","reminder":"Tus planes se guardan automáticamente en este ordenador."}
}
BG="#101719"; PANEL="#172326"; PANEL2="#203235"; INK="#e8f2f2"; MUTED="#9bb3b5"; ACCENT="#8bd6dc"; LINE="#30484b"
def load_data():
    try: return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception: return {}
def save_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp=DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    tmp.replace(DATA_FILE)
data=load_data()
def key(d): return d.strftime("%Y-%m-%d")
def parse_key(k):
    try: return date.fromisoformat(k)
    except Exception: return date.today()
def time_mins(s):
    try:
        h,m=map(int,s.split(":")); return h*60+m
    except Exception: return -1

class StreaklyApp:
    def __init__(self, root):
        self.root=root; self.lang="en"; self.selected=date.today()
        self.month=date.today().replace(day=1); self.editing_id=None
        root.title("Streakly Planner"); root.geometry("1120x780"); root.minsize(820,620); root.configure(bg=BG)
        try:
            icon=Path(__file__).with_name("streakly.ico")
            if icon.exists(): root.iconbitmap(str(icon))
        except Exception: pass
        self.style=ttk.Style()
        try: self.style.theme_use("clam")
        except Exception: pass
        self.style.configure("TCombobox",fieldbackground=PANEL2,background=PANEL2,foreground=INK,arrowcolor=INK)
        self._scroll_canvases=[]
        self.build_header(); self.body=tk.Frame(root,bg=BG); self.body.pack(fill="both",expand=True,padx=22,pady=(18,10))
        # One app-wide scroll handler supports mouse wheels, touchpads, and keyboard navigation.
        root.bind_all("<MouseWheel>", self._wheel_scroll, add="+")
        root.bind_all("<Button-4>", lambda e: self._wheel_scroll_linux(e, -1), add="+")
        root.bind_all("<Button-5>", lambda e: self._wheel_scroll_linux(e, 1), add="+")
        for seq in ("<Up>", "<Down>", "<Prior>", "<Next>"):
            root.bind_all(seq, self._keyboard_scroll, add="+")
        self.footer=tk.Label(root,text="",bg=BG,fg=MUTED,font=("Segoe UI",9)); self.footer.pack(fill="x",padx=24,pady=(0,12))
        self.show_calendar()

    def tr(self,k): return LANG[self.lang].get(k,LANG["en"].get(k,k))

    def _register_scroll_canvas(self, canvas):
        if canvas not in self._scroll_canvases:
            self._scroll_canvases.append(canvas)
        return canvas

    def _canvas_for_widget(self, widget):
        # Walk up from the widget under the pointer/focus, since wheel events often
        # arrive over labels, text boxes, or frames inside a scrollable canvas.
        while widget is not None:
            if widget in self._scroll_canvases:
                return widget
            try: widget = widget.master
            except Exception: break
        return None

    def _active_scroll_canvas(self):
        try:
            w = self.root.winfo_containing(self.root.winfo_pointerx(), self.root.winfo_pointery())
            canvas = self._canvas_for_widget(w)
            if canvas is not None: return canvas
        except Exception: pass
        try: return self._canvas_for_widget(self.root.focus_get())
        except Exception: return None

    def _wheel_scroll(self, event):
        canvas = self._active_scroll_canvas()
        if canvas is None: return
        # Preserve small touchpad deltas; standard mouse wheels normally send +/-120.
        delta = event.delta
        if not delta: return "break"
        units = -1 if delta > 0 else 1
        amount = max(1, round(abs(delta) / 120))
        try: canvas.yview_scroll(units * amount, "units")
        except tk.TclError: pass
        return "break"

    def _wheel_scroll_linux(self, event, direction):
        canvas = self._active_scroll_canvas()
        if canvas is not None:
            try: canvas.yview_scroll(direction, "units")
            except tk.TclError: pass
            return "break"

    def _keyboard_scroll(self, event):
        # Leave normal text editing alone; use keys to scroll when the pointer is
        # over a scrollable panel, or focus is on its canvas/container.
        focus = self.root.focus_get()
        if isinstance(focus, (tk.Text, ttk.Entry, tk.Entry, ttk.Combobox)):
            return
        canvas = self._active_scroll_canvas()
        if canvas is None: return
        key = event.keysym
        if key == "Up": canvas.yview_scroll(-1, "units")
        elif key == "Down": canvas.yview_scroll(1, "units")
        elif key == "Prior": canvas.yview_scroll(-1, "pages")
        elif key == "Next": canvas.yview_scroll(1, "pages")
        return "break"
    def build_header(self):
        head=tk.Frame(self.root,bg="#111a1c",height=62); head.pack(fill="x"); head.pack_propagate(False)
        # Draw the Streakly Planner calendar-and-check logo in the app header (no image dependency).
        logo=tk.Canvas(head,width=42,height=42,bg="#111a1c",highlightthickness=0)
        logo.pack(side="left",padx=(20,10),pady=9)
        logo.create_rectangle(4,9,38,37,fill="#40bfb4",outline="",width=0)
        logo.create_rectangle(4,9,38,17,fill="#31aaa3",outline="",width=0)
        logo.create_rectangle(11,4,16,13,fill="#e8f2f2",outline="",width=0)
        logo.create_rectangle(26,4,31,13,fill="#e8f2f2",outline="",width=0)
        logo.create_line(11,25,17,30,28,19,fill="#102023",width=3,capstyle="round",joinstyle="round")
        # Small flame accent mirrors the installed Streakly Planner icon.
        logo.create_polygon(31,3,35,9,33,14,29,13,28,9,fill="#ff875e",outline="")
        logo.create_oval(29,8,33,12,fill="#ffd16b",outline="")
        tk.Label(head,text="Streakly Planner",font=("Segoe UI",17,"bold"),bg="#111a1c",fg=INK).pack(side="left")
        self.lang_var=tk.StringVar(value="English")
        self.lang_box=ttk.Combobox(head,textvariable=self.lang_var,state="readonly",width=13,values=["English","Kiswahili","Français","Español"])
        self.lang_box.pack(side="right",padx=18); self.lang_box.bind("<<ComboboxSelected>>",self.change_lang)
        self.lang_label=tk.Label(head,text="Language",bg="#111a1c",fg=MUTED,font=("Segoe UI",9)); self.lang_label.pack(side="right",padx=(0,7))

    def clear_body(self):
        for w in self.body.winfo_children(): w.destroy()
        self._scroll_canvases = []
    def save_footer(self):
        self.footer.config(text=self.tr("privacy"))
    def change_lang(self,event=None):
        self.lang={"English":"en","Kiswahili":"sw","Français":"fr","Español":"es"}.get(self.lang_var.get(),"en")
        if getattr(self,"current_view","calendar")=="day": self.show_day()
        else: self.show_calendar()

    def month_title(self):
        loc={"en":"en_US","sw":"sw_KE","fr":"fr_FR","es":"es_ES"}[self.lang]
        try:
            import locale
            # Avoid changing process locale; month names are translated by a small map fallback.
            names={
             "en":["January","February","March","April","May","June","July","August","September","October","November","December"],
             "sw":["Januari","Februari","Machi","Aprili","Mei","Juni","Julai","Agosti","Septemba","Oktoba","Novemba","Desemba"],
             "fr":["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"],
             "es":["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]}
            return f"{names[self.lang][self.month.month-1].capitalize()} {self.month.year}"
        except Exception: return self.month.strftime("%B %Y")

    def button(self,parent,text,command,primary=False,width=None):
        b=tk.Button(parent,text=text,command=command,bg=ACCENT if primary else PANEL2,fg="#102023" if primary else INK,
          activebackground="#a5eef0",activeforeground="#102023",relief="flat",bd=0,cursor="hand2",font=("Segoe UI",10,"bold" if primary else "normal"),padx=12,pady=8)
        if width: b.config(width=width)
        return b
    def title_label(self,parent,text,size=24):
        return tk.Label(parent,text=text,bg=BG,fg=INK,font=("Segoe UI",size,"bold"),anchor="w")
    def subtitle(self,parent,text):
        return tk.Label(parent,text=text,bg=BG,fg=MUTED,font=("Segoe UI",10),anchor="w")

    def show_calendar(self):
        self.current_view="calendar"; self.clear_body()
        top=tk.Frame(self.body,bg=BG); top.pack(fill="x",pady=(0,17))
        left=tk.Frame(top,bg=BG); left.pack(side="left",fill="x",expand=True)
        self.title_label(left,self.tr("calendar"),26).pack(anchor="w")
        self.subtitle(left,self.tr("choose")).pack(anchor="w",pady=(4,0))
        nav=tk.Frame(top,bg=BG); nav.pack(side="right")
        self.button(nav,"‹",self.prev_month).pack(side="left",padx=4)
        tk.Label(nav,text=self.month_title(),bg=BG,fg=INK,font=("Segoe UI",15,"bold"),width=16).pack(side="left",padx=5)
        self.button(nav,"›",self.next_month).pack(side="left",padx=4)
        self.button(nav,self.tr("today"),self.go_today,True).pack(side="left",padx=(8,0))
        tk.Label(self.body,text=self.streak_text(),bg=BG,fg=ACCENT,font=("Segoe UI",10,"bold"),anchor="w").pack(fill="x",pady=(0,10))
        # Scrollable calendar area: keeps all six calendar weeks reachable on small screens.
        calwrap=tk.Frame(self.body,bg=BG); calwrap.pack(fill="both",expand=True)
        calcanvas=self._register_scroll_canvas(tk.Canvas(calwrap,bg=BG,highlightthickness=0))
        calscroll=ttk.Scrollbar(calwrap,orient="vertical",command=calcanvas.yview)
        calcanvas.configure(yscrollcommand=calscroll.set)
        calscroll.pack(side="right",fill="y")
        calcanvas.pack(side="left",fill="both",expand=True)
        grid=tk.Frame(calcanvas,bg=BG)
        win=calcanvas.create_window((0,0),window=grid,anchor="nw")
        grid.bind("<Configure>",lambda e:calcanvas.configure(scrollregion=calcanvas.bbox("all")))
        calcanvas.bind("<Configure>",lambda e:calcanvas.itemconfigure(win,width=e.width))
        weekdays={"en":["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],"sw":["Jum","Jum","Jum","Jum","Iju","Iju","Jum"],"fr":["Dim","Lun","Mar","Mer","Jeu","Ven","Sam"],"es":["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"]}[self.lang]
        for c in range(7):
            grid.grid_columnconfigure(c,weight=1,uniform="day")
            tk.Label(grid,text=weekdays[c],bg=BG,fg=MUTED,font=("Segoe UI",9,"bold")).grid(row=0,column=c,sticky="ew",pady=(0,8))
        for r in range(1,7): grid.grid_rowconfigure(r,minsize=82,weight=1,uniform="week")
        first=self.month; start=first.weekday()+1 # Sunday-based offset
        first_sunday=first-timedelta(days=start%7)
        for i in range(42):
            d=first_sunday+timedelta(days=i); k=key(d); tasks=sorted(data.get(k,{}).get("tasks",[]),key=lambda x:x.get("start",""))
            is_today=d==date.today(); is_selected=d==self.selected
            bg="#263b3e" if is_selected else PANEL
            border=ACCENT if is_selected or is_today else LINE
            cell=tk.Frame(grid,bg=bg,highlightbackground=border,highlightthickness=2 if is_selected or is_today else 1,cursor="hand2")
            cell.grid(row=1+i//7,column=i%7,sticky="nsew",padx=4,pady=4)
            cell.bind("<Button-1>",lambda e,day=d:self.pick_day(day))
            fg=INK if d.month==self.month.month else "#65797b"
            head=tk.Frame(cell,bg=bg); head.pack(fill="x",padx=7,pady=(6,2)); head.bind("<Button-1>",lambda e,day=d:self.pick_day(day))
            num=tk.Label(head,text=str(d.day),bg=bg,fg=fg,font=("Segoe UI",11,"bold")); num.pack(side="left"); num.bind("<Button-1>",lambda e,day=d:self.pick_day(day))
            if tasks:
                count=tk.Label(head,text=str(len(tasks)),bg="#38575a",fg="#d5fbfc",font=("Segoe UI",8),padx=5); count.pack(side="right"); count.bind("<Button-1>",lambda e,day=d:self.pick_day(day))
            for task in tasks[:2]:
                prefix = "✓ " if task.get("completed", False) else ""
                lbl=tk.Label(cell,text=f"{prefix}{task.get('start','')}  {task.get('title','')}",bg=bg,fg=ACCENT if task.get("completed",False) else "#a7dce0",font=("Segoe UI",8),anchor="w")
                lbl.pack(fill="x",padx=7,pady=1); lbl.bind("<Button-1>",lambda e,day=d:self.pick_day(day))
        self.save_footer()

    def prev_month(self):
        self.month=(self.month-timedelta(days=1)).replace(day=1); self.show_calendar()
    def next_month(self):
        self.month=(self.month.replace(day=28)+timedelta(days=4)).replace(day=1); self.show_calendar()
    def go_today(self):
        self.selected=date.today(); self.month=self.selected.replace(day=1); self.show_day()
    def pick_day(self,d):
        self.selected=d; self.show_day()

    def show_day(self):
        self.current_view="day"; self.clear_body(); k=key(self.selected); record=data.get(k,{"tasks":[],"notes":""})
        top=tk.Frame(self.body,bg=BG); top.pack(fill="x",pady=(0,15))
        self.button(top,self.tr("back"),self.show_calendar).pack(side="left",padx=(0,12))
        datefmt={"en":"%A, %B %d, %Y","sw":"%A, %d %B %Y","fr":"%A %d %B %Y","es":"%A, %d de %B de %Y"}[self.lang]
        date_title=self.selected.strftime(datefmt)
        title_group=tk.Frame(top,bg=BG); title_group.pack(side="left",fill="x",expand=True)
        self.title_label(title_group,date_title,20).pack(anchor="w")
        tk.Label(title_group,text=self.streak_text(),bg=BG,fg=ACCENT,font=("Segoe UI",9,"bold"),anchor="w").pack(anchor="w",pady=(2,0))
        self.button(top,"‹",lambda:self.move_day(-1)).pack(side="left",padx=3)
        self.button(top,"›",lambda:self.move_day(1)).pack(side="left",padx=3)
        self.button(top,self.tr("add"),self.new_task,True).pack(side="left",padx=(8,0))
        content=tk.Frame(self.body,bg=BG); content.pack(fill="both",expand=True)
        content.grid_columnconfigure(0,weight=3); content.grid_columnconfigure(1,weight=2); content.grid_rowconfigure(0,weight=1)
        timeline=tk.Frame(content,bg=PANEL,highlightbackground=LINE,highlightthickness=1); timeline.grid(row=0,column=0,sticky="nsew",padx=(0,12))
        th=tk.Frame(timeline,bg=PANEL); th.pack(fill="x",padx=15,pady=13)
        tk.Label(th,text=self.tr("daily"),bg=PANEL,fg=INK,font=("Segoe UI",14,"bold")).pack(side="left")
        tasks=sorted(record.get("tasks",[]),key=lambda x:x.get("start",""))
        tk.Label(th,text=f"{len(tasks)} {self.tr('taskcount')}",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(side="right")
        canvas=self._register_scroll_canvas(tk.Canvas(timeline,bg=PANEL,highlightthickness=0))
        scroll=ttk.Scrollbar(timeline,orient="vertical",command=canvas.yview)
        inner=tk.Frame(canvas,bg=PANEL); inner.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0),window=inner,anchor="nw",width=650); canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand=True,padx=(8,0),pady=(0,8)); scroll.pack(side="right",fill="y",pady=(0,8))
        # Responsive inner width follows the canvas; mouse wheel scrolls the timeline.
        canvas.bind("<Configure>",lambda e:canvas.itemconfigure(1,width=e.width))
        if not tasks:
            tk.Label(inner,text=self.tr("empty"),bg=PANEL,fg=MUTED,font=("Segoe UI",11),pady=30).pack(fill="x")
        else:
            for hour in range(6,24):
                row=tk.Frame(inner,bg=PANEL); row.pack(fill="x",padx=5)
                label=("12 AM" if hour==0 else "12 PM" if hour==12 else f"{hour} AM" if hour<12 else f"{hour-12} PM")
                tk.Label(row,text=label,bg="#131e20",fg=MUTED,width=8,anchor="e",font=("Segoe UI",8),pady=12).pack(side="left",fill="y")
                slot=tk.Frame(row,bg=PANEL); slot.pack(side="left",fill="both",expand=True,padx=4,pady=3)
                for task in [x for x in tasks if int(x.get("start","00:00").split(":")[0])==hour]:
                    card=tk.Frame(slot,bg="#2b4143",highlightbackground="#466366",highlightthickness=1,cursor="hand2")
                    card.pack(fill="x",pady=2)
                    done_var=tk.BooleanVar(value=bool(task.get("completed",False)))
                    done_box=tk.Checkbutton(card,variable=done_var,command=lambda tid=task["id"],v=done_var:self.toggle_task(tid,v.get()),bg="#2b4143",activebackground="#2b4143",fg=ACCENT,activeforeground=ACCENT,selectcolor="#172326",relief="flat",bd=0,cursor="hand2")
                    done_box.pack(side="left",padx=(4,3),pady=4)
                    tk.Frame(card,bg=ACCENT,width=4).pack(side="left",fill="y",padx=(0,7))
                    texts=tk.Frame(card,bg="#2b4143"); texts.pack(side="left",fill="x",expand=True,pady=7)
                    title_fg=ACCENT if task.get("completed",False) else "#bcecef"
                    title_text=("✓ " if task.get("completed",False) else "")+task.get("title","")
                    tk.Label(texts,text=title_text,bg="#2b4143",fg=title_fg,font=("Segoe UI",10,"bold"),anchor="w").pack(fill="x")
                    tk.Label(texts,text=f"{task.get('start','')}–{task.get('end','')} · {task.get('category','')}",bg="#2b4143",fg="#a8c5c8",font=("Segoe UI",8),anchor="w").pack(fill="x")
                    if task.get("notes"): tk.Label(texts,text=task["notes"],bg="#2b4143",fg=INK,font=("Segoe UI",9),anchor="w",wraplength=440,justify="left").pack(fill="x",pady=(3,0))
                    for w in [card,texts]+card.winfo_children()+texts.winfo_children(): w.bind("<Button-1>",lambda e,tid=task["id"]:self.edit_task(tid))
                tk.Frame(inner,bg=LINE,height=1).pack(fill="x",padx=4)
        # The task editor and daily-notes panel has its own vertical scroll area,
        # so every control remains reachable on shorter windows.
        side_outer=tk.Frame(content,bg=PANEL,highlightbackground=LINE,highlightthickness=1)
        side_outer.grid(row=0,column=1,sticky="nsew")
        side_canvas=self._register_scroll_canvas(tk.Canvas(side_outer,bg=PANEL,highlightthickness=0))
        side_scroll=ttk.Scrollbar(side_outer,orient="vertical",command=side_canvas.yview)
        side=tk.Frame(side_canvas,bg=PANEL)
        side_window=side_canvas.create_window((0,0),window=side,anchor="nw")
        side.configure(width=360)
        side.bind("<Configure>",lambda e:side_canvas.configure(scrollregion=side_canvas.bbox("all")))
        side_canvas.configure(yscrollcommand=side_scroll.set)
        side_canvas.pack(side="left",fill="both",expand=True)
        side_scroll.pack(side="right",fill="y")
        side_canvas.bind("<Configure>",lambda e:side_canvas.itemconfigure(side_window,width=e.width))
        tk.Label(side,text=self.tr("quick") if "quick" in LANG[self.lang] else self.tr("edit"),bg=PANEL,fg=INK,font=("Segoe UI",14,"bold")).pack(anchor="w",padx=15,pady=(13,8))
        self.form_title=tk.StringVar(); self.form_start=tk.StringVar(value="09:00"); self.form_end=tk.StringVar(value="10:00")
        self.form_category=tk.StringVar(value=self.tr("categories")[0]); self.form_notes=tk.StringVar()
        self.add_field(side,"title",self.form_title)
        row=tk.Frame(side,bg=PANEL); row.pack(fill="x",padx=14)
        self.add_field(row,"start",self.form_start,side_by_side=True)
        self.add_field(row,"end",self.form_end,side_by_side=True)
        tk.Label(side,text=self.tr("category"),bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=14,pady=(7,3))
        self.catbox=ttk.Combobox(side,textvariable=self.form_category,state="readonly",values=self.tr("categories")); self.catbox.pack(fill="x",padx=14)
        tk.Label(side,text=self.tr("notes"),bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=14,pady=(9,3))
        self.notes_text=tk.Text(side,height=4,bg="#101a1c",fg=INK,insertbackground=INK,relief="flat",font=("Segoe UI",9),wrap="word"); self.notes_text.pack(fill="x",padx=14)
        buttons=tk.Frame(side,bg=PANEL); buttons.pack(fill="x",padx=14,pady=10)
        self.button(buttons,self.tr("save"),self.save_task,True).pack(side="left",fill="x",expand=True)
        self.button(buttons,self.tr("clear"),self.new_task).pack(side="left",padx=(6,0))
        self.delete_btn=self.button(side,self.tr("delete"),self.delete_task); self.delete_btn.pack(anchor="w",padx=14); self.delete_btn.pack_forget()
        tk.Frame(side,bg=LINE,height=1).pack(fill="x",padx=14,pady=13)
        tk.Label(side,text=self.tr("daynotes"),bg=PANEL,fg=INK,font=("Segoe UI",12,"bold")).pack(anchor="w",padx=14)
        self.daily_notes=tk.Text(side,height=4,bg="#101a1c",fg=INK,insertbackground=INK,relief="flat",font=("Segoe UI",9),wrap="word")
        self.daily_notes.pack(fill="x",padx=14,pady=(6,6)); self.daily_notes.insert("1.0",record.get("notes",""))
        self.button(side,self.tr("savenotes"),self.save_day_notes).pack(anchor="w",padx=14,pady=(0,12))
        self.save_footer()

    def add_field(self,parent,label_key,var,side_by_side=False):
        wrap=tk.Frame(parent,bg=PANEL); wrap.pack(side="left" if side_by_side else "top",fill="x",expand=True,padx=(14 if not side_by_side else 0,6 if side_by_side else 14),pady=(4,0))
        tk.Label(wrap,text=self.tr(label_key),bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",pady=(0,3))
        e=tk.Entry(wrap,textvariable=var,bg="#101a1c",fg=INK,insertbackground=INK,relief="flat",font=("Segoe UI",10)); e.pack(fill="x",ipady=7)
        return e
    def streak_text(self):
        # A day counts when it has at least one task and every task is completed.
        # If today's plan is still in progress, keep the streak earned through yesterday.
        today=date.today(); today_tasks=data.get(key(today),{}).get("tasks",[])
        cursor=today if today_tasks and all(x.get("completed",False) for x in today_tasks) else today-timedelta(days=1)
        streak=0
        while True:
            tasks=data.get(key(cursor),{}).get("tasks",[])
            if not tasks or not all(x.get("completed",False) for x in tasks): break
            streak+=1; cursor-=timedelta(days=1)
        if self.lang=="sw": return f"🔥 Mfululizo: siku {streak}"
        if self.lang=="fr": return f"🔥 Série : {streak} jour(s)"
        if self.lang=="es": return f"🔥 Racha: {streak} día(s)"
        return f"🔥 Streak: {streak} day(s)"

    def toggle_task(self,tid,completed):
        for task in data.get(key(self.selected),{}).get("tasks",[]):
            if task.get("id")==tid:
                task["completed"]=bool(completed); break
        save_data(); self.show_day()

    def move_day(self,n):
        self.selected+=timedelta(days=n); self.month=self.selected.replace(day=1); self.show_day()
    def new_task(self):
        self.editing_id=None; self.form_title.set(""); self.form_start.set("09:00"); self.form_end.set("10:00"); self.form_category.set(self.tr("categories")[0]); self.notes_text.delete("1.0","end")
        self.delete_btn.pack_forget()
    def edit_task(self,tid):
        task=next((x for x in data.get(key(self.selected),{}).get("tasks",[]) if x.get("id")==tid),None)
        if not task:return
        self.editing_id=tid; self.form_title.set(task.get("title","")); self.form_start.set(task.get("start","09:00")); self.form_end.set(task.get("end","10:00"))
        self.form_category.set(task.get("category",self.tr("categories")[0])); self.notes_text.delete("1.0","end"); self.notes_text.insert("1.0",task.get("notes","")); self.delete_btn.pack(anchor="w",padx=14)
    def save_task(self):
        title=self.form_title.get().strip(); start=self.form_start.get().strip(); end=self.form_end.get().strip()
        if not title: messagebox.showwarning("Streakly Planner",self.tr("title")+" is required."); return
        if time_mins(start)<0 or time_mins(end)<=time_mins(start): messagebox.showwarning("Streakly Planner",self.tr("invalid")); return
        k=key(self.selected); data.setdefault(k,{"tasks":[],"notes":""})
        old_task=next((x for x in data[k]["tasks"] if x.get("id")==self.editing_id),{}) if self.editing_id else {}
        task={"id":self.editing_id or datetime.now().strftime("%Y%m%d%H%M%S%f"),"title":title,"start":start,"end":end,"category":self.form_category.get(),"notes":self.notes_text.get("1.0","end").strip(),"completed":bool(old_task.get("completed",False))}
        if self.editing_id:
            data[k]["tasks"]=[task if x.get("id")==self.editing_id else x for x in data[k]["tasks"]]
        else: data[k]["tasks"].append(task)
        save_data(); self.show_day()
    def delete_task(self):
        if not self.editing_id:return
        k=key(self.selected); data[k]["tasks"]=[x for x in data[k].get("tasks",[]) if x.get("id")!=self.editing_id]; save_data(); self.show_day()
    def save_day_notes(self):
        k=key(self.selected); data.setdefault(k,{"tasks":[],"notes":""}); data[k]["notes"]=self.daily_notes.get("1.0","end").strip(); save_data()
        messagebox.showinfo("Streakly Planner",self.tr("saved"))
if __name__=="__main__":
    root=tk.Tk(); app=StreaklyApp(root); root.mainloop()
