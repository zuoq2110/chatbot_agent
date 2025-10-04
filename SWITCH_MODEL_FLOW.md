# 📋 LUỒNG HOẠT ĐỘNG CHỨC NĂNG SWITCH MODEL

## 🎯 Tổng quan

Chức năng Switch Model cho phép Admin thay đổi model AI (Ollama/Gemini) mà hệ thống sử dụng **trong runtime** mà không cần restart server.

---

## 🔄 LUỒNG HOẠT ĐỘNG CHI TIẾT

### **BƯỚC 1: Admin gọi API Select Model**

#### 1.1. Request từ Client

**Endpoint:** `POST /api/admin/models/select`

**Request Body:**

```json
{
  "model_type": "ollama",
  "model_name": "llama3.1:8b"
}
```

**Headers:**

```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

#### 1.2. Xử lý trong FastAPI

**File:** `src/backend/api/admin_model.py`

**Hàm:** `select_model()` - **Line 245-318**

```python
@router.post("/select", dependencies=[Depends(security)])
async def select_model(
    request: ModelSelectionRequest,
    admin_user: dict = Depends(get_current_admin_user)
):
```

**Chi tiết thực thi:**

**Bước 1.2.1: Xác thực Admin**

- FastAPI gọi `get_current_admin_user()` từ `src/backend/auth/dependencies.py`
- Function này check:
  - Token có hợp lệ không (JWT validation)
  - User có role "admin" không
- Nếu fail → Trả về 401/403 Unauthorized

**Bước 1.2.2: Validate Request**

```python
model_type = request.model_type.lower()
model_name = request.model_name

# Kiểm tra model_type hợp lệ
if model_type not in ["ollama", "gemini"]:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid model type: {model_type}"
    )
```

**Bước 1.2.3: Validate Model tồn tại**

- **Với Ollama:**

```python
if model_type == "ollama":
    ollama_models = await get_ollama_models()
    available_names = [m["name"] for m in ollama_models]

    if model_name not in available_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ollama model '{model_name}' not found"
        )
```

- **Với Gemini:**

```python
elif model_type == "gemini":
    gemini_models = get_gemini_models()
    available_names = [m["name"] for m in gemini_models]

    if model_name not in available_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gemini model '{model_name}' not found"
        )
```

---

### **BƯỚC 2: Set Runtime Override**

#### 2.1. Gọi ModelManager

**File:** `src/backend/api/admin_model.py` - **Line 270-277**

```python
# Set model thông qua ModelManager
if model_type == "ollama":
    model_manager.set_ollama_model(model_name)

elif model_type == "gemini":
    model_manager.set_gemini_model(model_name)
```

#### 2.2. Xử lý trong ModelManager

**File:** `src/llm/model_manager.py`

##### 2.2.1. Method `set_ollama_model()` - **Line 322-337**

```python
def set_ollama_model(self, ollama_model: str):
    """
    Set runtime override cho Ollama model.

    Args:
        ollama_model: Tên Ollama model (vd: "llama3.1:8b")
    """
    # Lưu vào biến runtime trong memory
    self._runtime_ollama_model = ollama_model
    self._runtime_model_type = ModelType.OLLAMA

    # Set active model type
    if self._runtime_model_type:
        self.set_active_model_type(ModelType.OLLAMA)

    print(f"🔄 Runtime Ollama model set to: {ollama_model}")
```

**Các biến được thay đổi:**

- `self._runtime_ollama_model = "llama3.1:8b"` (lưu tên model)
- `self._runtime_model_type = ModelType.OLLAMA` (lưu loại model)

##### 2.2.2. Method `set_gemini_model()` - **Line 339-351**

```python
def set_gemini_model(self, gemini_model: str):
    """
    Set runtime override cho Gemini model.

    Args:
        gemini_model: Tên Gemini model (vd: "gemini-1.5-pro")
    """
    # Lưu vào biến runtime trong memory
    self._runtime_gemini_model = gemini_model
    self._runtime_model_type = ModelType.GEMINI

    # Set active model type
    if self._runtime_model_type:
        self.set_active_model_type(ModelType.GEMINI)

    print(f"🔄 Runtime Gemini model set to: {gemini_model}")
