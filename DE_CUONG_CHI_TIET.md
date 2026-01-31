# ĐỀ CƯƠNG CHI TIẾT ĐỒ ÁN TỐT NGHIỆP

## **ĐỀ TÀI: XÂY DỰNG HỆ THỐNG CHATBOT PHỤC VỤ TRY VẤN ĐIỂM VÀ TÀI LIỆU NỘI BỘ SỬ DỤNG LLM VÀ GRAPH RAG**

---

## I. MỞ ĐẦU

### 1. Tính cấp thiết của đề tài

#### Bối cảnh thực tế và nhu cầu xã hội

**a) Thực trạng giáo dục đại học và nhu cầu tiếp cận thông tin tại Việt Nam**

Theo số liệu của Bộ Giáo dục và Đào tạo, tính đến năm 2025, Việt Nam có hơn 240 trường đại học và cao đẳng với tổng số sinh viên đang theo học vượt mức 2 triệu người. Trong bối cảnh quy mô đào tạo ngày càng mở rộng, các cơ sở giáo dục đại học đang đối mặt với áp lực lớn trong việc cung cấp thông tin và hỗ trợ sinh viên một cách kịp thời, chính xác.

Tại Học viện Kỹ thuật Mật mã nói riêng và các trường đại học Việt Nam nói chung, mỗi năm học, các phòng ban chức năng như Phòng Đào tạo, Phòng Khảo thí phải tiếp nhận và xử lý hàng chục nghìn lượt câu hỏi từ sinh viên về các vấn đề: tra cứu điểm thi, quy chế đào tạo, thủ tục hành chính, lịch thi, đăng ký học phần, và các tài liệu nội bộ khác. Theo khảo sát sơ bộ, khoảng **60-70% các câu hỏi có tính chất lặp lại** và có thể được trả lời tự động nếu có hệ thống hỗ trợ phù hợp.

**b) Những bất cập và thách thức hiện nay**

Thực trạng hỗ trợ sinh viên tại các cơ sở giáo dục đại học Việt Nam đang tồn tại nhiều bất cập nghiêm trọng:

- **Sự quá tải tại các phòng ban chức năng:**

  - Nhân viên phải trả lời lặp đi lặp lại các câu hỏi tương tự (tra cứu điểm, hỏi lịch thi, thủ tục đăng ký, quy chế công tác...), gây lãng phí thời gian và nguồn lực con người.
  - Sinh viên phải chờ đợi từ vài giờ đến vài ngày để được giải đáp thắc mắc, đặc biệt trong các mùa cao điểm như đầu năm học, kỳ đăng ký học phần, mùa thi cuối kỳ.
  - Giảng viên và cán bộ nhân viên cũng gặp khó khăn khi cần tra cứu nhanh các quy chế, quy định nội bộ phục vụ công tác giảng dạy và quản lý.
  - Tình trạng xếp hàng dài tại các phòng ban vào giờ hành chính gây ảnh hưởng đến việc học tập của sinh viên và công việc của cán bộ.

- **Rào cản tiếp cận thông tin:**

  - Tài liệu nội bộ (quy chế, quy định, hướng dẫn, biểu mẫu) thường được lưu trữ phân tán trên nhiều hệ thống khác nhau: website trường, portal sinh viên, hệ thống văn bản nội bộ, email thông báo...
  - Thiếu hệ thống tìm kiếm thông minh khiến sinh viên, giảng viên và cán bộ khó khăn trong việc tìm đúng thông tin cần thiết trong khối lượng văn bản lớn và phức tạp.
  - Nhiều quy chế, quy định được cập nhật hàng năm nhưng người dùng (sinh viên, giảng viên, cán bộ) không nắm được phiên bản mới nhất.
  - Giảng viên cần tra cứu quy chế đào tạo, quy định thi cử để hướng dẫn sinh viên nhưng thiếu công cụ hỗ trợ nhanh chóng.
  - Cán bộ nhân viên cần nắm vững các quy trình, biểu mẫu để thực hiện công việc nhưng phải tìm kiếm thủ công.

- **Thiếu kênh hỗ trợ 24/7:**

  - Nhu cầu tra cứu thông tin của sinh viên không giới hạn trong giờ hành chính (7h30-17h00), đặc biệt vào buổi tối và cuối tuần khi sinh viên có thời gian tự học.
  - Giảng viên thường cần tra cứu quy chế, quy định vào buổi tối hoặc cuối tuần khi chuẩn bị bài giảng, chấm thi hoặc hướng dẫn sinh viên.
  - Sinh viên ở xa, sinh viên quốc tế (nếu có) gặp khó khăn do chênh lệch múi giờ hoặc khoảng cách địa lý.
  - Cán bộ nhân viên đôi khi cần tra cứu thông tin ngoài giờ làm việc để chuẩn bị công việc.

- **Chất lượng thông tin không đồng nhất:**
  - Thông tin truyền miệng giữa các sinh viên, hoặc giữa các đồng nghiệp có thể bị sai lệch, lỗi thời.
  - Các nhóm mạng xã hội (Facebook, Zalo) tuy phổ biến nhưng thiếu tính chính thống và không được kiểm soát nội dung.
  - Giảng viên mới hoặc cán bộ mới thiếu nguồn tham khảo chính thống về quy chế, quy trình làm việc.

**c) Thực trạng ứng dụng công nghệ hỗ trợ sinh viên trên thế giới**

Trên thế giới, việc ứng dụng công nghệ AI và Chatbot trong giáo dục đã trở thành xu hướng tất yếu:

