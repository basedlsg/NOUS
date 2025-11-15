#!/usr/bin/env python3
"""
Autonomous Spatial Shape vs Metadata Prioritization Experiment

This experiment runs autonomously in Google Cloud and can handle large-scale
experiments with real LLM API calls and cloud storage integration.
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
import requests
from google.cloud import storage
import openai
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpatialObject:
    """Represents a spatial object with shape and metadata"""
    id: str
    shape: str  # 'cube', 'sphere', 'cylinder', 'pyramid'
    color: str  # 'red', 'blue', 'green', 'yellow'
    size: str   # 'small', 'medium', 'large'
    position: tuple  # (x, y, z)
    metadata: Dict[str, Any]  # Additional metadata


@dataclass
class SpatialTask:
    """Represents a spatial reasoning task"""
    task_id: str
    description: str
    reference_object: SpatialObject
    target_objects: List[SpatialObject]
    instruction_type: str  # 'shape_priority' or 'metadata_priority'


class AutonomousSpatialExperiment:
    """Autonomous spatial experiment class with cloud integration"""
    
    def __init__(self, num_trials: int = 1000):
        self.num_trials = num_trials
        self.results = []
        self.shape_prioritization_count = 0
        self.metadata_prioritization_count = 0
        
        # Initialize shapes and metadata options
        self.shapes = ['cube', 'sphere', 'cylinder', 'pyramid']
        self.colors = ['red', 'blue', 'green', 'yellow']
        self.sizes = ['small', 'medium', 'large']
        
        # Cloud configuration
        self.output_bucket = os.getenv('OUTPUT_BUCKET', 'gs://your-bucket-name')
        self.project_id = os.getenv('PROJECT_ID', 'your-project-id')
        
        # LLM configuration
        self.llm_provider = os.getenv('LLM_PROVIDER', 'simulation')  # 'openai', 'groq', 'simulation'
        self.setup_llm_clients()
        
        logger.info(f"Initialized autonomous experiment with {num_trials} trials")
        logger.info(f"LLM Provider: {self.llm_provider}")
        logger.info(f"Output Bucket: {self.output_bucket}")
    
    def setup_llm_clients(self):
        """Setup LLM API clients based on configuration"""
        self.llm_client = None
        
        if self.llm_provider == 'openai':
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                logger.warning("OpenAI API key not found, falling back to simulation")
                self.llm_provider = 'simulation'
        
        elif self.llm_provider == 'groq':
            groq_api_key = os.getenv('GROQ_API_KEY')
            if groq_api_key:
                self.llm_client = Groq(api_key=groq_api_key)
            else:
                logger.warning("Groq API key not found, falling back to simulation")
                self.llm_provider = 'simulation'
        
        logger.info(f"LLM client setup complete: {self.llm_provider}")
    
    def create_spatial_objects(self, num_objects: int = 10) -> List[SpatialObject]:
        """Create a set of spatial objects for testing"""
        objects = []
        
        for i in range(num_objects):
            obj = SpatialObject(
                id=f"obj_{i}",
                shape=random.choice(self.shapes),
                color=random.choice(self.colors),
                size=random.choice(self.sizes),
                position=(random.uniform(0, 10), random.uniform(0, 10), random.uniform(0, 3)),
                metadata={
                    'weight': random.uniform(0.1, 5.0),
                    'material': random.choice(['metal', 'plastic', 'wood', 'glass']),
                    'priority': random.choice(['low', 'medium', 'high']),
                    'category': random.choice(['fragile', 'heavy', 'urgent', 'standard'])
                }
            )
            objects.append(obj)
        
        return objects
    
    def create_spatial_task(self, objects: List[SpatialObject], instruction_type: str) -> SpatialTask:
        """Create a spatial reasoning task"""
        reference_obj = random.choice(objects)
        target_objects = random.sample(objects, min(5, len(objects)))
        
        # Ensure target objects include both shape matches and metadata matches
        shape_matches = [obj for obj in target_objects if obj.shape == reference_obj.shape]
        metadata_matches = [obj for obj in target_objects if obj.metadata['priority'] == reference_obj.metadata['priority']]
        
        # If no matches exist, create them
        if not shape_matches:
            target_objects[0].shape = reference_obj.shape
        if not metadata_matches:
            target_objects[1].metadata['priority'] = reference_obj.metadata['priority']
        
        task = SpatialTask(
            task_id=f"task_{len(self.results)}_{instruction_type}",
            description=f"Find objects that match the reference object's {instruction_type}",
            reference_object=reference_obj,
            target_objects=target_objects,
            instruction_type=instruction_type
        )
        
        return task
    
    def create_llm_prompt(self, task: SpatialTask) -> str:
        """Create a prompt for the LLM to test spatial reasoning"""
        
        # Create object descriptions
        reference_desc = f"""
