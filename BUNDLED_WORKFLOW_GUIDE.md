# Bundled Workflow Guide - Build and Deploy to Staging

## 🚀 **Overview**

The `build-deploy-staging.yml` workflow combines the build-and-push and deploy-staging workflows into a single, streamlined process. This eliminates the need for `repository-dispatch` triggers and simplifies the CI/CD pipeline.

## 📋 **Workflow Structure**

### **Phase 1: Build Phase**
1. **Checkout Code** - Get latest code from develop branch
2. **Setup Docker Buildx** - Prepare Docker build environment
3. **Clean Local Cache** - Free up space and optimize builds
4. **Debug Secrets** - Verify required secrets are available
5. **Docker Hub Login** - Authenticate with Docker Hub
6. **Clean Old Images** - Remove old images (keep last 2 + protected tags)
7. **Extract Metadata** - Generate image tags and labels
8. **Build & Push** - Build Docker image and push to Docker Hub

### **Phase 2: Deployment Phase**
9. **Setup SSH** - Prepare SSH connection to staging server
10. **Set Variables** - Configure deployment parameters
11. **Deploy to Staging** - Deploy the built image to staging environment

### **Phase 3: Notifications**
12. **Slack Notifications** - Send success/failure notifications

## 🎯 **Key Benefits**

### **1. Simplified Pipeline**
- ✅ **Single Workflow**: One workflow handles both build and deployment
- ✅ **No Inter-Workflow Dependencies**: No need for `repository-dispatch` triggers
- ✅ **Atomic Operations**: Build and deploy happen in sequence
- ✅ **Easier Debugging**: All steps in one workflow

### **2. Improved Reliability**
- ✅ **No Trigger Failures**: Eliminates `repository-dispatch` trigger issues
- ✅ **Consistent State**: Build and deployment always use same image
- ✅ **Better Error Handling**: Single point of failure management
- ✅ **Simplified Monitoring**: One workflow to monitor

### **3. Enhanced Performance**
- ✅ **Faster Execution**: No waiting for trigger propagation
- ✅ **Reduced Complexity**: Fewer moving parts
- ✅ **Better Caching**: Shared context between build and deploy
- ✅ **Streamlined Process**: Direct build-to-deploy flow

## 🔧 **Workflow Configuration**

### **Triggers**
```yaml
on:
  push:
    branches:
      - develop
```

### **Environment Variables**
```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: fiftyeight/jgw-pandas-staging
  DEPLOYMENT_ENV: staging
  DEPLOYMENT_BRANCH: develop
```

### **Required Secrets**
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token
- `GOOGLE_CREDENTIALS_BASE64` - Base64 encoded Google credentials
- `STAGING_SSH_PRIVATE_KEY` - SSH private key for staging server
- `STAGING_HOST` - Staging server hostname/IP
- `STAGING_USERNAME` - Username for staging server
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications

## 📊 **Workflow Process**

### **Build Phase Details**
```
1. Checkout Code
   ↓
2. Setup Docker Buildx
   ↓
3. Clean Local Cache
   ↓
4. Debug Secrets
   ↓
5. Docker Hub Login
   ↓
6. Clean Old Images (keep last 2 + protected tags)
   ↓
7. Extract Metadata (generate tags)
   ↓
8. Build & Push Docker Image
```

### **Deployment Phase Details**
```
9. Setup SSH Connection
   ↓
10. Set Deployment Variables
    ↓
11. Deploy to Staging Server
    - Pull latest code
    - Login to Docker Hub
    - Pull latest images
    - Stop old containers
    - Start new containers
    - Clean up unused images
```

### **Notification Phase**
```
12. Send Slack Notifications
    - Success: Build and deployment details
    - Failure: Error information and troubleshooting
```

## 🎉 **Usage**

### **Automatic Execution**
The workflow runs automatically when:
- Code is pushed to the `develop` branch
- Pull requests are merged to `develop`

### **Manual Execution**
You can also trigger it manually:
1. Go to GitHub Actions
2. Select "Build and Deploy to Staging"
3. Click "Run workflow"
4. Choose the develop branch
5. Click "Run workflow"

## 📱 **Slack Notifications**

