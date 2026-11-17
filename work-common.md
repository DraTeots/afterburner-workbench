
# common rules

Two files run a program. The **program file** (`work-specific.md`) 
holds what is specific o this program: paths, pins, the ruler's workload, budgets, the variables
below. 

- This file holds the rules of every session; the program file points to them by section name.

This is scientific software: a change counts when a benchmark row and a plot show it. The user works with you in chat and reviews the uncommitted working tree. A session ends without warning, so the state of the work lives in files under `{space}`, written as you go. Results go upstream as issues and PRs for maintainers who never saw this chat.

## Variables set by the program file

- `{repo}` - the code tree the program works on: this repository, submodules included
- `{space}` - the folder for all notes, questions, decisions, plots and reports of this program
- `{ledger}` - the phase ledger, append-only: each phase's spec before the work, its outcome after
- `{data}` - input data and large outputs, never in git
- `{scratch}` - temporary files and caches: the scratch folder Claude Code reports
- `{memory}` - the agent-memory directory that holds `MEMORY.md`
- `{git}` - `off` or `on`: whether you may commit (Git section)
- `{online}` - `yes` when the user answers in chat during the session

## Scientific software — benchmark, scripts, plots

The user's words:

> We are scientists and I need plots from you.
> You need scientific approach and reproducibility:
> - Create scripts that analyse data
> - Create scripts that plot metrics
> - Create scripts that asses the results and can be used to compare results