- **Tại Hoa Kỳ:** Georgia Institute of Technology đã triển khai thành công **Jill Watson** - một trợ lý ảo dựa trên IBM Watson từ năm 2016, giúp trả lời hàng nghìn câu hỏi của sinh viên mỗi học kỳ với độ chính xác lên tới 97%. Nhiều trường đại học như Arizona State University, University of Michigan đã tích hợp chatbot vào hệ thống hỗ trợ sinh viên.

- **Tại Châu Âu:** Các trường đại học tại Anh, Đức, Hà Lan đã triển khai hệ thống chatbot hỗ trợ tuyển sinh, đăng ký môn học và giải đáp thắc mắc hành chính. Theo nghiên cứu của EDUCAUSE (2024), **hơn 60% các trường đại học hàng đầu châu Âu** đã hoặc đang triển khai một hình thức chatbot hỗ trợ sinh viên.

- **Tại Châu Á:** Singapore, Hàn Quốc, Nhật Bản là những quốc gia tiên phong trong việc ứng dụng AI vào giáo dục. National University of Singapore (NUS) đã triển khai hệ thống chatbot tích hợp với Learning Management System (LMS) để hỗ trợ sinh viên 24/7.

**d) Thực trạng tại Việt Nam**

Tại Việt Nam, chuyển đổi số giáo dục đang được Chính phủ và Bộ Giáo dục & Đào tạo thúc đẩy mạnh mẽ thông qua Đề án "Tăng cường ứng dụng công nghệ thông tin và chuyển đổi số trong giáo dục và đào tạo giai đoạn 2022-2025, định hướng đến năm 2030". Tuy nhiên, thực tế triển khai còn nhiều hạn chế:

- Đa số các trường đại học mới dừng ở mức **số hóa quy trình hành chính** (đăng ký trực tuyến, tra cứu điểm online) mà thiếu các công cụ hỗ trợ thông minh.
- Một số trường đã thử nghiệm chatbot đơn giản (rule-based) nhưng **khả năng hiểu ngữ cảnh kém**, chỉ trả lời được các câu hỏi cố định theo kịch bản.
- Chưa có hệ thống chatbot nào tại Việt Nam tích hợp **Graph RAG** để truy vấn thông tin có cấu trúc phức tạp như điểm số, quy chế đào tạo một cách thông minh.
- Vấn đề **xử lý ngôn ngữ tự nhiên tiếng Việt** trong lĩnh vực giáo dục còn nhiều thách thức do thiếu dữ liệu huấn luyện chuyên ngành.

**e) Khoảng trống nghiên cứu và cơ hội**

Từ phân tích thực trạng trên, có thể nhận thấy một **khoảng trống lớn** giữa nhu cầu thực tế của sinh viên và khả năng đáp ứng của các hệ thống hiện có:

| Nhu cầu thực tế                          | Giải pháp hiện tại                  | Khoảng trống                 |
| ---------------------------------------- | ----------------------------------- | ---------------------------- |
| Tra cứu thông tin 24/7                   | Chỉ hỗ trợ trong giờ hành chính     | Thiếu kênh tự động           |
| Hỏi đáp bằng ngôn ngữ tự nhiên           | FAQ cứng nhắc hoặc tìm kiếm từ khóa | Không hiểu ngữ cảnh          |
| Tra cứu thông tin đa nguồn               | Tài liệu phân tán                   | Không tổng hợp được          |
| Truy vấn có cấu trúc (điểm theo môn, HK) | Chỉ hiển thị bảng điểm              | Không trả lời câu hỏi cụ thể |
| GV tra cứu quy chế phục vụ giảng dạy     | Tự tìm trong hệ thống văn bản       | Mất thời gian, khó tìm       |
| CB tra cứu quy trình, biểu mẫu           | Hỏi đồng nghiệp hoặc tìm thủ công   | Không chính xác, chậm        |

Đây chính là cơ hội để nghiên cứu và phát triển một hệ thống chatbot thông minh, tích hợp công nghệ LLM và Graph RAG hiện đại, phù hợp với bối cảnh giáo dục đại học Việt Nam.

#### Xu hướng ứng dụng AI và LLM trong giáo dục

Trên thế giới, việc ứng dụng các mô hình ngôn ngữ lớn (Large Language Models - LLM) như GPT, Gemini, LLaMA trong lĩnh vực giáo dục đang trở thành xu hướng tất yếu. Đặc biệt, kỹ thuật **Retrieval-Augmented Generation (RAG)** đã chứng minh hiệu quả trong việc xây dựng các hệ thống chatbot có khả năng trả lời chính xác dựa trên nguồn tri thức cụ thể, giảm thiểu hiện tượng "hallucination" (ảo giác) của LLM.

Tại Việt Nam, chuyển đổi số giáo dục đang được Bộ Giáo dục và Đào tạo khuyến khích mạnh mẽ. Tuy nhiên, đa số các cơ sở giáo dục vẫn thiếu các công cụ hỗ trợ sinh viên thông minh, đặc biệt là hệ thống chatbot có khả năng hiểu ngữ cảnh và truy vấn thông tin chính xác.

#### Lý do sử dụng Graph RAG

Kỹ thuật RAG truyền thống (Vector RAG) tuy hiệu quả nhưng còn hạn chế trong việc:

- Hiểu mối quan hệ ngữ nghĩa giữa các khái niệm
- Truy vấn thông tin có cấu trúc phức tạp (như điểm số theo môn học, học kỳ, sinh viên)
- Tổng hợp thông tin từ nhiều nguồn tài liệu liên quan

**Graph RAG** (kết hợp Knowledge Graph với RAG) khắc phục các hạn chế trên bằng cách:

- Biểu diễn tri thức dưới dạng đồ thị với các thực thể và mối quan hệ
- Hỗ trợ truy vấn đa bước (multi-hop reasoning)
- Phân loại và định tuyến câu hỏi theo ngữ nghĩa đến đúng nguồn tri thức

