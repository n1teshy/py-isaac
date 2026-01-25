from typing import Optional

import requests

import isaac.constants as c
import isaac.globals as glb
from isaac.thinkers import ThinkerConfig, ThinkerInterface, ThoughtOptions
from isaac.thinkers.utils import update_token_cost


class GeminiThinker(ThinkerInterface):
    def __init__(self, config: ThinkerConfig):
        super().__init__(config)

    def think(
        self, query: str, options: Optional[ThoughtOptions] = None
    ) -> str:
        base = "https://generativelanguage.googleapis.com/v1beta/models"
        url = f"{base}/{self.config.model}:generateContent?key={self.config.api_key}"
        data = {}
        data[c.GMNI_FLD_SYS_INST] = {
            c.GMNI_FLD_PARTS: {
                c.GMNI_FLD_TEXT: (options and options.system_message)
                or self.config.system_message
                or "Hi"
            }
        }
        past_exchanges = (
            ((options and options.history) or glb.past_exchanges)
            if glb.settings.context_enabled
            else []
        )
        contents = []
        for user_msg, assistant_msg in past_exchanges:
            contents.append(
                {
                    c.GMNI_FLD_ROLE: c.GMNI_ROLE_USER,
                    c.GMNI_FLD_PARTS: [{c.GMNI_FLD_TEXT: user_msg}],
                }
            )
            contents.append(
                {
                    c.GMNI_FLD_ROLE: c.GMNI_ROLE_MODEL,
                    c.GMNI_FLD_PARTS: [{c.GMNI_FLD_TEXT: assistant_msg}],
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
            return response[c.GMNI_FLD_ERROR].get(
                c.GMNI_FLD_MESSAGE, c.MSG_LANG_MODEL_ERROR
            )
        update_token_cost(
            response[c.GMNI_FLD_USAGE][c.GMNI_USG_PROMPT],
            response[c.GMNI_FLD_USAGE][c.GMNI_USG_COMPLETION],
        )
        content = response[c.GMNI_FLD_CANDIDATES][0][c.GMNI_FLD_CONTENT]
        return content[c.GMNI_FLD_PARTS][0][c.GMNI_FLD_TEXT]
