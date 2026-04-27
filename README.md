# GCSE Grade 9 Planner — Flask Web UI Version

This is the Flask web version of your GCSE Grade 9 planner.

## Run in PyCharm

1. Open this folder in PyCharm.
2. Create/select the project `.venv` interpreter (Python 3.10+).
3. Open PyCharm Terminal.
4. Run:

```bash
pip install -r requirements.txt
python run.py
```

5. Open your browser:

```text
http://127.0.0.1:5001
```

## What it does

- Daily study/work structure capture
- Grade 9 trajectory score
- Daily targets
- Next-day timetable
- Weekend plan
- STEM prioritisation
- Adaptive subject-only tests from a SQLite question bank
- Topic and difficulty tracking per subject
- Paste-import question banks from ChatGPT or manual blocks
- Generate performance-based ChatGPT prompts for topic-wise bulk question creation
- Daily prompt poller that queues fresh prompt jobs from the latest test results
- Weak-area resource recommendations
- Email daily report to `kranthiksg@gmail.com`
- Optional ChatGPT/OpenAI test generation and scanned-answer marking

## Email setup

Set these environment variables:

```bash
GCSE_REPORT_EMAIL=your_sender_email@gmail.com
GCSE_REPORT_APP_PASSWORD=your_16_character_gmail_app_password
```

For Windows PowerShell:

```powershell
setx GCSE_REPORT_EMAIL "your_sender_email@gmail.com"
setx GCSE_REPORT_APP_PASSWORD "your_16_character_gmail_app_password"
```

Restart PyCharm after setting them.

## OpenAI setup

Optional:

```bash
OPENAI_API_KEY=your_openai_api_key
```

Windows PowerShell:

```powershell
setx OPENAI_API_KEY "your_openai_api_key"
```

## External env file

You can keep secrets outside the project directory.

1. Move your env file to an external path such as `C:/Downloads/grade9_planner.env`.
2. Set `GRADE9_ENV_FILE` to that full path before starting the app.
3. The app will load lines in either `KEY=value` or `export KEY=value` format.

## Notes

- Default URL: `http://127.0.0.1:5001`
- To access from another device on the same Wi-Fi, run with host `0.0.0.0`, but only do this on a trusted home network.
