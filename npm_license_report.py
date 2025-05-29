import json
import csv
import subprocess
import requests
from pathlib import Path

import requests


def get_latest_license_npm(package_name):
	#we try to get the license of the latest version of the requested package
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("dist-tags", {}).get("latest", "")
            license_info = data.get("versions", {}).get(latest_version, {}).get("license", "UNKNOWN")
            return latest_version, license_info
    except Exception as e:
        print(f"Failed to get License for {package_name}: {e}")
    
    return "UNKNOWN", "UNKNOWN"

projects= [
	{"name":"ABC","path":r"C:/Project/ABC/package-lock.json"},
	{"name":"XYZ","path":r"C:/Project/XYZ/package-lock.json"},
	{"name":"TEST","path":r"C:/Project/TEST/package-lock.json"}
]




for project in projects:
	project_name = project["name"]
	package_lock_path = Path(project["path"])
	project_dir = package_lock_path.parent
	license_json_path = project_dir / f"{project_name}_licenses.json"
	
	if not package_lock_path.exists():
		print(f"File not found:{package_lock_path}")
		continue
		
	#we'll try to fetch the licenses
	try:
		subprocess.run([r"C:\Program Files\nodejs\npm.cmd", "ci"],cwd=str(project_dir),check=True)
		subprocess.run(
			[r"C:\Program Files\nodejs\npx.cmd", "license-checker", "--json", "--production", "--out", str(license_json_path)],
			cwd=str(project_dir),
			check=True
		)
	except subprocess.CalledProcessError as e:
		print(f"License checker failed for project {project_name}: {e}")
		continue		
		
	#load license	
	try:
		with open(license_json_path,"r", encoding="utf-8") as f:
			license_data = json.load(f)
	except Exception as e:
		print(f"Failed to load License data for {project_name}:{e}")
		continue		
		
	try:
		with package_lock_path.open("r", encoding="utf-8") as f:
			data = json.load(f)
		
		packages = data.get("packages",{}).get("",{})
		dependencies = packages.get("dependencies",{})
		
		output_rows = []
		for name,version in dependencies.items():
			if version:
				key = f"{name}@{version}"
				license_info = license_data.get(key,{})
				license_name = license_info.get("licenses","UNKNOWN")
				# in case the version number is not number
				if license_name == "UNKNOWN":
					version,license_name = get_latest_license_npm(name)
			else:
				version,license_name = get_latest_license_npm(name)
			output_rows.append((name,version,license_name))
			
		
		output_csv = project_name+"_dependencies.csv"
		with open(output_csv,"w",newline="", encoding="utf-8") as f:
			writer = csv.writer(f)
			writer.writerow(["Library","Version","License"])
			writer.writerows(output_rows)
			
	except Exception as e:
		print(f"Error processing the package lock file")
