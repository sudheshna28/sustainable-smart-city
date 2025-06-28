🌆 Sustainable Smart City Assistant

An intelligent and interactive web-based assistant built to empower citizens and city planners with actionable insights for sustainable urban living. This AI-powered dashboard integrates key modules like recycling guidance, real-time health statistics, document summarization, image generation, and city comparison to help make data-driven decisions for a smarter and greener future.

---

🚀 Features

♻️ Recycle Advisor
- Suggests eco-friendly waste disposal and recycling tips.
- Utilizes NLP to understand user queries and provide tailored guidance.

📊 Health Dashboard
- Displays real-time city health indicators such as pollution levels, hospital availability, and public health alerts.
- Interactive Altair-based visualizations.

📙 RAG-based Problem Solver
- Retrieves and summarizes city policy documents, environmental reports, or municipal FAQs using Retrieval-Augmented Generation (RAG).
- Helps users get concise answers to complex queries.

🎨 AI Image Generator
- Converts descriptive text into visuals for urban planning, green infrastructure, or awareness posters using diffusion models.

🏙️ City Comparison Tool
- Compares sustainability indicators across multiple cities.
- Supports metrics like air quality, green cover, recycling rate, and water usage.


```📁 Project Structure
Sustainable-Smart-City-Assistant/
│
├── Sai_Sudheshna/
│   ├── image_generation.py
│   ├── city_health_dashboard.py
│   ├── image_generation_document.txt
│   ├── health_dashboard_document.txt
│
├── Samitha_Naga_Lakshmi_Devi/
│   ├── comparison_between_2_cities.py
│   ├── problems_and_solutions.py
│   ├── recycle_advisor.py
│
├── Alekya_Devi/
│   ├── all_gathered_things.py
│
├── Bhavya_Sri/
│   ├── frontend.py
│   └── background.jpg
│
├── Problem_Statements/
│   ├── recycle_module_problem.txt
│   ├── city_health_problem.txt
│   ├── document_summarizer_problem.txt
│
├── Documentation/
│   ├── README.md
│   ├── project_report.docx
│   ├── architecture_diagram.png
│   ├── sprint_planning.pdf
│
├── Demonstration_Video/
│   └── smart_city_demo.mp4
│
└── requirements.txt

```
⚙️ Installation & Running Locally

1. Clone the repository
   bash
   git clone https://github.com/sudheshna28/smart-city-assistant.git
   cd smart-city-assistant

2. Install dependencies
pip install -r requirements.txt

3.Run the app
streamlit run app/main.py


🛠️ Technologies Used
Frontend/UI: Streamlit
Backend: Python

AI Models:
LLMs (Hugging Face / IBM Granite)
Stable Diffusion (for image generation)
RAG (for document summarization)
Data Visualization: Altair

🔍 Use Cases
Citizens looking to make eco-conscious decisions.
Urban developers comparing sustainability benchmarks.
Local governments spreading awareness with AI-generated images.
Students/researchers needing summarized civic data.

🌱 Future Scope
Integration with IoT sensor data from smart bins and traffic systems.
Voice-based chatbot assistant.
Mobile app version for broader accessibility.
Personalized citizen dashboards using user profiles.

