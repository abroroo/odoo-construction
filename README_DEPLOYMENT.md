# 🏗️ Odoo Construction Management System - Phase 1

**Russian Specification Compliant Construction Management System**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/7b4a9d)

---

## 🎯 **What This System Provides**

This is a complete construction management system implementing **Phase 1 of Russian construction specifications**:

### ✅ **Supplier Workflow (Поставщик)**
- Project-based material delivery
- Automatic stock updates
- Catalog-based material selection
- Delivery tracking and documentation

### ✅ **Foreman Workflow (Прораб)**
- Project-restricted access
- **Task-first material consumption** (Russian compliance)
- Smeta task integration
- Additional task creation for non-smeta work

### ✅ **Task Management (Управление задачами)**
- Automatic task generation from smeta files
- Visual distinction: Blue (smeta) vs Orange (additional)
- Progress tracking: To Do → In Progress → Done
- Project completion percentages

---

## 🚀 **Quick Deploy (FREE)**

### **Option 1: Railway.app (Recommended)**
1. **Fork this repository** to your GitHub
2. **Sign up** at [Railway.app](https://railway.app) (free)
3. **Create new project** → **Deploy from GitHub**
4. **Add PostgreSQL database** (free)
5. **Deploy!** - Railway handles everything automatically

### **Option 2: One-Click Deploy**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/7b4a9d)

---

## 📋 **What's Included**

### **Custom Modules:**
- `construction_warehouse` - Physical warehouse management
- `construction_smeta_task_integration` - Russian smeta compliance
- `construction_mobile_manager` - Mobile dashboard
- `construction_business` - Core business logic

### **Key Features:**
- **Multi-project support** with isolation
- **Role-based security** (Admin, Foreman, Supplier)
- **Russian language support**
- **Excel smeta import** with automatic task creation
- **Real-time progress tracking**
- **Mobile-optimized interface**

---

## 📖 **Documentation**

- **[USER_GUIDE_PHASE1.md](USER_GUIDE_PHASE1.md)** - Complete step-by-step user workflows
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Detailed deployment instructions
- **[SYSTEM_SPECIFICATION.md](SYSTEM_SPECIFICATION.md)** - Technical requirements

---

## 🏃‍♂️ **Quick Start**

### **After Deployment:**

1. **Access your app** at your Railway URL
2. **Create database** with name `construction_business`
3. **Install modules** in this order:
   - Construction Material Management
   - Construction Warehouse Management
   - Construction Smeta Task Integration
4. **Create users** and **assign roles**
5. **Follow USER_GUIDE_PHASE1.md** for workflows

### **Test Data:**
- Import sample smeta files from `demo/` directory
- Create test projects and warehouses
- Try all workflows with sample data

---

## 💰 **Free Tier Resources**

### **Railway.app Free Tier:**
- ✅ **500 hours/month** (about 16 hours/day)
- ✅ **Free PostgreSQL database**
- ✅ **1GB RAM, 1 vCPU**
- ✅ **Automatic HTTPS & custom domains**
- ✅ **No credit card required initially**

**Perfect for:**
- Small construction teams (5-20 users)
- Development and testing
- Proof of concept deployments
- Regional construction projects

---

## 🔧 **Configuration**

### **Environment Variables:**
```bash
HOST=your_postgres_host
USER=your_postgres_user
PASSWORD=your_postgres_password
DB_NAME=construction_business
DB_PORT=5432
PORT=8069
ADMIN_PASSWORD=your_secure_password
```

### **Production Settings:**
- ✅ SSL/HTTPS enabled
- ✅ Database security configured
- ✅ Performance optimized for free tier
- ✅ Logging and monitoring ready

---

## 🎯 **Phase 1 Compliance**

This system **100% implements** the Russian Phase 1 specification:

| Requirement | Status |
|-------------|---------|
| Supplier material delivery workflow | ✅ Complete |
| Foreman project-restricted access | ✅ Complete |
| Task-centric material consumption | ✅ Complete |
| Automatic smeta → task generation | ✅ Complete |
| Progress tracking with percentages | ✅ Complete |
| Additional task creation and marking | ✅ Complete |
| Russian language compliance | ✅ Complete |

---

## 📱 **Mobile Support**

- ✅ **Responsive design** for tablets and phones
- ✅ **Touch-optimized** material consumption
- ✅ **Offline-ready** for construction sites
- ✅ **Photo upload** for material documentation

---

## 🔒 **Security Features**

- ✅ **Role-based access control**
- ✅ **Project-level data isolation**
- ✅ **Secure authentication**
- ✅ **Audit trails** for all material movements
- ✅ **Russian format logging**

---

## 🚀 **What's Next**

### **Phase 2 Roadmap:**
- Advanced reporting and analytics
- Integration with accounting systems
- Mobile app for offline usage
- Advanced workflow automation
- Multi-warehouse transfers

### **Scaling Options:**
- **Upgrade Railway plan** for more resources
- **Add team members** with role assignments
- **Import production smeta files**
- **Customize workflows** for your processes

---

## 🆘 **Support**

### **Getting Help:**
1. **Check the documentation** - comprehensive guides included
2. **Review logs** - Railway provides detailed application logs
3. **Test with sample data** - verify all workflows work
4. **Community support** - Odoo has extensive community

### **Common Issues:**
- **Build errors**: Check Dockerfile and dependencies
- **Database connection**: Verify environment variables
- **Module loading**: Ensure proper installation order
- **Performance**: Monitor usage and upgrade if needed

---

## 📊 **Technical Stack**

- **Backend**: Odoo 17 Community Edition
- **Database**: PostgreSQL
- **Frontend**: Odoo Web Client (responsive)
- **Languages**: Python, JavaScript, XML
- **Deployment**: Docker containers
- **Platform**: Railway.app (or other cloud providers)

---

## 🎉 **Ready to Deploy!**

Your complete **Russian Phase 1 compliant** construction management system is ready for production deployment.

**Click the deploy button above or follow the DEPLOYMENT_GUIDE.md for step-by-step instructions.**

---

## 📄 **License**

This project is built on Odoo Community Edition (LGPL-3.0). Custom modules and modifications are available under the same license.

---

**🏗️ Built for Russian construction teams who need reliable, specification-compliant project management! 🇷🇺**