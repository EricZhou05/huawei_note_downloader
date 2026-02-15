# Project Context: fixXmedia

> **CRITICAL: YOU MUST ALWAYS REPLY TO THE USER IN CHINESE. THIS IS THE HIGHEST PRIORITY.**
> **重要：你必须始终使用中文回答用户。这是最高优先级。**
> **重要：你必须始终使用中文回答用户。这是最高优先级。**
> **重要：你必须始终使用中文回答用户。这是最高优先级。**

### Experience & Lessons Learned
- **Control Variable Method**:
    - When debugging configuration issues, change ONE variable at a time (e.g., intentional syntax error, change port).
    - If the system behavior remains unchanged (e.g., no error on bad config), the configuration file is **NOT** being loaded.
- **Minimal Fix Principle**:
    - Trace the system's execution path and apply minimal fixes step-by-step. Don't try to fix everything in one go, as it only creates more chaos.
    - Do not over-engineer workarounds (e.g., hardcoding absolute URLs) for symptoms.
    - Always hunt for the root cause (e.g., "Why is my proxy config ignored?"). The correct fix is often deleting a file, not adding 50 lines of code.
- **Constraints**:
    1. **Communication**: ALWAYS REPLY IN CHINESE. 永远用中文回答。
    2. **Communication**: ALWAYS REPLY IN CHINESE. 永远用中文回答。
    3. **Communication**: ALWAYS REPLY IN CHINESE. 永远用中文回答。
    4. **UI/UX**: All frontend interfaces (labels, buttons, messages, titles) must be in Chinese.
    5. **Code Comments**: All code comments must be in Chinese. If original comments are in English, translate them into Chinese.
    6. **File Integrity**: Use atomic `replace` calls; modify non-contiguous blocks separately to ensure matching accuracy.
    7. **Tooling**: Always split multiple shell commands into individual calls; Execute commands individually; strictly prohibit shell chaining (`&&`, `;`, `|`).
    8. **Env Execution**: Use `backend\.venv\Scripts\python.exe` strictly; avoid global `python`.
    9. Prioritize local map processing; minimize external API calls.