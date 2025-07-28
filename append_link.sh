#!/bin/bash

# Usage: append_link.sh <draft_file_path> <formatted_link> <url>
DRAFT_FILE="$1"
FORMATTED_LINK="$2"
URL="$3"

# Function to determine which section a URL belongs to
determine_section() {
    local url="$1"
    local domain=$(echo "$url" | awk -F[/:] '{print $4}')
    
    # Check for specific patterns in URL or domain
    if [[ "$url" =~ (agile|scrum|product|leadership|management|team|culture|communication) ]]; then
        echo "agile"
    elif [[ "$url" =~ (github\.com|gitlab\.com|bitbucket) ]]; then
        echo "tools"
    elif [[ "$url" =~ (devops|kubernetes|k8s|docker|monitoring|observability|security|prometheus|grafana|terraform|ansible|jenkins|ci\/cd|cicd) ]]; then
        echo "devops"
    elif [[ "$url" =~ (architecture|development|software|programming|api|microservice|design-pattern|refactor|testing|code|developer|engineering) ]]; then
        echo "development"
    else
        # Default section based on common domains
        case "$domain" in
            *medium.com*)
                # Check if it's about leadership/management
                if [[ "$url" =~ (leadership|management|team|culture) ]]; then
                    echo "agile"
                else
                    echo "development"
                fi
                ;;
            *github.com*|*gitlab.com*)
                echo "tools"
                ;;
            *redhat.com*|*microsoft.com*|*aws.amazon.com*|*cloud.google.com*)
                echo "devops"
                ;;
            *)
                # Default to development section
                echo "development"
                ;;
        esac
    fi
}

# Function to check if link already exists in file
link_exists() {
    local file="$1"
    local url="$2"
    grep -q "$url" "$file"
    return $?
}

# Check if draft file exists
if [ ! -f "$DRAFT_FILE" ]; then
    echo "Error: Draft file not found: $DRAFT_FILE"
    exit 1
fi

# Check if link already exists
if link_exists "$DRAFT_FILE" "$URL"; then
    echo "Link already exists in draft"
    exit 0
fi

# Determine which section to add the link to
SECTION=$(determine_section "$URL")

# Create a temporary file
TEMP_FILE=$(mktemp)

# Process the file and add the link to the appropriate section
case "$SECTION" in
    "agile")
        SECTION_HEADER="## Agile, Leadership and Product"
        ;;
    "development")
        SECTION_HEADER="## Architecture, Development & Software development practices"
        ;;
    "devops")
        SECTION_HEADER="## DevOps, Observability & Security"
        ;;
    "tools")
        SECTION_HEADER="## Tools and things from Github"
        ;;
esac

# Flag to track if we've added the link
LINK_ADDED=false

# Read the file line by line and add the link in the appropriate section
while IFS= read -r line; do
    echo "$line" >> "$TEMP_FILE"
    
    # If we find the target section header and haven't added the link yet
    if [[ "$line" == "$SECTION_HEADER"* ]] && [ "$LINK_ADDED" = false ]; then
        # Read the next line (should be empty or contain existing links)
        if IFS= read -r next_line; then
            if [[ -z "$next_line" ]]; then
                # Empty line after header, add our link
                echo "" >> "$TEMP_FILE"
                echo "$FORMATTED_LINK" >> "$TEMP_FILE"
                LINK_ADDED=true
            elif [[ "$next_line" =~ ^-[[:space:]] ]] || [[ "$next_line" =~ ^\[[^]]+\] ]]; then
                # There are already links, add to the beginning of the section
                echo "" >> "$TEMP_FILE"
                echo "$FORMATTED_LINK" >> "$TEMP_FILE"
                echo "$next_line" >> "$TEMP_FILE"
                LINK_ADDED=true
            else
                # Just write the next line as is
                echo "$next_line" >> "$TEMP_FILE"
            fi
        fi
    fi
done < "$DRAFT_FILE"

# If we couldn't find the section, add it to favorites
if [ "$LINK_ADDED" = false ]; then
    # Try to add to favorites section
    TEMP_FILE2=$(mktemp)
    LINK_ADDED=false
    
    while IFS= read -r line; do
        echo "$line" >> "$TEMP_FILE2"
        
        if [[ "$line" == "# My favorites"* ]] && [ "$LINK_ADDED" = false ]; then
            # Read the next line
            if IFS= read -r next_line; then
                if [[ -z "$next_line" ]]; then
                    # Empty line after header, add our link
                    echo "" >> "$TEMP_FILE2"
                    echo "$FORMATTED_LINK" >> "$TEMP_FILE2"
                    LINK_ADDED=true
                elif [[ "$next_line" =~ ^-[[:space:]] ]]; then
                    # There are already links, add after them
                    echo "$next_line" >> "$TEMP_FILE2"
                    echo "$FORMATTED_LINK" >> "$TEMP_FILE2"
                    LINK_ADDED=true
                else
                    echo "$next_line" >> "$TEMP_FILE2"
                fi
            fi
        fi
    done < "$TEMP_FILE"
    
    mv "$TEMP_FILE2" "$TEMP_FILE"
fi

# Replace the original file with the updated one
mv "$TEMP_FILE" "$DRAFT_FILE"

echo "Link added to $SECTION section"