```

**Các biến được thay đổi:**

- `self._runtime_gemini_model = "gemini-1.5-pro"` (lưu tên model)
- `self._runtime_model_type = ModelType.GEMINI` (lưu loại model)

#### 2.3. Singleton Pattern

**File:** `src/llm/model_manager.py` - **Line 429-439**

```python
# Tạo singleton instance
model_manager = ModelManager()
```

**Đặc điểm:**

- Chỉ có **1 instance duy nhất** của ModelManager trong toàn bộ application
- Tất cả modules import `model_manager` đều dùng chung instance này
- Runtime overrides được lưu trong memory của instance này

---

### **BƯỚC 3: Response trả về Client**

#### 3.1. Response Success

**File:** `src/backend/api/admin_model.py` - **Line 279-288**

```python
# Lấy thông tin model mới
current_type = model_manager.get_model_type()
current_info = {}

if current_type == ModelType.OLLAMA:
    ollama_info = model_manager.get_ollama_info()
    current_info = {
        "model_type": "ollama",
        "model_name": ollama_info["model"],
        "url": ollama_info["url"]
    }
elif current_type == ModelType.GEMINI:
    gemini_info = model_manager.get_gemini_info()
    current_info = {
        "model_type": "gemini",
        "model_name": gemini_info["model"],
        "api_key_configured": bool(gemini_info["api_key"])
    }

return BaseResponse(
    statusCode=status.HTTP_200_OK,
    message=f"Successfully switched to {model_type} model: {model_name}",
    data=current_info
)
```

**Response JSON:**

```json
{
  "statusCode": 200,
  "message": "Successfully switched to ollama model: llama3.1:8b",
  "data": {
    "model_type": "ollama",
    "model_name": "llama3.1:8b",
    "url": "http://localhost:11434"
  }
}
```

---

### **BƯỚC 4: Tác động đến Chat API**

#### 4.1. User gửi Chat Message

**Endpoint:** `POST /api/chat/{conversation_id}/messages`

**File:** `src/backend/api/chat.py`

#### 4.2. Chat API tạo Agent

**File:** `src/backend/api/chat.py` - **Line ~100-150**

```python
# Tạo ReAct Graph (agent)
react_graph = ReActGraph()
```

#### 4.3. Agent khởi tạo LLM

**File:** `src/agent/supervisor_agent.py`

##### 4.3.1. Summarize Node - **Line 78**

```python
def summarize_node(state: AgentState):
    # Dùng get_llm() thay vì hardcode get_gemini_llm()
    llm = get_llm()  # ✅ Tự động lấy model từ runtime override

    # ... rest of code
```

##### 4.3.2. Agent Node - **Line 136**

```python
def agent_node(state: AgentState, config: RunnableConfig):
    # Bind tools với model mới
    model_with_tools = get_llm().bind_tools(tools)  # ✅ Dùng model mới

    # ... rest of code
```

#### 4.4. LLM Factory tạo Model Instance

**File:** `src/llm/llm_factory.py`

##### 4.4.1. Method `create_llm()` - **Line 18-46**

```python
@classmethod
def create_llm(cls, callback_manager: Optional[CallbackManager] = None) -> BaseChatModel:
    """
    Tạo instance LLM dựa trên model đang hoạt động với fallback logic.
    """
    # 🔍 BƯỚC QUAN TRỌNG: Lấy loại model từ ModelManager
    model_type = model_manager.get_model_type()

    # Lấy parameters
    temperature = model_manager.get_temperature()
    max_tokens = model_manager.get_max_tokens()

    # Tạo instance tương ứng
    if model_type == ModelType.OLLAMA:
        try:
            print("🤖 Attempting to create Ollama model...")
            return cls._create_ollama_model(temperature, max_tokens, callback_manager)
        except Exception as e:
            print(f"⚠️ Ollama model failed: {e}")
            print("🔄 Falling back to Gemini model...")
            return cls._create_gemini_model(temperature, max_tokens, callback_manager)

    elif model_type == ModelType.GEMINI:
        return cls._create_gemini_model(temperature, max_tokens, callback_manager)
    else:
        return cls._create_huggingface_model(temperature, max_tokens, callback_manager)
