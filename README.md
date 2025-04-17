## I.S.A.A.C - Intelligent System for Advanced Assistance and Companionship

![Demo Image](https://github.com/n1teshy/py-isaac/blob/main/images/1.png)

I.S.A.A.C is a on-terminal AI assistant that lets you use ChatGPT-like features on the terminal so you don't have to switch windows every 2 minutes, it comes with a set of commands and features that you can turn on or off to get the most out of it, I.S.A.A.C can talk to you using locally run speech-to-text and text-to-speech models allowing you to put your fingers to better use.

- Run `pip install py-isaac`.
- Run `isaac`.
- Type `:commands` to list all available commands.
- Type `hello` and you will be prompted to choose a language model provider.
- Select a provider from [Gemini](https://gemini.google.com/) and [Groq](https://console.groq.com/).
- Now, you will be prompted for an API key.
- Create a [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key) if you selected Gemini or a [Groq API key](https://console.groq.com/keys) if you selected Groq.
- Paste the API key to the prompt.
- Done.

### Available commands

- `:toggle`- toggles features on/off.
- - `:toggle speech` to toggle the assistant's speech.
- - `:toggle context` to toggle the use of conversation history for coherent responses, uses the last 5 or less user-assistant exchanges.
- - `:toggle hearing` to toggle the assistant's ability to hear you.
- - `NOTE: The textual input (REPL) is disabled when you enable hearing, so to run commands, you can either press ctrl + C and you'd be able to type one command or say one of the one-word commands like 'exit', 'status' etc and they will be processed as commands and not natural language text.`

`NOTE: for interacting with the assistant only using your voice, turn on both speech and hearing.`

---

- `:select` - selects from available options.
- - `:select lm_provider` to select the language model provider.
- - `:select lm` to select the model for generating responses.
- - `:select voice` to select a [Piper](https://github.com/rhasspy/piper) text-to-speech model for the assistant to speak with.
- - `:select whisper` to select a [Whisper](https://github.com/openai/whisper) speech-to-text model for the assistant to interpret your voice with.

---

- `!<shell-command>` runs shell commands without launching a shell session, .e.g. `!ls`.
- `:key` sets the LLM API key for the selected provider, run this when the assistant can't process your queries, it means the key most proabably expired.
- `:instruct` instructs the model to behave a certain way, using the [system message](https://promptmetheus.com/resources/llm-knowledge-base/system-message).
- `:status` to see status, selected settings and resource consumption.
- `:mute` to mute the assistant while it's speaking.
- `:cmd` to launch a shell session and pauses the assistant, `powershell` on windows and `/bin/sh` on linux, run the `exit` command in the shell session to get back to the assistant.
- `:commands` to see all available commands.
- `:clear` to clear the terminal.
- `:exit` to turn the assistant off.

---

### Features

- [x] Free LLM APIs to process natural language queries.
- [x] Voice-only conversations, assistant listens to you and speaks to you.
- [x] Dozens of assistant voices and multiple options for the listening ability.
- [x] Runs shell commands using the '!' (bang) prefix.
- [x] Assistant mutes when user starts speaking
- [x] Runs on both CPUs and GPUs.
- [x] Commands to control the assistant's behavior.
- [x] Other utllity commands to clear the screen, show resource consumption etc.

---

### Tasks

- [ ] add ollama support, user should be able to choose locally running ollama API as language model provider.
- [ ] User profiling, store general likes and dislikes, e.g. "concise answers", "a project they're working on" etc.

### Contributing

If you don't know where to start, pick one of the pending tasks and start with that. If if you want to fix a bug or add other enhancements, please raise an issue first.
