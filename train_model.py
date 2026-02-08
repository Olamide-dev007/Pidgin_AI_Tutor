"""
Model Training Script - Fine-tune GPT-2 on Pidgin English
This trains the AI to understand and respond in Pidgin
"""

import os
import pandas as pd
from datetime import datetime

print("=" * 70)
print("🎓 Pidgin AI Tutor - Model Training Script")
print("=" * 70)

# Check if transformers is installed
try:
    from transformers import (
        GPT2Tokenizer, 
        GPT2LMHeadModel,
        TextDataset,
        DataCollatorForLanguageModeling,
        Trainer,
        TrainingArguments
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("\n⚠️  Warning: Transformers library not installed!")
    print("To train the AI model, you need to install:")
    print("  pip install transformers torch datasets")
    print("\nFor now, you can still use the rule-based responses.")


class PidginModelTrainer:
    def __init__(self, model_name="distilgpt2", output_dir="models/fine_tuned_pidgin"):
        """Initialize the trainer"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Please install transformers and torch first")
            
        self.model_name = model_name
        self.output_dir = output_dir
        
        print(f"\n🤖 Loading base model: {model_name}")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # GPT-2 doesn't have a pad token by default
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("✅ Model loaded successfully!")
    
    def prepare_training_data(self, csv_file="data/pidgin_dataset.csv", 
                            output_file="data/training_data.txt"):
        """Convert CSV conversations to training format"""
        print(f"\n📝 Preparing training data from {csv_file}")
        
        if not os.path.exists(csv_file):
            print(f"❌ Error: {csv_file} not found!")
            print("Run: python data_collection.py first")
            return None
        
        df = pd.read_csv(csv_file)
        
        os.makedirs("data", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                # Create conversation format
                conversation = (
                    f"<|user|> {row['user_input']} "
                    f"<|bot|> {row['bot_response']} "
                    f"<|endoftext|>\n"
                )
                f.write(conversation)
        
        print(f"✅ Prepared {len(df)} conversations")
        print(f"💾 Saved to {output_file}")
        return output_file
    
    def create_dataset(self, file_path, block_size=128):
        """Create a TextDataset for training"""
        return TextDataset(
            tokenizer=self.tokenizer,
            file_path=file_path,
            block_size=block_size
        )
    
    def train(self, train_file="data/training_data.txt", 
              num_epochs=5, 
              batch_size=4,
              learning_rate=5e-5,
              save_steps=50):
        """Train the model"""
        print(f"\n🏋️ Starting training...")
        print(f"  Epochs: {num_epochs}")
        print(f"  Batch size: {batch_size}")
        print(f"  Learning rate: {learning_rate}")
        
        if not os.path.exists(train_file):
            print(f"❌ Training file not found: {train_file}")
            return False
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create dataset
        train_dataset = self.create_dataset(train_file)
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=save_steps,
            save_total_limit=2,
            learning_rate=learning_rate,
            warmup_steps=50,
            logging_steps=25,
            logging_dir='./logs',
            prediction_loss_only=True,
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=train_dataset,
        )
        
        # Train!
        print("\n🚀 Training started...")
        print("This may take 15-30 minutes depending on your computer.")
        print("You'll see progress updates below:\n")
        
        try:
            trainer.train()
            
            # Save final model
            print(f"\n💾 Saving model to {self.output_dir}")
            trainer.save_model(self.output_dir)
            self.tokenizer.save_pretrained(self.output_dir)
            
            print("\n✅ Training complete!")
            print(f"📁 Model saved in: {self.output_dir}")
            return True
            
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            return False
    
    def test_model(self, prompt="<|user|> Wetin be Python? <|bot|>", max_length=100):
        """Test the trained model"""
        print(f"\n🧪 Testing model...")
        print(f"Prompt: {prompt}")
        
        self.model.eval()
        
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(output[0], skip_special_tokens=False)
        print(f"\nGenerated: {response}")
        
        return response


def main():
    """Main training pipeline"""
    print("\n" + "=" * 70)
    
    if not TRANSFORMERS_AVAILABLE:
        print("\n❌ Cannot train model without transformers library")
        print("\nTo install, run:")
        print("  pip install transformers torch datasets")
        print("\nAfter installation, run this script again.")
        return
    
    # Check if data exists
    if not os.path.exists("data/pidgin_dataset.csv"):
        print("\n❌ Error: data/pidgin_dataset.csv not found!")
        print("Run data_collection.py first to create the dataset.")
        return
    
    # Check dataset size
    df = pd.read_csv("data/pidgin_dataset.csv")
    print(f"\n📊 Dataset contains {len(df)} conversations")
    
    if len(df) < 20:
        print("\n⚠️  Warning: Dataset is very small!")
        print("For better results, aim for 100+ conversation pairs.")
        print("You can:")
        print("1. Continue with current data (results may be limited)")
        print("2. Add more data first (recommended)")
        response = input("\nContinue training? (y/n): ").strip().lower()
        if response != 'y':
            print("Training cancelled. Add more data and try again.")
            return
    
    # Initialize trainer
    trainer = PidginModelTrainer(
        model_name="distilgpt2",
        output_dir="models/fine_tuned_pidgin"
    )
    
    # Prepare data
    train_file = trainer.prepare_training_data(
        csv_file="data/pidgin_dataset.csv",
        output_file="data/training_data.txt"
    )
    
    if not train_file:
        return
    
    # Confirm training
    print("\n" + "=" * 70)
    print("⚠️  Training will take 15-30 minutes")
    print("Your computer may run hot and fan may be loud")
    print("=" * 70)
    
    response = input("\nStart training? (y/n): ").strip().lower()
    if response != 'y':
        print("Training cancelled.")
        return
    
    # Train model
    success = trainer.train(
        train_file=train_file,
        num_epochs=5,
        batch_size=4,
        learning_rate=5e-5,
        save_steps=50
    )
    
    if not success:
        return
    
    # Test the model
    print("\n" + "=" * 70)
    test_prompts = [
        "<|user|> Wetin be Python? <|bot|>",
        "<|user|> How I go add 5 + 3? <|bot|>",
        "<|user|> Teach me about variables <|bot|>"
    ]
    
    print("\n🧪 Testing trained model with sample prompts...")
    for prompt in test_prompts:
        trainer.test_model(prompt, max_length=150)
        print("\n" + "-" * 70)
    
    print("\n✅ All done! Your model is ready to use.")
    print(f"📁 Model location: models/fine_tuned_pidgin/")
    print("\nNext step: Run the web app!")
    print("  streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()