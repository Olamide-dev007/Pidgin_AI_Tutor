"""
Pidgin AI Chatbot Engine
Handles conversation, context, and response generation
"""

import os
import re
from datetime import datetime
import json

# Try to import transformers
try:
    from transformers import GPT2Tokenizer, GPT2LMHeadModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class PidginChatbot:
    def __init__(self, model_path="models/fine_tuned_pidgin"):
        """Initialize the chatbot"""
        self.model_path = model_path
        self.conversation_history = []
        self.max_history = 5
        
        # Check if model exists
        if os.path.exists(model_path) and TRANSFORMERS_AVAILABLE:
            print(f"🤖 Loading chatbot from {model_path}...")
            try:
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
                self.model = GPT2LMHeadModel.from_pretrained(model_path)
                self.model.eval()
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model_loaded = True
                print("✅ AI model loaded successfully!")
            except Exception as e:
                print(f"⚠️  Could not load model: {e}")
                self.model_loaded = False
        else:
            self.model_loaded = False
            if not TRANSFORMERS_AVAILABLE:
                print("⚠️  Transformers not installed. Using rule-based responses.")
            else:
                print(f"⚠️  Model not found at {model_path}. Using rule-based responses.")
        
        # Keywords for intent detection
        self.math_keywords = [
            'add', 'subtract', 'multiply', 'divide', 'calculate', 'solve',
            'algebra', 'fraction', 'equation', 'math', 'number', 'count',
            'plus', 'minus', 'times', 'divided', '+', '-', '×', '÷', '*', '/'
        ]
        
        self.coding_keywords = [
            'code', 'programming', 'python', 'variable', 'function', 'loop',
            'if', 'else', 'for', 'while', 'print', 'input', 'class',
            'coding', 'program', 'script', 'debug', 'list', 'string'
        ]
    
    def detect_intent(self, user_input):
        """Detect if user wants math or coding help"""
        user_lower = user_input.lower()
        
        math_score = sum(1 for word in self.math_keywords if word in user_lower)
        coding_score = sum(1 for word in self.coding_keywords if word in user_lower)
        
        if math_score > coding_score:
            return 'math'
        elif coding_score > math_score:
            return 'coding'
        else:
            return 'general'
    
    def clean_response(self, response):
        """Clean up generated response"""
        if '<|bot|>' in response:
            response = response.split('<|bot|>')[-1]
        
        response = response.replace('<|endoftext|>', '')
        response = response.replace('<|user|>', '')
        response = response.strip()
        
        if len(response) > 300:
            sentences = re.split(r'[.!?]', response)
            response = '. '.join(sentences[:2]) + '.'
        
        return response.strip()
    
    def generate_response(self, user_input, max_length=150, temperature=0.7):
        """Generate a response to user input"""
        intent = self.detect_intent(user_input)
        
        # Use AI model if available
        if self.model_loaded:
            prompt = self._build_prompt(user_input, intent)
            
            input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
            
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_length=len(input_ids[0]) + max_length,
                    num_return_sequences=1,
                    no_repeat_ngram_size=3,
                    temperature=temperature,
                    top_k=50,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.encode('<|endoftext|>')[0]
                )
            
            full_response = self.tokenizer.decode(output[0], skip_special_tokens=False)
            clean_response = self.clean_response(full_response)
        else:
            # Fallback to rule-based responses
            clean_response = RuleBasedFallback.get_response(user_input)
            if not clean_response:
                clean_response = "I dey learn to answer that question. For now, try ask me about basic Math or Python coding!"
        
        # Update history
        self._update_history(user_input, clean_response, intent)
        
        return clean_response
    
    def _build_prompt(self, user_input, intent):
        """Build prompt with conversation history"""
        prompt = ""
        
        for exchange in self.conversation_history[-3:]:
            prompt += f"<|user|> {exchange['user']} <|bot|> {exchange['bot']} <|endoftext|>\n"
        
        prompt += f"<|user|> {user_input} <|bot|>"
        
        return prompt
    
    def _update_history(self, user_input, bot_response, intent):
        """Update conversation history"""
        self.conversation_history.append({
            'user': user_input,
            'bot': bot_response,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_history(self):
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def save_conversation(self, filename="conversation_log.json"):
        """Save conversation to file"""
        os.makedirs("data", exist_ok=True)
        filepath = f"data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        print(f"💾 Conversation saved to {filepath}")


class RuleBasedFallback:
    """Fallback responses when model is not available"""
    
    RESPONSES = {
        # Greetings
        'hello': "Hello! How you dey? I be AI wey dey teach Mathematics and Coding for Pidgin. Wetin you wan learn today?",
        'hi': "Hi! I dey here to help you learn Math and Coding. You fit ask me anything!",
        'good morning': "Good morning! Hope you dey ready to learn something new today?",
        'good afternoon': "Good afternoon! Wetin you wan learn this afternoon?",
        'good evening': "Good evening! How your day been? Make we learn something!",
        
        # Math basics
        'addition': "Addition na when you dey put numbers together. Like 2 + 3 = 5. You wan practice?",
        'add': "Addition na when you dey put numbers together. Like 5 + 7 = 12. You wan try?",
        'subtraction': "Subtraction na when you dey remove number from another number. Like 10 - 3 = 7. Make I give you example?",
        'subtract': "To subtract mean say you dey minus. Like 15 - 6 = 9. You understand?",
        'multiplication': "Multiplication na when you dey add same number many times. Like 4 × 3 = 12 (4 + 4 + 4). You wan learn more?",
        'multiply': "To multiply mean say you dey times. Like 6 × 5 = 30. E easy!",
        'division': "Division na when you dey share something equally. Like 12 ÷ 3 = 4. Make I explain more?",
        'divide': "To divide mean say you dey share. Like 20 ÷ 5 = 4. You fit try?",
        'algebra': "Algebra na mathematics wey dey use letters like x and y. E dey help us solve problems wey we never know some numbers.",
        'fraction': "Fraction na part of whole thing. Like 1/2 na half. 1/4 na quarter. E dey show how you cut something into pieces.",
        
        # Coding basics
        'python': "Python na very good programming language! E easy to learn and e dey powerful. You wan start learn Python?",
        'programming': "Programming na when you dey write instructions for computer. E be like you dey teach computer how to do something.",
        'coding': "Coding na same thing as programming. You dey write code make computer understand wetin to do.",
        'variable': "Variable na like box wey you fit keep information inside for your code. For Python, you write am like: name = 'Chidi'",
        'function': "Function na block of code wey you fit use many times. E be like shortcut wey dey do specific work.",
        'loop': "Loop na when you wan make computer repeat something many times. E dey save time!",
        'if statement': "If statement dey help computer make decision. Like 'if age >= 18, print You fit vote'.",
        'list': "List na like basket wey you fit put many things inside. For Python: fruits = ['apple', 'banana', 'orange']",
        
        # General
        'help': "I fit help you with:\n1. Mathematics (Addition, Subtraction, Algebra, etc.)\n2. Coding (Python basics, Variables, Loops, etc.)\n\nJust ask me anything!",
        'thank': "You dey welcome! I happy say I fit help you. You get another question?",
        'thanks': "No problem at all! If you need more help, just ask me!",
        'bye': "Bye bye! Come back anytime you wan learn something new. I go dey here!",
        'goodbye': "Goodbye! Hope you don learn something new. See you next time!",
    }
    
    @staticmethod
    def get_response(user_input):
        """Try to match user input to a fallback response"""
        user_lower = user_input.lower()
        
        for key, response in RuleBasedFallback.RESPONSES.items():
            if key in user_lower:
                return response
        
        return None


# Test the chatbot
if __name__ == "__main__":
    print("🧪 Testing Pidgin Chatbot\n")
    
    bot = PidginChatbot()
    
    test_inputs = [
        "Hello",
        "Wetin be Python?",
        "How I go add 15 and 27?",
        "Teach me about variables",
        "Thank you"
    ]
    
    print("=" * 70)
    for user_input in test_inputs:
        print(f"\n👤 User: {user_input}")
        response = bot.generate_response(user_input)
        print(f"🤖 Bot: {response}")
        print("-" * 70)