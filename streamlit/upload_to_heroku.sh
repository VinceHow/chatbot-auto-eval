#!/usr/bin/env bash
export PATH="$PATH"

app="chatbot-auto-eval"
process_type="web"
initial_tag="chatbot-auto-eval/web"
heroku_registry_url="registry.heroku.com/$app/$process_type"

heroku container:login 
docker build --platform=linux/amd64 -t $initial_tag . | tee image.build.log
docker tag $initial_tag $heroku_registry_url
docker push $heroku_registry_url
heroku container:release --app chatbot-auto-eval web
