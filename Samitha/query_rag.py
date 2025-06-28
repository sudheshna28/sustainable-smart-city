import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # (optional) if you want to disable oneDNN entirely
import faiss
import pickle
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging
from typing import List, Dict, Tuple, Optional
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartVillageComparator:
    def __init__(self, index_path=r"C:\Users\DELL\Desktop\sustainble\sustainable-smart-city\samitha\faiss_index"):
        """Initialize the village comparator with FAISS index and models."""
        self.index_path = index_path
        self.index = None
        self.texts = None
        self.metadata = None
        self.embedding_model = None
        self.llm_model = None
        self.tokenizer = None
        
        # Check if index files exist before loading
        if not self._check_index_files():
            self._prompt_for_index_path()
        
        self.load_components()

    def _check_index_files(self) -> bool:
        """Check if all required index files exist."""
        required_files = [
            f"{self.index_path}/village.index",
            f"{self.index_path}/texts.pkl",
            f"{self.index_path}/metadata.pkl"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing index files: {missing_files}")
            return False
        return True

    def _prompt_for_index_path(self):
        """Prompt user for correct index path or help them create the index."""
        print("❌ FAISS index files not found!")
        print(f"Looking for files in: {os.path.abspath(self.index_path)}")
        print("\nRequired files:")
        print("  - village.index")
        print("  - texts.pkl") 
        print("  - metadata.pkl")
        
        print("\nOptions:")
        print("1. Enter the correct path to your FAISS index directory")
        print("2. Create a new index (you'll need data files)")
        print("3. Exit")
        
        while True:
            choice = input("\nEnter your choice (1/2/3): ").strip()
            
            if choice == "1":
                new_path = input("Enter the correct index path: ").strip()
                if new_path:
                    self.index_path = new_path
                    if self._check_index_files():
                        print("✅ Index files found!")
                        return
                    else:
                        print("❌ Files still not found at the specified path.")
                        continue
            elif choice == "2":
                self._guide_index_creation()
                return
            elif choice == "3":
                raise SystemExit("Exiting application.")
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    def _guide_index_creation(self):
        """Guide user through index creation process."""
        print("\n📋 INDEX CREATION GUIDE")
        print("=" * 50)
        print("To create a FAISS index, you need:")
        print("1. Text data files (CSV, JSON, or TXT)")
        print("2. Run the indexing script")
        
        data_path = input("\nEnter path to your data files (or press Enter to skip): ").strip()
        
        if data_path and os.path.exists(data_path):
            print(f"Data path found: {data_path}")
            self._create_basic_index(data_path)
        else:
            print("\n⚠️  No data path provided or path doesn't exist.")
            print("Creating a demo mode with sample data...")
            self._create_demo_mode()

    def _create_demo_mode(self):
        """Create a demo mode with sample village data."""
        print("\n🎯 Creating demo mode with sample data...")
        
        # Sample village data
        sample_data = [
            "Hiware Bazar is a model village in Maharashtra known for water conservation and renewable energy initiatives.",
            "Punsari village in Gujarat has implemented smart governance with digital services and solar energy.",
            "Mawlynnong in Meghalaya is known as Asia's cleanest village with excellent waste management.",
            "Pothanikkad in Kerala has achieved 100% organic farming and sustainable agriculture practices.",
            "Ralegan Siddhi in Maharashtra is famous for watershed management and water harvesting.",
            "Dharnai village in Bihar became India's first solar-powered village with renewable energy.",
            "Shani Shingnapur in Maharashtra has digital banking and cashless transactions.",
            "Kokrebellur in Karnataka is known for bird conservation and eco-tourism.",
        ]
        
        sample_metadata = [f"Village data {i+1}" for i in range(len(sample_data))]
        
        # Create directory
        os.makedirs(self.index_path, exist_ok=True)
        
        # Save sample data
        with open(f"{self.index_path}/texts.pkl", "wb") as f:
            pickle.dump(sample_data, f)
            
        with open(f"{self.index_path}/metadata.pkl", "wb") as f:
            pickle.dump(sample_metadata, f)
        
        # Create embeddings and index
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            embeddings = model.encode(sample_data)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings.astype('float32'))
            index.add(embeddings.astype('float32'))
            
            # Save index
            faiss.write_index(index, f"{self.index_path}/village.index")
            
            print("✅ Demo index created successfully!")
            print(f"Created index with {len(sample_data)} sample villages")
            
        except Exception as e:
            logger.error(f"Error creating demo index: {e}")
            raise

    def _create_basic_index(self, data_path: str):
        """Create index from user data files."""
        try:
            # This is a placeholder for actual index creation
            # You would implement data loading and processing here
            print(f"🔄 Processing data from: {data_path}")
            print("⚠️  Index creation from custom data not implemented in this demo.")
            print("Using demo mode instead...")
            self._create_demo_mode()
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            self._create_demo_mode()

    def load_components(self):
        """Load all necessary components."""
        try:
            self.load_index()
            self.load_embedding_model()
            self.load_llm_model()
            logger.info("All components loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            raise

    def load_index(self):
        """Load FAISS index and associated data."""
        try:
            index_file = f"{self.index_path}/village.index"
            texts_file = f"{self.index_path}/texts.pkl"
            metadata_file = f"{self.index_path}/metadata.pkl"
            
            # Verify files exist
            for file_path in [index_file, texts_file, metadata_file]:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Required file not found: {file_path}")
            
            self.index = faiss.read_index(index_file)
            
            with open(texts_file, "rb") as f:
                self.texts = pickle.load(f)
                
            with open(metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
                
            logger.info(f"Loaded index with {len(self.texts)} documents")
            
        except FileNotFoundError as e:
            logger.error(f"Index files not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise

    def load_embedding_model(self):
        """Load the sentence transformer model for embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            print("⚠️  Installing sentence-transformers...")
            os.system("pip install sentence-transformers")
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                logger.info("Embedding model loaded successfully after installation")
            except Exception as e2:
                logger.error(f"Still failed to load embedding model: {e2}")
                raise

    def load_llm_model(self):
        """Load the language model for text generation."""
        try:
            model_name = "google/flan-t5-base"  # Using base instead of small for better results
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.llm_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            raise

    def embed_query(self, query: str) -> np.ndarray:
        """Convert text query to embedding vector."""
        try:
            embedding = self.embedding_model.encode([query])
            # Normalize for cosine similarity
            embedding = embedding.astype('float32')
            faiss.normalize_L2(embedding)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return np.array([]).astype("float32")

    def retrieve_village_data(self, village_name: str, top_k: int = 8) -> Tuple[List[str], List[float]]:
        """Retrieve relevant chunks for a village with similarity scores."""
        try:
            # Search with village name
            query_embedding = self.embed_query(village_name)
            if query_embedding.size == 0:
                return [], []
                
            distances, indices = self.index.search(query_embedding, min(top_k * 2, len(self.texts)))
            
            # Filter results that are actually about the village
            relevant_chunks = []
            similarity_scores = []
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.texts) and idx < len(self.metadata):
                    chunk = self.texts[idx]
                    metadata = self.metadata[idx]
                    
                    # Check if chunk is relevant to the village
                    if self._is_relevant_chunk(village_name, chunk, metadata):
                        relevant_chunks.append(chunk)
                        similarity_scores.append(float(distance))
                        
                        if len(relevant_chunks) >= top_k:
                            break
            
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks for {village_name}")
            return relevant_chunks, similarity_scores
            
        except Exception as e:
            logger.error(f"Error retrieving data for {village_name}: {e}")
            return [], []

    def _is_relevant_chunk(self, village_name: str, chunk: str, metadata: str) -> bool:
        """Check if a chunk is relevant to the village."""
        village_lower = village_name.lower()
        chunk_lower = chunk.lower()
        metadata_lower = metadata.lower()
        
        # Check multiple conditions for relevance
        conditions = [
            village_lower in chunk_lower,
            village_lower in metadata_lower,
            any(word in chunk_lower for word in village_lower.split()),
            # Add fuzzy matching for similar names
            self._fuzzy_match(village_lower, chunk_lower),
        ]
        
        return any(conditions)

    def _fuzzy_match(self, village_name: str, text: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy matching for village names."""
        village_words = village_name.split()
        for word in village_words:
            if len(word) > 3 and word in text:
                return True
        return False

    def extract_sustainability_features(self, chunks: List[str]) -> Dict[str, List[str]]:
        """Extract sustainability-related features from text chunks."""
        sustainability_keywords = {
            'energy': ['solar', 'renewable', 'wind', 'biogas', 'electricity', 'power', 'energy', 'generator', 'battery', 'grid'],
            'water': ['water', 'irrigation', 'wells', 'rainwater', 'watershed', 'drainage', 'bore', 'tank', 'reservoir', 'pipeline'],
            'waste': ['waste', 'recycling', 'compost', 'sewage', 'sanitation', 'garbage', 'toilet', 'latrine', 'disposal', 'collection'],
            'transport': ['transport', 'roads', 'connectivity', 'vehicles', 'public transport', 'bus', 'railway', 'highway', 'bridge'],
            'agriculture': ['organic', 'farming', 'crops', 'agriculture', 'sustainable farming', 'fertilizer', 'pesticide', 'irrigation', 'harvest'],
            'healthcare': ['hospital', 'clinic', 'health', 'medical', 'healthcare', 'doctor', 'medicine', 'pharmacy', 'ambulance'],
            'education': ['school', 'education', 'literacy', 'training', 'learning', 'teacher', 'college', 'university', 'library'],
            'economy': ['employment', 'income', 'business', 'economy', 'livelihood', 'market', 'shop', 'industry', 'cooperative'],
            'environment': ['forest', 'trees', 'pollution', 'environment', 'conservation', 'green', 'clean', 'biodiversity', 'wildlife'],
            'technology': ['digital', 'internet', 'technology', 'mobile', 'computer', 'wifi', 'network', 'online', 'app']
        }
        
        features = {category: [] for category in sustainability_keywords}
        
        combined_text = ' '.join(chunks).lower()
        
        for category, keywords in sustainability_keywords.items():
            category_features = set()  # Use set to avoid duplicates
            for keyword in keywords:
                if keyword in combined_text:
                    # Extract sentences containing the keyword
                    sentences = re.split(r'[.!?]+', combined_text)
                    for sentence in sentences:
                        if keyword in sentence and len(sentence.strip()) > 10:
                            # Clean and limit sentence length
                            clean_sentence = sentence.strip()[:150]
                            category_features.add(clean_sentence)
                            if len(category_features) >= 3:  # Limit to 3 features per category
                                break
                    if len(category_features) >= 3:
                        break
            
            features[category] = list(category_features)
        
        return features

    def generate_comparison(self, village1: str, village2: str, 
                          chunks1: List[str], chunks2: List[str]) -> str:
        """Generate a detailed comparison between two villages."""
        try:
            # Extract features for both villages
            features1 = self.extract_sustainability_features(chunks1)
            features2 = self.extract_sustainability_features(chunks2)
            
            # Create a comprehensive prompt
            prompt = self._create_comparison_prompt(village1, village2, features1, features2, chunks1, chunks2)
            
            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.llm_model.generate(
                **inputs, 
                max_new_tokens=800,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Post-process the output
            return self._post_process_output(village1, village2, generated_text, features1, features2)
            
        except Exception as e:
            logger.error(f"Error generating comparison: {e}")
            return self._create_fallback_comparison(village1, village2, chunks1, chunks2)

    def _create_comparison_prompt(self, village1: str, village2: str, 
                                features1: Dict, features2: Dict,
                                chunks1: List[str], chunks2: List[str]) -> str:
        """Create a structured prompt for comparison."""
        
        prompt = f"""Compare the sustainability features of {village1} and {village2}.

{village1} information:
{' '.join(chunks1[:3])}

{village2} information:  
{' '.join(chunks2[:3])}

Focus on sustainability aspects like:
- Energy systems and renewable sources
- Water management and conservation
- Waste management and sanitation
- Transportation and connectivity
- Environmental conservation
- Economic sustainability

Provide a structured comparison highlighting:
1. What {village1} has that {village2} lacks
2. What {village2} has that {village1} lacks  
3. Sustainability recommendations for {village1}

Answer:"""
        
        return prompt

    def _post_process_output(self, village1: str, village2: str, 
                           generated_text: str, features1: Dict, features2: Dict) -> str:
        """Post-process and enhance the generated output."""
        
        # Count features for each village
        village1_features = sum(len(features) for features in features1.values())
        village2_features = sum(len(features) for features in features2.values())
        
        more_sustainable = village1 if village1_features > village2_features else village2
        
        # Create enhanced output
        output = f"""
🌿 SUSTAINABILITY COMPARISON: {village1.upper()} vs {village2.upper()}

📊 SUSTAINABILITY OVERVIEW:
• {village1}: {village1_features} sustainability features identified
• {village2}: {village2_features} sustainability features identified
• More sustainable: {more_sustainable}

{generated_text}

🎯 KEY SUSTAINABILITY RECOMMENDATIONS FOR {village1.upper()}:

"""
        
        # Add specific recommendations based on missing features
        recommendations = self._generate_recommendations(village1, features1, features2)
        output += recommendations
        
        return output

    def _generate_recommendations(self, target_village: str, 
                                features1: Dict, features2: Dict) -> str:
        """Generate specific sustainability recommendations with detailed technologies."""
        recommendations = []
        missing_categories = []
        
        # Identify missing or weak categories
        for category, features2_list in features2.items():
            features1_list = features1.get(category, [])
            
            if features2_list and not features1_list:
                missing_categories.append(category)
            elif len(features1_list) < len(features2_list):
                missing_categories.append(category)
        
        # Add recommendations based on missing categories
        for category in set(missing_categories):  # Remove duplicates
            if category == 'energy':
                recommendations.extend([
                    "🔋 RENEWABLE ENERGY TECHNOLOGIES:",
                    "  • Solar rooftop systems (3-5 kW for households)",
                    "  • Community biogas plants using agricultural waste",
                    "  • Micro wind turbines for areas with good wind patterns",
                    "  • Solar street lighting with LED fixtures",
                    "  • Battery storage systems for energy backup"
                ])
            elif category == 'water':
                recommendations.extend([
                    "💧 WATER MANAGEMENT TECHNOLOGIES:",
                    "  • Rainwater harvesting tanks (5000-10000L capacity)",
                    "  • Drip irrigation systems for efficient farming",
                    "  • Solar-powered water pumps",
                    "  • Greywater recycling systems for households",
                    "  • Smart water meters for usage monitoring"
                ])
            elif category == 'waste':
                recommendations.extend([
                    "♻️ WASTE MANAGEMENT TECHNOLOGIES:",
                    "  • Composting units for organic waste (Khamba composting)",
                    "  • Biogas digesters for kitchen waste",
                    "  • Plastic shredding machines for recycling",
                    "  • Vermiculture systems for organic fertilizer",
                    "  • Mobile waste collection apps and scheduling"
                ])
            elif category == 'transport':
                recommendations.extend([
                    "🚌 SUSTAINABLE TRANSPORT SOLUTIONS:",
                    "  • Electric rickshaws/auto-rickshaws",
                    "  • Solar-powered bus stops with charging stations",
                    "  • Bike-sharing programs with GPS tracking",
                    "  • Carpooling apps for rural areas",
                    "  • Electric vehicle charging infrastructure"
                ])
            elif category == 'agriculture':
                recommendations.extend([
                    "🌾 SMART AGRICULTURE TECHNOLOGIES:",
                    "  • Precision farming with IoT sensors",
                    "  • Organic certification and marketing platforms",
                    "  • Drone-based crop monitoring",
                    "  • Soil health testing kits",
                    "  • Mobile apps for weather and market prices"
                ])
            elif category == 'environment':
                recommendations.extend([
                    "🌳 ENVIRONMENTAL CONSERVATION TECH:",
                    "  • Air quality monitoring sensors",
                    "  • Tree plantation with native species selection",
                    "  • Wetland restoration systems",
                    "  • Carbon footprint tracking apps",
                    "  • Biodiversity monitoring with camera traps"
                ])
            elif category == 'technology':
                recommendations.extend([
                    "📱 DIGITAL INFRASTRUCTURE:",
                    "  • Community Wi-Fi hotspots with solar power",
                    "  • Digital literacy centers with tablets/computers",
                    "  • Mobile banking and financial inclusion apps",
                    "  • Telemedicine platforms for remote healthcare",
                    "  • E-governance portals for citizen services"
                ])
            elif category == 'healthcare':
                recommendations.extend([
                    "🏥 HEALTHCARE TECHNOLOGIES:",
                    "  • Portable diagnostic devices (ECG, blood pressure)",
                    "  • Telemedicine kiosks with video consultation",
                    "  • Mobile health apps for vaccination tracking",
                    "  • Water purification tablets and testing kits",
                    "  • Solar-powered vaccine refrigerators"
                ])
            elif category == 'education':
                recommendations.extend([
                    "📚 EDUCATIONAL TECHNOLOGIES:",
                    "  • Solar-powered e-learning tablets",
                    "  • Digital libraries with offline content",
                    "  • Skill development through online platforms",
                    "  • Virtual reality for immersive learning",
                    "  • Satellite internet for remote connectivity"
                ])
            elif category == 'economy':
                recommendations.extend([
                    "💼 ECONOMIC DEVELOPMENT TECH:",
                    "  • E-commerce platforms for local products",
                    "  • Microfinance mobile applications",
                    "  • Digital payment systems (UPI, mobile wallets)",
                    "  • Supply chain management software",
                    "  • Online marketplaces for agricultural products"
                ])
        
        # Add general recommendations if no specific gaps found
        if not recommendations:
            recommendations.extend([
                "🚀 GENERAL SUSTAINABILITY ENHANCEMENTS:",
                "  • Smart meters for electricity and water monitoring",
                "  • Community-based renewable energy cooperatives",
                "  • Waste-to-energy conversion systems",
                "  • Green building certification programs",
                "  • Environmental education and awareness campaigns",
                "  • Sustainable tourism development platforms",
                "  • Local food processing and value addition units"
            ])
        
        # Add implementation guidance
        recommendations.extend([
            "",
            "💡 IMPLEMENTATION STRATEGY:",
            "  • Start with 1-2 pilot projects based on community priorities",
            "  • Seek government subsidies and schemes (PM-KUSUM, Swachh Bharat, etc.)",
            "  • Partner with NGOs and social enterprises",
            "  • Involve local youth and self-help groups in implementation",
            "  • Monitor progress with measurable indicators (energy saved, waste reduced, etc.)"
        ])
        
        return '\n'.join(recommendations)

    def _create_fallback_comparison(self, village1: str, village2: str, 
                                  chunks1: List[str], chunks2: List[str]) -> str:
        """Create a basic comparison when model generation fails."""
        return f"""
🌿 BASIC COMPARISON: {village1.upper()} vs {village2.upper()}

Data available for {village1}: {len(chunks1)} information chunks
Data available for {village2}: {len(chunks2)} information chunks

📋 Available information suggests differences in:
• Infrastructure development
• Resource availability  
• Sustainability initiatives
• Community programs

🎯 RECOMMENDATIONS FOR {village1.upper()}:
• Conduct detailed sustainability assessment
• Learn from successful practices in {village2}
• Implement community-based sustainability programs
• Focus on renewable energy and resource conservation
"""

    def run_interactive_session(self):
        """Run the interactive comparison session."""
        print("🌿 Welcome to the Enhanced Smart Village Comparison Assistant!")
        print("=" * 70)
        print("I can help you compare sustainability features between villages/cities")
        print("and provide actionable recommendations for improvement.")
        print("=" * 70)
        
        while True:
            try:
                print("\n" + "="*50)
                village1 = input("🏡 Enter the first village/city name (or 'quit'): ").strip()
                
                if village1.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using the Smart Village Comparator!")
                    print("Stay sustainable! 🌱")
                    break
                
                village2 = input("🏘️  Enter the second village/city name to compare: ").strip()
                
                if not village1 or not village2:
                    print("⚠️  Please enter valid village names.")
                    continue
                
                print(f"\n🔍 Searching for data on {village1} and {village2}...")
                
                # Retrieve data for both villages
                chunks1, scores1 = self.retrieve_village_data(village1)
                chunks2, scores2 = self.retrieve_village_data(village2)
                
                if not chunks1:
                    print(f"❌ No data found for {village1}. Please check the spelling or try another village.")
                    continue
                    
                if not chunks2:
                    print(f"❌ No data found for {village2}. Please check the spelling or try another village.")
                    continue
                
                print(f"✅ Found data for both villages!")
                print(f"   - {village1}: {len(chunks1)} relevant documents")
                print(f"   - {village2}: {len(chunks2)} relevant documents")
                
                print("\n🤖 Generating detailed sustainability comparison...")
                
                # Generate comparison
                comparison = self.generate_comparison(village1, village2, chunks1, chunks2)
                
                print("\n" + "="*70)
                print("📋 SUSTAINABILITY COMPARISON REPORT")
                print("="*70)
                print(comparison)
                print("="*70)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")
                print(f"⚠️  An error occurred: {e}")
                print("Please try again with different village names.")

def main():
    """Main function to run the application."""
    try:
        comparator = SmartVillageComparator()
        comparator.run_interactive_session()
    except SystemExit:
        pass  # Normal exit
    except Exception as e:
        print(f"❌ Failed to initialize the application: {e}")
        print("Please check if all required files and models are available.")

if __name__ == "__main__":
    main()