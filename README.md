## I.S.A.A.C - Intelligent System for Advanced Assistance And Companionship

![Demo Image](https://github.com/n1teshy/py-isaac/blob/main/images/1.png)

I.S.A.A.C is a completely local, on-terminal AI assistant that lets you use ChatGPT-like features on the terminal so you don't have to switch windows every 2 minutes, it comes with a set of commands and features that you can turn on or off to get the most out of it, I.S.A.A.C can talk to you using locally run speech-to-text and text-to-speech models allowing you to put your fingers to better use.

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
- - `:toggle context` to toggle the use of conversation history for coherent responses.
- - `:toggle hearing` to toggle the assistant's ability to hear you.

`NOTE: for interacting with the assistant only using your voice, turn on both speech and hearing.`

---

- `:select` - selects from available options.
- - `:select lm_provider` to select the language model provider.
- - `:select lm` to select the model for generating responses.
- - `:select voice` to select a [Piper](https://github.com/rhasspy/piper) text-to-speech model for the assistant to speak with.
- - `:select whisper` to select a [Whisper](https://github.com/openai/whisper) speech-to-text model for the assistant to interpret your voice with.
---
- `:key` sets the LLM API key for the selected provider, run this when the assistant can't process your queries, it means the key most proabably expired.
- `:instruct` instructs the model to behave a certain way, using the [system message](https://promptmetheus.com/resources/llm-knowledge-base/system-message).
- `:status` to see status, selected settings and resource consumption.
- `:mute` to mute the assistant while it's speaking.
- `:cmd` to launch a shell session to run shell commands, run the `exit` command in the shell session to get back to the assistant.
- `:commands` to see all available commands.
- `:clear` to clear the terminal.
- `:exit` to turn the assistant off.

---
### Tasks
- [ ] add deepseek support.
