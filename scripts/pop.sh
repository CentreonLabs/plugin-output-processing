#!/bin/bash

# This script prompts the user to input plugin output text, URL encodes the input,
# and sends it to a specified API endpoint for explanation. The response from the
# API is then formatted and displayed to the user.

# Prompt the user to input text
read -p "Enter plugin output you want to be explained: " input_text

echo
echo "----------"
echo

# URL encode the input text
encoded_text=$(echo -n "$input_text" | jq -s -R -r @uri)

api_endpoint="http://127.0.0.1:8000/explain"

# Make the GET request
response=$(curl -s "${api_endpoint}?type=service&output=${encoded_text}")

# replace return carriage and display the response
echo $response | sed 's/\\n/\n/g'
