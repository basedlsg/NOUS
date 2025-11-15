#!/usr/bin/env python3
"""
Direct Cloud Access Script
Uses Google Cloud client libraries to bypass CLI timeout issues
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Set up environment
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'seven-l-prod'

try:
    from google.cloud import storage
    from google.cloud import bigquery
    from google.cloud import logging
    from google.cloud import pubsub_v1
    from google.cloud import run_v2
except ImportError as e:
    print(f"Missing Google Cloud libraries: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.run(['pip', 'install', 'google-cloud-storage', 'google-cloud-bigquery', 'google-cloud-logging', 'google-cloud-pubsub', 'google-cloud-run'], check=True)
    from google.cloud import storage
    from google.cloud import bigquery
    from google.cloud import logging
    from google.cloud import pubsub_v1
    from google.cloud import run_v2

class DirectCloudAccess:
    def __init__(self, project_id: str = "seven-l-prod"):
        self.project_id = project_id
        self.results = {}
        
    def discover_gcs_buckets(self) -> Dict[str, Any]:
        """Discover GCS buckets and their contents using client library"""
        print("🔍 Discovering GCS buckets with client library...")
        
        try:
            client = storage.Client(project=self.project_id)
            buckets = list(client.list_buckets())
            
            bucket_info = []
            for bucket in buckets:
                print(f"  📦 Found bucket: {bucket.name}")
                
                # List objects with common prefixes
                prefixes = ['society/', 'cloudvr/', 'evolution/', 'spatial_lab/', 'warehouse/', 'padres/']
                bucket_contents = {}
                
                for prefix in prefixes:
                    try:
                        blobs = list(bucket.list_blobs(prefix=prefix, max_results=10))
                        if blobs:
                            bucket_contents[prefix] = [blob.name for blob in blobs]
                            print(f"    📁 {prefix}: {len(blobs)} objects")
                    except Exception as e:
                        print(f"    ⚠️ Error listing {prefix}: {e}")
                
                bucket_info.append({
                    "name": bucket.name,
                    "location": bucket.location,
                    "created": bucket.time_created.isoformat() if bucket.time_created else None,
                    "contents": bucket_contents
                })
            
            return {
                "buckets": bucket_info,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error accessing GCS: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def discover_bigquery_datasets(self) -> Dict[str, Any]:
        """Discover BigQuery datasets using client library"""
        print("📊 Discovering BigQuery datasets with client library...")
        
        try:
            client = bigquery.Client(project=self.project_id)
            datasets = list(client.list_datasets())
            
            dataset_info = []
            for dataset in datasets:
                print(f"  📋 Found dataset: {dataset.dataset_id}")
                
                # List tables in dataset
                try:
                    tables = list(client.list_tables(dataset.dataset_id))
                    table_names = [table.table_id for table in tables]
                    print(f"    📊 Tables: {len(table_names)}")
                    
                    dataset_info.append({
                        "dataset_id": dataset.dataset_id,
                        "location": dataset.location,
                        "created": dataset.created.isoformat() if dataset.created else None,
                        "tables": table_names
                    })
                except Exception as e:
                    print(f"    ⚠️ Error listing tables: {e}")
                    dataset_info.append({
                        "dataset_id": dataset.dataset_id,
                        "error": str(e)
                    })
            
            return {
                "datasets": dataset_info,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error accessing BigQuery: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def discover_cloud_run_services(self) -> Dict[str, Any]:
        """Discover Cloud Run services using client library"""
        print("🚀 Discovering Cloud Run services with client library...")
        
        try:
            client = run_v2.ServicesClient()
            parent = f"projects/{self.project_id}/locations/us-central1"
            
            services = []
            for service in client.list_services(parent=parent):
                print(f"  🚀 Found service: {service.name.split('/')[-1]}")
                
                services.append({
                    "name": service.name.split('/')[-1],
                    "full_name": service.name,
                    "uri": service.uri,
                    "created": service.create_time.isoformat() if service.create_time else None,
                    "updated": service.update_time.isoformat() if service.update_time else None
                })
            
            return {
                "services": services,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error accessing Cloud Run: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def discover_pubsub_topics(self) -> Dict[str, Any]:
        """Discover Pub/Sub topics using client library"""
        print("📡 Discovering Pub/Sub topics with client library...")
        
        try:
            publisher = pubsub_v1.PublisherClient()
            subscriber = pubsub_v1.SubscriberClient()
            
            project_path = f"projects/{self.project_id}"
            
            # List topics
            topics = []
            for topic in publisher.list_topics(request={"project": project_path}):
                topics.append(topic.name.split('/')[-1])
                print(f"  📡 Found topic: {topic.name.split('/')[-1]}")
            
            # List subscriptions
            subscriptions = []
            for subscription in subscriber.list_subscriptions(request={"project": project_path}):
                subscriptions.append(subscription.name.split('/')[-1])
                print(f"  📨 Found subscription: {subscription.name.split('/')[-1]}")
            
            return {
                "topics": topics,
                "subscriptions": subscriptions,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error accessing Pub/Sub: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def pull_ai_society_data(self) -> Dict[str, Any]:
        """Pull AI Society specific data from GCS"""
        print("🤖 Pulling AI Society data from GCS...")
        
        try:
            client = storage.Client(project=self.project_id)
            
            # Look for society data in various buckets
            buckets_to_check = ["7l-data", "7l-jsonl", "7l-pipelines"]
            society_data = {}
            
            for bucket_name in buckets_to_check:
                try:
                    bucket = client.bucket(bucket_name)
                    
                    # Look for live observations
                    blobs = list(bucket.list_blobs(prefix="society/live_observations_", max_results=5))
                    if blobs:
                        society_data[f"{bucket_name}_observations"] = [blob.name for blob in blobs]
                        print(f"  📊 Found {len(blobs)} observation files in {bucket_name}")
                    
                    # Look for other society data
                    blobs = list(bucket.list_blobs(prefix="society/", max_results=10))
                    if blobs:
                        society_data[f"{bucket_name}_all"] = [blob.name for blob in blobs]
                        print(f"  📁 Found {len(blobs)} society files in {bucket_name}")
                        
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
            client = storage.Client(project=self.project_id)
            
            # Look for spatial lab data in various buckets
            buckets_to_check = ["7l-data", "7l-jsonl", "7l-pipelines"]
            spatial_data = {}
            
            for bucket_name in buckets_to_check:
                try:
                    bucket = client.bucket(bucket_name)
                    
                    # Look for spatial lab data
                    blobs = list(bucket.list_blobs(prefix="spatial_lab/", max_results=10))
                    if blobs:
                        spatial_data[f"{bucket_name}_spatial"] = [blob.name for blob in blobs]
                        print(f"  🧠 Found {len(blobs)} spatial lab files in {bucket_name}")
                    
                    # Look for evaluation results
                    blobs = list(bucket.list_blobs(prefix="evaluation/", max_results=10))
                    if blobs:
                        spatial_data[f"{bucket_name}_evaluation"] = [blob.name for blob in blobs]
                        print(f"  📊 Found {len(blobs)} evaluation files in {bucket_name}")
                        
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
        print("📊 Generating comprehensive report with direct cloud access...")
        
        # Pull all data
        gcs_data = self.discover_gcs_buckets()
        bigquery_data = self.discover_bigquery_datasets()
        cloud_run_data = self.discover_cloud_run_services()
        pubsub_data = self.discover_pubsub_topics()
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
                "api_key_used": "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo",
                "method": "direct_cloud_client_libraries"
            },
            "cloud_infrastructure": {
                "gcs_buckets": gcs_data,
                "bigquery_datasets": bigquery_data,
                "cloud_run_services": cloud_run_data,
                "pubsub_topics": pubsub_data
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
                "pubsub_topics_found": len(pubsub_data.get("topics", [])) if pubsub_data.get("status") == "success" else 0,
                "local_components_analyzed": len(local_data.get("highlights", []))
            }
        }
        
        return comprehensive_report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"direct_cloud_analysis_{timestamp}.json"
        
        filepath = f"/Users/carlos/NOUS/results/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filepath}")
        return filepath

def main():
    """Main execution function"""
    print("🚀 Starting Direct Cloud Access Analysis")
    print("=" * 50)
    
    accessor = DirectCloudAccess()
    
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
        print(f"Pub/Sub Topics: {summary['pubsub_topics_found']}")
        print(f"Local Components: {summary['local_components_analyzed']}")
        
        print(f"\n✅ Direct cloud access analysis complete! Report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())











