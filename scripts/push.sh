# Name of the project
PROJECT=pop

# Registery where images are pushed
REGISTRY=centreonlabs

# Images are tagged with the project version
TAG=$(poetry version -s)

# Login to the registry
docker login

# Set the image name
IMAGE="$REGISTRY/$PROJECT:$TAG"

# Push the image
docker push $IMAGE






