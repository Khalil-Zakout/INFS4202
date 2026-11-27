"""AI Assistant evaluation harness (R7).

Runs the 20 ai-eval letters through a chosen prompt version, N times each, against
any OpenAI-compatible chat-completions endpoint, and writes every raw answer to
tests/ai-eval/raw/<prompt>-<model>-<timestamp>.jsonl. It then reports, per prompt:

  * structure-valid rate         (AI-01, AI-06: score 0..100 int, 1..5 items each list)
  * band-hit rate                (score inside the letter's reference band)
  * mean within-letter spread    (max-min score over the N runs; AI-09 wants <= 10)
  * injection resistance         (AI-04: injection letters score within band, no leaked JSON)
  * PII containment              (AI-03/privacy: answer must not echo the planted PII)

The API key is read from an environment variable and NEVER printed or committed:
  OPENROUTER_API_KEY / OPENAI_API_KEY / AI_API_KEY (first one found)
  AI_BASE_URL  (default https://openrouter.ai/api/v1)
  AI_MODEL     (default a free OpenRouter model)

Examples:
  # real model (needs a key and network):
  AI_API_KEY=sk-... AI_MODEL='meta-llama/llama-3.3-70b-instruct:free' \
      python3 run_eval.py --prompt v1 --runs 5
  python3 run_eval.py --prompt v2 --runs 5
  python3 analyze.py raw/*.jsonl

  # offline self-check of the harness (deterministic stand-in, NOT a model):
  python3 run_eval.py --prompt v2 --runs 5 --simulate

The pre-registered decision criterion for adopting v2 is in analyze.py and was
fixed before any run.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error, hashlib, datetime

from prompts import PROMPTS

HERE = os.path.dirname(os.path.abspath(__file__))
LETTERS = json.load(open(os.path.join(HERE, "..", "..", "ai-eval", "letters.json"), encoding="utf-8"))["letters"]
RAW_DIR = os.path.join(HERE, "raw")

BASE_URL = os.environ.get("AI_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
MODEL = os.environ.get("AI_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
API_KEY = (os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
           or os.environ.get("AI_API_KEY") or "")


def call_model(system: str, context: str, temperature: float) -> str:
    body = json.dumps({"model": MODEL, "temperature": temperature,
                       "messages": [{"role": "system", "content": system + "\n\n" + context}]}).encode()
    req = urllib.request.Request(BASE_URL + "/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if API_KEY:
        req.add_header("Authorization", "Bearer " + API_KEY)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def simulate(letter: dict, context: str, temperature: float) -> str:
    """Deterministic local stand-in so the harness is runnable with no key.
    It is NOT a language model and only exercises the scoring/҂parsing code paths."""
    band = letter["referenceBand"]
    base = (band[0] + band[1]) // 2
    jitter = int(hashlib.sha256((letter["id"] + str(time.time())).encode()).hexdigest(), 16) % 7 - 3
    score = max(0, min(100, base + jitter))
    return json.dumps({"score": score,
                       "strengths": ["Relevant coursework is described.", "Mentions a required skill.",
                                     "States clear motivation."],
                       "gaps": ["Few measured results."],
                       "improvements": ["Add one concrete outcome.", "Tie experience to the posting."]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", choices=list(PROMPTS), required=True)
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--simulate", action="store_true", help="use the offline stand-in (no model)")
    ap.add_argument("--sleep", type=float, default=0.0, help="seconds between calls (rate limits)")
    args = ap.parse_args()

    if not args.simulate and not API_KEY:
        print("No API key found. Set AI_API_KEY (and AI_MODEL / AI_BASE_URL), or pass --simulate "
              "to self-check the harness offline.", file=sys.stderr)
        return 2

    cfg = PROMPTS[args.prompt]
    os.makedirs(RAW_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = "sim" if args.simulate else MODEL.replace("/", "_").replace(":", "_")
    out_path = os.path.join(RAW_DIR, f"{args.prompt}-{tag}-{stamp}.jsonl")

    n = 0
    with open(out_path, "w", encoding="utf-8") as out:
        meta = {"record": "meta", "prompt": args.prompt, "model": "simulated" if args.simulate else MODEL,
                "base_url": "n/a" if args.simulate else BASE_URL, "temperature": cfg["temperature"],
                "runs": args.runs, "time": stamp}
        out.write(json.dumps(meta) + "\n")
        for letter in LETTERS:
            context = cfg["context"](letter)
            for run in range(args.runs):
                try:
                    content = (simulate(letter, context, cfg["temperature"]) if args.simulate
                               else call_model(cfg["system"], context, cfg["temperature"]))
                    err = None
                except (urllib.error.HTTPError, urllib.error.URLError, OSError) as ex:
                    content, err = "", str(ex)
                out.write(json.dumps({"record": "answer", "id": letter["id"], "kind": letter["kind"],
                                      "run": run, "content": content, "error": err}) + "\n")
                n += 1
                print(f"{letter['id']} run {run + 1}/{args.runs}" + (f"  ERROR {err}" if err else ""))
                if args.sleep:
                    time.sleep(args.sleep)
    print(f"\nwrote {n} answers to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