```

##### 4.4.2. Method `get_model_type()` - **Line 353-371**

**File:** `src/llm/model_manager.py`

```python
def get_model_type(self) -> ModelType:
    """
    Lấy loại model đang hoạt động.
    Thứ tự ưu tiên:
    1. Runtime override (admin vừa chọn)
    2. Environment variable (.env)
    3. Default configuration
    """
    # 🔥 ƯU TIÊN 1: Runtime override
    if self._runtime_model_type:
        return self._runtime_model_type

    # 🔥 ƯU TIÊN 2: Environment variable
    if os.getenv("ACTIVE_MODEL_TYPE"):
        return ModelType(os.getenv("ACTIVE_MODEL_TYPE"))

    # 🔥 ƯU TIÊN 3: Database hoặc default
    active_model = self.get_active_model()
    return ModelType(active_model.get("modelType", ModelType.GEMINI))
```

##### 4.4.3. Create Ollama Model - **Line 49-65**

**File:** `src/llm/llm_factory.py`

```python
@classmethod
def _create_ollama_model(cls, temperature: float, max_tokens: int,
                        callback_manager: Optional[CallbackManager] = None) -> ChatOllama:
    """Tạo Ollama model instance."""

    # 🔍 Lấy thông tin Ollama từ ModelManager
    ollama_info = model_manager.get_ollama_info()

    print(f"🔧 Initializing Ollama LLM with model: {ollama_info['model']}")

    return ChatOllama(
        model=ollama_info["model"],  # ✅ Model name từ runtime override
        base_url=ollama_info["url"],
        temperature=temperature,
        num_predict=max_tokens,
        callback_manager=callback_manager
    )
