#!/usr/bin/env python3
"""
Mechanicus Lingua Translator
Adeptus Mechanicus Style Text Translator
Powered by Ollama + Mistral 7B
"""

try:
    import customtkinter as ctk
    import ollama
    from translator import (MODEL_NAME, translate_stream, translate_to_english,
                            translate_to_french_stream, get_inference_device,
                            PERSONA_TECH_PRIEST, PERSONA_SKITARII)
except ImportError as e:
    import tkinter as tk
    import tkinter.messagebox
    root = tk.Tk()
    root.withdraw()
    tkinter.messagebox.showerror(
        "MISSING DEPENDENCIES",
        f"Install requirements first:\n\n    uv sync\n\nMissing: {e}"
    )
    raise SystemExit(1)

import threading
import subprocess

# ══════════════════════════════════════════════════════
# ADEPTUS MECHANICUS COLOR SCHEME
# ══════════════════════════════════════════════════════
BG_DARK      = "#080808"
BG_MEDIUM    = "#110404"
BG_PANEL     = "#160707"
BG_INPUT     = "#0C0303"
RED_DARK     = "#4A0000"
RED_PRIMARY  = "#8B0000"
RED_BRIGHT   = "#AA1515"
GOLD_DARK    = "#6B4E0B"
GOLD         = "#B8860B"
GOLD_BRIGHT  = "#D4A820"
TEXT_MAIN    = "#C8B89A"
TEXT_DIM     = "#6A5A4A"
TEXT_BRIGHT  = "#E8D8C0"
TEXT_RED     = "#CC4444"
BORDER_MED   = "#4A1010"



