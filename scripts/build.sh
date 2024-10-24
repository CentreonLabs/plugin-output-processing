# Name of the project
PROJECT=pop

# Registery where images are pushed
REGISTRY=centreonlabs

# Images are tagged with the project version
TAG=$(poetry version -s)

# Build the image
IMAGE="$REGISTRY/$PROJECT:$TAG"
echo
echo -e "Building image \e[34m$IMAGE\e[0m ..."
echo
docker build -t $IMAGE .
