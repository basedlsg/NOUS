#!/usr/bin/env python3
"""
Simplified Spatial Shape vs Metadata Experiment for Cloud Run
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpatialObject:
    """Represents a spatial object with shape and metadata"""
    id: str
    shape: str
    color: str
    size: str
    position: tuple
    metadata: Dict[str, Any]


@dataclass
class SpatialTask:
    """Represents a spatial reasoning task"""
    task_id: str
    description: str
    reference_object: SpatialObject
    target_objects: List[SpatialObject]
    instruction_type: str


class SimpleSpatialExperiment:
    """Simplified spatial experiment class"""
    
    def __init__(self, num_trials: int = 1000):
        self.num_trials = num_trials
        self.results = []
        self.shape_prioritization_count = 0
        self.metadata_prioritization_count = 0
        
        self.shapes = ['cube', 'sphere', 'cylinder', 'pyramid']
        self.colors = ['red', 'blue', 'green', 'yellow']
        self.sizes = ['small', 'medium', 'large']
        
        logger.info(f"Initialized simple experiment with {num_trials} trials")
    
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
    
    async def simulate_llm_response(self, task: SpatialTask) -> Dict[str, Any]:
        """Simulate LLM response based on prioritization behavior"""
        
        selected_objects = []
        reasoning = ""
        
        if task.instruction_type == 'shape_priority':
            shape_matches = [obj for obj in task.target_objects if obj.shape == task.reference_object.shape]
            metadata_matches = [obj for obj in task.target_objects if obj.metadata['priority'] == task.reference_object.metadata['priority']]
            
            selected_objects = [obj.id for obj in shape_matches[:3]]
            if len(selected_objects) < 3:
                remaining = [obj for obj in task.target_objects if obj.id not in selected_objects]
                selected_objects.extend([obj.id for obj in remaining[:3-len(selected_objects)]])
            
            reasoning = f"Selected objects based on shape similarity to {task.reference_object.shape}. Found {len(shape_matches)} shape matches."
            
        else:
            shape_matches = [obj for obj in task.target_objects if obj.shape == task.reference_object.shape]
            metadata_matches = [obj for obj in task.target_objects if obj.metadata['priority'] == task.reference_object.metadata['priority']]
            
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
        
        selected_objs = [obj for obj in task.target_objects if obj.id in selected_objects]
        
        shape_matches = len([obj for obj in selected_objs if obj.shape == task.reference_object.shape])
        metadata_matches = len([obj for obj in selected_objs if obj.metadata['priority'] == task.reference_object.metadata['priority']])
        
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
        
        if trial_num % 100 == 0:
            logger.info(f"Running trial {trial_num + 1}/{self.num_trials}")
        
        objects = self.create_spatial_objects()
        instruction_type = random.choice(['shape_priority', 'metadata_priority'])
        task = self.create_spatial_task(objects, instruction_type)
        
        response = await self.simulate_llm_response(task)
        analysis = self.analyze_response(task, response)
        
        trial_result = {
            'trial_number': trial_num + 1,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis
        }
        
        self.results.append(trial_result)
        return trial_result
    
    async def run_experiment(self) -> Dict[str, Any]:
        """Run the complete experiment"""
        
        logger.info(f"Starting simple spatial experiment with {self.num_trials} trials")
        start_time = time.time()
        
        for trial in range(self.num_trials):
            await self.run_single_trial(trial)
        
        total_time = time.time() - start_time
        
        shape_priority_tasks = [r for r in self.results if r['analysis']['task_type'] == 'shape_priority']
        metadata_priority_tasks = [r for r in self.results if r['analysis']['task_type'] == 'metadata_priority']
        
        shape_accuracy = sum(1 for r in shape_priority_tasks if r['analysis']['correct_prioritization']) / len(shape_priority_tasks) if shape_priority_tasks else 0
        metadata_accuracy = sum(1 for r in metadata_priority_tasks if r['analysis']['correct_prioritization']) / len(metadata_priority_tasks) if metadata_priority_tasks else 0
        overall_accuracy = sum(1 for r in self.results if r['analysis']['correct_prioritization']) / len(self.results)
        
        llm_prioritization = "shape" if self.shape_prioritization_count > self.metadata_prioritization_count else "metadata"
        prioritization_strength = abs(self.shape_prioritization_count - self.metadata_prioritization_count) / self.num_trials
        
        experiment_results = {
            'experiment_info': {
                'num_trials': self.num_trials,
                'start_time': datetime.now().isoformat(),
                'duration_seconds': total_time,
                'llm_prioritization': llm_prioritization,
                'prioritization_strength': prioritization_strength
            },
            'statistics': {
                'shape_priority_tasks': len(shape_priority_tasks),
                'metadata_priority_tasks': len(metadata_priority_tasks),
                'shape_accuracy': shape_accuracy,
                'metadata_accuracy': metadata_accuracy,
                'overall_accuracy': overall_accuracy,
                'shape_prioritization_count': self.shape_prioritization_count,
                'metadata_prioritization_count': self.metadata_prioritization_count
            }
        }
        
        logger.info(f"Experiment completed in {total_time:.2f} seconds")
        logger.info(f"LLM prioritizes: {llm_prioritization} (strength: {prioritization_strength:.2f})")
        logger.info(f"Overall accuracy: {overall_accuracy:.2%}")
        
        return experiment_results





