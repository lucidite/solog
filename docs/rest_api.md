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
    {"title": "Terminator", "text": "I'll be back"},
    {"title": "StarWars", "text": "May the Force be with You"},
    {"title": "DarkKnight", "text": "Why so Serious?", "actor": "Heath Ledger"},
    {"title": "StarWars", "text": "I Am Your Father", "note": "Darth Vader"}
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
GET /groups/{group}?{key}={value}
```
example:
```bash
$ curl -X GET 'localhost:8080/groups/movie?title=StarWars
```
```
{
  "logs": [
    {"_id": "5e8b5903804f41da5370d844, "title": "StarWars", "text": "May the Force be with You"},
    {"_id": "5e8b5903804f41da5370d846, "title": "StarWars", "text": "I Am Your Father", "note": "Darth Vader"}
}
```
* '_id' in response is determined automatically when inserted.
* You can get all logs of a group without specifying key-value, but this is not recommended when the dataset is large. 
* Only simple string key-value searching is supported currently. 