# Nur
The self actualizing documentation framework that heals its knowledge gaps as naturally as a ray of light

## Rough thoughts
- add a confluence space (url credentials and update interval)
- Pulls the confluence space and stores it in an sqlite database
- Uses Kafka for all operations
- Vectorizes the confluence space pages and stores the embeds in a chroma db collection
- Listens on specific slack channels for questions relevant to its domain
- Uses the vectorized embeds to find the most similar pages to a question
- Creates an assistant with the relevant pages and allows it to engage to provide the answer if confident enough
- Gets user feedback to either increase confidence or decrease confidence
- If confidence is below a certain threashold the assistant will add the question to a trivia quizz and runs it with the specialist team and recommends the update in a confluence comment


## Setup
Create setup_and_run.sh

chmod +x setup_and_run.sh

````bash
#!/bin/bash

# Function to check and install Miniconda if necessary
check_miniconda() {
    if ! [ -x "$(command -v conda)" ]; then
        echo "Miniconda is not installed. Installing Miniconda..."
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
        bash miniconda.sh -b -p $HOME/miniconda
        export PATH="$HOME/miniconda/bin:$PATH"
        echo "Miniconda installed."
    else
        echo "Miniconda is already installed."
    fi
}

# Check if already in Nur directory with main.py
if [ -d "Nur" ] && [ -f "Nur/main.py" ]; then
    echo "Nur directory with main.py already exists. Skipping cloning."
    cd Nur
else
    # Clone the GitHub repository if Nur directory doesn't exist
    git clone https://github.com/MDGrey33/Nur.git
    cd Nur
fi

# Check if the Miniconda environment already exists
env_name="myenv"
if conda info --envs | grep -q "$env_name"; then
    echo "Miniconda environment '$env_name' already exists. Activating it."
else
    echo "Creating Miniconda environment '$env_name'."
    conda create -n "$env_name" python=3.8 -y
fi

# Activate the Miniconda environment
# Modify this depending on your shell compatibility
source activate "$env_name"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping Python dependencies installation."
fi

# Start the Docker containers
echo "Starting Docker containers."
docker-compose up --build
````

## Run
````bash
./utility/setup_and_run.sh
````