Reference Object:
- ID: {task.reference_object.id}
- Shape: {task.reference_object.shape}
- Color: {task.reference_object.color}
- Size: {task.reference_object.size}
- Position: {task.reference_object.position}
- Metadata: {task.reference_object.metadata}
"""
        
        target_descs = []
        for obj in task.target_objects:
            desc = f"""
Object {obj.id}:
- Shape: {obj.shape}
- Color: {obj.color}
- Size: {obj.size}
- Position: {obj.position}
- Metadata: {obj.metadata}
"""
            target_descs.append(desc)
        
        # Create instruction based on task type
        if task.instruction_type == 'shape_priority':
            instruction = "Based on the reference object, identify which objects match its SHAPE. Prioritize shape similarity over other attributes."
        else:
            instruction = "Based on the reference object, identify which objects match its METADATA (priority level). Prioritize metadata similarity over physical attributes."
        
        prompt = f"""You are a warehouse robot making spatial reasoning decisions.

{reference_desc}

Available Objects:
{''.join(target_descs)}

Task: {instruction}

Which objects would you select? Respond with a JSON array of object IDs, ordered by your priority.
Example: ["obj_1", "obj_3", "obj_7"]

Reasoning: Briefly explain your selection criteria."""
        
        return prompt
    
    async def call_real_llm(self, prompt: str) -> Dict[str, Any]:
        """Call a real LLM API"""
        
        try:
            if self.llm_provider == 'openai':
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256,
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            elif self.llm_provider == 'groq':
                response = self.llm_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256,
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
            
            # Parse the response
            try:
                # Extract JSON from response
                import re
                json_match = re.search(r'\[.*?\]', content, re.DOTALL)
                if json_match:
                    selected_objects = json.loads(json_match.group())
                else:
                    selected_objects = []
                
                # Extract reasoning
                reasoning_match = re.search(r'Reasoning:\s*(.*)', content, re.IGNORECASE)
                reasoning = reasoning_match.group(1) if reasoning_match else "No reasoning provided"
                
                return {
                    'selected_objects': selected_objects,
                    'reasoning': reasoning,
                    'raw_response': content
                }
            
            except json.JSONDecodeError:
                return {
                    'selected_objects': [],
                    'reasoning': "Failed to parse response",
                    'raw_response': content
                }
        
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return {
                'selected_objects': [],
                'reasoning': f"API call failed: {str(e)}",
                'raw_response': ""
            }
    
    async def simulate_llm_response(self, task: SpatialTask) -> Dict[str, Any]:
        """Simulate LLM response based on prioritization behavior"""
        
        # Simulate LLM decision making
        # In a real experiment, this would call an actual LLM API
        
        selected_objects = []
        reasoning = ""
        
        if task.instruction_type == 'shape_priority':
            # Simulate shape prioritization
            shape_matches = [obj for obj in task.target_objects if obj.shape == task.reference_object.shape]
            metadata_matches = [obj for obj in task.target_objects if obj.metadata['priority'] == task.reference_object.metadata['priority']]
            
            # Prioritize shape matches
            selected_objects = [obj.id for obj in shape_matches[:3]]
            if len(selected_objects) < 3:
                remaining = [obj for obj in task.target_objects if obj.id not in selected_objects]
                selected_objects.extend([obj.id for obj in remaining[:3-len(selected_objects)]])
            
            reasoning = f"Selected objects based on shape similarity to {task.reference_object.shape}. Found {len(shape_matches)} shape matches."
            
        else:
            # Simulate metadata prioritization
            shape_matches = [obj for obj in task.target_objects if obj.shape == task.reference_object.shape]
            metadata_matches = [obj for obj in task.target_objects if obj.metadata['priority'] == task.reference_object.metadata['priority']]
            
            # Prioritize metadata matches
            selected_objects = [obj.id for obj in metadata_matches[:3]]
            if len(selected_objects) < 3:
                remaining = [obj for obj in task.target_objects if obj.id not in selected_objects]
                selected_objects.extend([obj.id for obj in remaining[:3-len(selected_objects)]])
            
            reasoning = f"Selected objects based on metadata priority '{task.reference_object.metadata['priority']}'. Found {len(metadata_matches)} metadata matches."
        
        return {
            'selected_objects': selected_objects,
            'reasoning': reasoning,
            'task_type': task.instruction_type
        }
    
    def analyze_response(self, task: SpatialTask, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the LLM response to determine prioritization behavior"""
        
        selected_objects = response['selected_objects']
        task_type = response['task_type']
        
        # Get the actual selected objects
        selected_objs = [obj for obj in task.target_objects if obj.id in selected_objects]
        
        # Count matches
        shape_matches = len([obj for obj in selected_objs if obj.shape == task.reference_object.shape])
        metadata_matches = len([obj for obj in selected_objs if obj.metadata['priority'] == task.reference_object.metadata['priority']])
        
        # Determine if the response prioritized the correct attribute
        correct_prioritization = False
        if task_type == 'shape_priority' and shape_matches >= metadata_matches:
            correct_prioritization = True
            self.shape_prioritization_count += 1
        elif task_type == 'metadata_priority' and metadata_matches >= shape_matches:
            correct_prioritization = True
            self.metadata_prioritization_count += 1
        
        analysis = {
            'task_id': task.task_id,
            'task_type': task_type,
            'selected_objects': selected_objects,
            'shape_matches': shape_matches,
            'metadata_matches': metadata_matches,
            'correct_prioritization': correct_prioritization,
            'reasoning': response['reasoning'],
            'reference_object': {
                'id': task.reference_object.id,
                'shape': task.reference_object.shape,
                'priority': task.reference_object.metadata['priority']
            }
        }
        
        return analysis
    
    async def run_single_trial(self, trial_num: int) -> Dict[str, Any]:
        """Run a single trial of the experiment"""
        
        if trial_num % 10 == 0:
            logger.info(f"Running trial {trial_num + 1}/{self.num_trials}")
        
        # Create objects and task
        objects = self.create_spatial_objects()
        instruction_type = random.choice(['shape_priority', 'metadata_priority'])
        task = self.create_spatial_task(objects, instruction_type)
        
        # Create prompt and get response
        prompt = self.create_llm_prompt(task)
        
        if self.llm_provider == 'simulation':
            response = await self.simulate_llm_response(task)
        else:
            response = await self.call_real_llm(prompt)
            response['task_type'] = task.instruction_type
        
        # Analyze response
        analysis = self.analyze_response(task, response)
        
        trial_result = {
            'trial_number': trial_num + 1,
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'response': response,
            'analysis': analysis
        }
        
        self.results.append(trial_result)
        
        return trial_result
    
    async def run_experiment(self) -> Dict[str, Any]:
        """Run the complete experiment"""
        
        logger.info(f"Starting autonomous spatial shape vs metadata experiment with {self.num_trials} trials")
        start_time = time.time()
        
        # Run all trials
        for trial in range(self.num_trials):
            await self.run_single_trial(trial)
        
        # Calculate final results
        total_time = time.time() - start_time
        
        # Calculate statistics
        shape_priority_tasks = [r for r in self.results if r['analysis']['task_type'] == 'shape_priority']
        metadata_priority_tasks = [r for r in self.results if r['analysis']['task_type'] == 'metadata_priority']
        
        shape_accuracy = sum(1 for r in shape_priority_tasks if r['analysis']['correct_prioritization']) / len(shape_priority_tasks) if shape_priority_tasks else 0
        metadata_accuracy = sum(1 for r in metadata_priority_tasks if r['analysis']['correct_prioritization']) / len(metadata_priority_tasks) if metadata_priority_tasks else 0
        
        overall_accuracy = sum(1 for r in self.results if r['analysis']['correct_prioritization']) / len(self.results)
        
        # Determine which the LLM prioritizes more
        llm_prioritization = "shape" if self.shape_prioritization_count > self.metadata_prioritization_count else "metadata"
        prioritization_strength = abs(self.shape_prioritization_count - self.metadata_prioritization_count) / self.num_trials
        
        experiment_results = {
            'experiment_info': {
                'num_trials': self.num_trials,
                'start_time': datetime.now().isoformat(),
                'duration_seconds': total_time,
                'llm_provider': self.llm_provider,
                'llm_prioritization': llm_prioritization,
                'prioritization_strength': prioritization_strength,
                'cloud_deployment': True
            },
            'statistics': {
                'shape_priority_tasks': len(shape_priority_tasks),
                'metadata_priority_tasks': len(metadata_priority_tasks),
                'shape_accuracy': shape_accuracy,
                'metadata_accuracy': metadata_accuracy,
                'overall_accuracy': overall_accuracy,
                'shape_prioritization_count': self.shape_prioritization_count,
                'metadata_prioritization_count': self.metadata_prioritization_count
            },
            'trials': self.results
        }
        
        logger.info(f"Experiment completed in {total_time:.2f} seconds")
        logger.info(f"LLM prioritizes: {llm_prioritization} (strength: {prioritization_strength:.2f})")
        logger.info(f"Overall accuracy: {overall_accuracy:.2%}")
        
        return experiment_results
    
    def upload_to_cloud_storage(self, results: Dict[str, Any]) -> str:
        """Upload results to Google Cloud Storage"""
        
        try:
            # Initialize Cloud Storage client
            client = storage.Client(project=self.project_id)
            
            # Extract bucket name from the output bucket URL
            bucket_name = self.output_bucket.replace('gs://', '').split('/')[0]
            bucket = client.bucket(bucket_name)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"autonomous_spatial_experiment_{timestamp}.json"
            
            # Upload results
            blob = bucket.blob(filename)
            blob.upload_from_string(json.dumps(results, indent=2, default=str))
            
            logger.info(f"Results uploaded to: gs://{bucket_name}/{filename}")
            return f"gs://{bucket_name}/{filename}"
        
        except Exception as e:
            logger.error(f"Failed to upload to cloud storage: {e}")
            return None
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save experiment results to file and cloud storage"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"autonomous_spatial_experiment_{timestamp}.json"
        
        # Save locally
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved locally to: {filename}")
        
        # Upload to cloud storage
        cloud_url = self.upload_to_cloud_storage(results)
        
        return filename


