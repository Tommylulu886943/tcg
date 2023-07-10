import json
from deepdiff import DeepDiff

# 假設我們有兩個OpenAPI文件的字典格式表示法，doc1和doc2
# 注意：實際使用時，請先將OpenAPI文件解析成字典格式
doc1 = {
    "paths": {
        "/api/v1/items": {
            "get": {
                "description": "get all items",
                "responses": {
                    "200": {
                        "description": "successful operation"
                    }
                }
            }
        }
    }
}

doc2 = {
    "paths": {
        "/api/v1/items": {
            "get": {
                "description": "get all items",
                "responses": {
                    "200": {
                        "description": "success operation"
                    }
                }
            }
        }
    }
}

# 使用DeepDiff進行比較
diff = DeepDiff(doc1, doc2)

# 將所有變動的路徑和方法抽取出來
changes = {}
for change_type, details in diff.items():
    for item in details:
        path = item.split('root')[1].split(' ')[0]  # Extract path
        changes[path] = change_type  # Add change type to changes dictionary

# 輸出變動的路徑和方法
for path, change_type in changes.items():
    print(f'Path {path} has changes: {change_type}')

