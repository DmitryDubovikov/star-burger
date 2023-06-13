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

# Path to .env
env_file="./star_burger/.env"

if [ -f "$env_file" ]; then
    # Read file .env
    while IFS= read -r line; do
        # If comment or empty
        if [[ $line == \#* ]] || [[ -z "$line" ]]; then
            continue
        fi

        # Split line to name and value
        IFS='=' read -r var_name var_value <<< "$line"

        # Set environment variable
        export "$var_name=$var_value"
    done < "$env_file"

    curl -H "X-Rollbar-Access-Token: '$ROLLBAR_TOKEN'" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "qa", "revision": "'$commit_hash'", "rollbar_name": "john", "local_username": "circle-ci", "comment": "bash deployment", "status": "succeeded"}'
else
    echo "File .env not found. Cannot inform Rollbar about deploy."
fi

  