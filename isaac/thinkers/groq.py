from typing import Optional

import requests

import isaac.constants as c
import isaac.globals as glb
from isaac.thinkers import ThinkerConfig, ThinkerInterface, ThoughtOptions
from isaac.thinkers.utils import format_messages, update_token_cost


class GroqThinker(ThinkerInterface):
    def __init__(self, config: ThinkerConfig):
        super().__init__(config)

    def think(
        self, query: str, options: Optional[ThoughtOptions] = None
    ) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "curl/7.68.0",
        }
        past_exchanges = (
            ((options and options.history) or glb.past_exchanges)
            if glb.settings.context_enabled
            else []
        )
        messages = format_messages(
            query=query,
            fld_role=c.GROQ_FLD_ROLE,
            fld_content=c.GROQ_FLD_CONTENT,
            role_user=c.GROQ_ROLE_USER,
            role_assistant=c.GROQ_ROLE_ASSISTANT,
            role_system=c.GROQ_ROLE_SYSTEM,
            system_message=(options and options.system_message)
            or self.config.system_message,
            past_exchanges=past_exchanges,
        )
        data = {
            c.GROQ_FLD_MESSAGES: messages,
            c.GROQ_FLD_MODEL: self.config.model,
        }
        response = requests.post(url, json=data, headers=headers).json()
        if c.GROQ_FLD_ERROR in response:
            if (
                response[c.GROQ_FLD_ERROR].get(c.GROQ_FLD_ERROR_CODE)
                == "model_decommissioned"
            ):
                return (
                    f"the model '{self.config.model}' has been decommissioned"
                    ", please use another Groq model."
                )
            return c.MSG_LANG_MODEL_ERROR
        update_token_cost(
            response[c.GROQ_FLD_USAGE][c.GROQ_USG_PROMPT],
            response[c.GROQ_FLD_USAGE][c.GROQ_USG_COMPLETION],
        )
        return response[c.GROQ_FLD_CHOICES][0][c.GROQ_FLD_MESSAGE][
            c.GROQ_FLD_CONTENT
        ]
