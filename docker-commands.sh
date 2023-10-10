cd server/
docker build --no-cache -t image_fastapi .
cd ../client/
docker build --no-cache -t image_streamlit .
cd ..
docker compose up -d