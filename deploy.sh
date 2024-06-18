# Login to the registry
docker login

# Set the image name and tag
NAME=pop
TAG=$(poetry version -s)

# Build the image
docker build -t $NAME:$TAG .

# Tag the image
REGISTRY=centreondocker
docker tag $NAME:$TAG $REGISTRY/$NAME:$TAG

# Push the image
docker push $REGISTRY/$NAME:$TAG