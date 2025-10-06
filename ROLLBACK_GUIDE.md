# Rollback Guide - Staging & Production

## 🔄 **Rollback Pipeline Overview**

The rollback pipeline provides a quick and safe way to revert both staging and production environments to a previous working version when issues arise. This is crucial for maintaining system stability and minimizing downtime.

## 🚀 **Available Rollback Workflows**

### **1. Rollback Staging (`rollback-staging.yml`)**
- **Purpose**: Revert staging environment to a previous version
- **Trigger**: Manual workflow dispatch
- **Safety**: Confirmation required
- **Impact**: Staging environment only

### **2. Rollback Production (`rollback-production.yml`)**
- **Purpose**: Revert production environment to a previous version
- **Trigger**: Manual workflow dispatch
- **Safety**: Confirmation required + URGENT warning
- **Impact**: Production environment (LIVE users)

### **3. List Image Tags (`list-image-tags.yml`)**
- **Purpose**: Discover available Docker image tags
- **Trigger**: Manual workflow dispatch
- **Output**: List of available tags for rollback selection

## 📋 **How to Perform a Rollback**

### **Step 1: Discover Available Tags**
1. Go to GitHub Actions
2. Select **"List Available Image Tags"**
3. Click **"Run workflow"**
4. Review available tags in the output
5. Note the tag you want to rollback to

### **Step 2: Choose Rollback Target**
- **Staging Rollback**: Use `rollback-staging.yml`
- **Production Rollback**: Use `rollback-production.yml`

### **Step 3: Configure Rollback**
1. Go to the appropriate rollback workflow
2. Click **"Run workflow"**
3. Select **image tag**:
   - `latest` - Most recent build
   - `develop` - Latest from develop branch
   - `sha-latest` - Most recent commit build
   - `custom` - Specify custom tag
4. **Confirm rollback** (required)
5. Click **"Run workflow"**

## 🎯 **Rollback Process Details**

### **Staging Rollback Process**
```
1. Verify image exists in Docker Hub
2. SSH to staging server
3. Pull latest code from develop
4. Login to Docker Hub
5. Update docker-compose.staging.yml with rollback image
6. Pull rollback image
7. Stop current containers
8. Start containers with rollback image
9. Clean up unused images
10. Send Slack notification
```

### **Production Rollback Process**
```
1. Verify image exists in Docker Hub
2. SSH to production server
3. Pull latest code from develop
4. Login to Docker Hub
5. Update docker-compose.production.yml with rollback image
6. Pull rollback image
7. Stop current containers
8. Start containers with rollback image
9. Clean up unused images
10. Send URGENT Slack notification
```

## 🔍 **Image Tag Discovery & Differentiation**

### **Available Tag Types**
- **`latest`** - Most recent successful build
- **`develop`** - Latest from develop branch
- **`sha-abc123`** - Specific commit build
- **Custom tags** - Any tag available in Docker Hub

### **How to Differentiate Between Images**

#### **1. Check Current Images First**
Before rolling back, check what's currently running:
1. Go to GitHub Actions
2. Select **"Check Current Image Versions"**
3. Choose environment (staging/production)
4. Review current image tags and container status

#### **2. Understanding Image Tags**
```
latest     → Most recent build (e.g., fiftyeight/jgw-pandas-staging:latest)
develop    → Latest from develop branch (e.g., fiftyeight/jgw-pandas-staging:develop)
sha-abc123 → Specific commit build (e.g., fiftyeight/jgw-pandas-staging:sha-abc123)
pr-456     → Pull request build (e.g., fiftyeight/jgw-pandas-staging:pr-456)
```

#### **3. Rollback Process Shows Before/After**
During rollback, you'll see:
```
🔍 Checking current image versions...
Current running images:
NAMES           IMAGE                                    STATUS
jgw-pandas-web  fiftyeight/jgw-pandas-staging:sha-abc123 Up 2 hours
...

📋 Rollback Summary:
  FROM: fiftyeight/jgw-pandas-staging:sha-abc123
  TO:   fiftyeight/jgw-pandas-staging:sha-def456
```

### **Finding the Right Tag**
1. **Check Current**: Use "Check Current Image Versions" workflow
2. **Recent Issues**: Use `latest` or `develop`
3. **Specific Commit**: Use `sha-abc123` format
4. **Known Working Version**: Use custom tag
5. **Emergency**: Use `latest` for quick rollback

## 🚨 **Emergency Rollback Procedures**

### **Critical Production Issues**
1. **Immediate Action**:
   - Go to GitHub Actions
   - Select "Rollback Production"
   - Choose `latest` tag (most recent)
   - Confirm rollback
   - Monitor progress

2. **If Rollback Fails**:
   - SSH to production server
   - Manually stop containers
   - Manually start previous working containers
   - Notify team immediately

### **Staging Issues**
1. **Quick Rollback**:
   - Use "Rollback Staging" workflow
   - Choose appropriate tag
   - Confirm rollback
   - Monitor progress

## 📊 **Rollback Safety Features**

### **1. Image Verification**
- ✅ **Pre-rollback Check**: Verifies image exists in Docker Hub
- ✅ **Error Prevention**: Prevents rollback to non-existent images
- ✅ **Tag Discovery**: Shows available tags if image not found

