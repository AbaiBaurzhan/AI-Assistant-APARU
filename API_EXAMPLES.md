# Примеры API запросов

## 🔍 Поиск ответов в FAQ

### Запрос

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Как заказать такси?"
  }'
```

### Ответ (высокая уверенность ≥0.8)

```json
{
  "reply": "Откройте приложение и нажмите кнопку 'Заказ'",
  "confidence": 0.85,
  "source": "q001",
  "similar_questions": []
}
```

### Ответ (средняя уверенность 0.6-0.8)

```json
{
  "reply": "Уточните, пожалуйста, ваш вопрос. Возможно, вы имели в виду:",
  "confidence": 0.72,
  "source": null,
  "similar_questions": [
    "Как заказать такси?",
    "Как вызвать машину?",
    "Как забронировать поездку?"
  ]
}
```

### Ответ (низкая уверенность <0.6)

```json
{
  "reply": "Не понял вопрос, передаю оператору",
  "confidence": 0.45,
  "source": null,
  "similar_questions": []
}
```

## 👍 Обратная связь

### Запрос

```bash
curl -X POST "http://localhost:8000/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Как заказать такси?",
    "answer_id": "q001",
    "feedback": "👍"
  }'
```

### Ответ

```json
{
  "status": "success",
  "message": "Спасибо за обратную связь!"
}
```

## 🏥 Health Check

### Запрос

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

### Ответ

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## 📚 JavaScript/TypeScript примеры

### Axios

```javascript
import axios from 'axios';

const FAQ_API_BASE = 'http://localhost:8000/api/v1';

// Поиск ответа
async function askQuestion(question) {
  try {
    const response = await axios.post(`${FAQ_API_BASE}/ask`, {
      query: question
    });

    const { reply, confidence, source, similar_questions } = response.data;

    if (confidence >= 0.8) {
      // Показать готовый ответ
      return { type: 'answer', reply, source };
    } else if (confidence >= 0.6) {
      // Показать похожие вопросы
      return { type: 'clarify', reply, similar_questions };
    } else {
      // Передать оператору
      return { type: 'operator' };
    }
  } catch (error) {
    console.error('FAQ API error:', error);
    return { type: 'operator' }; // Fallback на оператора
  }
}

// Отправка обратной связи
async function sendFeedback(query, answerId, feedback) {
  try {
    await axios.post(`${FAQ_API_BASE}/feedback`, {
      query,
      answer_id: answerId,
      feedback
    });
  } catch (error) {
    console.error('Feedback error:', error);
  }
}
```

### Fetch API

```javascript
// Поиск ответа
async function askQuestion(question) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: question })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('FAQ API error:', error);
    return { type: 'operator' };
  }
}
```

## 🐍 Python примеры

### Requests

```python
import requests
import asyncio
import aiohttp

# Синхронный запрос
def ask_question(question: str) -> dict:
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/ask',
            json={'query': question},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"FAQ API error: {e}")
        return {'type': 'operator'}

# Асинхронный запрос
async def ask_question_async(question: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8000/api/v1/ask',
                json={'query': question},
                timeout=5
            ) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"FAQ API error: {e}")
        return {'type': 'operator'}

# Отправка обратной связи
def send_feedback(query: str, answer_id: str, feedback: str) -> bool:
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/feedback',
            json={
                'query': query,
                'answer_id': answer_id,
                'feedback': feedback
            },
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Feedback error: {e}")
        return False
```

## 🦀 Rust примеры

```rust
use reqwest;
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();

    // Поиск ответа
    let response = client
        .post("http://localhost:8000/api/v1/ask")
        .json(&json!({
            "query": "Как заказать такси?"
        }))
        .send()
        .await?;

    let faq_response: serde_json::Value = response.json().await?;
    println!("FAQ Response: {}", faq_response);

    Ok(())
}
```

## 📱 Интеграция в чат

### Логика принятия решений

```javascript
async function handleUserMessage(message) {
  // Показываем индикатор загрузки
  showLoadingIndicator();

  try {
    // Вызываем FAQ API
    const faqResponse = await askQuestion(message);

    if (faqResponse.confidence >= 0.8) {
      // Высокая уверенность - показываем автоответ
      showAutoAnswer(faqResponse.reply, faqResponse.source);
      addFeedbackButtons(message, faqResponse.source);
    } else if (faqResponse.confidence >= 0.6) {
      // Средняя уверенность - просим уточнить
      showClarificationRequest(faqResponse.reply, faqResponse.similar_questions);
    } else {
      // Низкая уверенность - передаем оператору
      transferToOperator(message);
    }
  } catch (error) {
    // При ошибке API передаем оператору
    console.error('FAQ service error:', error);
    transferToOperator(message);
  } finally {
    hideLoadingIndicator();
  }
}
```

## 🔧 Настройка таймаутов

```javascript
// Настройка HTTP клиента
const FAQ_CLIENT = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 5000, // 5 секунд
  headers: {
    'Content-Type': 'application/json'
  }
});

// Retry логика
async function askQuestionWithRetry(question, maxRetries = 2) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await FAQ_CLIENT.post('/ask', { query: question });
      return response.data;
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error; // Последняя попытка
      }
      await new Promise(resolve => setTimeout(resolve, 1000)); // Ждем 1 сек
    }
  }
}
