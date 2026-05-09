import subprocess
import sys
import os

# --- Configuration ---
LIMIT = 5
JUDGE_MODEL = "google/gemma-4-E2B-it"
BASE_OUT_DIR = "wyniki/prompt_injection_eval"

# The 4 distinct models to test
MODELS = ["tinyllama", "qwen3-1-7b", "mistral-7b", "gemma-4b"]

# Define the isolated testing strategies
# Keys are folder names, values are lists of CLI flags
STRATEGIES = {
    "01_baseline": [],
    "02_no_defensive_system": ["--no-defensive-system"],
    "03_no_sanitize": ["--no-sanitize"],
    "04_heuristic_defense": ["--enable-heuristics", "--heuristic-reject"]
}

def main():
    print("Starting Prompt Injection Benchmark Suite (Python Wrapper)...")
    print(f"Judge Model: {JUDGE_MODEL} (Loaded in 4-bit)")
    print(f"Examples per run: {LIMIT}")
    print("-" * 60)

    # Keep track of successes and failures for the final summary
    summary_report = []

    for model in MODELS:
        for strategy_name, flags in STRATEGIES.items():
            out_dir = os.path.join(BASE_OUT_DIR, model, strategy_name)
            
            print(f"\n[>>] Running Model: {model} | Strategy: {strategy_name}")
            
            # Build the base command using the current Python executable
            cmd = [
                sys.executable, "run_prompt_injection.py",
                "--limit", str(LIMIT),
                "--model-preset", model,
                "--judge-model", JUDGE_MODEL,
                "--judge-load-in-4bit",
                "--output-dir", out_dir,
                "--write-summary"
            ]
            
            # Append the specific strategy flags
            cmd.extend(flags)
            
            try:
                # Run the command. 
                # We don't use capture_output=True so that the script's progress 
                # (like tqdm bars or model loading prints) still shows in your terminal.
                result = subprocess.run(cmd)
                
                if result.returncode == 0:
                    print(f"[OK] Successfully completed {strategy_name} for {model}.")
                    summary_report.append((model, strategy_name, "SUCCESS"))
                else:
                    print(f"[ERROR] Run failed for {model} - {strategy_name} (Exit code: {result.returncode}).")
                    summary_report.append((model, strategy_name, "FAILED"))
                    
            except Exception as e:
                print(f"[FATAL ERROR] An exception occurred while running {model} - {strategy_name}:\n{e}")
                summary_report.append((model, strategy_name, "ERROR"))
                
            print("-" * 60)

    # --- Print Final Summary ---
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED. FINAL SUMMARY:")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for model, strat, status in summary_report:
        # Format the output so the columns align nicely
        status_str = f"[{status}]".ljust(10)
        print(f"{status_str} {model.ljust(15)} | {strat}")
        
        if status == "SUCCESS":
            successful += 1
        else:
            failed += 1
            
    print("-" * 60)
    print(f"Total Successful: {successful}")
    print(f"Total Failed/Errors: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()