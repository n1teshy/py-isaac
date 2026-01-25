import re
from typing import Optional, Union

import isaac.globals as glb


def format_messages(
    query: str,
    fld_role: str,
    fld_content: str,
    role_user: str,
    role_assistant: str,
    role_system: Optional[str] = None,
    system_message: Optional[Union[str, dict]] = None,
    past_exchanges: Optional[list] = [],
) -> list:
    messages = []
    if system_message:
        messages.append({fld_role: role_system, fld_content: system_message})
    for user_msg, assistant_msg in past_exchanges:
        messages.append({fld_role: role_user, fld_content: user_msg})
        messages.append({fld_role: role_assistant, fld_content: assistant_msg})
    messages.append({fld_role: role_user, fld_content: query})
    return messages


def pre_query():
    if glb.settings.lang_model is None:
        glb.settings.select_lm()


def post_query(query: str, answer: str):
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
    glb.settings.prompt_tokens += prompt
    glb.settings.completion_tokens += completion
