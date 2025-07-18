# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import HumanMessage
# from langchain_core.outputs import LLMResult
# from src.llm.HFChatModel import get_mistral_llm
# from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
# def test_chains():
#     prompt = ChatPromptTemplate.from_messages(
#         [("system", "You are a helpful assistant."),
#          MessagesPlaceholder(variable_name="messages")]
#     )
#     model = get_mistral_llm()
#     chains = prompt | model
#     messages = [HumanMessage(content="Xin chào")]
#     response = chains.invoke({"messages": messages})
#     print(f"Raw response: {response}")
#     print(f"Response type: {type(response)}")

#     # Xử lý nếu response là LLMResult
#     if isinstance(response, LLMResult):
#         if response.generations and response.generations[0]:
#             response = response.generations[0][0].message
#         else:
#             raise ValueError("Empty generations in LLMResult")
#     # Xử lý nếu response là danh sách
#     elif isinstance(response, list):
#         print(f"Received list response: {response}")
#         if len(response) > 0:
#             response = response[0]
#             if hasattr(response, "message"):
#                 response = response.message
#         else:
#             raise ValueError("Empty response list")
#     # Kiểm tra nếu response không phải AIMessage
#     if not isinstance(response, AIMessage):
#         raise ValueError(f"Expected AIMessage, got {type(response)}: {response}")

#     print(f"Processed response: {response}")
#     print(f"Processed response type: {type(response)}")

# if __name__ == "__main__":
#     test_chains()

# from langchain_core.messages import HumanMessage
# from src.llm.HFChatModel import get_mistral_llm
# from src.score import get_student_scores, get_student_info, calculate_average_scores

# # Khởi tạo LLM và bind công cụ
# tools = [get_student_info, get_student_scores, calculate_average_scores]
# llm = get_mistral_llm().bind_tools(tools)

# # Gửi truy vấn
# messages = [HumanMessage(content="Lấy thông tin của sinh viên có mã CT060110")]
# response = llm.invoke(messages)

# # Kiểm tra phản hồi
# print(response)
# # Kỳ vọng: AIMessage với tool_calls=[{"name": "get_student_scores", "arguments": {"student_id": "123"}}]

# mistral_toolcalling_test.py

import os
from langchain_community.llms import HuggingFacePipeline
from langchain.agents import Tool, initialize_agent, AgentType
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load mô hình HuggingFace (có thể thay bằng model bạn thích)
model_id = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype="auto")

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)
llm = HuggingFacePipeline(pipeline=pipe)

# Tạo tool
def get_weather(location: str) -> str:
    return f"Thời tiết tại {location} là 30°C, nắng nhẹ."

tools = [
    Tool(
        name="get_weather",
        func=get_weather,
        description="Lấy thông tin thời tiết hiện tại theo tên thành phố. Input phải là tên thành phố (vd: Hanoi)"
    )
]

# Tạo agent kiểu ReAct (dùng mô hình HuggingFace)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Chạy thử
response = agent.run("Cho tôi biết thời tiết ở Hanoi")
print(response)
