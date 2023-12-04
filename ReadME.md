# Post Feature for Feed Feature 🥇

Simple implementation for Post Feature Where Users create accounts and confirm it via email confirmation.Users can create, read, update and delete posts.also users can like and unlike posts and comment on posts and edit and delete likes and comments.

## High-Level Design

![High-Level Design](./screenshots/post-feature-feed.drawio.png)

## Build Status

![Static Badge](https://img.shields.io/badge/Build_Status-Success-blue)
![Static Badge](https://img.shields.io/badge/Test_Coverage-95%25-green)
![Static Badge](https://img.shields.io/badge/CI_CD-Included-dark_green)

## Monitoring with Sentry

![Sentry Monitoring](./screenshots/monitoring.png)

## Logging with Logtail

![Logtail Logging](./screenshots/logging.png)

## How to Run Offline

Follow these steps to run the project offline:

1. **Clone the repository :**
```bash
   git clone https://github.com/mohamedramadan14/news-feed-posts-feature.git
```

2. **Create Virtual Environment :**
```bash
 python -m venv venv
 source venv/Scripts/activate [Windows]
 #OR
 source venv/bin/activate     [Linux/Mac]
```

3. **Install Dependencies :**
```bash
   pip install -r requirements.txt
```

4. **Fill the .env file :**
```bash
  cp .env.example .env
```

5. **Run the project :**
 ```bash
   cd socialmedia
   uvicorn main:app --reload
 ```
