# 🚀 Hướng dẫn tích hợp React với Admin Model API

## 📋 Tổng quan

API admin đã sẵn sàng tại `src/backend/api/admin_model.py` với các endpoints:

- `GET /admin/models/available` - Lấy danh sách models
- `POST /admin/models/select` - Chọn model
- `GET /admin/models/current` - Xem model hiện tại
- `POST /admin/models/test` - Test model
- `POST /admin/models/reset` - Reset về mặc định

## 🔧 1. Service Layer (services/adminModelService.js)

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

  // Lấy danh sách models từ Ollama và Gemini
  async getAvailableModels() {
    try {
      const response = await fetch(`${this.baseURL}/available`, {
        method: "GET",
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to fetch models:", error);
      throw error;
    }
  }

  // Chọn model (Ollama hoặc Gemini)
  async selectModel(modelType, modelName) {
    try {
      const response = await fetch(`${this.baseURL}/select`, {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({
          model_type: modelType,
          model_name: modelName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to select model:", error);
      throw error;
    }
  }

  // Lấy model hiện tại
  async getCurrentModel() {
    try {
      const response = await fetch(`${this.baseURL}/current`, {
        method: "GET",
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to get current model:", error);
      throw error;
    }
  }

  // Test model
  async testModel(modelType, modelName, testMessage = "Hello, test message") {
    try {
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
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to test model:", error);
      throw error;
    }
  }

  // Reset về mặc định
  async resetToDefault() {
    try {
      const response = await fetch(`${this.baseURL}/reset`, {
        method: "POST",
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to reset models:", error);
      throw error;
    }
  }
}

export default new AdminModelService();
```

## 🎨 2. React Component (components/AdminModelManager.jsx)

```jsx
import React, { useState, useEffect } from "react";
import adminModelService from "../services/adminModelService";
import "./AdminModelManager.css";

const AdminModelManager = () => {
  const [models, setModels] = useState({
    ollama_models: [],
    gemini_models: [],
    current_active: {},
  });
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(null);
  const [error, setError] = useState(null);

  // Load models khi component mount
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminModelService.getAvailableModels();
      setModels(data);
    } catch (error) {
      setError(`Không thể tải danh sách models: ${error.message}`);
    }
    setLoading(false);
  };

  const handleSelectModel = async (modelType, modelName) => {
    setLoading(true);
    setError(null);
    try {
      await adminModelService.selectModel(modelType, modelName);
      await loadModels(); // Reload để cập nhật current model
      alert(`✅ Đã chọn ${modelType} model: ${modelName}`);
    } catch (error) {
      setError(`Không thể chọn model: ${error.message}`);
    }
    setLoading(false);
  };

  const handleTestModel = async (modelType, modelName) => {
    setTesting(`${modelType}:${modelName}`);
    setError(null);
    try {
      const result = await adminModelService.testModel(
        modelType,
        modelName,
        "Xin chào, bạn có thể giới thiệu về mình được không?"
      );

      if (result.data.success) {
        alert(
          `✅ Test thành công!\n\nResponse: ${result.data.response.substring(
            0,
            150
          )}...`
        );
      } else {
        alert(`❌ Test thất bại: ${result.data.error}`);
      }
    } catch (error) {
      setError(`Test model thất bại: ${error.message}`);
    }
    setTesting(null);
  };

  const handleReset = async () => {
    if (!window.confirm("Bạn có chắc muốn reset về cấu hình mặc định?")) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await adminModelService.resetToDefault();
      await loadModels();
      alert("✅ Đã reset về cấu hình mặc định!");
    } catch (error) {
      setError(`Không thể reset: ${error.message}`);
    }
    setLoading(false);
  };

  if (loading && !models.ollama_models.length) {
    return (
      <div className="admin-model-manager">
        <div className="loading">🔄 Đang tải danh sách models...</div>
      </div>
    );
  }

  return (
    <div className="admin-model-manager">
      <div className="header">
        <h2>🤖 Quản lý Models</h2>
        <button onClick={loadModels} disabled={loading} className="refresh-btn">
          🔄 Làm mới
        </button>
      </div>

      {error && <div className="error-message">❌ {error}</div>}

      {/* Current Model */}
      <div className="current-model">
        <h3>📍 Model hiện tại</h3>
        <div className="model-info">
          <span className="model-type">{models.current_active.model_type}</span>
          <span className="model-name">{models.current_active.model_name}</span>
        </div>
        <button onClick={handleReset} disabled={loading} className="reset-btn">
          🔄 Reset về mặc định
        </button>
      </div>

      {/* Ollama Models */}
      <div className="model-section">
        <h3>🦙 Ollama Models ({models.ollama_models.length})</h3>
        {models.ollama_models.length === 0 ? (
          <div className="no-models">
            <p>Không có model Ollama nào được pull.</p>
            <p>
              Chạy: <code>ollama pull llama3.2</code>
            </p>
          </div>
        ) : (
          <div className="model-grid">
            {models.ollama_models.map((model) => (
              <ModelCard
                key={model.name}
                model={model}
                modelType="ollama"
                isActive={
                  models.current_active.model_type === "ollama" &&
                  models.current_active.model_name === model.name
                }
                onSelect={() => handleSelectModel("ollama", model.name)}
                onTest={() => handleTestModel("ollama", model.name)}
                loading={loading}
                testing={testing === `ollama:${model.name}`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Gemini Models */}
      <div className="model-section">
        <h3>🤖 Gemini Models</h3>
        <div className="model-grid">
          {models.gemini_models.map((model) => (
            <ModelCard
              key={model.name}
              model={model}
              modelType="gemini"
              isActive={
                models.current_active.model_type === "gemini" &&
                models.current_active.model_name === model.name
              }
              onSelect={() => handleSelectModel("gemini", model.name)}
              onTest={() => handleTestModel("gemini", model.name)}
              loading={loading}
              testing={testing === `gemini:${model.name}`}
            />
          ))}
        </div>
      </div>

      {loading && <div className="loading-overlay">🔄 Đang xử lý...</div>}
    </div>
  );
};

// Component con cho từng model card
const ModelCard = ({
  model,
  modelType,
  isActive,
  onSelect,
  onTest,
  loading,
  testing,
}) => {
  return (
    <div className={`model-card ${isActive ? "active" : ""}`}>
      <div className="model-header">
        <h4>{model.display_name || model.name}</h4>
        {model.size && <span className="model-size">{model.size}</span>}
      </div>

      {model.description && (
        <p className="model-description">{model.description}</p>
      )}

      <div className="model-actions">
        <button
          onClick={onSelect}
          disabled={loading || isActive}
          className={`select-btn ${isActive ? "active" : ""}`}
        >
          {isActive ? "✅ Đang dùng" : "🔄 Chọn"}
        </button>

        <button
          onClick={onTest}
          disabled={loading || testing}
          className="test-btn"
        >
          {testing ? "🧪 Testing..." : "🧪 Test"}
        </button>
      </div>
    </div>
  );
};

export default AdminModelManager;
```

## 🎨 3. CSS Styling (components/AdminModelManager.css)

```css
.admin-model-manager {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e1e5e9;
}

.refresh-btn {
  padding: 8px 16px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: #e9ecef;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
}

.current-model {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.current-model h3 {
  margin: 0 0 15px 0;
}

.model-info {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
}

.model-type {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  text-transform: uppercase;
  font-weight: 600;
}

.model-name {
  font-size: 1.1em;
  font-weight: 500;
}

.reset-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.model-section {
  margin-bottom: 40px;
}

.model-section h3 {
  margin-bottom: 20px;
  color: #495057;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.model-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  position: relative;
}

.model-card:hover {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.model-card.active {
  border-color: #28a745;
  background: #f8fff9;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.model-header h4 {
  margin: 0;
  color: #343a40;
  font-size: 1.1em;
}

.model-size {
  background: #e9ecef;
  color: #6c757d;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.model-description {
  color: #6c757d;
  font-size: 0.9em;
  margin: 10px 0;
  line-height: 1.4;
}

.model-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.select-btn,
.test-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.select-btn {
  background: #007bff;
  color: white;
}

.select-btn:hover {
  background: #0056b3;
}

.select-btn.active {
  background: #28a745;
}

.select-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.test-btn {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
}

.test-btn:hover {
  background: #e9ecef;
}

.no-models {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.no-models code {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "Monaco", "Menlo", monospace;
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
  z-index: 1000;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #6c757d;
}

@media (max-width: 768px) {
  .model-grid {
    grid-template-columns: 1fr;
  }

  .header {
    flex-direction: column;
    gap: 15px;
  }

  .model-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
```

## 🔧 4. Environment Variables (.env hoặc .env.local)

```env
REACT_APP_API_URL=http://localhost:3434
```

## 🚀 5. Sử dụng trong App

```jsx
// App.js hoặc AdminPage.js
import AdminModelManager from "./components/AdminModelManager";

function AdminPage() {
  return (
    <div className="admin-page">
      <h1>Admin Dashboard</h1>
      <AdminModelManager />
    </div>
  );
}

export default AdminPage;
```

## 📝 6. Chạy hệ thống

### Backend:

```bash
cd e:\My_Project\AI\ChatBot\chatbot_agent
python -m src.backend.main
```

### React Frontend:

```bash
npm install
npm start
```

## ✅ 7. Kết quả

Admin sẽ có giao diện để:

- ✅ Xem tất cả models Ollama đã pull
- ✅ Xem danh sách models Gemini có sẵn
- ✅ Chọn model bất kỳ cho hệ thống
- ✅ Test model trước khi switch
- ✅ Reset về cấu hình mặc định
- ✅ Real-time updates không cần restart server

**Hệ thống sẽ tự động fallback về Gemini nếu Ollama không khả dụng! 🎉**