Xuất phát từ những lý do trên, việc nghiên cứu và thực hiện đề tài **"Xây dựng hệ thống Chatbot phục vụ truy vấn điểm và tài liệu nội bộ sử dụng LLM và Graph RAG"** là vô cùng cấp thiết. Đề tài không chỉ giải quyết bài toán hỗ trợ sinh viên hiệu quả mà còn mang lại giá trị thực tiễn cao trong việc tối ưu hóa quy trình làm việc của các phòng ban chức năng trong cơ sở giáo dục.

---

### 2. Mục tiêu nghiên cứu của đề tài

Xây dựng thành công hệ thống Chatbot thông minh tích hợp mô hình ngôn ngữ lớn (LLM) và kỹ thuật Graph RAG, phục vụ việc truy vấn điểm số và tài liệu nội bộ tại Học viện Kỹ thuật Mật mã, đồng thời tối ưu hóa trải nghiệm người dùng và giảm tải cho các phòng ban chức năng.

#### Mục tiêu cụ thể:

**a) Về mặt khoa học:**

- **Nghiên cứu và ứng dụng Large Language Models (LLM):**

  - Tìm hiểu và triển khai các mô hình LLM tiên tiến (Gemini, GPT, Ollama/Qwen) cho tác vụ hội thoại và trả lời câu hỏi.
  - Nghiên cứu kỹ thuật Prompt Engineering để tối ưu hóa chất lượng phản hồi của LLM.
  - Xây dựng cơ chế Agent/ReAct để LLM có khả năng sử dụng công cụ và truy vấn dữ liệu.

- **Nghiên cứu và ứng dụng Graph RAG:**

  - Xây dựng Knowledge Graph từ tài liệu nội bộ với các thực thể (Entity) và mối quan hệ (Relationship).
  - Nghiên cứu kỹ thuật phân vùng đồ thị (Graph Partitioning) theo phòng ban/chủ đề.
  - Phát triển thuật toán Semantic Department Detection để định tuyến câu hỏi đến đúng nguồn tri thức.
  - Kết hợp Vector Embedding với Graph Structure để truy xuất thông tin chính xác.

- **Nghiên cứu kỹ thuật xử lý ngôn ngữ tự nhiên tiếng Việt:**
  - Xử lý văn bản tiếng Việt: Tách từ, chuẩn hóa, nhận dạng thực thể.
  - Tối ưu hóa embedding cho ngữ cảnh tiếng Việt trong lĩnh vực giáo dục.

**b) Về mặt thực tiễn:**

- **Xây dựng hệ thống Backend API:** Phát triển RESTful API với FastAPI, hỗ trợ xác thực đa vai trò (sinh viên, giảng viên, cán bộ, quản trị viên), tích hợp Rate Limiting và JWT Authentication.

- **Xây dựng ứng dụng Web:** Giao diện responsive, tương thích đa trình duyệt với các chức năng: Chat với Chatbot AI, tra cứu điểm (sinh viên), tra cứu quy chế/quy định, tra cứu biểu mẫu, quản lý tài liệu (admin).

- **Xây dựng ứng dụng Mobile (Android/iOS):** Phát triển bằng React Native hoặc Flutter với đầy đủ tính năng như Web, hỗ trợ Push Notification và chế độ offline.

- **Xây dựng Knowledge Base đa phòng ban:** Tổ chức tri thức theo phòng ban (Đào tạo, Khảo thí, Viện NC...), hỗ trợ đa định dạng (Markdown, PDF, Word), tự động cập nhật Knowledge Graph.

- **Triển khai Chatbot thông minh đa đối tượng:**

  - _Sinh viên:_ Tra cứu điểm, quy chế đào tạo, lịch thi, thủ tục hành chính.
  - _Giảng viên:_ Tra cứu quy chế để hướng dẫn sinh viên, quy định chấm thi, biểu mẫu.
  - _Cán bộ:_ Tra cứu quy trình nghiệp vụ, văn bản nội bộ, mẫu văn bản hành chính.

- **Đánh giá trải nghiệm người dùng:** Thời gian phản hồi < 5 giây, độ chính xác > 85%, giao diện thân thiện cho cả 3 nhóm đối tượng.

---

### 3. Đối tượng và phạm vi nghiên cứu

#### Đối tượng nghiên cứu:

- **Các mô hình ngôn ngữ lớn (LLM):**

  - Google Gemini (gemini-2.0-flash): LLM chính sử dụng qua API.
  - Ollama với Qwen 2.5 (3B): LLM local cho môi trường offline hoặc tiết kiệm chi phí.

- **Công nghệ OCR (Optical Character Recognition):**

  - Trích xuất văn bản từ tài liệu scan, hình ảnh.
  - Hỗ trợ xử lý các định dạng PDF dạng ảnh, tài liệu cũ chưa được số hóa.

- **Kỹ thuật Graph RAG:**

  - Knowledge Graph Construction từ văn bản.
  - Graph-based Retrieval và Multi-hop Reasoning.
  - Semantic Search kết hợp Graph Traversal.

- **Dữ liệu nội bộ cơ sở giáo dục:**

  - Tài liệu quy chế, quy định của các phòng ban.
  - Dữ liệu điểm số sinh viên (dạng mô phỏng/giả lập).
  - Hướng dẫn thực hành, giáo trình điện tử.

- **Hệ thống phần mềm:**
  - Kiến trúc Backend API với FastAPI.
  - Hệ thống lưu trữ Vector Database (FAISS).
  - Cơ sở dữ liệu quan hệ và đồ thị.

#### Phạm vi nghiên cứu:

**Phạm vi về nội dung:**

