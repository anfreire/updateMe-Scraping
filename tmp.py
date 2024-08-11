import astroid
import json
import ast

def get_top_level_functions(module) -> list[astroid.FunctionDef]:
    return [node for node in module.body if isinstance(node, astroid.FunctionDef)]

def extract_key_and_dict(func) -> tuple[str, dict[str, astroid.Name]]:
    for node in func.body:
        if (
            isinstance(node, astroid.Assign)
            and isinstance(node.value, astroid.Call)
            and isinstance(node.value.func, astroid.Name)
            and node.value.func.name == "AppBase"
        ):
            key = node.value.args[0].value
            items = {}
            if isinstance(node.value.args[1], astroid.Dict):
                for key_node, value_node in node.value.args[1].items:
                    if isinstance(key_node, astroid.Const):
                        items[key_node.value] = value_node
            return key, items
    return None, None

def find_function_def(func: astroid.FunctionDef, name: str) -> astroid.FunctionDef:
    return next((node for node in func.body if isinstance(node, astroid.FunctionDef) and node.name == name), None)

def safe_eval(s):
    try:
        return ast.literal_eval(s)
    except:
        return s

def extract_function_info(func_def: astroid.FunctionDef) -> dict:
    for node in func_def.body:
        if isinstance(node, astroid.Return) and isinstance(node.value, astroid.Call):
            if isinstance(node.value.func, astroid.Call):
                class_name = node.value.func.func.name
                init_args = [safe_eval(arg.as_string()) for arg in node.value.func.args]
                call_args = [safe_eval(arg.as_string()) for arg in node.value.args]
            elif isinstance(node.value.func, astroid.Name):
                class_name = node.value.func.name
                init_args = []
                call_args = [safe_eval(arg.as_string()) for arg in node.value.args]
            else:
                continue
            return {
                "class": class_name,
                "init_args": init_args,
                "call_args": call_args
            }
    return {}

with open("apps.py", "r") as file:
    module = astroid.parse(file.read())

result = {}
for func in get_top_level_functions(module):
    app_name, providers = extract_key_and_dict(func)
    if app_name is None:
        continue
    app = {}
    for provider_name, provider_ref in providers.items():
        if isinstance(provider_ref, astroid.Name):
            provider_func = find_function_def(func, provider_ref.name)
            if provider_func:
                app[provider_name] = extract_function_info(provider_func)
    result[app_name] = app

with open("apps.json", "w") as file:
    json.dump(result, file, indent=4)

print("Analysis complete. Results written to apps.json")