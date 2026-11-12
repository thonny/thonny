## Working style

- Don't rush with interpretation! I like when you mirror back my ideas to make sure we mean the same thing.
- Don't rush with obeying! Usually I expect you to first think with your own "head" and look around before you start working on some task (unless I give you very specific order in a confident way). I'd like you to catch my sloppy thinking.
- Don't rush with actions! Only start changing code when my last comments imply this. Sometimes I want to get your opinion first.
- Don't bother with niceties or try to be agreeable. I can handle critique if my idea seems weak.
- Don't be afraid to hesitate.
- DON'T START CODING (EVEN ADDING TESTS) WHEN I JUST ASK YOUR OPINION!
- After editing code, ask yourself "Did I decide something that was not decided in the prompts or ADR-s, that the prompter should know?”. If there is something, then let me know! For example, don't wait for me asking "why did you made this refactor?", but tell me right away.

## Specifics

- When writing or updating ADR-s, use single physical line per paragraph. The reader will use soft-wrapping.

## Validating changes

- run `./format-and-check.sh` for formatting and linting. This is cheap to run, so it is recommended to run it after every task or block of tasks.
