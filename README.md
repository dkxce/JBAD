# JBAD Python JSON BAD Parser

**usage**:
- jbad.loads(...)

**like**:    
- json.loads(...)
- orjson.loads(...)
- ujson.loads(...)
- pd.read_json(...)
- msgspec.json.decode(...)

**possibilities**:    
- no quotas
- no commas
- bad strings
- bad numbers
- empty elements
- bad decimals

**SAMPLE**:
```
text = """
{
        0126: 0.15,,,
        "XXX": .501,
        YYY: +111
        'timestamp': 1556283673.1523004,
        'timestamd': -556283673.1523004,
        "GUID": "700F5226-CB78-44F4-AC7B-C857AD569FD8",
        "task_level": [1, 2, , ,, -1],
        "action_status": @"started\r\nX",
        "action_type": "main",
        "bot": {"k": "V", , , ,,, "x": "Y", "z": "Z",}
        "bot2": {"k": "V", , , ,,, "x": "Y", "z": "Z",,,}
        key: "value",
        @par: @'Empty',
        "another_key": 123,
        @"and_another": ["a", "b", "c",]
        @"get_another": ["a", "b", "c",,,]
    }
"""
obj = json.loads(text)
```
