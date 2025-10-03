# Admin Model Management API Documentation

## Tổng quan

API này cung cấp các endpoint để admin quản lý models Ollama và Gemini cho hệ thống chatbot. API hỗ trợ:

- 🦙 **Lấy danh sách models Ollama thực tế** đã được pull từ `ollama list`
- 🤖 **Xem danh sách models Gemini** có sẵn từ Google AI
- ⚡ **Chọn bất kỳ model nào** từ danh sách để sử dụng (runtime switching)
- 🧪 **Test kết nối** đến model cụ thể trước khi sử dụng
- 🛡️ **Fallback tự động** từ Ollama về Gemini khi Ollama không khả dụng
- 🔄 **Không cần restart server** khi chuyển đổi model

## Base URL

```
http://localhost:3434/admin/models
```

## Authentication

Tất cả endpoints yêu cầu Bearer token trong header:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### 1. GET `/available` - Lấy danh sách models có sẵn

**Response:**

```json
{
  "ollama_models": [
    {
      "name": "llama3.2:latest",
      "size": "4.7GB",
      "modified": "2024-01-15T10:30:00Z",
      "digest": "sha256:...",
      "details": {}
    },
    {
      "name": "qwen2.5:7b",
      "size": "4.2GB",
      "modified": "2024-01-14T09:20:00Z",
      "digest": "sha256:...",
      "details": {}
    }
  ],
  "gemini_models": [
    {
      "name": "gemini-2.0-flash",
      "display_name": "Gemini 2.0 Flash",
      "description": "Latest Gemini model with improved performance",
      "supported_generation_methods": [
        "generateContent",
        "streamGenerateContent"
      ]
    }
  ],
  "current_active": {
    "model_type": "ollama",
    "model_name": "llama3.2:latest",
    "url": "http://localhost:11434"
  }
}
```

### 2. POST `/select` - Chọn model để sử dụng

**Request Body:**

```json
{
  "model_type": "ollama", // hoặc "gemini"
  "model_name": "llama3.2:latest" // Tên chính xác từ danh sách available models
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully selected ollama model: qwen3:8b",
  "data": {
    "model_type": "ollama",
    "model_name": "qwen3:8b",
    "timestamp": "now"
  }
}
```

### 3. GET `/current` - Lấy thông tin model hiện tại

**Response:**

```json
{
  "success": true,
  "message": "Current model information",
  "data": {
    "model_type": "ollama",
    "model_name": "qwen3:8b",
    "url": "http://localhost:11434",
    "timestamp": "now"
  }
}
```

### 4. POST `/test` - Test kết nối model

**Request Body:**

```json
{
  "model_type": "ollama",
  "model_name": "qwen3:8b",
  "test_message": "Hello, test message"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Model test successful for ollama:qwen3:8b",
  "data": {
    "success": true,
    "response": "Hello! I'm an AI assistant...",
    "model_type": "ollama",
    "model_name": "qwen3:8b"
  }
}
```

### 5. POST `/reset` - Reset về cấu hình mặc định

**Response:**

```json
{
  "success": true,
  "message": "Successfully reset to default model configuration",
  "data": {
    "message": "All runtime overrides cleared",
    "timestamp": "now"
  }
}
```

## React Frontend Integration

### 1. Service Layer

Tạo file `services/adminModelService.js`:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:3434";

class AdminModelService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/admin/models`;
  }

  // Get auth headers
  getHeaders() {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    };
  }

  // Get available models
  async getAvailableModels() {
    const response = await fetch(`${this.baseURL}/available`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`);
    }

    return response.json();
  }

  // Select a model
  async selectModel(modelType, modelName) {
    const response = await fetch(`${this.baseURL}/select`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        model_type: modelType,
        model_name: modelName,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to select model: ${response.statusText}`);
    }

    return response.json();
  }

  // Get current model
  async getCurrentModel() {
    const response = await fetch(`${this.baseURL}/current`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get current model: ${response.statusText}`);
    }

    return response.json();
  }

  // Test model connection
  async testModel(modelType, modelName, testMessage = "Hello world") {
    const response = await fetch(`${this.baseURL}/test`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        model_type: modelType,
        model_name: modelName,
        test_message: testMessage,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to test model: ${response.statusText}`);
    }

    return response.json();
  }

  // Reset to default
  async resetToDefault() {
    const response = await fetch(`${this.baseURL}/reset`, {
      method: "POST",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to reset models: ${response.statusText}`);
    }

    return response.json();
  }
}

export default new AdminModelService();
```

### 2. React Component Example

```jsx
import React, { useState, useEffect } from "react";
import adminModelService from "../services/adminModelService";

