"pydantic 模型返回结构化数据"
from pydantic import BaseModel, Field

from init_llm import deepseek_llm

# 返回嵌套对象
class Actor(BaseModel):
    name: str = Field(description="演员姓名")
    role: str = Field(description="演员在电影中的角色")


class Movie(BaseModel):
    title: str = Field(description="电影标题")
    year: int = Field(description="电影上映年份")
    director: str = Field(description="电影导演")
    rating: float = Field(description="电影评分")
    cast: list[Actor] = Field(description="电影演员列表")


model_with_structured_output = deepseek_llm.with_structured_output(Movie,include_raw=True)

resp = model_with_structured_output.invoke("介绍下电影《泰坦尼克号》")

print(type(resp))
print(resp)


# 定义一个 Pydantic 模型，用于结构化输出简单对象
# class Movie(BaseModel):
#     title: str = Field(description="电影标题")
#     year: int = Field(description="电影上映年份")
#     director: str = Field(description="电影导演")
#     rating: float = Field(description="电影评分")
#
#
# model_with_structured_output = deepseek_llm.with_structured_output(Movie,)
#
# resp = model_with_structured_output.invoke("介绍下电影《78》不超过10字,禁止返回电影年份和导演任何信息")
#
# print(type(resp))
# print(resp)
