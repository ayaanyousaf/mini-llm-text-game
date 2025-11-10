# Temple of the Ancients — LLM Text Adventure
##### Author: Ayaan Yousaf
A short PG-13 text-based adventure powered by a local LLM via Ollama.  
The player explores a crumbling temple, gathers items, and seeks the **Black Materia** while surviving until the end. This text adventure is inspired by Final Fantasy VII.

---

## 🧩 Setup & Installation

### 1. Create a Virtual Environment
```bash
python -m venv .venv
```
Windows: 
```bash
.venv\Scripts\activate
```
Linux/MacOS: 
```bash
source .venv/bin/activate
```

### 2. Install Ollama
Follow [https://ollama.ai](https://ollama.ai) for your OS.  
Then open a terminal and pull the model:

```bash
pip install ollama
ollama pull gemma3:1b
```
(It is recommended to use a better model, I used gemma3:1b due to hardware limitations)

### 3. Run the Game
```bash
python main.py
```

---

## ⚙️ Modifying Rules
Within rules.json: 
- Add a new command: Append it to COMMANDS and teach the model that action in gm.txt.

- Add a lock: Add a "ROOM": "required_flag" pair under LOCKS.

- Change quest: Update the QUEST intro/goal text.

- Change win/lose: Edit END_CONDITIONS.

---

## Example Gameplay
Using a good model, you should achieve something that looks like this: 

\> look
<br>You stand before the Temple of the Ancients...

\> move
<br>The path east is sealed by ancient magic.
(Refusal due to LOCKS: Inner Sanctum requires temple_key.)

\> take key
<br>You pick up the temple key from the altar.

\> move
<br>The seal fades. You enter the Inner Sanctum.

\> take black materia
<br>Light engulfs you as the Black Materia binds to your soul.
Quest complete — victory achieved!

\> load
<br>Game loaded.

\> move
<br>A trap triggers — your HP drops to 0.
You have fallen. The temple claims another soul.

