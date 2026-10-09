"""Smoke-test the documented command without loading models or making API calls."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TASKS = {
    "biology", "earth_science", "economics", "pony", "psychology",
    "robotics", "stackoverflow", "sustainable_living",
}


class QuickStartTest(unittest.TestCase):
    def test_readme_and_site_commands(self):
        for filename in ("README.md", "docs/index.md"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                blocks = re.findall(r"```bash\n(.*?)```", (ROOT / filename).read_text(),
                                    flags=re.DOTALL)
                commands = [b for b in blocks if "CHUNK_CHARS=20000" in b]
                self.assertEqual(len(commands), 1)
                stub = Path(tmp) / "python"
                stub.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$COMMAND_LOG"\n')
                stub.chmod(0o755)
                log = Path(tmp) / "commands.log"
                env = {
                    **os.environ, "PATH": f"{tmp}:{os.environ['PATH']}",
                    "COMMAND_LOG": str(log), "MODEL_NAME": "invalid",
                    "REWRITE_EVAL": "false", "LONG_CONTEXT": "false",
                    "CHUNK_CHARS": "0", "DEBUG": "false",
                    "REWRITE_FOLDER": "./rewrite_data",
                }
                subprocess.run(["bash", "-c", commands[0]], cwd=ROOT, env=env,
                               check=True, capture_output=True, text=True)
                calls = [shlex.split(line) for line in log.read_text().splitlines()]
                self.assertEqual(len(calls), 8)
                self.assertEqual({c[c.index("--task") + 1] for c in calls}, TASKS)
                for call in calls:
                    self.assertIn("--long_context", call)
                    for key, value in {
                        "--model": "inf", "--chunk_chars": "20000",
                        "--doc_max_length": "8192", "--query_max_length": "8192",
                        "--encode_batch_size": "1",
                        "--output_dir": "./output/INF-X-Retriever-chunkmax",
                    }.items():
                        self.assertEqual(call[call.index(key) + 1], value)
                    task = call[call.index("--task") + 1]
                    self.assertEqual(call[call.index("--input_file") + 1],
                                     f"./rewrite_data/{task}_queries.json")


if __name__ == "__main__":
    unittest.main()