async def main():
    """Main function to run the autonomous experiment"""
    
    print("🧪 AUTONOMOUS SPATIAL SHAPE VS METADATA PRIORITIZATION EXPERIMENT")
    print("=" * 70)
    
    # Get configuration from environment variables
    num_trials = int(os.getenv('NUM_TRIALS', '1000'))
    experiment_mode = os.getenv('EXPERIMENT_MODE', 'autonomous')
    
    print(f"📊 Experiment Mode: {experiment_mode}")
    print(f"🔢 Number of Trials: {num_trials}")
    
    # Initialize experiment
    experiment = AutonomousSpatialExperiment(num_trials=num_trials)
    
    # Run experiment
    results = await experiment.run_experiment()
    
    # Save results
    filename = experiment.save_results(results)
    
    # Print summary
    print(f"\n📊 EXPERIMENT RESULTS:")
    print(f"   Total trials: {results['experiment_info']['num_trials']}")
    print(f"   Duration: {results['experiment_info']['duration_seconds']:.2f} seconds")
    print(f"   LLM Provider: {results['experiment_info']['llm_provider']}")
    print(f"   LLM prioritizes: {results['experiment_info']['llm_prioritization']}")
    print(f"   Prioritization strength: {results['experiment_info']['prioritization_strength']:.2f}")
    print(f"   Overall accuracy: {results['statistics']['overall_accuracy']:.2%}")
    print(f"   Shape accuracy: {results['statistics']['shape_accuracy']:.2%}")
    print(f"   Metadata accuracy: {results['statistics']['metadata_accuracy']:.2%}")
    
    print(f"\n📁 Results saved to: {filename}")
    print("\n✅ Autonomous experiment completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
