# oss4ai-hackathon-2024-11-16

```
python3 -m venv .venv
poetry install
poetry shell
python -m src.app
```

# Development

Get dress preview

```
curl -X POST http://127.0.0.1:5000/wearit -H "Content-Type: application/json" -d '{
           "person_path": "uploads/images/person.jpg",
           "cloth_path": "uploads/images/red_shirt.jpg",
           "category": "tops"
         }'
```
