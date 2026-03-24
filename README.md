# 🧘‍♀️ KnowInMy

A smart, subscription-based yoga platform for clients, trainers, and students – integrating AI pose detection, personalized asana mapping, and dynamic plan flexibility.

---

## 📄 Description

**KnowInMy** is a yoga-centric SaaS platform built to streamline yoga training and monitoring through intelligent pose detection and role-based user experiences.

Initially designed to allow yoga trainers to train an AI model using body keypoints for pose recognition, the platform evolved into a full-fledged subscription-based system. It now supports client onboarding, trainer-student management, and customizable subscription plans.

---

## ✅ Problem It Solves

- Enables **remote yoga training** with real-time AI pose feedback.
- Helps **yoga institutions manage** clients, trainers, students, and subscriptions.
- Offers **customizable pricing** based on specific user requirements.

---

## 👤 Target Users

- Yoga training institutes or individual yoga coaches.
- Yoga students preferring guided self-practice at home.
- Clients managing multiple trainers and student cohorts.

---

## 🌟 Standout Features

- 🤖 AI-powered yoga pose recognition using body keypoints.
- 👥 Role-based access: **Client**, **Trainer**, **Student**.
- 🔁 Dynamic subscription management.
- 📞 Customizable plans via admin communication.
- 💳 Integrated with **Razorpay** for secure payments.

---

## 🚀 Installation / Setup Instructions

### 🔧 Clone the Repository

```bash
git clone https://github.com/yourusername/knowinmy.git
cd knowinmy
pip install -r requirements.txt
```

## 🧪 Usage

---

### 💡 Train AI Pose Model (Initial Version)

- Trainers upload **pose images** or **body keypoints** for various asanas.
- The system learns and stores **ideal body positions**.
- These trained positions are used as reference for future comparisons.

---

### 🧘‍♂️ Student Practice

- Students use their **webcam** to perform asanas.
- The system provides **real-time feedback** by comparing the student's pose with the trained model.
- **Pose similarity** is calculated to guide corrections and improvements.

---

### 🖥️ Admin/Client Panel

- Clients can **onboard trainers and students** using the admin panel.
- Subscription plans are created and assigned based on specific needs.
- Clients can communicate with the admin to **customize plans dynamically**.

---

### 💰 Subscription & Payment

Subscriptions are **flexible and dynamic**, based on:

- 📌 **Number of asanas**
- 📌 **Number of trainers/students**
- 📌 **Duration** (in months)

- Integrated with **Razorpay** for **secure online payments**.
- Admin can **dynamically customize plans** to suit the needs of each client.

---
## 📦 Technologies Used

### 🖥️ Languages
- Python
- JavaScript

### 🧰 Backend
- Django

### 🎨 Frontend
- HTMX
- HTML, CSS, JavaScript
- (Optional: React for future versions)

### 🗄️ Database
- PostgreSQL

### 🤖 AI / ML
- Pose detection using body keypoints
- Powered by MediaPipe or OpenCV

### 💳 Payment Gateway
- Razorpay

### 📦 Containerization
- Docker
- Docker Compose

### 🔄 Version Control
- Git

