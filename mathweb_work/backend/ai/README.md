# MATH WEB AI v3

## API

- `GET /api/ai/health`
- `GET /api/ai/knowledge?grade=10`
- `GET /api/ai/knowledge/{topic_id}`
- `POST /api/ai/questions`
- `POST /api/ai/practice/session`
- `POST /api/ai/questions/{question_id}/answer`
- `POST /api/ai/battle/topics`
- `POST /api/ai/battle/create`
- `WS /api/ai/battle/ws/{battle_id}/{user_id}`

## Compatibility

`POST /api/ai/questions` accepts both the current format:

```json
{"grade":10,"topics":["xac_suat"],"count":10,"difficulty":"medium","question_type":"multiple_choice","history":[]}
```

and the older single-topic form:

```json
{"grade":10,"topic":"xac_suat","count":10}
```

## Security

Question answers and solutions stay server-side. The question API only returns public question data. The answer API reveals the correct answer and solution only after a submitted answer is checked.

The default store is in-memory with a one-hour TTL. For multiple production workers, replace it with Redis or a database-backed store.
