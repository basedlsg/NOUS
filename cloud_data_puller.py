#!/usr/bin/env python3
"""
Cloud Data Puller for Multi-Part AI Platform Analysis
Pulls data from Google Cloud Services and correlates with local artifacts
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

class CloudDataPuller:
    def __init__(self, project_id: str = "seven-l-prod", region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.results = {}
        
    def run_command(self, command: str, timeout: int = 30) -> Optional[str]:
        """Run a shell command with timeout"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Command failed: {command}")
                print(f"Error: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {command}")
            return None
        except Exception as e:
            print(f"Error running command: {e}")
            return None
    
    def discover_gcs_buckets(self) -> Dict[str, Any]:
        """Discover GCS buckets and their contents"""
        print("🔍 Discovering GCS buckets...")
        
        # List buckets
        buckets_output = self.run_command("gcloud storage buckets list --format='value(name)'")
        buckets = buckets_output.split('\n') if buckets_output else []
        
        bucket_contents = {}
        for bucket in buckets[:5]:  # Limit to first 5 buckets
            if bucket:
                print(f"  📦 Exploring bucket: {bucket}")
                # List objects with prefix patterns
                prefixes = ['society/', 'cloudvr/', 'evolution/', 'spatial_lab/', 'warehouse/']
                for prefix in prefixes:
                    objects = self.run_command(f"gsutil ls gs://{bucket}/{prefix} 2>/dev/null | head -10")
                    if objects:
                        bucket_contents[f"{bucket}/{prefix}"] = objects.split('\n')[:10]
        
        return {
            "buckets": buckets,
            "contents": bucket_contents,
            "timestamp": datetime.now().isoformat()
        }
    
    def discover_cloud_run_services(self) -> Dict[str, Any]:
        """Discover Cloud Run services and their logs"""
        print("🚀 Discovering Cloud Run services...")
        
        # List services
        services_output = self.run_command(
            f"gcloud run services list --region={self.region} --platform=managed --format='value(metadata.name,status.url)'"
        )
        
        services = []
        if services_output:
            for line in services_output.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        services.append({
                            "name": parts[0],
                            "url": parts[1]
                        })
        
        # Get logs for each service
        service_logs = {}
        for service in services:
            service_name = service["name"]
            print(f"  📋 Getting logs for: {service_name}")
            
            # Get recent logs
            logs = self.run_command(
                f'gcloud logging read \'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"\' --limit=50 --format="value(textPayload)"'
            )
            
            if logs:
                service_logs[service_name] = logs.split('\n')[:20]  # Limit to 20 log entries
        
        return {
            "services": services,
            "logs": service_logs,
            "timestamp": datetime.now().isoformat()
        }
    
    def discover_bigquery_datasets(self) -> Dict[str, Any]:
        """Discover BigQuery datasets and tables"""
        print("📊 Discovering BigQuery datasets...")
        
        # List datasets
        datasets_output = self.run_command(f"bq ls --project_id={self.project_id}")
        
        datasets = []
        if datasets_output:
            for line in datasets_output.split('\n')[2:]:  # Skip header lines
                if line.strip():
                    datasets.append(line.strip())
        
        # For each dataset, try to list tables
        dataset_tables = {}
        for dataset in datasets[:3]:  # Limit to first 3 datasets
            print(f"  📋 Exploring dataset: {dataset}")
            tables_output = self.run_command(f"bq ls {self.project_id}:{dataset}")
            
            if tables_output:
                tables = []
                for line in tables_output.split('\n')[2:]:  # Skip header lines
                    if line.strip():
                        tables.append(line.strip())
                dataset_tables[dataset] = tables
        
        return {
            "datasets": datasets,
            "tables": dataset_tables,
            "timestamp": datetime.now().isoformat()
        }
    
    def discover_pubsub_topics(self) -> Dict[str, Any]:
        """Discover Pub/Sub topics and subscriptions"""
        print("📡 Discovering Pub/Sub topics...")
        
        # List topics
        topics_output = self.run_command("gcloud pubsub topics list --format='value(name)'")
        topics = topics_output.split('\n') if topics_output else []
        
        # List subscriptions
        subscriptions_output = self.run_command("gcloud pubsub subscriptions list --format='value(name)'")
        subscriptions = subscriptions_output.split('\n') if subscriptions_output else []
        
        return {
            "topics": topics,
            "subscriptions": subscriptions,
            "timestamp": datetime.now().isoformat()
        }
    
    def pull_ai_society_data(self) -> Dict[str, Any]:
        """Pull AI Society specific data"""
        print("🤖 Pulling AI Society data...")
        
        # Try to get live observations from GCS
        society_data = {}
        
        # Look for live observations in various buckets
        buckets_to_check = ["7l-data", "7l-jsonl"]
        for bucket in buckets_to_check:
            observations = self.run_command(f"gsutil ls gs://{bucket}/society/live_observations_*.json 2>/dev/null | head -5")
            if observations:
                society_data[f"{bucket}_observations"] = observations.split('\n')
                break
        
        # Get Cloud Run logs for society services
        society_logs = self.run_command(
            f'gcloud logging read \'resource.type="cloud_run_revision" AND textPayload:"society"\' --limit=20 --format="value(textPayload)"'
        )
        
        if society_logs:
            society_data["logs"] = society_logs.split('\n')[:10]
        
        return {
            "data": society_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def pull_spatial_lab_data(self) -> Dict[str, Any]:
        """Pull Spatial Lab specific data"""
        print("🧠 Pulling Spatial Lab data...")
        
        spatial_data = {}
        
        # Look for spatial task results in GCS
        buckets_to_check = ["7l-data", "7l-jsonl"]
        for bucket in buckets_to_check:
            spatial_results = self.run_command(f"gsutil ls gs://{bucket}/spatial_lab/*.json 2>/dev/null | head -5")
            if spatial_results:
                spatial_data[f"{bucket}_results"] = spatial_results.split('\n')
                break
        
        # Get logs for spatial lab services
        spatial_logs = self.run_command(
            f'gcloud logging read \'resource.type="cloud_run_revision" AND textPayload:"spatial"\' --limit=20 --format="value(textPayload)"'
        )
        
        if spatial_logs:
            spatial_data["logs"] = spatial_logs.split('\n')[:10]
        
        return {
            "data": spatial_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("📊 Generating comprehensive report...")
        
        # Pull all data
        gcs_data = self.discover_gcs_buckets()
        cloud_run_data = self.discover_cloud_run_services()
        bigquery_data = self.discover_bigquery_datasets()
        pubsub_data = self.discover_pubsub_topics()
        ai_society_data = self.pull_ai_society_data()
        spatial_lab_data = self.pull_spatial_lab_data()
        
        # Combine with local data
        local_data_path = "/Users/carlos/NOUS/results/component_reports/combined_summary.json"
        local_data = {}
        if os.path.exists(local_data_path):
            with open(local_data_path, 'r') as f:
                local_data = json.load(f)
        
        comprehensive_report = {
            "metadata": {
                "project_id": self.project_id,
                "region": self.region,
                "analysis_timestamp": datetime.now().isoformat(),
                "api_key_provided": "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo"
            },
            "cloud_infrastructure": {
                "gcs_buckets": gcs_data,
                "cloud_run_services": cloud_run_data,
                "bigquery_datasets": bigquery_data,
                "pubsub_topics": pubsub_data
            },
            "component_data": {
                "ai_society": ai_society_data,
                "spatial_lab": spatial_lab_data
            },
            "local_analysis": local_data,
            "summary": {
                "gcs_buckets_found": len(gcs_data.get("buckets", [])),
                "cloud_run_services_found": len(cloud_run_data.get("services", [])),
                "bigquery_datasets_found": len(bigquery_data.get("datasets", [])),
                "pubsub_topics_found": len(pubsub_data.get("topics", [])),
                "local_components_analyzed": len(local_data.get("highlights", []))
            }
        }
        
        return comprehensive_report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cloud_analysis_report_{timestamp}.json"
        
        filepath = f"/Users/carlos/NOUS/results/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filepath}")
        return filepath

def main():
    """Main execution function"""
    print("🚀 Starting Cloud Data Analysis for Multi-Part AI Platform")
    print("=" * 60)
    
    puller = CloudDataPuller()
    
    try:
        # Generate comprehensive report
        report = puller.generate_comprehensive_report()
        
        # Save report
        report_path = puller.save_report(report)
        
        # Print summary
        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 30)
        summary = report["summary"]
        print(f"GCS Buckets: {summary['gcs_buckets_found']}")
        print(f"Cloud Run Services: {summary['cloud_run_services_found']}")
        print(f"BigQuery Datasets: {summary['bigquery_datasets_found']}")
        print(f"Pub/Sub Topics: {summary['pubsub_topics_found']}")
        print(f"Local Components: {summary['local_components_analyzed']}")
        
        print(f"\n✅ Analysis complete! Report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())











