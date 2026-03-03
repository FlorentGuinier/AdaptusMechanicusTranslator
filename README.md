# ⚙ MECHANICUS LINGUA TRANSLATOR ⚙

> *"Knowledge is power, guard it well."*

A Warhammer 40,000-themed text translator that reformulates any input into the sacred techno-religious language of the **Adeptus Mechanicus** — simultaneously in French and English.

Powered by [Ollama](https://ollama.com/) running **Mistral 7B** locally. No data leaves your machine. The Omnissiah approves.

---

## REQUIREMENTS — PREREQUISITES OF THE RITUAL

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Mistral 7B model (auto-downloaded on first launch if not present)
- A GPU is recommended but not required (CPU mode works)

---

## INSTALLATION — INITIATION RITES

### Using `uv` (recommended)

```bash
uv sync
uv run mechanicus_translator.py
```

### Using `pip`

```bash
pip install customtkinter ollama
python mechanicus_translator.py
```

On first launch, if Mistral 7B is not already pulled, the app will download it automatically (~4 GB). Progress is displayed in the status bar.

---

## USAGE — OPERATION OF THE SACRED COGITATOR

1. Launch the application
2. Wait for the status bar to confirm the model is loaded
3. Enter your profane flesh-words in the input field
4. Click **TRANSMUTE TO BINARIC CANT**
5. Receive the blessed output in both French and English
6. Use the **COPY** buttons to copy each translation to clipboard

---

## PROJECT STRUCTURE

```
mechanicus_translator.py   # Main application (single file)
pyproject.toml             # Project metadata and dependencies
```

---

## LICENSE

MIT — do whatever you want with this. See [LICENSE](LICENSE) for the full text.

---

*This project is a fan creation and is not affiliated with or endorsed by Games Workshop. Warhammer 40,000 and Adeptus Mechanicus are trademarks of Games Workshop Ltd.*
