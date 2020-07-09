aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 961070163841.dkr.ecr.us-east-2.amazonaws.com
docker build -t kursach .
docker tag kursach:latest 961070163841.dkr.ecr.us-east-2.amazonaws.com/kursach:latest
docker push 961070163841.dkr.ecr.us-east-2.amazonaws.com/kursach:latest