- Hệ thống tập trung phục vụ truy vấn thông tin của các phòng ban: Phòng Đào tạo, Phòng Khảo thí, Viện Nghiên cứu và Hợp tác Phát triển.
- Hỗ trợ trả lời các câu hỏi về: Quy chế đào tạo, tra cứu điểm, lịch thi, hướng dẫn thủ tục hành chính.

**Phạm vi về dữ liệu:**

- Sử dụng tài liệu nội bộ thực tế của Học viện Kỹ thuật Mật mã (đã được chuẩn hóa).
- Dữ liệu điểm số được mô phỏng để đảm bảo tính bảo mật.
- Giới hạn xử lý văn bản tiếng Việt.

**Phạm vi về công nghệ:**

- Sử dụng các LLM có sẵn (Gemini, Ollama) thông qua API, không tự huấn luyện mô hình mới.
- Xây dựng ứng dụng dưới dạng Web API với khả năng tích hợp vào các hệ thống khác.

**Phạm vi về không gian và thời gian:**

- Hệ thống xây dựng dựa trên mô hình chatbot phục vụ môi trường giáo dục đại học.
- Triển khai thử nghiệm tại Học viện Kỹ thuật Mật mã.

---

### 4. Các nhiệm vụ chính cần thực hiện

Nội dung nghiên cứu được tập trung vào các nội dung chính như sau:

- Nghiên cứu cơ sở lý thuyết về Large Language Models (LLM), kỹ thuật RAG, Graph RAG và Knowledge Graph.
- Thu thập tài liệu nội bộ từ các phòng ban và thực hiện tiền xử lý dữ liệu (trích xuất nội dung, OCR, chunking, metadata extraction, chuẩn hóa định dạng).
- Thiết kế schema và xây dựng Knowledge Graph theo cấu trúc phòng ban (Department-based Graph Partitioning).
- Xây dựng hệ thống Graph RAG với Vector Store (FAISS), Graph Retriever và Semantic Department Detector.
- Tích hợp các LLM providers (Gemini, Ollama/Qwen) và xây dựng hệ thống Agent (ReAct Agent, Supervisor Agent).
- Phát triển Backend API với FastAPI, triển khai Authentication (JWT) và Rate Limiting.
- Phân tích và thiết kế hệ thống (giao diện Web, Mobile, Dashboard quản trị).
- Triển khai ứng dụng trên môi trường production với Docker.
- Kiểm thử, đánh giá hiệu năng và độ chính xác của hệ thống.

---

### 5. Kết quả dự kiến

#### Lý thuyết:

- Nắm vững kiến thức về Large Language Models, RAG và Graph RAG.
- Hiểu rõ kiến trúc và cách hoạt động của Knowledge Graph trong bài toán Q&A.
- Thành thạo các kỹ thuật Prompt Engineering và Agent Design Pattern.
- Sử dụng thành thạo các thư viện và framework: LangChain, LangGraph, FastAPI, FAISS, NetworkX.

#### Thực nghiệm:

Hệ thống có các chức năng sau:

- **Chức năng Chatbot:**

  - Trả lời câu hỏi về quy chế, quy định của các phòng ban.
  - Tra cứu thông tin điểm số (mô phỏng).
  - Hỗ trợ hội thoại đa lượt (multi-turn conversation).
  - Cung cấp nguồn trích dẫn cho câu trả lời.

- **Chức năng quản lý tri thức:**

  - Upload và xử lý tài liệu mới.
  - Tự động cập nhật Knowledge Graph.
  - Quản lý tài liệu theo phòng ban.

- **Chức năng hệ thống:**
  - API RESTful cho tích hợp với các hệ thống khác.
  - Dashboard quản trị (tùy chọn).
  - Logging và monitoring.

---

## LỜI CẢM ƠN

## LỜI NÓI ĐẦU

## DANH MỤC KÝ HIỆU VÀ CHỮ VIẾT TẮT

| Ký hiệu | Giải nghĩa                                                         |
| ------- | ------------------------------------------------------------------ |
| LLM     | Large Language Model - Mô hình ngôn ngữ lớn                        |
| RAG     | Retrieval-Augmented Generation - Sinh văn bản tăng cường truy xuất |
| NLP     | Natural Language Processing - Xử lý ngôn ngữ tự nhiên              |
| API     | Application Programming Interface - Giao diện lập trình ứng dụng   |
| FAISS   | Facebook AI Similarity Search                                      |
| KG      | Knowledge Graph - Đồ thị tri thức                                  |
| AI      | Artificial Intelligence - Trí tuệ nhân tạo                         |
| Q&A     | Question and Answering - Hỏi đáp                                   |
| REST    | Representational State Transfer                                    |
| JWT     | JSON Web Token                                                     |

## DANH MỤC HÌNH VẼ

## DANH MỤC BẢNG BIỂU

---

## CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

### 1.1. Khảo sát hệ thống Chatbot hỗ trợ sinh viên hiện có

#### 1.1.1. Các hệ thống Chatbot giáo dục trên thế giới

- Georgia Tech's Jill Watson (IBM Watson)
- Duolingo Chatbot
- Carnegie Learning's AI Tutoring Systems

#### 1.1.2. Các hệ thống Chatbot tại Việt Nam

- Chatbot hỗ trợ tuyển sinh các trường đại học
- Hệ thống FAQ tự động

#### 1.1.3. Đánh giá ưu nhược điểm và định hướng phát triển

### 1.2. Tìm hiểu về Large Language Models (LLM)

#### 1.2.1. Khái niệm về LLM

- Định nghĩa và lịch sử phát triển
- Kiến trúc Transformer
- Pre-training và Fine-tuning

#### 1.2.2. Các mô hình LLM phổ biến