```

##### 4.4.4. Get Ollama Info - **Line 371-394**

**File:** `src/llm/model_manager.py`

```python
def get_ollama_info(self) -> Dict[str, Any]:
    """
    Lấy thông tin Ollama (có thể là runtime override).
    """
    # 🔥 ƯU TIÊN Runtime override
    if self._runtime_ollama_model:
        return {
            "model": self._runtime_ollama_model,  # ✅ "llama3.1:8b"
            "url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }

    # Fallback về environment hoặc default
    return {
        "model": os.getenv("OLLAMA_MODEL", "llama3"),
        "url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    }
```

---

### **BƯỚC 5: LLM xử lý Chat Request**

#### 5.1. Agent invoke với Model mới

**File:** `src/agent/supervisor_agent.py` - **Line 140-160**

```python
# Invoke model với tools
response = chains.invoke({"messages": state["messages"]})

# Model mới (llama3.1:8b) xử lý request
# - Nếu cần tool → gọi tool
# - Nếu có response → trả về user
```

#### 5.2. HTTP Request đến Ollama Server

**Log:**

```
HTTP Request: POST http://127.0.0.1:11434/api/chat "HTTP/1.1 200 OK"
```

**Payload:**

```json
{
  "model": "llama3.1:8b",
  "messages": [...],
  "stream": false,
  "tools": [...]
}
```

#### 5.3. Response trả về User

**File:** `src/backend/api/chat.py`

```python
return BaseResponse(
    statusCode=200,
    message="Chat message processed successfully",
    data={
        "conversation_id": conversation_id,
        "message": agent_response,
        "timestamp": datetime.utcnow()
    }
)
```

---

## 📊 SƠ ĐỒ LUỒNG DỮ LIỆU

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. ADMIN GỌI API SELECT                       │
│  POST /api/admin/models/select                                  │
│  Body: {"model_type": "ollama", "model_name": "llama3.1:8b"}   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. FASTAPI ROUTE HANDLER                           │
│  File: src/backend/api/admin_model.py                          │
│  Function: select_model() - Line 245                           │
│  - Xác thực admin (get_current_admin_user)                     │
│  - Validate model_type và model_name                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. MODEL MANAGER - SET RUNTIME                     │
│  File: src/llm/model_manager.py                                │
│  Function: set_ollama_model() - Line 322                       │
│  OR: set_gemini_model() - Line 339                             │
│                                                                 │
│  THAY ĐỔI:                                                      │
│  - self._runtime_model_type = ModelType.OLLAMA                 │
│  - self._runtime_ollama_model = "llama3.1:8b"                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              4. RESPONSE TRẢ VỀ CLIENT                          │
│  Status: 200 OK                                                 │
│  Message: "Successfully switched to ollama model"              │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                    5. USER GỬI CHAT MESSAGE                      │
│  POST /api/chat/{conversation_id}/messages                      │
└────────────────────────────────────────────────────────────────┬┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              6. AGENT KHỞI TẠO                                  │
│  File: src/agent/supervisor_agent.py                           │
│  - summarize_node() gọi get_llm() - Line 78                    │
│  - agent_node() gọi get_llm().bind_tools() - Line 136          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. LLM FACTORY - TẠO MODEL                         │
│  File: src/llm/llm_factory.py                                  │
│  Function: create_llm() - Line 18                              │
│                                                                 │
│  LOGIC:                                                         │
│  1. model_type = model_manager.get_model_type()                │
│     → Trả về ModelType.OLLAMA (từ runtime override)            │
│                                                                 │
│  2. _create_ollama_model()                                     │
│     - Lấy info: model_manager.get_ollama_info()                │
│       → {"model": "llama3.1:8b", "url": "..."}                 │
│     - Tạo: ChatOllama(model="llama3.1:8b")                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              8. MODEL XỬ LÝ REQUEST                             │
│  HTTP POST → http://localhost:11434/api/chat                   │
│  Model: llama3.1:8b                                            │
│  - Nhận messages + tools                                       │
│  - Xử lý và trả về response                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              9. RESPONSE TRẢ VỀ USER                            │
│  Chat message với nội dung từ model mới                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 DANH SÁCH FILES LIÊN QUAN

### **Backend API**

1. **`src/backend/api/admin_model.py`**

   - Endpoint `/select` - Line 245-318
   - Endpoint `/available` - Line 181-243
   - Endpoint `/current` - Line 320-361
   - Endpoint `/test` - Line 363-401
   - Endpoint `/reset` - Line 403-429

2. **`src/backend/auth/dependencies.py`**
   - Function `get_current_admin_user()` - Line 28-59
   - Xác thực admin authentication

### **LLM Core**

3. **`src/llm/model_manager.py`**

   - Class `ModelManager` - Line 18-428
   - Method `set_ollama_model()` - Line 322-337
   - Method `set_gemini_model()` - Line 339-351
   - Method `get_model_type()` - Line 353-371
   - Method `get_ollama_info()` - Line 371-394
   - Method `get_gemini_info()` - Line 396-413
   - Method `clear_runtime_overrides()` - Line 415-426
   - Singleton instance - Line 429-439

4. **`src/llm/llm_factory.py`**

   - Class `LLMFactory` - Line 13-92
   - Method `create_llm()` - Line 18-46
   - Method `_create_ollama_model()` - Line 49-65
   - Method `_create_gemini_model()` - Line 67-85
   - Method `_create_huggingface_model()` - Line 87-92

5. **`src/llm/config.py`**
   - Function `get_llm()` - Wrapper cho LLMFactory.create_llm()

### **Agent**

6. **`src/agent/supervisor_agent.py`**
   - Function `summarize_node()` - Line 62-102
     - Gọi `get_llm()` - Line 78
   - Function `agent_node()` - Line 104-193
     - Gọi `get_llm().bind_tools()` - Line 136

### **Configuration**

7. **`.env`**
   - `ACTIVE_MODEL_TYPE=gemini` - Default model type
   - `OLLAMA_BASE_URL=http://localhost:11434`
   - `GOOGLE_API_KEY=...`

---

## 🔑 CÁC BIẾN RUNTIME QUAN TRỌNG

### **Trong ModelManager Singleton Instance**

```python
# Private variables lưu runtime override
self._runtime_model_type: Optional[ModelType] = None
self._runtime_ollama_model: Optional[str] = None
self._runtime_gemini_model: Optional[str] = None

# Ví dụ sau khi select Ollama:
self._runtime_model_type = ModelType.OLLAMA
self._runtime_ollama_model = "llama3.1:8b"
self._runtime_gemini_model = None
```

### **Thứ tự ưu tiên khi lấy model:**

1. **Runtime Override** (memory) - Cao nhất
2. **Environment Variable** (.env file)
3. **Default Configuration** (hardcoded)

---

## 🧪 TEST FLOW

### **Test 1: Select Ollama Model**

```powershell
$body = @{
    model_type = "ollama"
    model_name = "llama3.1:8b"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/admin/models/select" -Method POST -Headers @{"Authorization"="Bearer TOKEN"; "Content-Type"="application/json"} -Body $body
```

**Kỳ vọng:**

- Runtime override được set
- Response 200 OK với thông tin model mới

### **Test 2: Verify Current Model**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/admin/models/current" -Method GET -Headers @{"Authorization"="Bearer TOKEN"}
```

**Kỳ vọng:**

```json
{
  "model_type": "ollama",
  "model_name": "llama3.1:8b"
}
```

### **Test 3: Chat với Model mới**

```powershell
$body = @{
    message = "Hello, what model are you?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/chat/CONVERSATION_ID/messages" -Method POST -Headers @{"Authorization"="Bearer TOKEN"; "Content-Type"="application/json"} -Body $body
```

**Kỳ vọng:**

- Log hiển thị: `Initializing Ollama LLM with model: llama3.1:8b`
- Response từ Ollama model

### **Test 4: Reset về Default**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/admin/models/reset" -Method POST -Headers @{"Authorization"="Bearer TOKEN"}
```

**Kỳ vọng:**

- Runtime overrides bị xóa
- Quay về model từ .env: `ACTIVE_MODEL_TYPE=gemini`

---

## 🎨 ƯU ĐIỂM THIẾT KẾ

### **1. Runtime Switching**

- ✅ Không cần restart server
- ✅ Thay đổi tức thì
- ✅ Zero downtime

### **2. Singleton Pattern**

- ✅ Chỉ 1 instance ModelManager
- ✅ State được share toàn hệ thống
- ✅ Thread-safe

### **3. Priority Logic**

- ✅ Runtime override > Environment > Default
- ✅ Linh hoạt cho nhiều scenarios
- ✅ Dễ debug và maintain

### **4. Fallback Mechanism**

- ✅ Ollama fail → Auto switch Gemini
- ✅ Đảm bảo service availability
- ✅ Graceful degradation

### **5. Separation of Concerns**

- ✅ API Layer: admin_model.py
- ✅ Business Logic: model_manager.py
- ✅ Factory Pattern: llm_factory.py
- ✅ Agent Layer: supervisor_agent.py

---

## 📝 GHI CHÚ QUAN TRỌNG

### **Hạn chế:**

1. Runtime override **chỉ lưu trong memory**

   - Restart server → Mất override
   - Quay về .env configuration

2. Một số Ollama models **không hỗ trợ tools**

   - Ví dụ: qwen:1.8b
   - Cần dùng: llama3.1:8b, llama3.2, qwen2.5:7b

3. **Không có persistent storage**

   - Không lưu vào database
   - Không lưu vào file

4. ⚠️ **RACE CONDITION - NHIỀU ADMIN CONFLICT**
   - **Vấn đề nghiêm trọng:** Nếu có nhiều admin cùng thay đổi model
   - ModelManager singleton **KHÔNG thread-safe**
   - Admin A chọn Ollama → Admin B chọn Gemini → Override lẫn nhau
   - Last-write-wins: Admin cuối cùng thắng, admin trước bị ghi đè
   - Không có lock mechanism để đồng bộ
   - **Chi tiết:** Xem phần "VẤN ĐỀ RACE CONDITION & GIẢI PHÁP" bên dưới

---

## ⚠️ VẤN ĐỀ RACE CONDITION & GIẢI PHÁP

### **🔴 RACE CONDITION CHI TIẾT:**

#### **Scenario 1: Last-Write-Wins (Ghi đè)**

```
Timeline:
10:00:00 - Admin A: select_model(ollama, llama3.1)
          → _runtime_model_type = OLLAMA
          → _runtime_ollama_model = "llama3.1:8b"

10:00:05 - Admin B: select_model(gemini, gemini-1.5-pro)
          → _runtime_model_type = GEMINI ❌ GHI ĐÈ
          → _runtime_gemini_model = "gemini-1.5-pro"

10:00:10 - User chat request
          → Dùng Gemini (Admin B thắng)
          → Admin A không biết model đã bị đổi
```

#### **Scenario 2: Partial Override (Không nhất quán)**

```
Timeline:
10:00:00 - Admin A: set_ollama_model("llama3.1:8b")
          → _runtime_model_type = OLLAMA
          → _runtime_ollama_model = "llama3.1:8b"

10:00:01 - Admin B: set_gemini_model("gemini-pro") (đồng thời)
          → _runtime_model_type = GEMINI ❌ GHI ĐÈ
          → _runtime_gemini_model = "gemini-pro"
          → _runtime_ollama_model vẫn còn "llama3.1:8b" ⚠️

Kết quả: State không nhất quán
```

#### **Scenario 3: Read-After-Write Issue**

```
Timeline:
Admin A:
10:00:00 - GET /current → {"model": "ollama"}
10:00:01 - Hiển thị UI: "Current: Ollama"

Admin B:
10:00:02 - POST /select → Switch to Gemini

10:00:03 - Admin A chat (nghĩ đang dùng Ollama)
          → Thực tế đang dùng Gemini ❌
```

### **💡 GIẢI PHÁP ĐỀ XUẤT:**

#### **Solution 1: Threading Lock (Đơn giản - Single Server)**

```python
# File: src/llm/model_manager.py
import threading

class ModelManager:
    def __init__(self):
        self._lock = threading.Lock()
        # ... existing code

    def set_ollama_model(self, ollama_model: str):
        with self._lock:  # Thread-safe
            self._runtime_ollama_model = ollama_model
            self._runtime_model_type = ModelType.OLLAMA
```

**Ưu điểm:** ✅ Đơn giản, ✅ Thread-safe
**Nhược điểm:** ❌ Không work với multiple servers

#### **Solution 2: Redis Distributed Lock (Production)**

```python
# File: src/llm/model_manager.py
import redis

class ModelManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)

    def set_ollama_model(self, ollama_model: str):
        lock = self.redis.lock("model_switch_lock", timeout=10)

        if lock.acquire(blocking=True):
            try:
                # Store in Redis (persistent + distributed)
                self.redis.hset("runtime_config", {
                    "model_type": "ollama",
                    "ollama_model": ollama_model
                })
            finally:
                lock.release()
```

**Ưu điểm:** ✅ Multi-server, ✅ Persistent, ✅ Distributed
**Nhược điểm:** ❌ Cần Redis

#### **Solution 3: Database with Transactions**

```python
# File: src/llm/model_manager.py
async def set_ollama_model(self, ollama_model: str, admin_id: str):
    async with mongodb.client.start_session() as session:
        async with session.start_transaction():
            # Deactivate all configs
            await mongodb.db.model_config.update_many(
                {"active": True},
                {"$set": {"active": False}},
                session=session
            )

            # Insert new config
            await mongodb.db.model_config.insert_one({
                "model_type": "ollama",
                "ollama_model": ollama_model,
                "changed_by": admin_id,
                "changed_at": datetime.utcnow(),
                "active": True
            }, session=session)
```

**Ưu điểm:** ✅ Persistent, ✅ Audit trail, ✅ Atomic
**Nhược điểm:** ❌ Complex, ❌ Slower

#### **Solution 4: WebSocket Notifications**

```python
# File: src/backend/api/admin_model.py
from fastapi import WebSocket

class ModelSwitchNotifier:
    def __init__(self):
        self.connections = set()

    async def broadcast(self, message: dict):
        for ws in self.connections:
            await ws.send_json(message)

@router.post("/select")
async def select_model(...):
    # ... set model

    # Notify all admins
    await notifier.broadcast({
        "type": "model_switch",
        "model": model_name,
        "by": admin_user["username"]
    })
```

**Ưu điểm:** ✅ Real-time notification
**Nhược điểm:** ❌ Không ngăn conflict

### **🎯 KHUYẾN NGHỊ:**

| Môi trường                             | Giải pháp đề xuất                                          | Lý do                                    |
| -------------------------------------- | ---------------------------------------------------------- | ---------------------------------------- |
| **Single Server + Last-Write-Wins OK** | Solution 3 (DB Audit) + Solution 4 (WebSocket)             | Không cần lock, chỉ cần notify + history |
| **Single Server + Muốn ngăn conflict** | Solution 1 (Lock) + Solution 3 (DB) + Solution 4 (Notify)  | Lock để đồng bộ, DB để audit             |
| **Production/Multi-server**            | Solution 2 (Redis) + Solution 3 (DB) + Solution 4 (Notify) | Redis lock distributed                   |

### **⚠️ LƯU Ý QUAN TRỌNG:**

**Nếu bạn chấp nhận "last-write-wins" (model mới nhất thắng):**

- ✅ Hệ thống hiện tại **HOẠT ĐỘNG ĐÚNG**
- ✅ Admin sau sẽ override admin trước
- ❌ Vấn đề là: **Không có notification** và **không có audit log**

**→ Giải pháp:** Chỉ cần thêm **Database Audit Trail + WebSocket Notification**

### **📊 So sánh chi tiết:**

| Tiêu chí         | Lock | Redis | Database | WebSocket |
| ---------------- | ---- | ----- | -------- | --------- |
| Thread-safe      | ✅   | ✅    | ✅       | ❌        |
| Multi-server     | ❌   | ✅    | ✅       | ✅        |
| Persistent       | ❌   | ✅    | ✅       | ❌        |
| Audit Trail      | ❌   | ⚠️    | ✅       | ❌        |
| Real-time Notify | ❌   | ❌    | ❌       | ✅        |
| Complexity       | ⭐   | ⭐⭐  | ⭐⭐⭐   | ⭐⭐      |

---

### **Cải tiến có thể thực hiện:**

1. **[CRITICAL]** Implement lock mechanism (Solution 1 hoặc 2)
2. **[HIGH]** Add WebSocket notification cho admins (Solution 4)
3. Add validation cho tool support
4. Add model performance metrics
5. Implement A/B testing giữa models
6. Add cost tracking (Gemini API cost)
7. **[MEDIUM]** Store config history trong database (audit trail)

---

## 📚 TÀI LIỆU THAM KHẢO

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Google Gemini API](https://ai.google.dev/docs)
