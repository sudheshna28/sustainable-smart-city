import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import torch
import re
from typing import List, Dict

# Import with error handling
try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    HAS_T5 = True
except ImportError as e:
    print(f"⚠️  T5 models not available: {e}")
    print("💡 Install with: pip install transformers sentencepiece")
    HAS_T5 = False

class SmartCityRAGSolver:
    def __init__(self, index_path="faiss_index", use_t5=True, models_cache_dir=None):
        """
        Initialize Smart City RAG Solver using existing FAISS index
        
        Args:
            index_path: Path to FAISS index directory
            use_t5: Whether to use T5 for generation
            models_cache_dir: Directory where models are cached (optional)
        """
        self.index_path = index_path
        self.use_t5 = use_t5 and HAS_T5
        self.models_cache_dir = models_cache_dir
        
        # Load models (using existing downloaded models)
        print("🔄 Loading models...")
        self.load_models()
        
        # Load existing index and data
        self.load_existing_index()
        
        # Smart city keywords for query filtering
        self.smart_city_keywords = [
            'traffic', 'parking', 'waste', 'pollution', 'energy', 'water', 'transport',
            'infrastructure', 'urban', 'city', 'municipal', 'public', 'environment',
            'smart', 'digital', 'iot', 'sensor', 'monitoring', 'management', 'efficiency',
            'sustainability', 'green', 'renewable', 'congestion', 'mobility', 'housing',
            'street', 'lighting', 'safety', 'security', 'governance', 'citizen', 'service',
            'village', 'rural', 'community', 'development', 'healthcare', 'education',
            'connectivity', 'road', 'drainage', 'irrigation', 'power', 'electricity'
        ]
    
    def load_models(self):
        """Load embedding and generation models"""
        try:
            # Load sentence transformer model
            if self.models_cache_dir:
                model_path = os.path.join(self.models_cache_dir, "sentence-transformers--all-MiniLM-L6-v2")
                if os.path.exists(model_path):
                    self.embedding_model = SentenceTransformer(model_path)
                    print(f"✅ Loaded embedding model from: {model_path}")
                else:
                    self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                    print("✅ Loaded embedding model from HuggingFace cache")
            else:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                print("✅ Embedding model loaded successfully")
                
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            raise
        
        # Load T5 models only if available and requested
        if self.use_t5:
            try:
                print("🔄 Loading T5 generation model...")
                
                if self.models_cache_dir:
                    t5_path = os.path.join(self.models_cache_dir, "google--flan-t5-base")
                    if os.path.exists(t5_path):
                        self.generation_model = T5ForConditionalGeneration.from_pretrained(t5_path)
                        self.tokenizer = T5Tokenizer.from_pretrained(t5_path)
                        print(f"✅ Loaded T5 models from: {t5_path}")
                    else:
                        self.generation_model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
                        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
                        print("✅ Loaded T5 models from HuggingFace cache")
                else:
                    self.generation_model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
                    self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
                    print("✅ T5 models loaded successfully")
                    
            except Exception as e:
                print(f"❌ Error loading T5 models: {e}")
                print("💡 Falling back to template-based generation")
                self.use_t5 = False
        else:
            print("ℹ️  Using template-based solution generation")
    
    def load_existing_index(self):
        """Load pre-built FAISS index and associated data"""
        try:
            # Load FAISS index
            index_file = os.path.join(self.index_path, "problems.index")
            
            if not os.path.exists(index_file):
                raise FileNotFoundError(f"FAISS index not found: {index_file}")
            
            self.index = faiss.read_index(index_file)
            
            # Load texts and metadata
            texts_file = os.path.join(self.index_path, "texts.pkl")
            metadata_file = os.path.join(self.index_path, "metadata.pkl")
            
            with open(texts_file, "rb") as f:
                self.texts = pickle.load(f)
            
            with open(metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
            
            print(f"✅ Loaded index with {len(self.texts)} chunks")
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            print("Please make sure the FAISS index exists and was created properly.")
            print("Expected files:")
            print(f"  - {self.index_path}/problems.index")
            print(f"  - {self.index_path}/texts.pkl")
            print(f"  - {self.index_path}/metadata.pkl")
            raise
    
    def is_smart_city_query(self, query):
        """Check if query is related to smart city problems"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.smart_city_keywords)
    
    def identify_problem_category(self, query):
        """Identify the main category of the smart city problem"""
        query_lower = query.lower()
        
        category_keywords = {
            'traffic': ['traffic', 'congestion', 'jam', 'flow', 'signal', 'vehicles'],
            'parking': ['parking', 'park', 'space', 'lot', 'garage'],
            'waste': ['waste', 'garbage', 'trash', 'refuse', 'recycling', 'disposal'],
            'energy': ['energy', 'power', 'electricity', 'solar', 'renewable', 'grid'],
            'water': ['water', 'supply', 'drainage', 'sewage', 'irrigation', 'leak'],
            'transport': ['transport', 'bus', 'metro', 'public transport', 'mobility', 'transit'],
            'pollution': ['pollution', 'air quality', 'noise', 'emission', 'contamination', 'smog'],
            'housing': ['housing', 'residential', 'accommodation', 'shelter', 'building'],
            'safety': ['safety', 'security', 'crime', 'surveillance', 'emergency'],
            'governance': ['governance', 'administration', 'service', 'citizen', 'digital'],
            'healthcare': ['healthcare', 'health', 'medical', 'clinic', 'hospital', 'doctor'],
            'education': ['education', 'school', 'teacher', 'learning', 'student'],
            'connectivity': ['connectivity', 'internet', 'network', 'communication', 'wifi'],
            'infrastructure': ['road', 'bridge', 'construction', 'infrastructure', 'connectivity']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def search_relevant_solutions(self, query, k=5):
        """Search for most relevant problem-solution pairs using semantic similarity"""
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            query_embedding = np.array(query_embedding).astype("float32")
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, k)
            
            # Get relevant chunks with metadata
            relevant_solutions = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.texts) and idx != -1:  # Ensure valid index
                    relevant_solutions.append({
                        'text': self.texts[idx],
                        'metadata': self.metadata[idx] if isinstance(self.metadata[idx], str) else str(self.metadata[idx]),
                        'distance': float(distance),
                        'similarity_score': 1.0 / (1.0 + distance),  # Convert distance to similarity
                        'rank': i + 1
                    })
            
            return relevant_solutions
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return []
    
    def extract_problem_solution_pair(self, text):
        """Extract problem and solution from text chunk more effectively"""
        # Clean the text first
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Split by common delimiters to find problem-solution pairs
        parts = re.split(r'(?:problem:|solution:|issue:|resolution:|challenge:|approach:)', text, flags=re.IGNORECASE)
        
        problem = ""
        solution = ""
        
        # If we have structured parts
        if len(parts) > 1:
            # Try to identify problem and solution from parts
            for i, part in enumerate(parts[1:], 1):  # Skip first empty part
                part = part.strip()
                if part and len(part) > 10:  # Only consider meaningful parts
                    if i % 2 == 1:  # Odd indices after problem/issue
                        if not problem:
                            problem = part[:200]  # Limit length
                    else:  # Even indices after solution/resolution
                        if not solution:
                            solution = part[:300]  # Limit length
        
        # If no structured format, try to extract from whole text
        if not problem and not solution:
            # Look for solution-indicating keywords
            solution_keywords = ['implement', 'establish', 'create', 'develop', 'install', 'deploy', 'set up', 'build', 'construct']
            
            sentences = re.split(r'[.!?]+', text)
            solution_sentences = []
            problem_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15:  # Only meaningful sentences
                    if any(keyword in sentence.lower() for keyword in solution_keywords):
                        solution_sentences.append(sentence)
                    else:
                        problem_sentences.append(sentence)
            
            # Combine sentences
            if solution_sentences:
                solution = '. '.join(solution_sentences[:2])  # Max 2 sentences
            if problem_sentences:
                problem = '. '.join(problem_sentences[:2])  # Max 2 sentences
        
        return problem.strip(), solution.strip()
    
    def create_solution_steps(self, query, category, relevant_solutions):
        """Create clean, actionable steps based on query and category"""
        
        # Extract key solutions from relevant documents
        key_solutions = []
        for sol_data in relevant_solutions:
            problem, solution = self.extract_problem_solution_pair(sol_data['text'])
            if solution and len(solution) > 20:
                # Clean and extract key actions
                solution_clean = re.sub(r'\s+', ' ', solution)
                key_solutions.append(solution_clean)
        
        # Create category-specific steps
        category_steps = {
            'traffic': [
                "Conduct traffic flow analysis and identify bottlenecks",
                "Install smart traffic signals with adaptive timing",
                "Implement intelligent transportation system (ITS)",
                "Deploy traffic monitoring cameras and sensors",
                "Create alternative route recommendations",
                "Monitor and optimize traffic patterns continuously"
            ],
            'parking': [
                "Survey current parking capacity and utilization",
                "Install smart parking sensors and meters",
                "Develop mobile app for parking availability",
                "Implement dynamic pricing based on demand", 
                "Create designated parking zones",
                "Monitor usage and adjust policies accordingly"
            ],
            'waste': [
                "Assess current waste generation and disposal patterns",
                "Install smart waste bins with fill-level sensors",
                "Implement waste segregation at source",
                "Optimize collection routes using IoT data",
                "Establish recycling and composting facilities",
                "Monitor waste reduction and recycling rates"
            ],
            'energy': [
                "Conduct energy audit and identify inefficiencies", 
                "Install renewable energy sources (solar/wind)",
                "Deploy smart grid infrastructure",
                "Implement energy monitoring systems",
                "Create energy conservation programs",
                "Track energy consumption and savings"
            ],
            'water': [
                "Assess water supply and demand patterns",
                "Install smart water meters and leak detection",
                "Implement rainwater harvesting systems",
                "Deploy water quality monitoring sensors",
                "Create water conservation programs",
                "Monitor water usage and quality continuously"
            ],
            'transport': [
                "Analyze current transportation needs and gaps",
                "Establish efficient public transport routes",
                "Deploy GPS tracking for vehicles",
                "Implement digital ticketing system",
                "Create integrated transport network",
                "Monitor ridership and service quality"
            ],
            'connectivity': [
                "Assess current connectivity infrastructure",
                "Install fiber optic or wireless networks",
                "Set up public Wi-Fi hotspots",
                "Implement digital service platforms",
                "Provide digital literacy training",
                "Monitor network performance and usage"
            ],
            'healthcare': [
                "Assess healthcare needs and service gaps",
                "Establish mobile health clinics or telemedicine",
                "Deploy health monitoring systems",
                "Create health awareness programs",
                "Train local healthcare workers",
                "Monitor health outcomes and service delivery"
            ]
        }
        
        # Get base steps for category
        base_steps = category_steps.get(category, category_steps.get('general', [
            "Analyze the current situation and identify key issues",
            "Develop comprehensive solution strategy",
            "Implement pilot project with monitoring systems",
            "Scale up successful interventions",
            "Establish ongoing monitoring and evaluation",
            "Continuously improve based on feedback"
        ]))
        
        # Enhance with specific solutions from knowledge base
        enhanced_steps = []
        step_num = 1
        
        for i, base_step in enumerate(base_steps):
            # Add base step
            enhanced_steps.append(f"Step {step_num}: {base_step}")
            step_num += 1
            
            # Add specific solution if available
            if i < len(key_solutions):
                specific_solution = key_solutions[i][:100] + "..." if len(key_solutions[i]) > 100 else key_solutions[i]
                enhanced_steps.append(f"Step {step_num}: {specific_solution}")
                step_num += 1
            
            # Limit to 8 steps total
            if step_num > 8:
                break
        
        return enhanced_steps[:8]  # Ensure max 8 steps

    def solve_smart_city_problem(self, query):
        """Main method to solve smart city problems using RAG"""
        # Check if query is smart city related
        if not self.is_smart_city_query(query):
            return {
                'is_smart_city_related': False,
                'message': 'This query doesn\'t appear to be related to smart city problems. Please ask about urban infrastructure, city management, or municipal services.',
                'steps': [],
                'original_solutions': []
            }
        
        print(f"🔍 Searching for solutions to: {query}")
        
        # Identify problem category
        category = self.identify_problem_category(query)
        print(f"📂 Problem category: {category}")
        
        # Search for relevant problem-solution pairs
        relevant_solutions = self.search_relevant_solutions(query, k=5)
        
        if not relevant_solutions:
            return {
                'is_smart_city_related': True,
                'query': query,
                'category': category,
                'message': 'No relevant solutions found in the knowledge base for this specific problem.',
                'steps': [
                    "Step 1: Research similar problems and solutions",
                    "Step 2: Consult with domain experts", 
                    "Step 3: Develop custom solution based on best practices",
                    "Step 4: Pilot test the solution",
                    "Step 5: Scale up if successful",
                    "Step 6: Monitor and evaluate continuously"
                ],
                'original_solutions': [],
                'confidence_score': 0.0
            }
        
        # Extract solutions from knowledge base
        knowledge_solutions = []
        for solution_data in relevant_solutions:
            problem, solution = self.extract_problem_solution_pair(solution_data['text'])
            if solution:
                knowledge_solutions.append({
                    'problem': problem,
                    'solution': solution,
                    'similarity_score': solution_data['similarity_score'],
                    'text': solution_data['text'][:200] + "..." if len(solution_data['text']) > 200 else solution_data['text']
                })
        
        # Create clean, actionable steps
        solution_steps = self.create_solution_steps(query, category, relevant_solutions)
        
        # Calculate overall confidence
        avg_confidence = sum(sol['similarity_score'] for sol in knowledge_solutions) / len(knowledge_solutions) if knowledge_solutions else 0.0
        
        return {
            'is_smart_city_related': True,
            'query': query,
            'category': category,
            'steps': solution_steps,
            'original_solutions': knowledge_solutions,
            'confidence_score': avg_confidence,
            'num_sources': len(relevant_solutions),
            'method': 'enhanced_template'
        }

def interactive_smart_city_solver():
    """Interactive function to get user input and solve problems"""
    
    print("\n" + "="*70)
    print("🏙️  SMART CITY PROBLEM SOLVER - INTERACTIVE MODE")
    print("="*70)
    print("Ask me about any smart city problem and I'll provide step-by-step solutions!")
    print("Examples: traffic congestion, waste management, air pollution, parking issues, etc.")
    print("Type 'quit' to exit.")
    print("-" * 70)
    
    try:
        # Initialize the solver - UPDATE THIS PATH TO YOUR INDEX LOCATION
        INDEX_PATH = r"C:\Users\DELL\Desktop\sustainble\sustainable-smart-city\problems_index"
        
        # Optional: Specify where your models are cached
        # MODELS_CACHE_DIR = r"C:\Users\DELL\.cache\huggingface\hub"  # Uncomment and adjust if needed
        
        solver = SmartCityRAGSolver(
            index_path=INDEX_PATH,
            use_t5=False  # Disabled T5 for cleaner, faster responses
            # models_cache_dir=MODELS_CACHE_DIR  # Uncomment if you want to specify cache directory
        )
        
        while True:
            print("\n" + "🔸" * 35)
            user_query = input("🤔 What smart city problem would you like to solve? \n   → ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using Smart City Problem Solver!")
                break
            
            if not user_query:
                print("❌ Please enter a valid question.")
                continue
            
            print(f"\n🔍 Processing your query: '{user_query}'")
            print("-" * 50)
            
            # Get solution
            result = solver.solve_smart_city_problem(user_query)
            
            if not result['is_smart_city_related']:
                print(f"❌ {result['message']}")
                continue
            
            # Display results
            print(f"📂 Problem Category: {result['category'].upper()}")
            print(f"🎯 Confidence Score: {result['confidence_score']:.3f}")
            print(f"📚 Sources Found: {result.get('num_sources', 0)} relevant documents")
            
            if result.get('original_solutions'):
                print(f"\n💡 Knowledge Base Solutions ({len(result['original_solutions'])}):")
                for i, sol in enumerate(result['original_solutions'][:3], 1):
                    print(f"   {i}. {sol['solution'][:150]}...")
                    print(f"      Similarity: {sol['similarity_score']:.3f}")
            
            print(f"\n📝 STEP-BY-STEP SOLUTION:")
            print("=" * 50)
            
            if result['steps']:
                for step in result['steps']:
                    print(f"✅ {step}")
            else:
                print("No specific steps generated. Please try rephrasing your question.")
            
            print("\n" + "="*50)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting steps:")
        print("1. Make sure the FAISS index exists in the specified folder")
        print("2. Check that these files exist:")
        print("   - problems_index/problems.index")
        print("   - problems_index/texts.pkl") 
        print("   - problems_index/metadata.pkl")
        print("3. Update the INDEX_PATH variable with correct path")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n💡 Make sure all required packages are installed:")
        print("pip install sentence-transformers faiss-cpu transformers sentencepiece torch numpy")

# Quick solve function for single queries
def quick_solve_problem(user_query, index_path="problems_index", models_cache_dir=None):
    """Quick solve function for single problem"""
    try:
        solver = SmartCityRAGSolver(index_path=index_path, models_cache_dir=models_cache_dir, use_t5=False)
        result = solver.solve_smart_city_problem(user_query)
        
        if not result['is_smart_city_related']:
            return result['message']
        
        # Format response
        response = f"🏙️ **Smart City Solution for {result['category'].title()} Problem**\n\n"
        response += f"**Query:** {result['query']}\n"
        response += f"**Confidence Score:** {result['confidence_score']:.3f}\n"
        response += f"**Sources:** {result.get('num_sources', 0)} relevant documents\n\n"
        
        if result.get('original_solutions'):
            response += f"**Knowledge Base Solutions Found:** {len(result['original_solutions'])}\n\n"
        
        response += "**STEP-BY-STEP SOLUTION:**\n\n"
        
        for step in result['steps']:
            response += f"• {step}\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error processing query: {str(e)}"

# Main execution
if __name__ == "__main__":
    # Run interactive solver
    interactive_smart_city_solver()