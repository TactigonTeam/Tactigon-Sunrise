docker build -t sunrise_app .
docker run -d -p 5123:5123 -v sunrise_data:/data --name sunrise_app_container sunrise_app