- GPT Series (OpenAI)
- Gemini (Google)
- LLaMA, Qwen (Open-source)
- So sánh ưu nhược điểm

#### 1.2.3. Kỹ thuật Prompt Engineering

- Zero-shot, Few-shot Learning
- Chain-of-Thought Prompting
- System Prompts và Role-playing

#### 1.2.4. Hạn chế của LLM và giải pháp

- Hallucination problem
- Knowledge cutoff
- Context window limitation

### 1.3. Tìm hiểu về Retrieval-Augmented Generation (RAG)

#### 1.3.1. Tổng quan về RAG

- Khái niệm và kiến trúc
- Quy trình hoạt động: Retrieve → Augment → Generate
- Ưu điểm so với Fine-tuning

#### 1.3.2. Vector RAG truyền thống

- Text Embedding và Vector Similarity Search
- Chunking strategies
- Vector Databases: FAISS, Chroma, Pinecone

#### 1.3.3. Graph RAG

- Khái niệm Knowledge Graph
- Kết hợp Graph Structure với Vector Embedding
- Multi-hop Reasoning
- Ưu điểm so với Vector RAG

#### 1.3.4. Các kỹ thuật nâng cao trong RAG

- Hybrid Search (BM25 + Vector)
- Re-ranking
- Query Transformation
- Self-RAG

### 1.4. Tìm hiểu về Knowledge Graph

#### 1.4.1. Khái niệm và cấu trúc

- Entities, Relationships, Properties
- Ontology và Schema Design
- RDF và Property Graph Model

#### 1.4.2. Xây dựng Knowledge Graph từ văn bản

- Named Entity Recognition (NER)
- Relation Extraction
- Entity Linking

#### 1.4.3. Graph Database và Query Language

- Neo4j và Cypher
- NetworkX cho Python
- Graph Traversal Algorithms

### 1.5. Tìm hiểu về Agent và Multi-Agent Systems

#### 1.5.1. Khái niệm AI Agent

- Định nghĩa Agent trong AI
- Perception → Decision → Action Loop
- Tool Use và Function Calling

#### 1.5.2. ReAct Pattern

- Reasoning + Acting
- Thought → Action → Observation Loop
- Ứng dụng trong Chatbot

#### 1.5.3. Multi-Agent Architecture

- Supervisor Agent Pattern
- Agent Communication
- Task Decomposition

### 1.6. Một số công cụ và công nghệ sử dụng

#### 1.6.1. Ngôn ngữ lập trình Python

- Python 3.10+
- Asyncio cho lập trình bất đồng bộ

#### 1.6.2. Các thư viện và Framework AI

- LangChain: Framework xây dựng ứng dụng LLM
- LangGraph: Xây dựng Agent workflows
- Sentence Transformers: Text Embedding
- FAISS: Vector Similarity Search

#### 1.6.3. Framework Backend

- FastAPI: Web framework hiệu năng cao
- Pydantic: Data validation
- SQLAlchemy: ORM

#### 1.6.4. Công cụ phát triển

- VS Code: IDE
- Docker: Containerization
- Git: Version control

#### 1.6.5. Hệ quản trị cơ sở dữ liệu

- MongoDB: Document database
- FAISS: Vector store
- Neo4j/NetworkX: Graph database

### 1.7. Tổng kết chương 1

---

## CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG CHATBOT TRY VẤN ĐIỂM VÀ TÀI LIỆU

### 2.1. Phân tích hệ thống

#### 2.1.1. Phân tích yêu cầu

- Khảo sát nhu cầu người dùng (sinh viên, giảng viên, cán bộ nhân viên)
- Thu thập và phân loại các câu hỏi thường gặp theo từng nhóm đối tượng
- Xác định các nguồn tài liệu cần tích hợp cho từng phòng ban

#### 2.1.2. Yêu cầu chức năng

**Nhóm chức năng dành cho Sinh viên:**
| STT | Chức năng | Mô tả |
|-----|-----------|-------|
| 1 | Chat với Chatbot | Đặt câu hỏi bằng ngôn ngữ tự nhiên |
| 2 | Tra cứu điểm | Xem điểm các môn học, điểm tích lũy |
| 3 | Tra cứu quy chế | Tìm hiểu quy định đào tạo, thi cử |
| 4 | Xem lịch sử chat | Truy cập các cuộc hội thoại trước |

**Nhóm chức năng dành cho Giảng viên:**
| STT | Chức năng | Mô tả |
|-----|-----------|-------|
| 1 | Chat với Chatbot | Đặt câu hỏi bằng ngôn ngữ tự nhiên |
| 2 | Tra cứu quy chế đào tạo | Tìm hiểu quy định để hướng dẫn sinh viên |
| 3 | Tra cứu quy định thi cử | Nắm vững quy chế chấm thi, coi thi |
| 4 | Tra cứu biểu mẫu | Tìm các mẫu đơn, báo cáo cần thiết |

**Nhóm chức năng dành cho Cán bộ nhân viên:**
| STT | Chức năng | Mô tả |
|-----|-----------|-------|
| 1 | Chat với Chatbot | Đặt câu hỏi bằng ngôn ngữ tự nhiên |
| 2 | Tra cứu quy trình công tác | Tìm hiểu các quy trình nghiệp vụ |
| 3 | Tra cứu văn bản nội bộ | Tìm kiếm quyết định, thông báo, hướng dẫn |
| 4 | Tra cứu biểu mẫu | Tìm các mẫu văn bản hành chính |

**Nhóm chức năng dành cho Quản trị viên:**
| STT | Chức năng | Mô tả |
|-----|-----------|-------|
| 1 | Quản lý tài liệu | Upload, cập nhật, xóa tài liệu |
| 2 | Quản lý Knowledge Base | Cấu hình phòng ban, cập nhật KG |
| 3 | Xem thống kê | Theo dõi số lượng câu hỏi, hiệu suất |
| 4 | Cấu hình hệ thống | Thiết lập LLM, RAG parameters |

