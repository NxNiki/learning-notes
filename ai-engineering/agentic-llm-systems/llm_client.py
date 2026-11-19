"""The one interface the agents need from a language model, and two implementations.

complete(system, messages, tools) -> LLMResponse

- ScriptedLLM replays a fixed list of replies. The tests use it, so the whole
  multi-agent flow runs offline, for free, and gives the same result every time.
- ClaudeLLM calls the Claude API. Messages use the Anthropic format throughout,
  so nothing is translated on the way in.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    content: list[Any]            # content blocks, appended to the history unchanged
    text: str                     # the text blocks joined
    tool_calls: list[ToolCall]
    stop_reason: str


class LLMError(Exception):
    """The model stopped for a reason the agent cannot continue from (refusal, max_tokens)."""


class ScriptedLLM:
    """Replays a script. Each entry is one model turn:

    - a string: the model answers with that text and stops;
    - a list of (tool_name, input) pairs: the model calls those tools.

    Every request is recorded in `requests`, so a test can check what the
    model was shown (for example that a tool result reached it).
    """

    def __init__(self, script: list):
        self.script = list(script)
        self.requests: list[dict] = []
        self._next_id = 0

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> LLMResponse:
        self.requests.append({
            "system": system,
            "messages": [dict(m) for m in messages],
            "tools": [t["name"] for t in tools],
        })
        if not self.script:
            raise LLMError("ScriptedLLM: script exhausted; the agent asked for more turns than scripted")
        turn = self.script.pop(0)
        if isinstance(turn, str):
            return LLMResponse([{"type": "text", "text": turn}], turn, [], "end_turn")
        calls = []
        for name, args in turn:
            self._next_id += 1
            calls.append(ToolCall(f"toolu_{self._next_id:03d}", name, args))
        content = [{"type": "tool_use", "id": c.id, "name": c.name, "input": c.input} for c in calls]
        return LLMResponse(content, "", calls, "tool_use")


class ClaudeLLM:
    """Calls Claude through the Anthropic SDK (`pip install anthropic`).

    Credentials come from the environment (ANTHROPIC_API_KEY or an
    `ant auth login` profile). Server-side refusal fallbacks are on: if the
    model declines a request, the API retries it on a fallback model inside
    the same call.
    """

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium",
                 max_tokens: int = 16000, client=None):
        if client is None:
            import anthropic
            client = anthropic.Anthropic()
        self.client = client
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> LLMResponse:
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            tools=tools,
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if response.stop_reason == "refusal":
            raise LLMError(f"model refused: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            raise LLMError(f"reply cut off at max_tokens={self.max_tokens}")
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = [ToolCall(b.id, b.name, b.input) for b in response.content if b.type == "tool_use"]
        return LLMResponse(list(response.content), text, calls, response.stop_reason)