const AdminModelManager = () => {
  const [models, setModels] = useState({
    ollama_models: [],
    gemini_models: [],
    current_active: {},
  });
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [selectedModel, setSelectedModel] = useState({ type: "", name: "" });

  // Load available models
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await adminModelService.getAvailableModels();
      setModels(data);
    } catch (error) {
      console.error("Failed to load models:", error);
      alert("Không thể tải danh sách models");
    }
    setLoading(false);
  };

  const handleSelectModel = async (modelType, modelName) => {
    setLoading(true);
    try {
      await adminModelService.selectModel(modelType, modelName);
      alert("Chọn model thành công!");
      loadModels(); // Reload to get updated current model
    } catch (error) {
      console.error("Failed to select model:", error);
      alert("Không thể chọn model");
    }
    setLoading(false);
  };

  const handleTestModel = async (modelType, modelName) => {
    setTesting(true);
    try {
      const result = await adminModelService.testModel(
        modelType,
        modelName,
        "Xin chào, bạn có thể giới thiệu về mình được không?"
      );

      if (result.data.success) {
        alert(
          `Test thành công!\nResponse: ${result.data.response.substring(
            0,
            100
          )}...`
        );
      } else {
        alert(`Test thất bại: ${result.data.error}`);
      }
    } catch (error) {
      console.error("Failed to test model:", error);
      alert("Không thể test model");
    }
    setTesting(false);
  };

  const handleReset = async () => {
    if (confirm("Bạn có chắc muốn reset về cấu hình mặc định?")) {
      setLoading(true);
      try {
        await adminModelService.resetToDefault();
        alert("Reset thành công!");
        loadModels();
      } catch (error) {
        console.error("Failed to reset:", error);
        alert("Không thể reset");
      }
      setLoading(false);
    }
  };

  if (loading && !models.ollama_models.length) {
    return <div>Đang tải...</div>;
  }

  return (
    <div className="admin-model-manager">
      <h2>Quản lý Models</h2>

      {/* Current Model */}
      <div className="current-model">
        <h3>Model hiện tại</h3>
        <p>
          <strong>{models.current_active.model_type}:</strong>{" "}
          {models.current_active.model_name}
        </p>
        <button onClick={handleReset} disabled={loading}>
          Reset về mặc định
        </button>
      </div>

      {/* Ollama Models */}
      <div className="ollama-models">
        <h3>Ollama Models ({models.ollama_models.length})</h3>
        {models.ollama_models.length === 0 ? (
          <p>Không có model Ollama nào được pull</p>
        ) : (
          <div className="model-list">
            {models.ollama_models.map((model) => (
              <div key={model.name} className="model-item">
                <div>
                  <strong>{model.name}</strong>
                  <span>({model.size})</span>
                </div>
                <div>
                  <button
                    onClick={() => handleSelectModel("ollama", model.name)}
                    disabled={loading}
                    className={
                      models.current_active.model_type === "ollama" &&
                      models.current_active.model_name === model.name
                        ? "active"
                        : ""
                    }
                  >
                    Chọn
                  </button>
                  <button
                    onClick={() => handleTestModel("ollama", model.name)}
                    disabled={testing}
                  >
                    Test
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Gemini Models */}
      <div className="gemini-models">
        <h3>Gemini Models</h3>
        <div className="model-list">
          {models.gemini_models.map((model) => (
            <div key={model.name} className="model-item">
              <div>
                <strong>{model.display_name}</strong>
                <p>{model.description}</p>
              </div>
              <div>
                <button
                  onClick={() => handleSelectModel("gemini", model.name)}
                  disabled={loading}
                  className={
                    models.current_active.model_type === "gemini" &&
                    models.current_active.model_name === model.name
                      ? "active"
                      : ""
                  }
                >
                  Chọn
                </button>
                <button
                  onClick={() => handleTestModel("gemini", model.name)}
                  disabled={testing}
                >
                  Test
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {loading && <div className="loading-overlay">Đang xử lý...</div>}
    </div>
  );
};

export default AdminModelManager;
```

### 3. CSS Styling Example

```css
.admin-model-manager {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.current-model {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.model-list {
  display: grid;
  gap: 10px;
}

.model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
}

.model-item button {
  margin-left: 10px;
  padding: 5px 15px;
  border: 1px solid #007bff;
  background: white;
  color: #007bff;
  border-radius: 3px;
  cursor: pointer;
}

.model-item button:hover {
  background: #007bff;
  color: white;
}

.model-item button.active {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.model-item button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}
```

## Testing

1. Chạy server backend:

```bash
cd e:\My_Project\AI\ChatBot\chatbot_agent
python -m src.backend.main
```

2. Test API:

```bash
python test_admin_model_api.py
```

## Lưu ý

1. **Fallback Logic**: Khi chọn Ollama model nhưng Ollama không khả dụng, hệ thống sẽ tự động fallback về Gemini
2. **Runtime Override**: Model selection chỉ có hiệu lực trong phiên làm việc hiện tại, không lưu vào database
3. **Authentication**: Tất cả endpoints yêu cầu admin authentication
4. **Error Handling**: Luôn wrap API calls trong try-catch để xử lý lỗi gracefully
5. **Environment Variables**: Đảm bảo có `GOOGLE_API_KEY` và `OLLAMA_BASE_URL` trong .env
