#!/usr/bin/env python3
"""
REST API Cloud Access Script
Uses Google Cloud REST APIs directly to bypass CLI and library issues
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
API_KEY = "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo"
PROJECT_ID = "seven-l-prod"
REGION = "us-central1"

class RestAPICloudAccess:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = "https://storage.googleapis.com"
        self.results = {}
        
    def make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            if params is None:
                params = {}
            params['key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return None
    
    def discover_gcs_buckets(self) -> Dict[str, Any]:
        """Discover GCS buckets using REST API"""
        print("🔍 Discovering GCS buckets with REST API...")
        
        try:
            # List buckets
            url = f"https://storage.googleapis.com/storage/v1/b"
            params = {"project": self.project_id}
            
            response = requests.get(url, params={**params, "key": self.api_key}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                buckets = data.get("items", [])
                
                bucket_info = []
                for bucket in buckets:
                    bucket_name = bucket.get("name", "")
                    print(f"  📦 Found bucket: {bucket_name}")
                    
                    # List objects in bucket with common prefixes
                    prefixes = ["society/", "cloudvr/", "evolution/", "spatial_lab/", "warehouse/", "padres/"]
                    bucket_contents = {}
                    
                    for prefix in prefixes:
                        try:
                            objects_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o"
                            objects_params = {"prefix": prefix, "maxResults": 10}
                            
                            objects_response = requests.get(
                                objects_url, 
                                params={**objects_params, "key": self.api_key}, 
                                timeout=15
                            )
                            
                            if objects_response.status_code == 200:
                                objects_data = objects_response.json()
                                objects = objects_data.get("items", [])
                                if objects:
                                    bucket_contents[prefix] = [obj.get("name", "") for obj in objects]
                                    print(f"    📁 {prefix}: {len(objects)} objects")
                        except Exception as e:
                            print(f"    ⚠️ Error listing {prefix}: {e}")
                    
                    bucket_info.append({
                        "name": bucket_name,
                        "location": bucket.get("location", ""),
                        "created": bucket.get("timeCreated", ""),
                        "contents": bucket_contents
                    })
                
                return {
                    "buckets": bucket_info,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                print(f"❌ Failed to list buckets: {response.status_code} - {response.text}")
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "error"
                }
                
        except Exception as e:
            print(f"❌ Error accessing GCS: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def discover_bigquery_datasets(self) -> Dict[str, Any]:
        """Discover BigQuery datasets using REST API"""
        print("📊 Discovering BigQuery datasets with REST API...")
        
        try:
            url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets"
            
            response = requests.get(url, params={"key": self.api_key}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                datasets = data.get("datasets", [])
                
                dataset_info = []
                for dataset in datasets:
                    dataset_id = dataset.get("datasetReference", {}).get("datasetId", "")
                    print(f"  📋 Found dataset: {dataset_id}")
                    
                    # List tables in dataset
                    try:
                        tables_url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets/{dataset_id}/tables"
                        tables_response = requests.get(tables_url, params={"key": self.api_key}, timeout=15)
                        
                        if tables_response.status_code == 200:
                            tables_data = tables_response.json()
                            tables = tables_data.get("tables", [])
                            table_names = [table.get("tableReference", {}).get("tableId", "") for table in tables]
                            print(f"    📊 Tables: {len(table_names)}")
                            
                            dataset_info.append({
                                "dataset_id": dataset_id,
                                "location": dataset.get("location", ""),
                                "created": dataset.get("creationTime", ""),
                                "tables": table_names
                            })
                        else:
                            print(f"    ⚠️ Error listing tables: {tables_response.status_code}")
                            dataset_info.append({
                                "dataset_id": dataset_id,
                                "error": f"HTTP {tables_response.status_code}"
                            })
                    except Exception as e:
                        print(f"    ⚠️ Error listing tables: {e}")
                        dataset_info.append({
                            "dataset_id": dataset_id,
                            "error": str(e)
                        })
                
                return {
                    "datasets": dataset_info,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                print(f"❌ Failed to list datasets: {response.status_code} - {response.text}")
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "error"
                }
                
        except Exception as e:
            print(f"❌ Error accessing BigQuery: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def discover_cloud_run_services(self) -> Dict[str, Any]:
        """Discover Cloud Run services using REST API"""
        print("🚀 Discovering Cloud Run services with REST API...")
        
        try:
            url = f"https://{REGION}-run.googleapis.com/v2/projects/{self.project_id}/locations/{REGION}/services"
            
            response = requests.get(url, params={"key": self.api_key}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", [])
                
                service_info = []
                for service in services:
                    service_name = service.get("name", "").split("/")[-1]
                    print(f"  🚀 Found service: {service_name}")
                    
                    service_info.append({
                        "name": service_name,
                        "full_name": service.get("name", ""),
                        "uri": service.get("uri", ""),
                        "created": service.get("createTime", ""),
                        "updated": service.get("updateTime", "")
                    })
                
                return {
                    "services": service_info,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                print(f"❌ Failed to list services: {response.status_code} - {response.text}")
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "error"
                }
                
        except Exception as e:
            print(f"❌ Error accessing Cloud Run: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def pull_ai_society_data(self) -> Dict[str, Any]:
        """Pull AI Society specific data from GCS"""
        print("🤖 Pulling AI Society data from GCS...")
        
        try:
            # Look for society data in various buckets
            buckets_to_check = ["7l-data", "7l-jsonl", "7l-pipelines"]
            society_data = {}
            
            for bucket_name in buckets_to_check:
                try:
                    # Look for live observations
                    objects_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o"
                    objects_params = {"prefix": "society/live_observations_", "maxResults": 5}
                    
                    objects_response = requests.get(
                        objects_url, 
                        params={**objects_params, "key": self.api_key}, 
                        timeout=15
                    )
                    
                    if objects_response.status_code == 200:
                        objects_data = objects_response.json()
                        objects = objects_data.get("items", [])
                        if objects:
                            society_data[f"{bucket_name}_observations"] = [obj.get("name", "") for obj in objects]
                            print(f"  📊 Found {len(objects)} observation files in {bucket_name}")
                    
                    # Look for other society data
                    objects_params = {"prefix": "society/", "maxResults": 10}
                    objects_response = requests.get(
                        objects_url, 
                        params={**objects_params, "key": self.api_key}, 
                        timeout=15
                    )
                    
                    if objects_response.status_code == 200:
                        objects_data = objects_response.json()
                        objects = objects_data.get("items", [])
                        if objects:
                            society_data[f"{bucket_name}_all"] = [obj.get("name", "") for obj in objects]
                            print(f"  📁 Found {len(objects)} society files in {bucket_name}")
                            
                except Exception as e:
                    print(f"  ⚠️ Error accessing {bucket_name}: {e}")
            
            return {
                "data": society_data,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error pulling AI Society data: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def pull_spatial_lab_data(self) -> Dict[str, Any]:
        """Pull Spatial Lab specific data from GCS"""
        print("🧠 Pulling Spatial Lab data from GCS...")
        
        try:
            # Look for spatial lab data in various buckets
            buckets_to_check = ["7l-data", "7l-jsonl", "7l-pipelines"]
            spatial_data = {}
            
            for bucket_name in buckets_to_check:
                try:
                    # Look for spatial lab data
                    objects_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o"
                    objects_params = {"prefix": "spatial_lab/", "maxResults": 10}
                    
                    objects_response = requests.get(
                        objects_url, 
                        params={**objects_params, "key": self.api_key}, 
                        timeout=15
                    )
                    
                    if objects_response.status_code == 200:
                        objects_data = objects_response.json()
                        objects = objects_data.get("items", [])
                        if objects:
                            spatial_data[f"{bucket_name}_spatial"] = [obj.get("name", "") for obj in objects]
                            print(f"  🧠 Found {len(objects)} spatial lab files in {bucket_name}")
                    
                    # Look for evaluation results
                    objects_params = {"prefix": "evaluation/", "maxResults": 10}
                    objects_response = requests.get(
                        objects_url, 
                        params={**objects_params, "key": self.api_key}, 
                        timeout=15
                    )
                    
                    if objects_response.status_code == 200:
                        objects_data = objects_response.json()
                        objects = objects_data.get("items", [])
                        if objects:
                            spatial_data[f"{bucket_name}_evaluation"] = [obj.get("name", "") for obj in objects]
                            print(f"  📊 Found {len(objects)} evaluation files in {bucket_name}")
                            
                except Exception as e:
                    print(f"  ⚠️ Error accessing {bucket_name}: {e}")
            
            return {
                "data": spatial_data,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error pulling Spatial Lab data: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("📊 Generating comprehensive report with REST API access...")
        
        # Pull all data
        gcs_data = self.discover_gcs_buckets()
        bigquery_data = self.discover_bigquery_datasets()
        cloud_run_data = self.discover_cloud_run_services()
        ai_society_data = self.pull_ai_society_data()
        spatial_lab_data = self.pull_spatial_lab_data()
        
        # Load local data
        local_data_path = "/Users/carlos/NOUS/results/component_reports/combined_summary.json"
        local_data = {}
        if os.path.exists(local_data_path):
            with open(local_data_path, 'r') as f:
                local_data = json.load(f)
        
        comprehensive_report = {
            "metadata": {
                "project_id": self.project_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "api_key_used": self.api_key,
                "method": "rest_api_direct_access"
            },
            "cloud_infrastructure": {
                "gcs_buckets": gcs_data,
                "bigquery_datasets": bigquery_data,
                "cloud_run_services": cloud_run_data
            },
            "component_data": {
                "ai_society": ai_society_data,
                "spatial_lab": spatial_lab_data
            },
            "local_analysis": local_data,
            "summary": {
                "gcs_buckets_found": len(gcs_data.get("buckets", [])) if gcs_data.get("status") == "success" else 0,
                "bigquery_datasets_found": len(bigquery_data.get("datasets", [])) if bigquery_data.get("status") == "success" else 0,
                "cloud_run_services_found": len(cloud_run_data.get("services", [])) if cloud_run_data.get("status") == "success" else 0,
                "local_components_analyzed": len(local_data.get("highlights", []))
            }
        }
        
        return comprehensive_report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rest_api_cloud_analysis_{timestamp}.json"
        
        filepath = f"/Users/carlos/NOUS/results/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filepath}")
        return filepath

def main():
    """Main execution function"""
    print("🚀 Starting REST API Cloud Access Analysis")
    print("=" * 50)
    
    accessor = RestAPICloudAccess(API_KEY, PROJECT_ID)
    
    try:
        # Generate comprehensive report
        report = accessor.generate_comprehensive_report()
        
        # Save report
        report_path = accessor.save_report(report)
        
        # Print summary
        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 30)
        summary = report["summary"]
        print(f"GCS Buckets: {summary['gcs_buckets_found']}")
        print(f"BigQuery Datasets: {summary['bigquery_datasets_found']}")
        print(f"Cloud Run Services: {summary['cloud_run_services_found']}")
        print(f"Local Components: {summary['local_components_analyzed']}")
        
        print(f"\n✅ REST API cloud access analysis complete! Report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())











