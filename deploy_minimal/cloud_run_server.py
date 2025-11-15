#!/usr/bin/env python3
"""
Cloud Run Server for Autonomous Spatial Experiment
"""

import os
import json
import asyncio
from flask import Flask, jsonify, request
from simple_spatial_experiment import SimpleSpatialExperiment

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "autonomous-spatial-experiment",
        "message": "Ready to run spatial shape vs metadata experiments"
    })

@app.route('/run-experiment', methods=['POST'])
def run_experiment():
    """Run the autonomous spatial experiment"""
    try:
        # Get parameters from request
        data = request.get_json() or {}
        num_trials = data.get('num_trials', 1000)
        llm_provider = data.get('llm_provider', 'simulation')
        
        # Set environment variables
        os.environ['NUM_TRIALS'] = str(num_trials)
        os.environ['LLM_PROVIDER'] = llm_provider
        os.environ['EXPERIMENT_MODE'] = 'cloud'
        
        # Run the experiment
        experiment = SimpleSpatialExperiment(num_trials=num_trials)
        results = asyncio.run(experiment.run_experiment())
        
        return jsonify({
            "status": "success",
            "message": "Experiment completed successfully",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/run-experiment', methods=['GET'])
def run_experiment_get():
    """Run experiment with GET request (for easy triggering)"""
    try:
        # Get parameters from query string
        num_trials = int(request.args.get('trials', 1000))
        llm_provider = request.args.get('provider', 'simulation')
        
        # Set environment variables
        os.environ['NUM_TRIALS'] = str(num_trials)
        os.environ['LLM_PROVIDER'] = llm_provider
        os.environ['EXPERIMENT_MODE'] = 'cloud'
        
        # Run the experiment
        experiment = SimpleSpatialExperiment(num_trials=num_trials)
        results = asyncio.run(experiment.run_experiment())
        
        return jsonify({
            "status": "success",
            "message": f"Experiment completed with {num_trials} trials",
            "summary": {
                "total_trials": results['experiment_info']['num_trials'],
                "duration_seconds": results['experiment_info']['duration_seconds'],
                "llm_prioritization": results['experiment_info']['llm_prioritization'],
                "prioritization_strength": results['experiment_info']['prioritization_strength'],
                "overall_accuracy": results['statistics']['overall_accuracy'],
                "shape_accuracy": results['statistics']['shape_accuracy'],
                "metadata_accuracy": results['statistics']['metadata_accuracy']
            },
            "full_results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