### **2. Confirmation Required**
- ✅ **Staging**: Must confirm rollback
- ✅ **Production**: Must confirm + URGENT warning
- ✅ **No Accidental Rollbacks**: Prevents mistakes

### **3. Comprehensive Logging**
- ✅ **Detailed Logs**: Every step is logged
- ✅ **Slack Notifications**: Immediate status updates
- ✅ **Audit Trail**: Who, what, when, why

## 🔧 **Rollback Workflow Configuration**

### **Staging Rollback Inputs**
```yaml
image_tag:
  description: 'Docker image tag to rollback to'
  required: true
  type: choice
  options:
  - latest
  - develop
  - sha-latest
  - custom

custom_tag:
  description: 'Custom image tag (if "custom" is selected)'
  required: false
  type: string

confirm_rollback:
  description: 'Confirm you want to rollback staging'
  required: true
  type: boolean
  default: false
```

### **Production Rollback Inputs**
```yaml
image_tag:
  description: 'Docker image tag to rollback to'
  required: true
  type: choice
  options:
  - latest
  - develop
  - sha-latest
  - custom

custom_tag:
  description: 'Custom image tag (if "custom" is selected)'
  required: false
  type: string

confirm_rollback:
  description: 'Confirm you want to rollback production (URGENT)'
  required: true
  type: boolean
  default: false
```

## 📱 **Slack Notifications**

### **Staging Rollback Success**
```
🔄 Staging Rollback Successful
Environment: Staging
Rolled back to: fiftyeight/jgw-pandas-staging:sha-abc123
Branch: develop
Commit: def456ghi789
Rolled back by: username
Triggered by: manual-rollback
✅ Staging has been rolled back successfully!
```

### **Production Rollback Success**
```
🔄 Production Rollback Successful
Environment: Production
Rolled back to: fiftyeight/jgw-pandas-staging:sha-abc123
Branch: develop
Commit: def456ghi789
Rolled back by: username
Triggered by: manual-rollback
✅ Production has been rolled back successfully!
🚨 This is now LIVE in production!
```

### **Rollback Failure**
```
❌ Production Rollback Failed
Environment: Production
Attempted rollback to: fiftyeight/jgw-pandas-staging:sha-abc123
Branch: develop
Commit: def456ghi789
Rolled back by: username
Triggered by: manual-rollback
🚨 CRITICAL: Production rollback failed!
IMMEDIATE ACTION REQUIRED!
```

## 🔍 **Troubleshooting Rollbacks**

### **Common Issues**

#### **1. Image Not Found**
- **Error**: "Image not found in Docker Hub"
- **Solution**: Use "List Available Image Tags" workflow
- **Prevention**: Verify image exists before rollback

#### **2. SSH Connection Failed**
- **Error**: "SSH connection failed"
- **Solution**: Check SSH keys and server access
- **Prevention**: Test SSH connection regularly

#### **3. Container Startup Failed**
- **Error**: "Container startup failed"
- **Solution**: Check server resources and logs
- **Prevention**: Monitor server health

#### **4. Docker Compose Update Failed**
- **Error**: "Failed to update docker-compose file"
- **Solution**: Check file permissions and syntax
- **Prevention**: Regular file validation

### **Debugging Steps**

1. **Check GitHub Actions Logs**
   - Go to Actions tab
   - Click on failed rollback
   - Review step logs

2. **Check Server Status**
   - SSH to target server
   - Check Docker containers: `docker ps -a`
   - Check logs: `docker logs <container_name>`

3. **Verify Image Availability**
   - Use "List Available Image Tags" workflow
   - Check Docker Hub directly
   - Verify image permissions

## 🎯 **Best Practices**

### **1. Pre-Rollback**
- ✅ **Identify Issue**: Understand what went wrong
- ✅ **Choose Target**: Select appropriate rollback version
- ✅ **Test in Staging**: Rollback staging first if possible
- ✅ **Notify Team**: Inform team of rollback plan

### **2. During Rollback**
- ✅ **Monitor Progress**: Watch GitHub Actions logs
- ✅ **Check Slack**: Monitor Slack notifications
- ✅ **Verify Services**: Check if services are running
- ✅ **Be Ready**: Prepare for manual intervention if needed

### **3. Post-Rollback**
- ✅ **Verify Functionality**: Test critical features
- ✅ **Monitor Metrics**: Watch application metrics
- ✅ **Document Issue**: Record what went wrong
- ✅ **Plan Fix**: Prepare proper fix for next deployment

## 🚀 **Quick Reference**

### **Emergency Commands**
```bash
# List available tags
curl -s "https://hub.docker.com/v2/repositories/fiftyeight/jgw-pandas-staging/tags/?page_size=10" | jq -r '.results[].name'

# Check container status
docker ps -a

# Check container logs
docker logs <container_name>

# Manual rollback (emergency)
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml up -d
```

### **Workflow URLs**
- **Staging Rollback**: `/actions/workflows/rollback-staging.yml`
- **Production Rollback**: `/actions/workflows/rollback-production.yml`
- **List Tags**: `/actions/workflows/list-image-tags.yml`

This rollback pipeline provides a robust, safe, and efficient way to handle deployment issues and maintain system stability! 🚀
