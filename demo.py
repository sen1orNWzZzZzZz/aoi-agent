from langchain_core.prompts import ChatPromptTemplate

# 类似 Thymeleaf 模板
template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，擅长{skill}"),
    ("human", "{question}")
])

# 填充变量
prompt = template.format_messages(
    role="Java专家",
    skill="高并发架构",
    question="如何设计秒杀系统？"
)

print(prompt)