#### 2.1.3. Yêu cầu phi chức năng

- **Hiệu năng:** Thời gian phản hồi < 5 giây
- **Độ chính xác:** > 85% câu trả lời đúng với ngữ cảnh
- **Khả năng mở rộng:** Hỗ trợ đa phòng ban, đa nguồn dữ liệu
- **Bảo mật:** Xác thực JWT, mã hóa dữ liệu nhạy cảm
- **Khả dụng:** Uptime > 99%

#### 2.1.4. Usecase tổng quát

- Biểu đồ Usecase cho Sinh viên
- Biểu đồ Usecase cho Quản trị viên
- Mô tả chi tiết các Usecase chính

#### 2.1.5. Biểu đồ hoạt động

- Quy trình Chat với Chatbot
- Quy trình Tra cứu điểm
- Quy trình Upload tài liệu và cập nhật Knowledge Graph

### 2.2. Thiết kế hệ thống

#### 2.2.1. Thiết kế kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Web App    │  │  Mobile App  │  │   API Client │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Nginx (Load Balancer, Rate Limiting, SSL)           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend                          │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │   │
│  │  │ Auth API   │ │  Chat API  │ │ Document   │        │   │
│  │  │            │ │            │ │ API        │        │   │
│  │  └────────────┘ └────────────┘ └────────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI/ML LAYER                             │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │ Supervisor     │  │  Graph RAG     │                     │
│  │ Agent          │  │  Engine        │                     │
│  │ ┌────────────┐ │  │ ┌────────────┐ │                     │
│  │ │ ReAct Agent│ │  │ │ Retriever  │ │                     │
│  │ └────────────┘ │  │ └────────────┘ │                     │
│  │ ┌────────────┐ │  │ ┌────────────┐ │                     │
│  │ │ Tool Agent │ │  │ │ Dept.      │ │                     │
│  │ └────────────┘ │  │ │ Detector   │ │                     │
│  └────────────────┘  │ └────────────┘ │                     │
│                      └────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  MongoDB   │  │   FAISS    │  │ Department │             │
│  │  (User,    │  │  (Vector   │  │ Graphs     │             │
│  │   Logs)    │  │   Store)   │  │ (JSON/Neo4j│             │
│  └────────────┘  └────────────┘  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  Gemini    │  │  Ollama    │  │  OpenAI    │             │
│  │  API       │  │  (Local)   │  │  API       │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.2.2. Thiết kế kiến trúc Graph RAG

```
┌─────────────────────────────────────────────────────────────┐
│                    GRAPH RAG PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

    User Query
        │
        ▼
┌───────────────────┐
│ Semantic Department│
│ Detector          │ ──► Xác định phòng ban liên quan
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Department Graph  │
│ Manager           │ ──► Load graph tương ứng
└───────────────────┘
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
┌───────────────────┐            ┌───────────────────┐
│ Vector Retriever  │            │ Graph Retriever   │
│ (Semantic Search) │            │ (Graph Traversal) │
└───────────────────┘            └───────────────────┘
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
              ┌───────────────────┐
              │ Result Fusion &   │
              │ Re-ranking        │
              └───────────────────┘
                       │
                       ▼
              ┌───────────────────┐
              │ Context Builder   │
              └───────────────────┘
                       │
                       ▼
              ┌───────────────────┐
              │ LLM Generation    │
              └───────────────────┘
                       │
                       ▼
                  Response
```

#### 2.2.3. Thiết kế cơ sở dữ liệu

**a) Schema MongoDB - User Collection:**

```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "role": "enum[student, admin]",
  "student_id": "string",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

**b) Schema MongoDB - Conversation Collection:**

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "messages": [
    {
      "role": "enum[user, assistant]",
      "content": "string",
      "timestamp": "datetime",
      "sources": ["string"]
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**c) Schema Knowledge Graph - Department Graph:**

```json
{
  "department_id": "phongdaotao",
  "department_name": "Phòng Đào tạo",
  "nodes": [
    {
      "id": "node_1",
      "type": "Document",
      "title": "Quy chế đào tạo 2025",
      "content": "...",
      "embedding": [0.1, 0.2, ...],
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "node_1",
      "target": "node_2",
      "relationship": "REFERENCES",
      "weight": 0.8
    }
  ]
}
```

#### 2.2.4. Thiết kế API Endpoints

| Method | Endpoint              | Mô tả                    |
| ------ | --------------------- | ------------------------ |
| POST   | /api/auth/login       | Đăng nhập                |
| POST   | /api/auth/register    | Đăng ký tài khoản        |
| POST   | /api/chat             | Gửi tin nhắn cho chatbot |
| GET    | /api/chat/history     | Lấy lịch sử chat         |
| POST   | /api/documents/upload | Upload tài liệu mới      |
| GET    | /api/documents        | Danh sách tài liệu       |
| POST   | /api/graph/rebuild    | Rebuild Knowledge Graph  |
| GET    | /api/stats            | Thống kê hệ thống        |

#### 2.2.5. Thiết kế giao diện người dùng

- Mockup giao diện Chat
- Mockup giao diện Dashboard quản trị
- Mockup giao diện Upload tài liệu

### 2.3. Tổng kết chương 2

---

## CHƯƠNG 3. XÂY DỰNG HỆ THỐNG GRAPH RAG VÀ TÍCH HỢP LLM

### 3.1. Thu thập và Tiền xử lý dữ liệu

#### 3.1.1. Thu thập tài liệu

- Danh sách nguồn tài liệu từ các phòng ban
- Định dạng tài liệu: Markdown, PDF, Word
- Quy trình số hóa và chuẩn hóa

#### 3.1.2. Trích xuất nội dung (Document Extraction)

- Sử dụng Docling/Unstructured cho PDF parsing
- Markdown parsing với metadata extraction
- Xử lý bảng biểu và hình ảnh

#### 3.1.3. Chunking Strategy

- Semantic Chunking vs Fixed-size Chunking
- Table-aware Chunking cho bảng điểm
- Overlap và context preservation

#### 3.1.4. Metadata Extraction

- Tự động trích xuất: Tiêu đề, phòng ban, ngày ban hành
- Named Entity Recognition cho văn bản tiếng Việt
- Cấu hình metadata theo loại tài liệu

### 3.2. Xây dựng Knowledge Graph

#### 3.2.1. Thiết kế Schema Knowledge Graph

- Entity Types: Document, Topic, Regulation, Term
- Relationship Types: CONTAINS, REFERENCES, RELATES_TO
- Property Design cho mỗi entity type

#### 3.2.2. Graph Construction Pipeline

```python
# Pseudocode
def build_knowledge_graph(documents):
    graph = Graph()

    for doc in documents:
        # 1. Extract entities
        entities = extract_entities(doc)

        # 2. Create nodes
        for entity in entities:
            graph.add_node(entity)

        # 3. Extract relationships
        relationships = extract_relationships(doc, entities)

        # 4. Create edges
        for rel in relationships:
            graph.add_edge(rel.source, rel.target, rel.type)

    # 5. Compute embeddings
    graph.compute_embeddings()

    return graph
