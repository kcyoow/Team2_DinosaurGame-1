# Team2_DinosaurGame

The Chrome Dinosaur 🦖 Game in build with Pygame in Python.

# Request

---

| Method | URL           | Data Format | Description                                  |
| ------ | ------------- | ----------- | -------------------------------------------- |
| POST   | /user/v1/data | json        | push user's point data                       |
| POST   | /user/v1/info | json        | receive user's rank data in descending order |
| POST   | /user/v1/rank | json        | receive the top 5 rank points |

# Response

---

| Method | URL           | Data Format |
| ------ | ------------- | ----------- |
| POST   | /user/v1/data | json        |
| POST   | /user/v1/info | json/array  |
| POST   | /user/v1/rank | json        |

## Success Response

---

- Response Code: 200
- Content:

```yaml
/user/v1/data, /user/v1/info
{ "Message": array }
--
/user/v1/rank
{ "Args": double-dimensional array, "Count": integer, "Message": boolean }
```

## Error Response

---

- Response Code: 401 UNAUTHORIZED
- Content:

```yaml
{ "Message": "Invalid Contents." }
```

---

- Response Code: 422 UNPROCESSABLE ENTRY
- Content:

```yaml
{ "Message": "Please Check Your Data sets again." }
```