The benchmark (the program file's Ruler) is the test suite of every change, and its rows are the numbers each PR cites. A change passes by changing the code under study, never by changing a check, a tolerance, the reference or the workload. A check that looks wrong goes to the user with the evidence and stays until they decide. When a change fails, rerun with it reverted: if that fails too, the ruler is broken, and nothing measured with it counts.

<example>
abconv applies no beam energy spread, so the energy-spread check fails in every setup. Removing the check would turn the benchmark green; the user kept it failing (D-user-7, "Keep as check"), because the failure is the finding (F3).
</example>

Every number, plot and table in a report comes from a script in `{repo}` that reruns from its inputs; the report names the script and the run. A number retyped from memory drifts; one read from an output file can be rechecked.

- Put plots in {space}/plots/phase{#}/ and write results up in
  {space}/reports/phase{#}_.... Previous results, plots and knowledge must
  persist as you progress. Every plot is a PNG.
- A figure that a report cites is copied into that phase's plots folder: benchmark figures live under `{data}/bench/<label>/results/`, and a rerun under the same label overwrites them.
- A plot puts the change, the reference and the expectation on the same axes, so it shows cause and size.

<example>
`vertices.png` of the afterburner benchmark: the angle between a decay's displacement and its parent's momentum against cos θ of the parent, abconv and Pythia8 + eicBeamShape, with the expectation for momenta turned and vertices not, (12.5 mrad)(1 + cos θ), as a dashed line. abconv follows the line (median 24.93–24.99 mrad over 19 setups); Pythia8 stays at zero.
</example>

## Phases

- **Phase** — one entry of the ledger: a task with a Step 0, a ruler and a
  done criterion. A phase takes one or several runs. 
  Usually results of a phase are checked by a human before continuation

A phase's spec goes into `{ledger}` before its work starts. A finished phase leaves:

- its ledger entry, the outcome appended
- `{space}/plots/phase{#}/` - its figures
- `{space}/reports/phase{#}_*.md` - its report: what was measured, with the plots; the defaults you took; the questions for the next phase
- `{space}/reports/phase{#}_findings.md` - the full entries of the findings it discovered
- STATUS.md's first line: `PHASE<N> DONE — report at <path>`

The plan changes only when the user changes it: a discovery that would change the scope goes to the user as a finding with a proposal.

## Memory — findings, questions, decisions, lessons, notes

What is not in a file is gone when the session ends. Each fact has one home and everything else points at it, so a changed fact changes one file.

### Findings

A bug in the code under study is an expected finding, and with the repairs it is what the program delivers upstream. `{space}/reports/FINDINGS.md` indexes every finding, one line each, status first (FIXED, RESOLVED, WON'T FIX, OPEN), so a reader sees what is fixed and what is open without opening another file. F-numbers are permanent: issues, PRs and decisions cite them. The full entry (reproducer, cause, evidence) lives in the phase's findings file; change it and the index line together, and keep the counts line true.

<example>
| OPEN | F7 | `abconv --version` prints 0.1.3 at tag v0.2.1 and on main (`ArgumentProcessor.cc` line 39, a string literal); `cpp/CMakeLists.txt` declares project version 1.0.0. | eic/afterburner `ArgumentProcessor.cc` | Phase 1, branch `fix/version-string` |
| FIXED | F8 | abconv's histogrammer (v0.2.1) takes the first status-4 particle as the hadron beam. Fixed upstream on main (32c9429, select by PDG id). | eic/afterburner `Histogrammer.cc` | upstream main |
</example>

### Questions

When `{online}` is `yes`, ask in chat: one question, answerable by a letter, your recommendation first. A question that must outlive the session goes to `{space}/QUESTIONS.md`; the user answers there between sessions. A question about a tool, a threshold, a rule, a budget or code is yours to DECIDE: a sister program asked 76 questions in four days, most about its own measuring tools, and the user called that inhumane.

<example>
## Q4 2026-11-11 — Fix shape for the mirrored IP crossing term (F2) [closed 2026-11-11]
- Options: A) turn the IP, x → −x B) the root fix (no convention flip). Recommendation: A.
- ANSWER: B → D-user-4
</example>

### Decisions

- Record every decision that constrains later work in
  {space}/notes/DECISIONS.md (format in the Memory section). Tie decisions
  to evidence and measured numbers; the numbers themselves stay in the
  reports.
- A changed decision edits its entry; a veto of a default becomes a `D-user` entry.

<example>
- D-user-6 (2026-11-11, user, Q5): "All PRs and work must be separated. All findings will go to new issues and PRs": one finding, one branch, one issue, one PR.
- D-default-1 (2026-11-11, agent, setup): afterburner submodule at upstream main (32c9429), the base of the repair branches; eicSimuBeamEffects at v1.1, the version eic_xl 26.11 ships.
</example>

### Lessons

- Store one lesson per file in {space}/notes/ with a one-line summary
  at the top; update rather than duplicate; delete notes that turn out wrong.
  A lesson's rule changes the config or script that caused the trap in the
  same step, and the lesson names that edit (try 1 wrote the disk lesson and
  left the cause in the config template).
  A lesson that generalizes beyond this program is promoted the same day
  (Memory section).
- Agent memory (`{memory}`) takes only what outlives this program: an environment trap, a user correction that generalizes.

<example>
notes/lesson-zsh-word-split.md: the shell is zsh, so an unquoted `$C` holding `--config A=1 B=2` stays one word; Snakemake took it as one target (MissingRuleException) and nothing ran. Write the arguments out.
</example>

### Notes

- `STATUS.md` - where to resume, under ~40 lines, never a journal
- `notes/runlog.md` - what was tried, when, with what result; append-only; the reports win where numbers disagree
- `notes/ENVIRONMENT.md` - what a future session must install

<example>
STATUS.md:
PHASE0 NOT STARTED — workbench set up 2026-11-11; next session starts Phase 0, Step 0
## LIVE
- nothing running
## RESUME
- Before any benchmark run: `git -C generator_benchmarks checkout afterburner-benchmark` (local branch 2a87b52; the gitlink stays at upstream main 1a92e6b).
## Waiting on the user
- nothing blocking
</example>

## Environment

- EIC software (abconv, Pythia8, eicBeamShape, ROOT, Snakemake) runs in the pinned `eic_xl` image through the program file's container wrapper: the host has no EIC stack.
- YOU ARE NOT ALLOWED TO DO ANY CHANGES IN GIT. No commits, no pushes. But
  allowed to read, checkout, compare as needed. The setup file may grant
  commits explicitly (`{git}` = `on`); the Git section then applies.
- The machine is the user's workstation: change nothing on the system (no package manager, no `sudo`, no services). Python runs in `eic_xl` or on the host through **uv** (`uv run --with <package>`); plain argparse, no typer. A missing tool: its install command goes to `{space}/notes/ENVIRONMENT.md` and one line to the user.
- Check the core count (`nproc`) and use it (parallel jobs), keep ~2 cores headroom.

## How you work

- On start: read {space}/STATUS.md if it exists, then resume from where the
  last session stopped instead of restarting.
- STATUS.md is the resume entrypoint. Its shape and size are fixed in the
  Memory section: a `## LIVE` block, a `## RESUME` block, what waits on the
  user, pointers — under ~40 lines, never a journal.
- Write the `## LIVE` block the MOMENT any background job, slurm array, GPU
  allocation or monitor starts or ends — not at session end. Then a mid-run
  death costs nothing and context compaction needs no steering.
- When you create code, make it easy for humans to use and maintain:
  anywhere someone starts reading, the context is quickly clear.
- When you have enough information to act, act. Do not re-litigate decisions
  already made. If weighing a choice about a tool, a threshold, a rule, a
  budget, naming or code, pick one and record it as a `D-default` decision
  (DECIDE). A doubt about the user's wishes, the physics goal or a frozen
  item stays a question.
- The user's time is the scarce resource. Only what the user alone knows
  reaches the user as a question: the goal, the physics, the scope, which
  dataset counts, a frozen item. Everything else is yours to decide and
  record, where the user can veto it.
- Every timestamp you write into the ledger, the run log, DECISIONS.md or
  QUESTIONS.md comes from `date -u` in the command that writes the entry,
  never from your own sense of time (try 1 wrote some early timestamps ahead
  of the clock).
- For reversible actions that follow from the program file, proceed. When
  anything unexpected happens — or you catch yourself about to assume
  something the user could have specified — ask (Memory section, Questions).
  Never pursue a doubtful assumption silently.
- Token thrift: you run on a limited LLM budget, so be economical with your
  own effort — compute is cheap, tokens are expensive:
  - Never load raw data into your context. Write scripts that print small
    samples, stats, and summaries; read those instead.
  - Redirect ALL build and run stdout/stderr to log files; inspect them only
    via tail/grep.
  - Run long jobs detached (nohup, background) and poll their logs; never
    block a tool call on a long run. Loop over parameters INSIDE scripts,
    never one tool call per point.
  - Prefer one well-prepared production over many small iterations. CPU
    hours cost nothing from your budget; thinking loops and subagents do.
  - Validate from printed numbers (counts, hashes, MB/s); look at a
    rendered plot at most once per milestone.
  - Do not re-read files you just wrote; re-read only the region you are
    editing.
  - Milestone-first: each phase file names its Step 0; finish and record it
    before any other work. A finished verified milestone is worth more than
    three half-finished ones.
  - Before any open-ended search, state in your notes what you expect to
    find and why. If you can't, put it in the report as "recommended next
    step" instead of doing it.
  - Assume you can be interrupted at any moment (rate limits): keep scripts,
    notes, and partial results on disk at all times so a future run resumes
    rather than restarts; update STATUS.md as you go.

## How you document

Applies to user-facing documents, texts and code+comments. For yourself you
write how it is better for your recall and understanding.

- Act as a technical writer following the Google Developer Documentation Style
  Guide.
- Strip every sentence to its cleanest components: remove every word that
  does not contribute to the meaning.
- Eliminate clutter: avoid redundancies ("completely finished" → "finished").
- Remove hedge words that weaken prose: very, little, pretty, rather,
  actually.
- Avoid jargon: use simple, direct language a general reader understands
  without a dictionary (established domain terms are fine).
- Never the rhetorical "X, not Y" construction ("fast, not correct" prose);
  state X and let the reader infer not-Y. A negation that is itself the
  instruction ("output must not differ") is fine.
- No slang and no editorializing epithets (nominal, finally, honest,
  clever).
- Use the hypen for any dash in text, ranges included, no en dashes and em dashes allowed (if not specified by user).
- Eliminate excessive claims. Never use words that assume the user's skill
  level or the task's difficulty. Avoid words such as: simply, just, easily,
  easy, obvious, obviously, straightforward, trivial, painless, and basically.
- Eliminate ambiguous pronouns. Never use first person plural pronouns (we, us,
  our).
- Use direct address and imperative mood. Speak directly to the reader as
  "you" or give direct commands. Example: "Run the script" instead of "We will
  run the script".
- State the goal before the action. Example: "To start the server, run the
  command" instead of "Run the command to start the server".
- Omit unnecessary politeness. Do not use "please" or "kindly".
- Be objective and literal: describe what the software does.
- Don't write code history, sentiments about code changes or prompt details in
  text. Any written text exists for a new human reader to understand the
  context in the minimal time.
- History or details may still exist if they help prevent a bug or warn of
  risky places. E.g. "Trying to optimize X will involve Y and will probably
  fail because of Z".
- Never leave pieces of prompt context and prompt jargon in comments.
  BAD: "As it said in the phase file ...".
- A comment earns its place by saying something the code can't: the rationale,
  the constraint, the non-obvious consequence. BAD: "// loop over events".
- Lead a non-trivial block with a short intent line, then the mechanism. Name
  the trap or the gotcha explicitly.

### Titles and headings

A title is a label for the content under it, not a hook for the reader. In the
fewest words, state what the reader finds there. This applies to every heading
level, to slide titles, to table captions and to summary blocks.

- Be factual about the content. The reader must be able to predict the section
  from its title alone.
- No analogies, no comparisons, no metaphor, no wordplay.
- No instruction to the reader and no rhetorical framing. A title describes;
  it does not advise, tease or conclude.
- No counting formulas that carry no content ("Three things to know").
- Strip filler: "about", "overview of", "a note on", "the same thing as",
  "what this means".

| Bad | Good |
|---|---|
| Pick the energy first | Processes per beam energy |
| Where this leaves the plan | Recommendations and open requests |
| The four things to take away | Summary of findings |
| The one rule that matters most | Crossing angle requirement |
| Vacuum vs gold — and which is the real one | Beampipe coating: rates and campaign history |
| The same thing as events per frame | Expected events per 2 µs frame |
| Caveats that decide whether a branch is usable | Usability caveats per branch |

A subtitle after an em dash is allowed when it adds content the title cannot
carry alone, and it follows the same rules: "Background sources — rates and
status codes" is a label; "Background sources — the part everyone forgets" is
not.

## How you code

- You write for humans, so a human maintainer feels comfortable reading
  (minimal cognitive load) and editing the code.
- Match the surrounding style when editing code you don't own: a library
  has its own naming and layout — new code inside it follows the file it
  lives in, not your defaults.
- You don't follow 80-character line cut-offs. If it is easier to read in one
  long line — do it. If a function definition reads better with each argument
  on its own line — use it. Decide from a human reader's point of view.
- Don't use short obscure variable names like `ac3` or `bumdbx`, but also don't
  make them unnecessarily long like `my_variable_to_hold_data`. Keep balance.
- Any place in the code must satisfy: if a new reader reads only this place,
  the variable names and comments let them understand the context and what is
  going on.
- A lot of import nesting is bad. Import B from A which is imported from C
  from D makes humans follow the whole chain and open all files. One very long
  file with everything is bad too. Decide on balance.
- For a single loop `i` is OK; for nested loops indexes must help understand
  the context: `col_i, row_i` for tables, `file_i, event_i` for event loops.
  Decide on balance.
- For analysis scripts configuration use **OmegaConf + YAML** to organize where
  data lives and what goes in/out of each stage.

## Git

Commits need `please-git` in the user's chat message. `{git}` records that permission and never grants it: `on` without the phrase in the chat counts as `off`. Without it git is read-only; keep each code experiment as a patch under `{space}/notes/patches/`. The user edits this tree too: leave changes that are not yours as they are.

Each repair goes upstream as its own PR for the afterburner maintainers to review (D-user-6): its own local branch in its submodule, from upstream `main` unless the program file names another base. It leaves the machine only as a PR the user asked for (D-user-2), drafted under `{space}/issues/` first. A gitlink points only at a commit its submodule's URL serves, so a fresh clone can check it out.
