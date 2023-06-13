#!/bin/bash

set -e

directory_path="/opt/star-burger"
cd "$directory_path"

echo "Updating git-repo..."
git pull origin master

echo "Installing requirements..."
source venv/bin/activate
pip install -r requirements.txt

echo "Applying migrations..."
python3 ./manage.py migrate --noinput

echo "Collecting static..."
python3 ./manage.py collectstatic  --noinput

#deactivate

echo "Installing Node.js packages..."
#npm ci --dev

echo "Frontend building.."
#./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Reloading nginx..."
systemctl reload nginx

echo "Reloading star-burger..."
systemctl reload star-burger

commit_hash=$(git rev-parse --short HEAD)
echo "Deploy up to $commit_hash completed!"

curl -H "X-Rollbar-Access-Token: 9540da83eabf4faa828da369da00a78d" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "qa", "revision": "'$commit_hash'", "rollbar_name": "john", "local_username": "circle-ci", "comment": "bash deployment", "status": "succeeded"}'