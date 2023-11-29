# Deploying AIR Quality API to Google Cloud Run using Terraform and GitHub Actions

This repository will deploy a Dockerized AIR QUALITY REQUEST API to Google Cloud Run, while provisioning the required infrastructure with Terraform. 

### **1. AIR Quality APP**

The web application periodically (every 15 minutes) request air quality data for the city of Stuttgart, Germany, using the aqicn.org API service.
   - The retrieved data stored in a SQlite database.

API exposes following Endpoints:
   - `GET /status`: Returns the status of the application, including key metrics and system status.
   - `GET /aqi`: Provides the current Air Quality Index (AQI) along with the time of the last update.
   - `GET /refresh`: Forcefully updates and returns the current AQI.
   - `GET /fetch_and_store`: Update the current AQI (Added for testing purpose)

### **2. Run application locally**

Set the environment variable API_TOKEN using the following command:

```
$ export API_TOKEN="YOUR_API_TOKEN"
```
Here, we have stored the application in the app folder. APP can be launched locally using the following command:

```
$ python main.py
```
### **3. Dockerize the Flask app**

Now that our web application is built, we need to find a way to package it before deploying it to the cloud. The following command can be used to build your Docker image: 
```
docker build . -t <image_tag>
```

When you Docker image is built, you can run the image locally using the following command: 
```
docker run -p 5000:5000 <image_tag>
```

### **4. Configure Cloud Storage bucket to store Terraform state**
By default, Terraform saves the state locally in a `terraform.tfstate` file. However, if we want to provision our infrastructure through CI/CD we should use a backend for Terraform, so our state is stored remotely in a Cloud Storage bucket

### **5. Build the cloud infrastructure using Terraform**
In this project, the Cloud infrastructure is stored in the *infra/main* folder. All files present in this folder contain Terraform code in order to maintain the following Cloud infrastructures:
- Enable API's of features we need like Cloud Run or Artifact registry
- Save the current Terraform state to the remove Cloud Storage bucket
- Create a service account for pushing the Docker image to Artifact Registry
- Deploy the Docker image to an endpoint

### **6. Deploy using Github Actions (CI/CD)**
This project is currently using Github Actions for the CI/CD so that the code is deployed on production when you do a pull request or a push to the `main` branch.

When you push a new version of the code on the `main` branch, one workflow containing the following steps will be created:
- **Build Docker image**: This step will trigger the build of a new Docker image containing the code that was just pushed. This image will then be push to the Artifact Registry on GCP. 
- **Infrastructure for Terraform**: This step will maintain the Cloud infrastructure using Terraform and will also trigger the deployment of the Docker image previously built to an endpoint. 

After the deployment on production, you will be able to access API in your Web browser using a public url. 

## 🔑 What secret keys are required? 

In order to deploy using Github actions, we need to store the credentials of the service accounts that we created previously in a safe location. Those can be stored in Github secrets related to your project. 

| Name | Description | Type | Required |
|------|-------------|------|:--------:|
| GCP_DOCKER_PUSHER_AUTH | Access key of the Docker pusher service account | `json` | yes |
| GCP_SERVICE_ACCOUNT_AUTH  | Access key of the infrastructure service account | `json` | yes |