### **Success Notification**
```
🚀 Build and Deploy to Staging Successful
Environment: Staging
Image: docker.io/fiftyeight/jgw-pandas-staging
Tags: latest,develop,sha-abc123
Branch: develop
Commit: abc123def456
Deployed by: username
✨ Old images cleaned up, kept last 2 + latest + develop for rollback
✅ Staging environment updated successfully!
```

### **Failure Notification**
```
❌ Build and Deploy to Staging Failed
Environment: Staging
Image: docker.io/fiftyeight/jgw-pandas-staging
Branch: develop
Commit: abc123def456
Deployed by: username
Check the logs for details.
```

## 🔍 **Monitoring and Debugging**

### **Workflow Status**
- Check GitHub Actions tab for workflow runs
- Look for "Build and Deploy to Staging" workflow
- Monitor both build and deployment phases

### **Build Phase Monitoring**
- **Docker Build**: Check build logs for compilation issues
- **Image Push**: Verify images are pushed to Docker Hub
- **Cleanup**: Monitor old image cleanup process

### **Deployment Phase Monitoring**
- **SSH Connection**: Verify staging server connectivity
- **Docker Pull**: Check if images are pulled successfully
- **Container Management**: Monitor container start/stop process

### **Common Issues**

#### **1. Build Failures**
- **Google Credentials**: Check `GOOGLE_CREDENTIALS_BASE64` secret
- **Docker Hub Auth**: Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`
- **Build Context**: Check for missing files or dependencies

#### **2. Deployment Failures**
- **SSH Connection**: Verify `STAGING_SSH_PRIVATE_KEY` and `STAGING_HOST`
- **Server Access**: Check staging server availability
- **Docker Compose**: Verify `docker-compose.staging.yml` exists

#### **3. Image Cleanup Issues**
- **Docker Hub API**: Check API rate limits and permissions
- **Tag Deletion**: Verify tag deletion permissions
- **Network Issues**: Check connectivity to Docker Hub

## 🚀 **Migration from Separate Workflows**

### **What's Replaced**
- ❌ `build-and-push.yml` - Replaced by build phase
- ❌ `deploy-staging.yml` - Replaced by deployment phase
- ❌ `repository-dispatch` trigger - No longer needed

### **What's Preserved**
- ✅ All build functionality
- ✅ All deployment functionality
- ✅ Image retention policy
- ✅ Slack notifications
- ✅ Error handling

### **Migration Steps**
1. **Test New Workflow**: Run the bundled workflow to ensure it works
2. **Disable Old Workflows**: Disable or delete the separate workflows
3. **Update Documentation**: Update any references to the old workflows
4. **Monitor**: Watch for any issues during the transition

## 📋 **Best Practices**

### **1. Regular Monitoring**
- ✅ **Check Workflow Runs**: Monitor workflow execution regularly
- ✅ **Review Logs**: Check build and deployment logs for issues
- ✅ **Verify Deployments**: Confirm staging environment is updated

### **2. Secret Management**
- ✅ **Rotate Secrets**: Regularly update Docker Hub and SSH keys
- ✅ **Verify Access**: Test secret access before critical deployments
- ✅ **Monitor Usage**: Watch for unauthorized access attempts

### **3. Error Handling**
- ✅ **Quick Response**: Address failures promptly
- ✅ **Log Analysis**: Use detailed logs for troubleshooting
- ✅ **Rollback Ready**: Be prepared to rollback if needed

## 🎯 **Advantages Over Separate Workflows**

### **1. Simplicity**
- **Single Workflow**: Easier to understand and maintain
- **No Dependencies**: No inter-workflow communication needed
- **Unified Logging**: All logs in one place

### **2. Reliability**
- **No Trigger Issues**: Eliminates `repository-dispatch` problems
- **Atomic Operations**: Build and deploy are guaranteed to be in sync
- **Consistent State**: Same image used for build and deployment

### **3. Performance**
- **Faster Execution**: No waiting for trigger propagation
- **Better Caching**: Shared context between phases
- **Reduced Overhead**: Less workflow management overhead

This bundled workflow provides a robust, reliable, and efficient way to build and deploy to staging in a single, streamlined process! 🚀
