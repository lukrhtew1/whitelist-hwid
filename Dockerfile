# Step 1: Use a base image with Python
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy all files from your local project into the container
COPY . /app

# Step 4: Install Python dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose the port (Render will automatically handle port management)
EXPOSE 8000

# Step 6: Command to run the Flask app (Python script)
CMD ["python", "app.py"]
