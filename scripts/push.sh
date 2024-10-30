# Name of the project
PROJECT=pop

# Registery where images are pushed
REGISTRY=centreonlabs

# Images are tagged with the project version
TAG=$(poetry version -s)

# Login to the registry
echo
docker login

# Set the image name
IMAGE="$REGISTRY/$PROJECT"

# Push the image
echo
echo -e "Pushing image \e[34m$IMAGE:$TAG (latest) \e[0m ..."
echo
docker push $IMAGE
docker push "$IMAGE:$TAG"






