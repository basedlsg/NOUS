#!/usr/bin/env python3
"""
Final Cloud Analysis Script
Uses curl and gcloud auth to access cloud data and generate comprehensive reports
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

class FinalCloudAnalysis:
    def __init__(self, project_id: str = "seven-l-prod"):
        self.project_id = project_id
        self.results = {}
        
    def run_command(self, command: str) -> Optional[str]:
        """Run a shell command and return output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
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
    
    def get_access_token(self) -> Optional[str]:
        """Get Google Cloud access token"""
        try:
            export_path = "export PATH='/Users/carlos/Downloads/google-cloud-sdk/bin:$PATH' && "
            command = export_path + "gcloud auth print-access-token"
            token = self.run_command(command)
            return token
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None
    
    def discover_gcs_buckets(self) -> Dict[str, Any]:
        """Discover GCS buckets using curl and access token"""
        print("🔍 Discovering GCS buckets with authenticated curl...")
        
        token = self.get_access_token()
        if not token:
            return {"error": "Failed to get access token", "status": "error"}
        
        try:
            # List buckets
            curl_command = f'curl -s -H "Authorization: Bearer {token}" "https://storage.googleapis.com/storage/v1/b?project={self.project_id}"'
            output = self.run_command(curl_command)
            
            if output:
                data = json.loads(output)
                buckets = data.get("items", [])
                
                bucket_info = []
                for bucket in buckets:
                    bucket_name = bucket.get("name", "")
                    print(f"  📦 Found bucket: {bucket_name}")
                    
                    # List objects in bucket
                    objects_command = f'curl -s -H "Authorization: Bearer {token}" "https://storage.googleapis.com/storage/v1/b/{bucket_name}/o?maxResults=20"'
                    objects_output = self.run_command(objects_command)
                    
                    bucket_contents = []
                    if objects_output:
                        try:
                            objects_data = json.loads(objects_output)
                            objects = objects_data.get("items", [])
                            bucket_contents = [obj.get("name", "") for obj in objects]
                            print(f"    📁 Found {len(objects)} objects")
                        except json.JSONDecodeError:
                            print(f"    ⚠️ Could not parse objects for {bucket_name}")
                    
                    bucket_info.append({
                        "name": bucket_name,
                        "location": bucket.get("location", ""),
                        "created": bucket.get("timeCreated", ""),
                        "object_count": len(bucket_contents),
                        "sample_objects": bucket_contents[:10]  # First 10 objects
                    })
                
                return {
                    "buckets": bucket_info,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "error": "Failed to list buckets",
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
        """Discover BigQuery datasets using curl and access token"""
        print("📊 Discovering BigQuery datasets with authenticated curl...")
        
        token = self.get_access_token()
        if not token:
            return {"error": "Failed to get access token", "status": "error"}
        
        try:
            # List datasets
            curl_command = f'curl -s -H "Authorization: Bearer {token}" "https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets"'
            output = self.run_command(curl_command)
            
            if output:
                data = json.loads(output)
                datasets = data.get("datasets", [])
                
                dataset_info = []
                for dataset in datasets:
                    dataset_id = dataset.get("datasetReference", {}).get("datasetId", "")
                    print(f"  📋 Found dataset: {dataset_id}")
                    
                    # List tables in dataset
                    tables_command = f'curl -s -H "Authorization: Bearer {token}" "https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets/{dataset_id}/tables"'
                    tables_output = self.run_command(tables_command)
                    
                    table_names = []
                    if tables_output:
                        try:
                            tables_data = json.loads(tables_output)
                            tables = tables_data.get("tables", [])
                            table_names = [table.get("tableReference", {}).get("tableId", "") for table in tables]
                            print(f"    📊 Found {len(tables)} tables")
                        except json.JSONDecodeError:
                            print(f"    ⚠️ Could not parse tables for {dataset_id}")
                    
                    dataset_info.append({
                        "dataset_id": dataset_id,
                        "location": dataset.get("location", ""),
                        "created": dataset.get("creationTime", ""),
                        "table_count": len(table_names),
                        "tables": table_names
                    })
                
                return {
                    "datasets": dataset_info,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "error": "Failed to list datasets",
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
        """Discover Cloud Run services using gcloud command"""
        print("🚀 Discovering Cloud Run services with gcloud...")
        
        try:
            export_path = "export PATH='/Users/carlos/Downloads/google-cloud-sdk/bin:$PATH' && "
            command = export_path + f"gcloud run services list --region=us-central1 --platform=managed --format=json"
            output = self.run_command(command)
            
            if output:
                services = json.loads(output)
                
                service_info = []
                for service in services:
                    service_name = service.get("metadata", {}).get("name", "")
                    print(f"  🚀 Found service: {service_name}")
                    
                    service_info.append({
                        "name": service_name,
                        "url": service.get("status", {}).get("url", ""),
                        "created": service.get("metadata", {}).get("creationTimestamp", ""),
                        "region": service.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location", "")
                    })
                
                return {
                    "services": service_info,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "error": "Failed to list Cloud Run services",
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
    
    def pull_experimental_data(self) -> Dict[str, Any]:
        """Pull experimental data from GCS buckets"""
        print("🧪 Pulling experimental data from GCS...")
        
        token = self.get_access_token()
        if not token:
            return {"error": "Failed to get access token", "status": "error"}
        
        try:
            # Look for experimental data in various buckets
            buckets_to_check = ["7l-data", "7l-jsonl", "7l-pipelines", "7l-models"]
            experimental_data = {}
            
            for bucket_name in buckets_to_check:
                print(f"  🔍 Checking bucket: {bucket_name}")
                
                # Look for various experimental data patterns
                prefixes = [
                    "society/", "ai_society/", "live_observations_",
                    "spatial_lab/", "spatial/", "evaluation/",
                    "warehouse/", "coordination/", "padres/",
                    "cloudvr/", "vr/", "research/",
                    "evolution/", "experiments/", "results/"
                ]
                
                bucket_data = {}
                for prefix in prefixes:
                    curl_command = f'curl -s -H "Authorization: Bearer {token}" "https://storage.googleapis.com/storage/v1/b/{bucket_name}/o?prefix={prefix}&maxResults=10"'
                    output = self.run_command(curl_command)
                    
                    if output:
                        try:
                            data = json.loads(output)
                            objects = data.get("items", [])
                            if objects:
                                bucket_data[prefix] = [obj.get("name", "") for obj in objects]
                                print(f"    📁 {prefix}: {len(objects)} objects")
                        except json.JSONDecodeError:
                            pass
                
                if bucket_data:
                    experimental_data[bucket_name] = bucket_data
            
            return {
                "data": experimental_data,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error pulling experimental data: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("📊 Generating comprehensive report with cloud data access...")
        
        # Pull all data
        gcs_data = self.discover_gcs_buckets()
        bigquery_data = self.discover_bigquery_datasets()
        cloud_run_data = self.discover_cloud_run_services()
        experimental_data = self.pull_experimental_data()
        
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
                "method": "authenticated_curl_and_gcloud"
            },
            "cloud_infrastructure": {
                "gcs_buckets": gcs_data,
                "bigquery_datasets": bigquery_data,
                "cloud_run_services": cloud_run_data
            },
            "experimental_data": experimental_data,
            "local_analysis": local_data,
            "summary": {
                "gcs_buckets_found": len(gcs_data.get("buckets", [])) if gcs_data.get("status") == "success" else 0,
                "bigquery_datasets_found": len(bigquery_data.get("datasets", [])) if bigquery_data.get("status") == "success" else 0,
                "cloud_run_services_found": len(cloud_run_data.get("services", [])) if cloud_run_data.get("status") == "success" else 0,
                "experimental_data_sources": len(experimental_data.get("data", {})) if experimental_data.get("status") == "success" else 0,
                "local_components_analyzed": len(local_data.get("highlights", []))
            }
        }
        
        return comprehensive_report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"final_cloud_analysis_{timestamp}.json"
        
        filepath = f"/Users/carlos/NOUS/results/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filepath}")
        return filepath

def main():
    """Main execution function"""
    print("🚀 Starting Final Cloud Analysis")
    print("=" * 50)
    
    analyzer = FinalCloudAnalysis()
    
    try:
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()
        
        # Save report
        report_path = analyzer.save_report(report)
        
        # Print summary
        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 30)
        summary = report["summary"]
        print(f"GCS Buckets: {summary['gcs_buckets_found']}")
        print(f"BigQuery Datasets: {summary['bigquery_datasets_found']}")
        print(f"Cloud Run Services: {summary['cloud_run_services_found']}")
        print(f"Experimental Data Sources: {summary['experimental_data_sources']}")
        print(f"Local Components: {summary['local_components_analyzed']}")
        
        print(f"\n✅ Final cloud analysis complete! Report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())











