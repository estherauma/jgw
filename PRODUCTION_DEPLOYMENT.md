# Production Deployment Guide

## 🚀 **Production Deployment Overview**

The production deployment workflow mirrors the staging deployment but is **manually triggered** and uses the **same Docker Hub repository** as staging. This ensures consistency between environments while maintaining production safety through manual control.

## 📋 **Key Features**

### **1. Manual Trigger Only**
- ✅ **No Automatic Deployment**: Production deployments are always manual
- ✅ **Confirmation Required**: Must confirm deployment to proceed
- ✅ **Image Tag Selection**: Can choose specific Docker image tag to deploy

### **2. Same Docker Hub Repository**
- ✅ **Consistent Images**: Uses `fiftyeight/jgw-pandas-staging` repository
- ✅ **Same Build Process**: Images built by the same CI/CD pipeline
- ✅ **Version Control**: Can deploy any available image tag

### **3. Production Safety**
- ✅ **Manual Control**: Only authorized users can trigger deployments
- ✅ **Confirmation Step**: Prevents accidental deployments
- ✅ **Detailed Logging**: Comprehensive deployment logs
- ✅ **Slack Notifications**: Immediate notification of deployment status

## 🔧 **Required GitHub Secrets**

### **Production Server Access**
```yaml
PRODUCTION_SSH_PRIVATE_KEY: "your_production_ssh_private_key"
PRODUCTION_HOST: "your_production_server_ip"
PRODUCTION_USERNAME: "your_production_username"
```

### **Docker Hub Access**
```yaml
DOCKERHUB_USERNAME: "fiftyeight"
DOCKERHUB_TOKEN: "your_dockerhub_token"
```

### **Notifications**
```yaml
SLACK_WEBHOOK_URL: "your_slack_webhook_url"
```

## 🎯 **How to Deploy to Production**

### **Step 1: Access GitHub Actions**
1. Go to your GitHub repository
2. Click on **"Actions"** tab
3. Select **"Deploy to Production"** workflow

### **Step 2: Configure Deployment**
1. Click **"Run workflow"** button
2. Select the branch (usually `develop`)
3. **Image Tag**: Choose the Docker image tag to deploy
   - `latest` - Most recent build
   - `develop` - Latest from develop branch
   - `sha-abc123` - Specific commit build
   - Custom tag if available
4. **Confirm Deployment**: Check the confirmation box
5. Click **"Run workflow"**

### **Step 3: Monitor Deployment**
1. Watch the workflow progress in GitHub Actions
2. Check Slack notifications for status updates
3. Verify deployment on production server

## 📊 **Deployment Process**

### **1. Pre-deployment Checks**
- ✅ **Confirmation**: Verifies user confirmed deployment
- ✅ **SSH Setup**: Establishes secure connection to production server
- ✅ **Variable Setup**: Configures deployment parameters

### **2. Server Deployment**
- ✅ **Code Pull**: Pulls latest code from `develop` branch
- ✅ **Docker Hub Login**: Authenticates with Docker Hub
- ✅ **Image Pull**: Pulls specified Docker image
- ✅ **Container Management**: Stops old containers, starts new ones
- ✅ **Cleanup**: Removes unused Docker images

### **3. Post-deployment**
- ✅ **Status Verification**: Confirms all services are running
- ✅ **Slack Notification**: Sends success/failure notification
- ✅ **Logging**: Records deployment details

## 🔄 **Deployment Workflow**

```
Manual Trigger
      ↓
Confirmation Check
      ↓
SSH Setup
      ↓
Set Variables
      ↓
Deploy to Production
      ↓
Slack Notification
```

## 📋 **Available Image Tags**

### **Automatic Tags**
- `latest` - Most recent successful build
- `develop` - Latest from develop branch
- `sha-abc123` - Specific commit build

### **Custom Tags**
- Any tag available in Docker Hub repository
- Can specify exact version for rollback

## 🚨 **Production Safety Features**

### **1. Confirmation Required**
```yaml
confirm_deployment:
  description: 'Confirm you want to deploy to production'
  required: true
  type: boolean
  default: false
```

### **2. Manual Trigger Only**
- No automatic triggers
- No webhook triggers
- Only manual workflow dispatch

### **3. Environment Protection**
- Uses GitHub environment protection
- Requires proper permissions
- Logs all deployment activities

## 📱 **Slack Notifications**

### **Success Notification**
```
🎉 Production Deployment Successful
Environment: Production
Image: fiftyeight/jgw-pandas-staging:latest
Branch: develop
Commit: abc123def456
Deployed by: username
Triggered by: manual
⚠️ This is now LIVE in production!
```

### **Failure Notification**
```
🚨 Production Deployment Failed
Environment: Production
Image: fiftyeight/jgw-pandas-staging:latest
Branch: develop
Commit: abc123def456
Deployed by: username
Triggered by: manual
⚠️ URGENT: Production deployment failed!
Check the logs immediately.
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. SSH Connection Failed**
- Check `PRODUCTION_SSH_PRIVATE_KEY` secret
- Verify `PRODUCTION_HOST` and `PRODUCTION_USERNAME`
- Ensure SSH key has proper permissions

#### **2. Docker Hub Authentication Failed**
- Check `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`
- Verify token has proper permissions
- Ensure repository access

#### **3. Image Pull Failed**
- Check if image tag exists in Docker Hub
- Verify image name is correct
- Check Docker Hub repository permissions

#### **4. Container Startup Failed**
- Check production server resources
- Verify environment variables in `.env`
- Check container logs on production server

### **Debugging Steps**

1. **Check GitHub Actions Logs**
   - Go to Actions tab
   - Click on failed workflow
   - Review step logs

2. **Check Production Server**
   - SSH to production server
   - Check Docker containers: `docker ps -a`
   - Check logs: `docker logs <container_name>`

3. **Check Slack Notifications**
   - Review notification details
   - Check for error messages

## 🎉 **Best Practices**

### **1. Pre-deployment**
- ✅ Test in staging first
- ✅ Verify image exists in Docker Hub
- ✅ Check production server resources
- ✅ Notify team of deployment

### **2. During Deployment**
- ✅ Monitor GitHub Actions progress
- ✅ Watch Slack notifications
- ✅ Be ready to rollback if needed

### **3. Post-deployment**
- ✅ Verify application is working
- ✅ Check all services are running
- ✅ Monitor for any issues
- ✅ Document deployment details

## 🔄 **Rollback Procedure**

### **Quick Rollback**
1. Go to GitHub Actions
2. Run "Deploy to Production" workflow
3. Select previous working image tag
4. Confirm deployment
5. Monitor rollback progress

### **Emergency Rollback**
1. SSH to production server
2. Stop current containers
3. Start previous working containers
4. Notify team of rollback

## 📈 **Monitoring**

### **Deployment Metrics**
- Deployment frequency
- Success/failure rates
- Deployment duration
- Rollback frequency

### **Application Metrics**
- Application uptime
- Response times
- Error rates
- Resource usage

This production deployment setup provides a safe, controlled, and reliable way to deploy your application to production! 🚀
