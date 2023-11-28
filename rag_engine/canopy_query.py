import os

from canopy.knowledge_base import KnowledgeBase
from canopy.models.data_models import Query
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
import json
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage
from canopy.models.api_models import (
    StreamingChatResponse,
    ChatResponse,
)
from typing import cast, Union
from sse_starlette.sse import EventSourceResponse

Tokenizer.initialize()

kb = KnowledgeBase(index_name=os.getenv("PINECONE_INDEX_NAME") or "canopy--plana-demo")
kb.connect()

# results = kb.query([Query(text="COP28")])
#
# print(results[0].documents[0].text)
#
# print(f"score - {results[0].documents[0].score:.4f}")

context_engine = ContextEngine(kb)

# result = context_engine.query([Query(text="PlanA")], max_context_tokens=500)
#
# print(json.dumps(json.loads(result.to_text()), indent=2, ensure_ascii=False))
# print(f"\n# tokens in context returned: {result.num_tokens}")

chat_engine = ChatEngine(context_engine)


openai_response = chat_engine.chat(messages=[UserMessage(content="what is PlanA?")], stream=True)

openai_response_id = ""
internal_model = ""
output = ""
for chunk in cast(StreamingChatResponse, openai_response).chunks:
    openai_response_id = chunk.id
    internal_model = chunk.model
    text = chunk.choices[0].delta["content"] or ""
    output += text
    print(text)

print(openai_response_id)
print(internal_model)
print(output)
