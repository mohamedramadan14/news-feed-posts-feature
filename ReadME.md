# Post Feature For Feed Feature (Social Media) 🥇



Simple implementation of a social media post feature.Users can sign up and activate their account via confirmation email. They can then create posts, comment on them and like them. 



## High-Level Design



![High-Level Design](./images/post-feature-feed.drawio.png)



## Build Status

![Static Badge](https://img.shields.io/badge/Build_Status-Sucess-blue) 
![Static Badge](https://img.shields.io/badge/Test_Coverage-94%25-green)
![Static Badge](https://img.shields.io/badge/CI_CD-Included-dark_green)



## Monitoring with Sentry



![Sentry Monitoring](./images/monitoring.png)



## Logging with Logtail



![Logtail Logging](./images/logging.png)



## How to Run Offline



Follow these steps to run the project offline:



1. Clone the repository:

 ```bash

   git clone https://github.com/mohamedramadan14/news-feed-posts-feature.git

```



2. Create Virtual Environment :

```bash

   python -m venv venv

   source venv/Scripts/activate [Windows] 

   # OR 

   source venv/bin/activate     [Linux/Mac]

```

3. Install Dependencies :

```bash

   pip install -r requirements.txt

```

4. Run the project :

```bash

   cd socialmedia

   uvicorn main:app --reload

```