# ══════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════
class MechanicusApp(ctk.CTk):

    _ANIM_FRAMES = [
        "⚙  PROCESSING — PRAISE THE OMNISSIAH  ◈",
        "◈  PROCESSING — PRAISE THE OMNISSIAH  ⚙",
        "◉  PROCESSING — PRAISE THE OMNISSIAH  ◈",
        "◈  PROCESSING — PRAISE THE OMNISSIAH  ◉",
    ]

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("MECHANICUS LINGUA TRANSLATOR — PRAISE THE OMNISSIAH")
        self.geometry("1180x800")
        self.minsize(900, 640)
        self.configure(fg_color=BG_DARK)

        self._is_translating = False
        self._anim_id = None
        self._anim_frame = 0

        self._build_ui()
        self._check_ollama_async()

    # ──────────────────────────────────────────────────
    # UI CONSTRUCTION
    # ──────────────────────────────────────────────────
    def _build_ui(self):
        # ── HEADER ────────────────────────────────────
        header = ctk.CTkFrame(
            self, fg_color=BG_MEDIUM,
            border_color=RED_PRIMARY, border_width=2,
            corner_radius=0
        )
        header.pack(fill="x", padx=8, pady=(8, 0))

        ctk.CTkLabel(
            header,
            text="⚙  ADEPTUS MECHANICUS  ⚙",
            font=ctk.CTkFont(family="Courier New", size=24, weight="bold"),
            text_color=GOLD_BRIGHT
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            header,
            text="LINGUA-TECHNIS TRANSLATOR  ·  KNOWLEDGE IS POWER, GUARD IT WELL",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM
        ).pack(pady=(0, 12))

        # ── TOP SEPARATOR ─────────────────────────────
        ctk.CTkFrame(self, fg_color=RED_PRIMARY, height=2, corner_radius=0).pack(
            fill="x", padx=8
        )

        # ── BODY ──────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True, padx=8, pady=4)

        # Input label
        ctk.CTkLabel(
            body,
            text="◈  FLESH-WORDS INPUT",
            font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
            text_color=GOLD
        ).pack(anchor="w", padx=14, pady=(8, 3))

        # Input textbox
        self.input_text = ctk.CTkTextbox(
            body,
            height=110,
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color=BG_INPUT,
            text_color=TEXT_MAIN,
            border_color=RED_DARK,
            border_width=2,
            corner_radius=4,
            scrollbar_button_color=RED_PRIMARY,
            scrollbar_button_hover_color=RED_BRIGHT,
        )
        self.input_text.pack(fill="x", padx=14, pady=(0, 8))
        self.input_text.insert("0.0", "Enter your text here...")
        self.input_text.bind("<FocusIn>", self._clear_placeholder)

        # Language + Persona selectors + Translate button (same row)
        btn_row = ctk.CTkFrame(body, fg_color=BG_DARK)
        btn_row.pack(fill="x", padx=14, pady=5)
        btn_row.columnconfigure(0, weight=0)
        btn_row.columnconfigure(1, weight=0)
        btn_row.columnconfigure(2, weight=1)

        _combo_kwargs = dict(
            font=ctk.CTkFont(family="Courier New", size=12, weight="bold"),
            fg_color=BG_INPUT,
            text_color=GOLD,
            border_color=RED_DARK,
            button_color=RED_PRIMARY,
            button_hover_color=RED_BRIGHT,
            dropdown_fg_color=BG_MEDIUM,
            dropdown_text_color=GOLD,
            dropdown_hover_color=RED_DARK,
            height=46,
            corner_radius=4,
            state="readonly",
        )

        self.lang_var = ctk.StringVar(value="ENGLISH")
        ctk.CTkComboBox(
            btn_row,
            values=["ENGLISH", "FRENCH"],
            variable=self.lang_var,
            width=150,
            **_combo_kwargs,
        ).grid(row=0, column=0, padx=(0, 8))

        self.persona_var = ctk.StringVar(value="TECH-PRIEST")
        ctk.CTkComboBox(
            btn_row,
            values=["TECH-PRIEST", "SKITARII"],
            variable=self.persona_var,
            width=200,
            **_combo_kwargs,
        ).grid(row=0, column=1, padx=(0, 8))

        self.translate_btn = ctk.CTkButton(
            btn_row,
            text="⚙  TRANSMUTE TO BINARIC CANT  ⚙",
            command=self._start_translation,
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            fg_color=RED_PRIMARY,
            hover_color=RED_BRIGHT,
            text_color=GOLD_BRIGHT,
            border_color=GOLD_DARK,
            border_width=1,
            height=46,
            corner_radius=4,
        )
        self.translate_btn.grid(row=0, column=2, sticky="ew")

        # Output columns (English + French side by side)
        out_cols = ctk.CTkFrame(body, fg_color=BG_DARK)
        out_cols.pack(fill="both", expand=True, padx=14, pady=(8, 4))
        out_cols.columnconfigure(0, weight=1)
        out_cols.columnconfigure(1, weight=1)
        out_cols.rowconfigure(1, weight=1)

        # English output
        en_hdr = ctk.CTkFrame(out_cols, fg_color=BG_DARK)
        en_hdr.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 3))
        self.left_label = ctk.CTkLabel(
            en_hdr,
            text="◈  SACRED OUTPUT — MECHANICUS LINGUA",
            font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
            text_color=GOLD
        )
        self.left_label.pack(side="left")
        ctk.CTkButton(
            en_hdr, text="COPY", width=54, height=22,
            font=ctk.CTkFont(family="Courier New", size=9, weight="bold"),
            fg_color=RED_DARK, hover_color=RED_PRIMARY,
            text_color=GOLD, corner_radius=3,
            command=lambda: self._copy_text(self.output)
        ).pack(side="right")

        self.output = ctk.CTkTextbox(
            out_cols,
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color=BG_PANEL,
            text_color=TEXT_MAIN,
            border_color=BORDER_MED,
            border_width=1,
            corner_radius=4,
            state="disabled",
            scrollbar_button_color=RED_DARK,
            scrollbar_button_hover_color=RED_PRIMARY,
            wrap="word",
        )
        self.output.grid(row=1, column=0, sticky="nsew", padx=(0, 4))

        # French translation output
        fr_hdr = ctk.CTkFrame(out_cols, fg_color=BG_DARK)
        fr_hdr.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=(0, 3))
        self.right_label = ctk.CTkLabel(
            fr_hdr,
            text="◈  TRADUCTION FRANÇAISE",
            font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
            text_color=GOLD
        )
        self.right_label.pack(side="left")
        ctk.CTkButton(
            fr_hdr, text="COPY", width=54, height=22,
            font=ctk.CTkFont(family="Courier New", size=9, weight="bold"),
            fg_color=RED_DARK, hover_color=RED_PRIMARY,
            text_color=GOLD, corner_radius=3,
            command=lambda: self._copy_text(self.fr_output)
        ).pack(side="right")

        self.fr_output = ctk.CTkTextbox(
            out_cols,
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color=BG_PANEL,
            text_color=TEXT_MAIN,
            border_color=BORDER_MED,
            border_width=1,
            corner_radius=4,
            state="disabled",
            scrollbar_button_color=RED_DARK,
            scrollbar_button_hover_color=RED_PRIMARY,
            wrap="word",
        )
        self.fr_output.grid(row=1, column=1, sticky="nsew", padx=(4, 0))

        # ── STATUS BAR ────────────────────────────────
        ctk.CTkFrame(self, fg_color=RED_DARK, height=1, corner_radius=0).pack(
            fill="x", padx=8
        )

        status_bar = ctk.CTkFrame(self, fg_color=BG_MEDIUM, corner_radius=0)
        status_bar.pack(fill="x", padx=8, pady=(0, 8))

        self.status_label = ctk.CTkLabel(
            status_bar,
            text="◈ INITIALIZING MACHINE SPIRIT...",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM,
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        self.gpu_label = ctk.CTkLabel(
            status_bar,
            text="⚙ DETECTING HARDWARE...",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM,
        )
        self.gpu_label.pack(side="right", padx=10, pady=5)

    # ──────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────
    def _clear_placeholder(self, _event):
        current = self.input_text.get("0.0", "end").strip()
        if current == "Entrez votre texte ici — Enter your text here...":
            self.input_text.delete("0.0", "end")

    def _set_status(self, text: str, color: str = TEXT_DIM):
        self.status_label.configure(text=f"◈ {text}", text_color=color)

    def _set_output(self, widget: ctk.CTkTextbox, text: str):
        widget.configure(state="normal")
        widget.delete("0.0", "end")
        if text:
            widget.insert("0.0", text)
        widget.configure(state="disabled")

    def _append_output(self, widget: ctk.CTkTextbox, text: str):
        widget.configure(state="normal")
        widget.insert("end", text)
        widget.see("end")
        widget.configure(state="disabled")

    def _copy_text(self, widget: ctk.CTkTextbox):
        content = widget.get("0.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)

    def _detect_gpu(self) -> str:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(",")
                name = parts[0].strip()
                vram = parts[1].strip() if len(parts) > 1 else "?"
                return f"⚙ GPU: {name} [{int(vram)//1024}GB]"
        except Exception:
            pass
        return "⚙ GPU: CPU MODE"

    def _query_inference_device(self):
        """Called from worker thread after first token — updates gpu_label with live inference location."""
        info = get_inference_device(MODEL_NAME)
        if info["running"] and info["on_gpu"]:
            gb = info["size_vram"] / (1024 ** 3)
            text = f"⚙ INFERENCE: GPU [{gb:.1f}GB VRAM]"
            color = GOLD_BRIGHT
        else:
            text = "⚙ INFERENCE: CPU MODE"
            color = TEXT_DIM
        self.after(0, lambda t=text, c=color: self.gpu_label.configure(text=t, text_color=c))

    # ──────────────────────────────────────────────────
    # ANIMATION
    # ──────────────────────────────────────────────────
    def _start_anim(self):
        self._anim_frame = 0
        self._tick_anim()

    def _tick_anim(self):
        if not self._is_translating:
            return
        self.translate_btn.configure(
            text=self._ANIM_FRAMES[self._anim_frame % len(self._ANIM_FRAMES)]
        )
        self._anim_frame += 1
        self._anim_id = self.after(450, self._tick_anim)

    def _stop_anim(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self.translate_btn.configure(text="⚙  TRANSMUTE TO BINARIC CANT  ⚙")

    # ──────────────────────────────────────────────────
    # OLLAMA STARTUP CHECK
    # ──────────────────────────────────────────────────
    def _check_ollama_async(self):
        def _get_model_names(response) -> list[str]:
            """Handle both old dict API and new object API from ollama library."""
            if hasattr(response, "models"):
                return [
                    getattr(m, "model", getattr(m, "name", ""))
                    for m in response.models
                ]
            return [
                m.get("name", m.get("model", ""))
                for m in response.get("models", [])
            ]

        def check():
            # GPU detection (separate from Ollama)
            gpu_text = self._detect_gpu()
            self.after(0, lambda: self.gpu_label.configure(
                text=gpu_text, text_color=GOLD if "GPU:" in gpu_text else TEXT_DIM
            ))

            try:
                names = _get_model_names(ollama.list())
                has_mistral = any("mistral" in n.lower() for n in names)

                if has_mistral:
                    self.after(0, lambda: self._set_status(
                        "OMNISSIAH APPROVES — MISTRAL 7B LOADED", GOLD_BRIGHT
                    ))
                else:
                    self.after(0, lambda: self._set_status(
                        "PULLING MISTRAL — INITIATING DOWNLOAD RITES...", TEXT_RED
                    ))
                    for progress in ollama.pull(MODEL_NAME, stream=True):
                        status    = getattr(progress, "status",    "")
                        completed = getattr(progress, "completed", 0)
                        total     = getattr(progress, "total",     0)
                        if total and completed:
                            pct = completed / total * 100
                            msg = f"DOWNLOADING MISTRAL — {pct:05.1f}%  [{completed/1e9:.2f} / {total/1e9:.2f} GB]"
                        elif status:
                            msg = f"DOWNLOADING MISTRAL — {status}"
                        else:
                            continue
                        self.after(0, lambda m=msg: self._set_status(m, TEXT_RED))
                    self.after(0, lambda: self._set_status(
                        "MODEL SANCTIFIED — READY FOR TRANSMUTATION", GOLD_BRIGHT
                    ))

            except Exception as e:
                msg = str(e)[:55]
                self.after(0, lambda: self._set_status(
                    f"HERESY DETECTED — {msg}", TEXT_RED
                ))
                self.after(0, lambda: self.translate_btn.configure(state="disabled"))

        threading.Thread(target=check, daemon=True).start()

    # ──────────────────────────────────────────────────
    # TRANSLATION
    # ──────────────────────────────────────────────────
    def _start_translation(self):
        text = self.input_text.get("0.0", "end").strip()
        placeholder = "Enter your text here..."
        if not text or text == placeholder:
            self._set_status("ERROR — NO FLESH-WORDS DETECTED IN COGITATOR", TEXT_RED)
            return

        self._is_translating = True
        self.translate_btn.configure(state="disabled")
        self._start_anim()
        persona = (PERSONA_SKITARII
                   if self.persona_var.get() == "SKITARII"
                   else PERSONA_TECH_PRIEST)
        input_lang = self.lang_var.get().lower()  # "english" or "french"

        self._set_status("TRANSMUTING BIOLOGICAL DATA TO BINARIC CANT...", GOLD_BRIGHT)
        self._set_output(self.output, "")
        self._set_output(self.fr_output, "")

        def worker():
            try:
                if input_lang == "french":
                    # ── LEFT: FR → EN → Mechanicus(EN) → FR ────
                    self.after(0, lambda: self.left_label.configure(
                        text="◈  FR→EN→MECHANICUS→FR"
                    ))
                    self.after(0, lambda: self.right_label.configure(
                        text="◈  FR→MECHANICUS(FR) — DIRECT"
                    ))

                    self.after(0, lambda: self._set_status("TRANSLATING INPUT TO ENGLISH...", GOLD))
                    en_input = translate_to_english(text)

                    self.after(0, lambda: self._set_status("TRANSMUTING LINGUA (EN)...", GOLD))
                    en_tokens = []
                    _inference_checked = False
                    for token in translate_stream(en_input, persona, "english"):
                        if not _inference_checked:
                            self._query_inference_device()
                            _inference_checked = True
                        en_tokens.append(token)

                    self.after(0, lambda: self._set_status("TRANSLATING BACK TO FRENCH...", GOLD))
                    for token in translate_to_french_stream("".join(en_tokens)):
                        self.after(0, lambda t=token: self._append_output(self.output, t))

                    # ── RIGHT: FR → Mechanicus(FR) direct ───────
                    self.after(0, lambda: self._set_status("TRANSMUTING LINGUA (FR) DIRECT...", GOLD))
                    for token in translate_stream(text, persona, "french"):
                        self.after(0, lambda t=token: self._append_output(self.fr_output, t))

                else:
                    # ── LEFT: EN → Mechanicus(EN) ────────────────
                    self.after(0, lambda: self.left_label.configure(
                        text="◈  SACRED OUTPUT — MECHANICUS LINGUA"
                    ))
                    self.after(0, lambda: self.right_label.configure(
                        text="◈  TRADUCTION FRANÇAISE"
                    ))

                    self.after(0, lambda: self._set_status("TRANSMUTING LINGUA...", GOLD))
                    en_tokens = []
                    _inference_checked = False
                    for token in translate_stream(text, persona, "english"):
                        if not _inference_checked:
                            self._query_inference_device()
                            _inference_checked = True
                        en_tokens.append(token)
                        self.after(0, lambda t=token: self._append_output(self.output, t))

                    # ── RIGHT: EN Mechanicus → FR ─────────────────
                    self.after(0, lambda: self._set_status("TRANSLATING TO FRENCH...", GOLD))
                    for token in translate_to_french_stream("".join(en_tokens)):
                        self.after(0, lambda t=token: self._append_output(self.fr_output, t))

                self.after(0, lambda: self._set_status(
                    "TRANSMUTATION COMPLETE — PRAISE THE OMNISSIAH", GOLD_BRIGHT
                ))

            except Exception as e:
                err = str(e)[:70]
                self.after(0, lambda: self._set_status(
                    f"MACHINE SPIRIT FAILURE: {err}", TEXT_RED
                ))
            finally:
                self._is_translating = False
                self.after(0, self._stop_anim)
                self.after(0, lambda: self.translate_btn.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()


# ══════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = MechanicusApp()
    app.mainloop()
