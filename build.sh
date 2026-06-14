#!/usr/bin/env bash
# Render.com build script — installs all deps and builds the frontend

set -o errexit  # Exit on error

echo "=== Installing backend Python dependencies ==="
cd backend
pip install -r requirements.txt

echo "=== Installing frontend Node.js dependencies ==="
cd ../frontend
npm install

echo "=== Building frontend for production ==="
npm run build

echo "=== Copying frontend build to backend/static ==="
rm -rf ../backend/static
cp -r dist ../backend/static

echo "=== Build complete ==="
ls -la ../backend/static/
