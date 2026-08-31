from init_llm import deepseek_llm



json_schema = {
    "title": "MovieInfo", #不能使用中文
    "description": "电影信息",
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "电影标题"},
        "year": {"type": "integer", "description": "电影上映年份"},
        "director": {"type": "string", "description": "电影导演"},
        "rating": {"type": "number", "description": "电影评分"},
        "cast": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "演员姓名"},
                    "role": {"type": "string", "description": "演员在电影中的角色"},
                },
                "required": ["name", "role"],
            },
            "description": "电影演员列表",
        },
    },
    "required": ["title", "year", "director", "rating", "cast"],
}


# 模型绑定结构化输出 jsonSchema
model_with_structured_output = deepseek_llm.with_structured_output(json_schema)

resp = model_with_structured_output.invoke("介绍下电影《泰坦尼克号》")
# resp = model_with_structured_output.invoke("介绍下电影《78》不超过10字,禁止返回电影年份和导演任何信息")
print(type(resp))
print(resp)

# 验证返回的对象是不是满足jsonSchema
import jsonschema

error = jsonschema.validate(instance=resp, schema=json_schema)


# 定义 jsonSchema 结构化输出模型
# json_schema = {
#     "title": "MovieInfo", #不能使用中文
#     "description": "电影信息",
#     "type": "object",
#     "properties": {
#         "title": {"type": "string", "description": "电影标题"},
#         "year": {"type": "integer", "description": "电影上映年份"},
#         "director": {"type": "string", "description": "电影导演"},
#         "rating": {"type": "number", "description": "电影评分"},
#     },
#     "required": ["title", "year", "director", "rating"],
# }
#
#
# # 模型绑定结构化输出 jsonSchema
# model_with_structured_output = deepseek_llm.with_structured_output(json_schema)
#
# # resp = model_with_structured_output.invoke("介绍下电影《泰坦尼克号》")
# resp = model_with_structured_output.invoke("介绍下电影《78》不超过10字,禁止返回电影年份和导演任何信息")
# print(type(resp))
# print(resp)


# json_schema = {
#     "type": "object",
#     "properties": {
#         "title": {"type": "string", "description": "电影标题"},
#         "year": {"type": "integer", "description": "电影上映年份"},
#         "director": {"type": "string", "description": "电影导演"},
#         "rating": {"type": "number", "description": "电影评分"},
#         "cast": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string", "description": "演员姓名"},
#                     "role": {"type": "string", "description": "演员在电影中的角色"},
#                 },
#                 "required": ["name", "role"],
#             },
#             "description": "电影演员列表",
#         },
#     },
#     "required": ["title", "year", "director", "rating", "cast"],
# }