```

#### 3.2.3. Department-based Graph Partitioning

- Phân vùng theo cấu trúc phòng ban
- Common Graph cho thông tin dùng chung
- Cross-department linking

#### 3.2.4. Graph Storage và Indexing

- JSON-based storage cho đơn giản
- FAISS indexing cho vector search
- Graph indexing cho traversal queries

### 3.3. Xây dựng hệ thống Retrieval

#### 3.3.1. Semantic Department Detection

- Embedding-based classification
- Keyword matching fallback
- Confidence scoring

```python
class SemanticDepartmentDetector:
    def detect(self, query: str) -> List[DepartmentMatch]:
        # 1. Encode query
        query_embedding = self.encoder.encode(query)

        # 2. Compare with department embeddings
        scores = cosine_similarity(query_embedding, self.dept_embeddings)

        # 3. Return ranked departments
        return self.rank_departments(scores)
```

#### 3.3.2. Graph Retriever

- Subgraph extraction based on query
- Multi-hop traversal for related content
- Score aggregation from multiple paths

#### 3.3.3. Hybrid Retrieval

- Kết hợp Vector Search và Graph Traversal
- Re-ranking với Cross-encoder
- Diversity-aware selection

### 3.4. Tích hợp Large Language Models

#### 3.4.1. LLM Factory Pattern

- Abstraction layer cho multiple LLM providers
- Configuration-based model selection
- Fallback mechanism

```python
class LLMFactory:
    @staticmethod
    def create(provider: str, config: dict) -> BaseLLM:
        if provider == "gemini":
            return GeminiLLM(config)
        elif provider == "ollama":
            return OllamaLLM(config)
        elif provider == "openai":
            return OpenAILLM(config)
