# API

### Store logs
Store logs to a specific group:
```
POST /groups/{group}
- body: list of logs (JSON string)
```
example:
```bash
$ curl -X POST 'localhost:8080/groups/movie
  --data-raw '[
    {"title": "Terminator", "text": "I'll be back", "year": 1984, "stars": 3.9},
    {"title": "StarWars", "text": "May the Force be with You", "year": 1977, "stars": 3.9},
    {"title": "DarkKnight", "text": "Why so Serious?", "actor": "Heath Ledger", "year": 2008, "stars": 4.3},
    {"title": "StarWars", "subtitle": "The Empire Strikes Back", "text": "I Am Your Father", "year": 1980, "stars": 4.0}
  ]'
```
```
  {
    "success": true,
    "id": [
        "5e8b5903804f41da5370d843", 
        "5e8b5903804f41da5370d844", 
        "5e8b5903804f41da5370d845", 
        "5e8b5903804f41da5370d846",
    ]
  } 
```
* 'id' in response is determined automatically when inserted.

### Find logs
Find logs in a group which has a specific key-value:
```
GET /groups/{group}?{query_cond1}&{query_cond2}&...
```
{query_cond} for a specific value
```
{key}={value}       # string value
{key}:int={value}   # int value   
```
{query_cond} for a range

```
{key}=[{value1}:{value2}]       # string in [value1, value2)
{key}=[{value}:]                # string greater than or equal to value (≥ value)
{key}=[:{value2}]               # string less than value (< value)

{key}:int=[{value1}:{value2}]   # int in [value1, value2)   
{key}:int=[{value}:]            # int greater than or equal to value (≥ value)   
{key}:int=[:{value}]            # int less than value (< value)
   
{key}:float=[{value1}:{value2}] # float in [value1, value2)   
{key}:float=[{value}:]          # int greater than or equal to value (≥ value)   
{key}:float=[:{value}]          # int less than value (< value)
```
- Note that the upper and lower case letters are treated as different.
In comparing strings, the character with lower Unicode value will be considered to be smaller,
therefore the comparison results will be different from the dictionary order
if the strings contain both upper and lower case letters. 
It is recommended not to use both upper and lower case letters 
in the string-typed fields which require range searching.

example:
```bash
$ curl -X GET 'localhost:8080/groups/movie?title=StarWars
```
```
{
    "logs": [
        {
            "_id": "5e9325677efe79d511b112cc",
            "title": "StarWars",
            "text": "May the Force be with You",
            "year": 1977,
            "stars": 3.9
        },
        {
            "_id": "5e9325677efe79d511b112ce",
            "title": "StarWars",
            "subtitle": "The Empire Strikes Back",
            "text": "I Am Your Father",
            "year": 1980,
            "stars": 4
        }
    ]
}
```
```bash
$ curl -X GET 'localhost:8080/groups/movie?text=[I'll:Why]
```
```
{
    "logs": [
        {
            "_id": "5e9325677efe79d511b112cb",
            "title": "Terminator",
            "text": "I'll be back",
            "year": 1984,
            "stars": 3.9
        },
        {
            "_id": "5e9325677efe79d511b112cc",
            "title": "StarWars",
            "text": "May the Force be with You",
            "year": 1977,
            "stars": 3.9
        }
    ]
}
```
```bash
$ curl -X GET 'localhost:8080/groups/movie?year:int=1984
```
```
{
    "logs": [
        {
            "_id": "5e9325677efe79d511b112cb",
            "title": "Terminator",
            "text": "I'll be back",
            "year": 1984,
            "stars": 3.9
        }
    ]
}
```
```bash
$ curl -X GET 'localhost:8080/groups/movie?stars:float=[4.0:]
```
```
{
    "logs": [
        {
            "_id": "5e9325677efe79d511b112cd",
            "title": "DarkKnight",
            "text": "Why so Serious?",
            "actor": "Heath Ledger",
            "year": 2008,
            "stars": 4.3
        },
        {
            "_id": "5e9325677efe79d511b112ce",
            "title": "StarWars",
            "subtitle": "The Empire Strikes Back",
            "text": "I Am Your Father",
            "year": 1980,
            "stars": 4
        }
    ]
}
```
```bash
$ curl -X GET 'localhost:8080/groups/movie?text=[I:J]&stars:float=[3.8:4.2]
```
```
{
    "logs": [
        {
            "_id": "5e9325677efe79d511b112cb",
            "title": "Terminator",
            "text": "I'll be back",
            "year": 1984,
            "stars": 3.9
        },
        {
            "_id": "5e9325677efe79d511b112ce",
            "title": "StarWars",
            "subtitle": "The Empire Strikes Back",
            "text": "I Am Your Father",
            "year": 1980,
            "stars": 4
        }
    ]
}
```

* '_id' in response is determined automatically when inserted.
* You can get all logs of a group without specifying key-value, but this is not recommended when the dataset is large. 
