# Docker Image Retention Policy

## 🏗️ **Overview**

The build-and-push workflow now implements a smart image retention policy that keeps recent images for rollback purposes while cleaning up old ones to save storage space and costs.

## 📋 **Retention Policy**

### **What Gets Kept:**
- ✅ **Latest 2 Images**: Most recent builds for rollback
- ✅ **Protected Tags**: `latest` and `develop` (always kept)
- ✅ **Current Build**: The image being built in this workflow

### **What Gets Deleted:**
- ❌ **Older Images**: Images beyond the last 2 recent ones
- ❌ **Unused Tags**: Tags that are no longer needed
- ❌ **Failed Builds**: Images from failed deployments

## 🔧 **Configuration**

### **Current Settings:**
```yaml
# Number of recent images to keep for rollback
KEEP_RECENT_IMAGES: 2

# Tags that should never be deleted
PROTECTED_TAGS: "latest develop"

# Maximum tags to fetch from Docker Hub API
MAX_TAGS_FETCH: 100
```

### **How to Modify:**
Edit the configuration in `.github/workflows/build-and-push.yml`:

```bash
# Change number of recent images to keep
KEEP_RECENT_IMAGES=3  # Keep last 3 instead of 2

# Add more protected tags
PROTECTED_TAGS="latest develop staging"  # Add staging to protected tags

# Increase API fetch limit
MAX_TAGS_FETCH=200  # Fetch more tags if needed
```

## 📊 **Example Retention Behavior**

### **Before Cleanup:**
```
Tags in Docker Hub:
  • latest (protected)
  • develop (protected)
  • sha-abc123 (recent - keep)
  • sha-def456 (recent - keep)
  • sha-ghi789 (old - delete)
  • sha-jkl012 (old - delete)
  • pr-123 (old - delete)
```

### **After Cleanup:**
```
Tags Remaining:
  • latest (protected)
  • develop (protected)
  • sha-abc123 (recent - kept)
  • sha-def456 (recent - kept)
  • sha-xyz789 (new build - added)
```

## 🎯 **Benefits**

### **1. Rollback Safety**
- ✅ **Recent Images Available**: Always have last 2 builds for rollback
- ✅ **Protected Tags**: Critical tags never deleted
- ✅ **Quick Recovery**: Can rollback to recent working versions

### **2. Storage Optimization**
- ✅ **Reduced Storage**: Deletes old unused images
- ✅ **Cost Savings**: Lower Docker Hub storage costs
- ✅ **Clean Repository**: Keeps only relevant images

### **3. Performance**
- ✅ **Faster Builds**: Less images to process
- ✅ **Better Caching**: Focus on recent images
- ✅ **Cleaner Logs**: Less clutter in Docker Hub

## 🔄 **Rollback Scenarios**

### **Scenario 1: Recent Issue**
- **Current**: `sha-xyz789` (latest build)
- **Issue**: Bug in latest build
- **Rollback**: Use `sha-abc123` or `sha-def456` (kept recent images)
- **Result**: ✅ Quick rollback to working version

### **Scenario 2: Critical Issue**
- **Current**: `sha-xyz789` (latest build)
- **Issue**: Critical production bug
- **Rollback**: Use `latest` or `develop` (protected tags)
- **Result**: ✅ Emergency rollback to stable version

### **Scenario 3: Specific Version**
- **Current**: `sha-xyz789` (latest build)
- **Issue**: Need specific commit
- **Rollback**: Use `sha-abc123` (if still available)
- **Result**: ✅ Rollback to specific working version

## 📈 **Monitoring & Logs**

### **Build Logs Show:**
```
🧹 Cleaning up old images from Docker Hub...
📋 Retention policy: Keep last 2 images + protected tags (latest develop)
📊 Total tags in repository: 15

📋 Current tags (keeping last 2 + protected tags):
  • latest (updated: 2024-01-15T10:30:00Z)
  • develop (updated: 2024-01-15T10:30:00Z)
  • sha-abc123 (updated: 2024-01-15T09:15:00Z)
  • sha-def456 (updated: 2024-01-15T08:00:00Z)
  • sha-ghi789 (updated: 2024-01-14T16:45:00Z)

🗑️ Tags to delete (keeping last 2 for rollback):
  • sha-ghi789
  • sha-jkl012
  • pr-123

Deleting old tags...
Deleting tag: sha-ghi789
  ✅ Successfully deleted sha-ghi789
Deleting tag: sha-jkl012
  ✅ Successfully deleted sha-jkl012
Deleting tag: pr-123
  ✅ Successfully deleted pr-123

✅ Cleanup completed:
  • Kept last 2 images for rollback
  • Protected tags: latest develop
  • Total tags remaining: 5
```

### **Slack Notifications:**
```
🐳 Docker Image Built Successfully
Image: docker.io/fiftyeight/jgw-pandas-staging
Tags: latest,develop,sha-xyz789
Branch: develop
Commit: xyz789abc123
✨ Old images cleaned up, kept last 2 + latest + develop for rollback
🚀 Triggering staging deployment...
```

## 🚨 **Emergency Scenarios**

### **If Rollback Images Are Missing:**
1. **Check Protected Tags**: Use `latest` or `develop`
2. **Check Recent Builds**: Look for recent `sha-xxx` tags
3. **Manual Rollback**: Use Docker Hub directly if needed
4. **Rebuild**: Trigger new build if necessary

### **If Cleanup Fails:**
1. **Check Logs**: Review cleanup step logs
2. **Manual Cleanup**: Use Docker Hub web interface
3. **Retry Build**: Run workflow again
4. **Contact Support**: If persistent issues

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Authentication Failed**
```
❌ Failed to authenticate with Docker Hub
```
**Solution**: Check `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets

#### **2. API Rate Limit**
```
❌ Failed to fetch tags from Docker Hub
```
**Solution**: Wait and retry, or reduce `MAX_TAGS_FETCH`

#### **3. Tag Deletion Failed**
```
❌ Failed to delete sha-abc123: Permission denied
```
**Solution**: Check Docker Hub permissions, some tags may be protected

### **Debug Commands:**
```bash
# Check current tags
curl -s "https://hub.docker.com/v2/repositories/fiftyeight/jgw-pandas-staging/tags/?page_size=10" | jq -r '.results[].name'

# Check specific tag
curl -s "https://hub.docker.com/v2/repositories/fiftyeight/jgw-pandas-staging/tags/sha-abc123/"

# List all tags with dates
curl -s "https://hub.docker.com/v2/repositories/fiftyeight/jgw-pandas-staging/tags/?page_size=20" | jq -r '.results[] | "\(.name) - \(.last_updated)"'
```

## 📋 **Best Practices**

### **1. Regular Monitoring**
- ✅ **Check Build Logs**: Monitor cleanup success
- ✅ **Verify Rollback**: Test rollback scenarios
- ✅ **Review Storage**: Monitor Docker Hub usage

### **2. Configuration Management**
- ✅ **Adjust Retention**: Modify `KEEP_RECENT_IMAGES` as needed
- ✅ **Add Protected Tags**: Include important tags
- ✅ **Monitor Performance**: Adjust `MAX_TAGS_FETCH` if needed

### **3. Emergency Preparedness**
- ✅ **Know Protected Tags**: Always available for rollback
- ✅ **Test Rollback**: Regular rollback testing
- ✅ **Document Process**: Keep rollback procedures updated

This retention policy provides the perfect balance between rollback safety and storage efficiency! 🚀
