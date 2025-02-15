from typing import List, Optional, Tuple

import requests

import isaac.constants as c
import isaac.globals as glb
from isaac.utils import check_internet

import re


def ask_gemini(
    model: str,
    api_key: str,
    query: str,
    sys_msg: Optional[str] = None,
    past_exchanges: Optional[List[Tuple[str, str]]] = None,
) -> str:
    """
    queries the selected `Gemini` model and returns its repsonse as a string.
    """
    base = "https://generativelanguage.googleapis.com/v1beta/models"
    url = f"{base}/{model}:generateContent?key={api_key}"
    data = {}
    if sys_msg is not None:
        data[c.GMNI_FLD_SYS_INST] = {c.GMNI_FLD_PARTS: {c.GMNI_FLD_TEXT: sys_msg}}
    contents = []
    if past_exchanges is not None:
        for exchange in past_exchanges:
            contents.append(
                {
                    c.GMNI_FLD_ROLE: c.GMNI_ROLE_USER,
                    c.GMNI_FLD_PARTS: [{c.GMNI_FLD_TEXT: exchange[0]}],
                }
            )
            contents.append(
                {
                    c.GMNI_FLD_ROLE: c.GMNI_ROLE_MODEL,
                    c.GMNI_FLD_PARTS: [{c.GMNI_FLD_TEXT: exchange[1]}],
                }
            )
    contents.append(
        {
            c.GMNI_FLD_ROLE: c.GMNI_ROLE_USER,
            c.GMNI_FLD_PARTS: [{c.GMNI_FLD_TEXT: query}],
        }
    )
    data[c.GMNI_FLD_CONTENTS] = contents
    response = requests.post(url, json=data).json()
    if c.GMNI_FLD_ERROR in response:
        return c.MSG_LANG_MODEL_ERROR
    update_token_cost(
        response[c.GMNI_FLD_USAGE][c.GMNI_USG_PROMPT],
        response[c.GMNI_FLD_USAGE][c.GMNI_USG_COMPLETION],
    )
    content = response[c.GMNI_FLD_CANDIDATES][0][c.GMNI_FLD_CONTENT]
    return content[c.GMNI_FLD_PARTS][0][c.GMNI_FLD_TEXT]


def ask_groq(
    model: str,
    api_key: str,
    query: str,
    sys_msg: Optional[str] = None,
    past_exhanges: Optional[List[Tuple[str, str]]] = None,
) -> str:
    """
    queries the selected `Groq` model and returns its repsonse as a string.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "curl/7.68.0",
    }
    messages = []
    if sys_msg is not None:
        messages.append(
            {c.GROQ_FLD_ROLE: c.GROQ_ROLE_SYSTEM, c.GROQ_FLD_CONTENT: sys_msg}
        )
    if past_exhanges is not None:
        for exchange in past_exhanges:
            messages.append(
                {
                    c.GROQ_FLD_ROLE: c.GROQ_ROLE_USER,
                    c.GROQ_FLD_CONTENT: exchange[0],
                }
            )
            messages.append(
                {
                    c.GROQ_FLD_ROLE: c.GROQ_ROLE_ASSISTANT,
                    c.GROQ_FLD_CONTENT: exchange[1],
                }
            )
    messages.append({c.GROQ_FLD_ROLE: c.GROQ_ROLE_USER, c.GROQ_FLD_CONTENT: query})
    data = {c.GROQ_FLD_MESSAGES: messages, c.GROQ_FLD_MODEL: model}
    response = requests.post(url, json=data, headers=headers).json()
    if c.GROQ_FLD_ERROR in response:
        if (
            response[c.GROQ_FLD_ERROR].get(c.GROQ_FLD_ERROR_CODE)
            == "model_decommissioned"
        ):
            return (
                f"the model '{model}' has been decommissioned"
                ", please use another Groq model."
            )
        return c.MSG_LANG_MODEL_ERROR
    update_token_cost(
        response[c.GROQ_FLD_USAGE][c.GROQ_USG_PROMPT],
        response[c.GROQ_FLD_USAGE][c.GROQ_USG_COMPLETION],
    )
    return response[c.GROQ_FLD_CHOICES][0][c.GROQ_FLD_MESSAGE][c.GROQ_FLD_CONTENT]


def ask(query: str) -> Tuple[bool, str]:
    """
    queries the selected language model and returns response as a string,
    sends chat context if context is enabled.
    """
    if glb.settings.response_generator is None:
        glb.settings.select_lm_provider()
    if glb.settings.lang_model is None:
        glb.settings.select_lm()

    exchanges = glb.past_exchanges if glb.settings.context_enabled else None
    try:
        if glb.settings.response_generator == c.RSPNS_GNRTR_GEMINI:
            response = ask_gemini(
                glb.settings.gemini_model,
                glb.settings.gemini_key,
                query,
                glb.settings.system_message,
                exchanges,
            )
        else:
            response = ask_groq(
                glb.settings.groq_model,
                glb.settings.groq_key,
                query,
                glb.settings.system_message,
                exchanges,
            )
    except Exception:
        if check_internet():
            raise
        response = c.MSG_NO_INTERNET
    post_ask(query, response)
    return response


def post_ask(query: str, answer: str):
    """
    stores query-response exchange to send as context with later queries,
    if the response contains code, only keeps code as response, if response
    contains plain text, response is truncated.
    """
    max_answer_words = 30
    max_exchanges = 5
    code_blocks = re.findall(r"```.*?```", answer, re.DOTALL)

    if len(code_blocks) > 0:
        answer = "\n\n".join(code_blocks)
    else:
        parts = answer.split()
        if len(parts) > max_answer_words:
            answer = " ".join(parts[:max_answer_words]) + "..."
    glb.past_exchanges.append((query, answer))
    if len(glb.past_exchanges) > max_exchanges:
        glb.past_exchanges = glb.past_exchanges[-max_exchanges:]


def update_token_cost(prompt: int, completion: int):
    """updates the token cost to keep track of token expenditure."""
    glb.settings.prompt_tokens += prompt
    glb.settings.completion_tokens += completion