```

#### 3.4.2. Prompt Templates

- System Prompt cho context setting
- RAG Prompt với retrieved documents
- Few-shot examples cho tiếng Việt

#### 3.4.3. Token Management

- Token counting cho context window
- Dynamic context truncation
- Cost optimization

### 3.5. Xây dựng Agent System

#### 3.5.1. ReAct Agent Implementation

- State management với LangGraph
- Tool definitions (RAG Tool, Calculator, etc.)
- Observation → Thought → Action loop

#### 3.5.2. Supervisor Agent

- Multi-agent coordination
- Task routing logic
- Result aggregation

#### 3.5.3. Conversation Memory

- Short-term memory (current session)
- Long-term memory (cross-session)
- Memory retrieval và summarization

### 3.6. Tổng kết chương 3

---

## CHƯƠNG 4. KẾT QUẢ VÀ THỰC NGHIỆM

### 4.1. Môi trường thực nghiệm

#### 4.1.1. Cấu hình phần cứng

- CPU, RAM, GPU (nếu có)
- Storage requirements

#### 4.1.2. Cấu hình phần mềm

- Python version, dependencies
- Docker configuration
- LLM API configurations

#### 4.1.3. Dataset thử nghiệm

- Số lượng tài liệu theo phòng ban
- Số lượng câu hỏi test
- Ground truth labels

### 4.2. Đánh giá mô hình Retrieval

#### 4.2.1. Metrics đánh giá

- Precision@K, Recall@K
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG)

#### 4.2.2. So sánh Vector RAG vs Graph RAG

| Metric      | Vector RAG | Graph RAG | Improvement |
| ----------- | ---------- | --------- | ----------- |
| Precision@5 |            |           |             |
| Recall@10   |            |           |             |
| MRR         |            |           |             |

#### 4.2.3. Đánh giá Department Detection

- Accuracy theo phòng ban
- Confusion matrix
- Error analysis

### 4.3. Đánh giá chất lượng câu trả lời

#### 4.3.1. Metrics đánh giá

- BLEU, ROUGE scores
- Human evaluation (Relevance, Fluency, Accuracy)
- Faithfulness score (hallucination detection)

#### 4.3.2. Kết quả đánh giá

- Bảng kết quả theo loại câu hỏi
- So sánh với baseline (LLM không có RAG)
- Case studies

### 4.4. Đánh giá hiệu năng hệ thống

#### 4.4.1. Response Time

- Latency distribution
- Breakdown: Retrieval time vs Generation time
- Optimization results

#### 4.4.2. Throughput

- Requests per second
- Concurrent users support
- Resource utilization

#### 4.4.3. Scalability

- Horizontal scaling test
- Knowledge base size impact

### 4.5. Demo chức năng hệ thống

#### 4.5.1. Demo Chat Interface

- Screenshots giao diện
- Ví dụ các cuộc hội thoại mẫu

#### 4.5.2. Demo tra cứu điểm

- Quy trình tra cứu
- Kết quả trả về

#### 4.5.3. Demo tra cứu quy chế

- Các loại câu hỏi về quy chế
- Độ chính xác và nguồn trích dẫn

#### 4.5.4. Demo quản lý tài liệu

- Upload tài liệu mới
- Cập nhật Knowledge Graph

### 4.6. Phân tích và thảo luận

#### 4.6.1. Ưu điểm của hệ thống

- Độ chính xác cao với Graph RAG
- Khả năng mở rộng
- Dễ bảo trì và cập nhật

#### 4.6.2. Hạn chế và hướng cải thiện

- Xử lý câu hỏi phức tạp
- Tốc độ với large knowledge base
- Đa ngôn ngữ support

### 4.7. Tổng kết chương 4

---

## KẾT LUẬN

### Kết quả đạt được

- Tóm tắt các mục tiêu đã hoàn thành
- Đóng góp về mặt khoa học
- Đóng góp về mặt thực tiễn

### Hạn chế của đề tài

- Các hạn chế về scope
- Các hạn chế về kỹ thuật
- Các hạn chế về dữ liệu

### Hướng phát triển

- Tích hợp thêm nguồn dữ liệu
- Cải thiện mô hình NLP tiếng Việt
- Phát triển mobile app
- Fine-tuning LLM cho domain cụ thể
- Tích hợp voice interface

---

## TÀI LIỆU THAM KHẢO

### Tài liệu tiếng Việt

[1] ...

### Tài liệu tiếng Anh

[1] Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020.

[2] Edge, D., et al. (2024). "From Local to Global: A Graph RAG Approach to Query-Focused Summarization." arXiv preprint.

[3] Yao, S., et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023.

[4] Brown, T., et al. (2020). "Language Models are Few-Shot Learners." NeurIPS 2020.

[5] Vaswani, A., et al. (2017). "Attention Is All You Need." NeurIPS 2017.

[6] ...

### Tài liệu Web

[1] LangChain Documentation. https://python.langchain.com/

[2] LangGraph Documentation. https://langchain-ai.github.io/langgraph/

[3] FAISS Documentation. https://faiss.ai/

[4] FastAPI Documentation. https://fastapi.tiangolo.com/

---

## VI. KẾ HOẠCH THỰC HIỆN

| STT | Thời gian               | Nội dung thực hiện                                                                                                                                                                      | Kết quả dự kiến                                                                                                                |
| --- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | 15/01/2026 – 29/01/2026 | Nghiên cứu lý thuyết về LLM, RAG, Graph RAG, Knowledge Graph; khảo sát các hệ thống chatbot hiện có; thu thập và tiền xử lý tài liệu từ các phòng ban (Đào tạo, Khảo thí, Viện NC&HTPT) | Nắm vững cơ sở lý thuyết; bộ dữ liệu tài liệu đã chuẩn hóa định dạng Markdown với metadata đầy đủ                              |
| 2   | 30/01/2026 – 19/02/2026 | Phân tích yêu cầu chức năng, phi chức năng; thiết kế kiến trúc hệ thống; xây dựng Knowledge Graph với schema phân vùng theo phòng ban và tích hợp Vector Embedding                      | Tài liệu thiết kế hoàn chỉnh; Knowledge Graph hoạt động với 3 phòng ban và Common Graph; Vector Store FAISS được index         |
| 3   | 20/02/2026 – 19/03/2026 | Xây dựng Semantic Department Detector, Graph Retriever, Re-ranking module; tích hợp LLM (Gemini, Ollama); phát triển ReAct Agent và Supervisor Agent                                    | Hệ thống Retrieval đạt accuracy > 80%; Agent trả lời câu hỏi chính xác với khả năng multi-turn conversation và trích dẫn nguồn |
| 4   | 20/03/2026 – 02/04/2026 | Phát triển Backend API với FastAPI, JWT Authentication, Rate Limiting; xây dựng Web App responsive và Mobile App (React Native/Flutter); triển khai Docker                              | Backend API hoạt động ổn định; Web/Mobile App đầy đủ chức năng chat, tra cứu điểm, tra cứu quy chế; hệ thống deploy thành công |
| 5   | 03/04/2026 – 07/04/2026 | Kiểm thử chức năng End-to-End; đánh giá Retrieval (Precision, Recall, MRR); đánh giá chất lượng câu trả lời và hiệu năng hệ thống                                                       | Response time < 5s; accuracy > 85%; báo cáo đánh giá chi tiết với các metrics và case studies                                  |
| 6   | 08/04/2026 – 10/04/2026 | Hoàn thiện báo cáo đồ án; chuẩn bị slide thuyết trình; demo hệ thống; chỉnh sửa theo góp ý                                                                                              | Báo cáo đồ án hoàn chỉnh đầy đủ các chương; slide thuyết trình; video demo hệ thống hoạt động                                  |

---

## PHỤ LỤC

### Phụ lục A: Hướng dẫn cài đặt và triển khai

### Phụ lục B: Cấu trúc mã nguồn

### Phụ lục C: Danh sách tài liệu trong Knowledge Base

### Phụ lục D: Bộ câu hỏi đánh giá

### Phụ lục E: Kết quả đánh giá chi tiết
