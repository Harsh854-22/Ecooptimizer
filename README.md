# EcoOptimizer
In the simplest sense, EcoOptimizer is a system that uses AI to help cloud servers use energy more efficiently. It looks at data to predict when there will be high or low demand on the servers, then adjusts how many servers are working based on that. When demand is low, it can turn off some servers to save energy, and when demand is high, it makes sure enough servers are running to handle it smoothly. This way, EcoOptimizer reduces wasted energy and keeps things running efficiently.
Have a look...
![image](https://github.com/user-attachments/assets/65a98cab-dce7-4b6f-b868-975ac42dedff)
![image](https://github.com/user-attachments/assets/f15014ac-0dd8-437a-ac4f-7a0e131c02a7)
![image](https://github.com/user-attachments/assets/a00df8b8-bddc-423f-80d1-fee9f832d59b)
How to use it:
1. Download ZIP/Git clone
2. I used python 3.12.6
3. pip install flask celery redis plotly dash pandas scikit-learn
4. Download and run redis(https://github.com/MicrosoftArchive/redis/releases)
5. celery -A celery_worker worker --loglevel=info
6. python dash_app.py(run in different terminal)
7. python app.py
